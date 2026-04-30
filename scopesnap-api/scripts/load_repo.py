"""
WS-A — Data Repo Loader
========================
Ingests ac_data_repo.json (v2.0) and SnapAI_HVAC_Master_Price_List_2026.xlsx
into the 9 new WS-A tables created by migration 007.

Usage (from the scopesnap-api directory, after running migration 007):
    python scripts/load_repo.py

    # Dry-run (schema check only, no DB writes):
    python scripts/load_repo.py --dry-run

Idempotent: each table is truncated and re-seeded on every run so re-running
after a data-repo update always produces the correct state.

Acceptance criteria (WS-A M1):
  - 15  rows in brands
  - 40  rows in parts_catalog
  - 19  rows in fault_cards
  - ≥159 rows in error_codes  (may be more after mini-split additions)
  - 19  rows × 3 tiers = 57 rows in pricing_tiers
  - 1   row in labor_rates_houston
  - 75  rows in legacy_model_prefixes
  - GET /api/repo/version returns {"version": "2.0"}
"""

import asyncio
import json
import sys
import re
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from db.database import AsyncSessionLocal

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_DIR = Path(__file__).parent.parent.parent.parent  # ScopeSnapAI/..
PERSONAL_CLAUDE = REPO_DIR.parent / "Personal Claude"

# Try multiple candidate paths for the data files
_REPO_JSON_CANDIDATES = [
    Path("/app/data/ac_data_repo.json"),                          # Railway container
    PERSONAL_CLAUDE / "ScopeSnapAI" / "ac_data_repo.json",
    Path(__file__).parent.parent.parent / "ac_data_repo.json",
    Path("/sessions/pensive-vigilant-cray/mnt/Personal Claude/ScopeSnapAI/ac_data_repo.json"),
]
_PRICE_LIST_CANDIDATES = [
    Path("/app/data/SnapAI_HVAC_Master_Price_List_2026.xlsx"),     # Railway container
    PERSONAL_CLAUDE / "SnapAI_HVAC_Master_Price_List_2026.xlsx",
    Path(__file__).parent.parent.parent / "SnapAI_HVAC_Master_Price_List_2026.xlsx",
    Path("/sessions/pensive-vigilant-cray/mnt/Personal Claude/SnapAI_HVAC_Master_Price_List_2026.xlsx"),
]

def _find_file(candidates):
    for p in candidates:
        if Path(p).exists():
            return Path(p)
    raise FileNotFoundError(
        f"Could not find file. Tried:\n" + "\n".join(str(c) for c in candidates)
    )


# ── Helpers ────────────────────────────────────────────────────────────────────
def _parse_labor(labor_str: str):
    """'0.4–0.75' → (0.4, 0.75, 0.575)"""
    if not labor_str:
        return None, None, None
    # Remove non-numeric / non-dash chars, normalise dash variants
    s = labor_str.replace("–", "-").replace("—", "-").strip()
    parts = re.split(r"[-–—]", s)
    try:
        lo = float(parts[0].strip())
        hi = float(parts[-1].strip())
        avg = round((lo + hi) / 2, 3)
        return lo, hi, avg
    except (ValueError, IndexError):
        return None, None, None


# ── Brand loader ───────────────────────────────────────────────────────────────
async def load_brands(db, data: dict) -> int:
    await db.execute(text("TRUNCATE brands CASCADE"))
    brands = data["brands"]
    for b in brands:
        await db.execute(
            text("""
                INSERT INTO brands
                    (id, name, parent_company, sister_brands, houston_prevalence,
                     manufactured_in_tx, series, legacy_model_prefixes, legacy_years,
                     legacy_refrigerant, legacy_notes)
                VALUES
                    (:id, :name, :parent_company, :sister_brands, :houston_prevalence,
                     :manufactured_in_tx, CAST(:series AS jsonb), :legacy_model_prefixes,
                     :legacy_years, :legacy_refrigerant, :legacy_notes)
            """),
            {
                "id": b["id"],
                "name": b["name"],
                "parent_company": b.get("parent_company"),
                "sister_brands": b.get("sister_brands"),
                "houston_prevalence": b.get("houston_prevalence"),
                "manufactured_in_tx": b.get("manufactured_in_tx", False),
                "series": json.dumps(b.get("series", [])),
                "legacy_model_prefixes": b.get("legacy_model_prefixes"),
                "legacy_years": b.get("legacy_years"),
                "legacy_refrigerant": b.get("legacy_refrigerant"),
                "legacy_notes": b.get("legacy_notes"),
            },
        )
    print(f"  ✓ brands: {len(brands)} rows")
    return len(brands)


# ── Parts catalog loader ───────────────────────────────────────────────────────
async def load_parts(db, data: dict) -> int:
    await db.execute(text("TRUNCATE parts_catalog CASCADE"))
    parts = data["parts_catalog"]
    for p in parts:
        await db.execute(
            text("""
                INSERT INTO parts_catalog
                    (id, name, category, fault_cards, description,
                     part_cost_wholesale, part_cost_retail,
                     total_installed_houston, labor_hours)
                VALUES
                    (:id, :name, :category, :fault_cards, :description,
                     CAST(:part_cost_wholesale AS jsonb),
                     CAST(:part_cost_retail AS jsonb),
                     CAST(:total_installed_houston AS jsonb),
                     CAST(:labor_hours AS jsonb))
            """),
            {
                "id": p["id"],
                "name": p["name"],
                "category": p.get("category"),
                "fault_cards": p.get("fault_cards") if isinstance(p.get("fault_cards"), list) else None,
                "description": p.get("description"),
                "part_cost_wholesale": json.dumps(p.get("part_cost_wholesale", {})),
                "part_cost_retail": json.dumps(p.get("part_cost_retail", {})),
                "total_installed_houston": json.dumps(p.get("total_installed_houston", {})),
                "labor_hours": json.dumps(p.get("labor_hours", {})),
            },
        )
    print(f"  ✓ parts_catalog: {len(parts)} rows")
    return len(parts)


# ── Fault cards loader ─────────────────────────────────────────────────────────
async def load_fault_cards(db, data: dict, price_rows: list) -> int:
    await db.execute(text("TRUNCATE fault_cards CASCADE"))
    cards = data["fault_card_estimates"]

    # Build price list lookup keyed by card_id (int)
    price_map = {}
    for row in price_rows:
        card_num = row[0]
        if isinstance(card_num, int):
            price_map[card_num] = row

    for c in cards:
        lo, hi, avg = _parse_labor(
            f"{c['labor_hours']['min']}-{c['labor_hours']['max']}"
        )
        pl = price_map.get(c["card_id"], {})
        # price_rows tuple indices: 0=card#, 1=name, 2=freq, 3=primary_parts,
        # 4=optional, 5=labor_str, 6=min, 7=typical, 8=max, 9=phase,
        # 10=difficulty, 11=marks_notes
        await db.execute(
            text("""
                INSERT INTO fault_cards
                    (card_id, card_name, houston_frequency_pct,
                     primary_parts, optional_parts,
                     labor_hours_min, labor_hours_max, labor_hours_avg,
                     estimate_min, estimate_typical, estimate_max,
                     price_list_min, price_list_typical, price_list_max,
                     price_list_primary_parts, price_list_optional_parts,
                     price_list_labor_hours, marks_field_notes,
                     phase, difficulty, tech_notes)
                VALUES
                    (:card_id, :card_name, :houston_freq,
                     :primary_parts, :optional_parts,
                     :labor_min, :labor_max, :labor_avg,
                     :est_min, :est_typical, :est_max,
                     :pl_min, :pl_typical, :pl_max,
                     :pl_primary, :pl_optional, :pl_labor, :marks_notes,
                     :phase, :difficulty, :tech_notes)
            """),
            {
                "card_id": c["card_id"],
                "card_name": c["card_name"],
                "houston_freq": c.get("houston_frequency_pct"),
                "primary_parts": c.get("primary_parts"),
                "optional_parts": c.get("optional_parts"),
                "labor_min": lo or c["labor_hours"].get("min"),
                "labor_max": hi or c["labor_hours"].get("max"),
                "labor_avg": avg or c["labor_hours"].get("average"),
                "est_min": c.get("total_estimate_houston", {}).get("min"),
                "est_typical": c.get("total_estimate_houston", {}).get("typical"),
                "est_max": c.get("total_estimate_houston", {}).get("max"),
                "pl_min": pl[6] if pl else None,
                "pl_typical": pl[7] if pl else None,
                "pl_max": pl[8] if pl else None,
                "pl_primary": pl[3] if pl else None,
                "pl_optional": pl[4] if pl else None,
                "pl_labor": pl[5] if pl else None,
                "marks_notes": pl[11] if pl else None,
                "phase": c.get("phase"),
                "difficulty": c.get("difficulty"),
                "tech_notes": c.get("tech_notes"),
            },
        )
    print(f"  ✓ fault_cards: {len(cards)} rows")
    return len(cards)


# ── Pricing tiers loader ───────────────────────────────────────────────────────
async def load_pricing_tiers(db, price_rows: list) -> int:
    await db.execute(text("TRUNCATE pricing_tiers CASCADE"))
    count = 0
    for row in price_rows:
        card_id = row[0]
        if not isinstance(card_id, int):
            continue
        # A=min, B=typical, C=max (Decision D-8)
        for tier, amount in [("A", row[6]), ("B", row[7]), ("C", row[8])]:
            if amount is None:
                amount = 0
            await db.execute(
                text("""
                    INSERT INTO pricing_tiers (card_id, tier, estimate_amount)
                    VALUES (:card_id, :tier, :amount)
                    ON CONFLICT ON CONSTRAINT uq_pricing_tier_card_tier
                    DO UPDATE SET estimate_amount = EXCLUDED.estimate_amount
                """),
                {"card_id": card_id, "tier": tier, "amount": amount},
            )
            count += 1
    print(f"  ✓ pricing_tiers: {count} rows  (19 cards × 3 tiers = 57 expected)")
    return count


# ── Error codes loader ─────────────────────────────────────────────────────────
async def load_error_codes(db, data: dict) -> int:
    await db.execute(text("TRUNCATE error_codes CASCADE"))
    edb = data["error_code_db"]
    brands_edb = edb.get("brands", {})

    # Standalone mini-split brand keys at the top level of error_code_db
    # (lg, samsung, gree, pioneer, mrcool, bosch)
    mini_split_keys = {"lg", "samsung", "gree", "pioneer", "mrcool", "bosch"}

    total = 0

    def _insert_codes(brand_family, brand_family_members, subsystem, codes_list):
        return [
            {
                "brand_family": brand_family,
                "brand_family_members": brand_family_members,
                "subsystem": subsystem,
                "error_code": c.get("code", ""),
                "meaning": c.get("meaning") or c.get("description"),
                "severity": c.get("severity"),
                "action": c.get("action") or c.get("recommendation"),
                "decision_tree_card": c.get("decision_tree_card"),
            }
            for c in codes_list
            if isinstance(c, dict) and c.get("code")
        ]

    rows_to_insert = []

    # ── 8 standard brand families ────────────────────────────────────────────
    for brand_key, brand_val in brands_edb.items():
        if not isinstance(brand_val, dict):
            continue
        members = brand_val.get("brand_ids", [])
        # Each brand family has subsystem keys (led_flash_system,
        # communicating_infinity, error_code_list, etc.) each with a "codes" list
        for subsys_key, subsys_val in brand_val.items():
            if subsys_key in ("brand_ids",):
                continue
            if isinstance(subsys_val, dict):
                codes_list = subsys_val.get("codes", [])
                if codes_list:
                    rows_to_insert.extend(
                        _insert_codes(brand_key, members, subsys_key, codes_list)
                    )
            elif isinstance(subsys_val, list):
                rows_to_insert.extend(
                    _insert_codes(brand_key, members, subsys_key, subsys_val)
                )

    # ── Standalone mini-split brands ──────────────────────────────────────────
    for brand_key in mini_split_keys:
        brand_data = edb.get(brand_key)
        if not brand_data:
            continue
        if isinstance(brand_data, list):
            rows_to_insert.extend(
                _insert_codes(brand_key, [brand_key], "mini_split", brand_data)
            )
        elif isinstance(brand_data, dict):
            for subsys_key, subsys_val in brand_data.items():
                if isinstance(subsys_val, list):
                    rows_to_insert.extend(
                        _insert_codes(brand_key, [brand_key], subsys_key, subsys_val)
                    )
                elif isinstance(subsys_val, dict):
                    codes_list = subsys_val.get("codes", [])
                    if codes_list:
                        rows_to_insert.extend(
                            _insert_codes(brand_key, [brand_key], subsys_key, codes_list)
                        )

    for row in rows_to_insert:
        await db.execute(
            text("""
                INSERT INTO error_codes
                    (brand_family, brand_family_members, subsystem,
                     error_code, meaning, severity, action, decision_tree_card)
                VALUES
                    (:brand_family, :brand_family_members, :subsystem,
                     :error_code, :meaning, :severity, :action, :decision_tree_card)
            """),
            row,
        )
        total += 1

    print(f"  ✓ error_codes: {total} rows  (≥159 expected)")
    return total


# ── Labor rates loader ─────────────────────────────────────────────────────────
async def load_labor_rates(db, data: dict) -> int:
    await db.execute(text("TRUNCATE labor_rates_houston CASCADE"))
    lr = data["labor_rates_houston"]
    await db.execute(
        text("""
            INSERT INTO labor_rates_houston
                (version, standard_hourly_min, standard_hourly_max,
                 flat_rate_note, after_hours_premium, emergency_weekend_premium,
                 attic_premium_min, attic_premium_max, attic_premium_note,
                 r22_surcharge_min, r22_surcharge_max, effective_date)
            VALUES
                (:version, :hr_min, :hr_max,
                 :flat_note, :after_hours, :emergency,
                 :attic_min, :attic_max, :attic_note,
                 :r22_min, :r22_max, :eff_date)
        """),
        {
            "version": data["metadata"]["version"],
            "hr_min": lr["standard_hourly"]["min"],
            "hr_max": lr["standard_hourly"]["max"],
            "flat_note": lr.get("flat_rate_note"),
            "after_hours": lr.get("after_hours_premium"),
            "emergency": lr.get("emergency_weekend_premium"),
            "attic_min": lr.get("attic_work_premium", {}).get("min"),
            "attic_max": lr.get("attic_work_premium", {}).get("max"),
            "attic_note": lr.get("attic_work_premium", {}).get("note"),
            "r22_min": lr.get("r22_handling_surcharge", {}).get("min"),
            "r22_max": lr.get("r22_handling_surcharge", {}).get("max"),
            "eff_date": date.today().isoformat(),
        },
    )
    print("  ✓ labor_rates_houston: 1 row")
    return 1


# ── Legacy prefixes loader ─────────────────────────────────────────────────────
async def load_legacy_prefixes(db, data: dict) -> int:
    await db.execute(text("TRUNCATE legacy_model_prefixes CASCADE"))
    lmp = data["legacy_model_prefix_lookup"]
    lookup = lmp.get("lookup_table", {})
    count = 0
    for prefix, entry in lookup.items():
        if isinstance(entry, dict):
            await db.execute(
                text("""
                    INSERT INTO legacy_model_prefixes
                        (prefix, brand_id, brand_name, years,
                         refrigerant, series_name, notes)
                    VALUES
                        (:prefix, :brand_id, :brand_name, :years,
                         :refrigerant, :series_name, :notes)
                """),
                {
                    "prefix": prefix,
                    "brand_id": entry.get("brand_id") or entry.get("brand"),
                    "brand_name": entry.get("brand_name") or entry.get("brand"),
                    "years": entry.get("years") or entry.get("legacy_years"),
                    "refrigerant": entry.get("refrigerant"),
                    "series_name": entry.get("series") or entry.get("series_name"),
                    "notes": entry.get("notes"),
                },
            )
            count += 1
        elif isinstance(entry, str):
            # Simple string value — store as notes
            await db.execute(
                text("""
                    INSERT INTO legacy_model_prefixes (prefix, notes)
                    VALUES (:prefix, :notes)
                """),
                {"prefix": prefix, "notes": entry},
            )
            count += 1
    print(f"  ✓ legacy_model_prefixes: {count} rows  (75 expected)")
    return count


# ── Lifecycle rules loader ─────────────────────────────────────────────────────
async def load_lifecycle_rules(db) -> int:
    """
    Hardcoded domain rules derived from HVAC field knowledge and the diagnostic
    guide (Part 5 — AI Model Strategy).  These map component age + condition
    signals → recommended A/B/C tier.
    """
    await db.execute(text("TRUNCATE lifecycle_rules CASCADE"))
    rules = [
        # Capacitor (Card 1) — replace (C) if unit 7+ yrs and pitting visible
        ("run_capacitor", 1, 7, "photo_confirmed_pitting", "C",
         "Unit ≥7 yr with photo-confirmed pitting → recommend full replace (C tier)"),
        ("run_capacitor", 1, 2, "under_warranty", "A",
         "Unit ≤2 yr under warranty → Min repair (A tier)"),
        ("run_capacitor", 1, None, "default", "B",
         "Default capacitor recommendation — Typical (B tier)"),
        # Contactor (Card 3)
        ("contactor", 3, 7, "photo_confirmed_pitting", "C",
         "7+ yr unit with pitted contacts → replace contactor (C tier)"),
        ("contactor", 3, None, "default", "B",
         "Default contactor recommendation"),
        # Blower motor (Card 4)
        ("blower_motor", 4, 10, "bearing_noise", "C",
         "10+ yr unit with bearing noise → full ECM replacement (C tier)"),
        ("blower_motor", 4, None, "default", "B",
         "Default blower motor recommendation"),
        # Drain system (Card 5)
        ("drain_system", 5, None, "recurring_clog", "C",
         "Recurring drain clog → full drain pan clean + UV tab install (C tier)"),
        ("drain_system", 5, None, "default", "A",
         "Standard drain flush is sufficient (A tier) — lowest intervention"),
        # Compressor (Card 10) — age-driven replacement recommendation
        ("compressor", 10, 8, "rla_over_nameplate", "C",
         "8+ yr compressor over-amping → present full system replacement (C tier)"),
        ("compressor", 10, None, "default", "B",
         "Default compressor recommendation"),
        # Evap coil / formicary (Card 19)
        ("evaporator_coil", 19, None, "formicary_confirmed", "C",
         "Formicary corrosion confirmed → full coil replacement (C tier)"),
        ("evaporator_coil", 8, None, "formicary_confirmed", "C",
         "Refrigerant leak at evap coil → coil replacement (C tier)"),
        # Ductwork (Card 13) — attic premium
        ("ductwork", 13, None, "attic_location", "C",
         "Attic ductwork in Houston summer → C tier with attic premium"),
        ("ductwork", 13, None, "default", "B",
         "Default ductwork recommendation"),
        # Ignitor / flame sensor (Card 11)
        ("flame_sensor", 11, None, "sensor_only", "A",
         "Clean flame sensor only → A tier (cheapest first step)"),
        ("ignitor", 11, None, "cracked_ignitor", "B",
         "Cracked ignitor confirmed → replace (B tier)"),
    ]
    for (component, card_id, age, condition, tier, note) in rules:
        await db.execute(
            text("""
                INSERT INTO lifecycle_rules
                    (component_name, card_id, age_threshold_years,
                     condition_signal, recommended_tier, note)
                VALUES
                    (:component, :card_id, :age, :condition, :tier, :note)
            """),
            {
                "component": component,
                "card_id": card_id,
                "age": age,
                "condition": condition,
                "tier": tier,
                "note": note,
            },
        )
    print(f"  ✓ lifecycle_rules: {len(rules)} rows")
    return len(rules)


# ── data_repo_versions record ──────────────────────────────────────────────────
async def record_version(db, data: dict, counts: dict) -> None:
    version = data["metadata"]["version"]
    await db.execute(
        text("""
            INSERT INTO data_repo_versions (version, source_file, row_counts, notes)
            VALUES (:version, :source_file, CAST(:row_counts AS jsonb), :notes)
        """),
        {
            "version": version,
            "source_file": "ac_data_repo.json + SnapAI_HVAC_Master_Price_List_2026.xlsx",
            "row_counts": json.dumps(counts),
            "notes": f"Loaded by load_repo.py on {date.today().isoformat()}",
        },
    )
    print(f"  ✓ data_repo_versions: recorded v{version}")


# ── Main ───────────────────────────────────────────────────────────────────────
async def main(dry_run: bool = False) -> None:
    print("=== SnapAI WS-A Data Repo Loader ===")
    print()

    # ── Load source files ─────────────────────────────────────────────────────
    json_path = _find_file(_REPO_JSON_CANDIDATES)
    xlsx_path = _find_file(_PRICE_LIST_CANDIDATES)
    print(f"JSON:  {json_path}")
    print(f"XLSX:  {xlsx_path}")
    print()

    with open(json_path) as f:
        data = json.load(f)

    # Read price list fault-cards sheet
    try:
        import openpyxl
    except ImportError:
        print("ERROR: openpyxl not installed. Run: pip install openpyxl")
        sys.exit(1)

    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb["13. FAULT CARDS"]
    price_rows = list(ws.iter_rows(values_only=True))
    # Skip header rows (row 0 = title, row 1 = column headers, data starts row 2)
    price_rows = price_rows[2:]

    if dry_run:
        print("[DRY RUN] Schema and file checks passed. No DB writes.")
        print(f"  brands: {len(data['brands'])} to insert")
        print(f"  parts:  {len(data['parts_catalog'])} to insert")
        print(f"  cards:  {len(data['fault_card_estimates'])} to insert")
        data_rows = [r for r in price_rows if isinstance(r[0], int)]
        print(f"  price list card rows: {len(data_rows)}")
        return

    # ── Write to DB ────────────────────────────────────────────────────────────
    print("Loading into database...")
    async with AsyncSessionLocal() as db:
        counts = {}
        counts["brands"]    = await load_brands(db, data)
        counts["parts"]     = await load_parts(db, data)
        counts["fault_cards"] = await load_fault_cards(db, data, price_rows)
        counts["pricing_tiers"] = await load_pricing_tiers(db, price_rows)
        counts["error_codes"] = await load_error_codes(db, data)
        counts["labor_rates"] = await load_labor_rates(db, data)
        counts["legacy_prefixes"] = await load_legacy_prefixes(db, data)
        counts["lifecycle_rules"] = await load_lifecycle_rules(db)

        await record_version(db, data, counts)
        await db.commit()

    # ── Acceptance check ───────────────────────────────────────────────────────
    print()
    print("=== Acceptance Check ===")
    checks = [
        ("brands",               counts["brands"],          15,  "=="),
        ("parts_catalog",        counts["parts"],           40,  "=="),
        ("fault_cards",          counts["fault_cards"],     19,  "=="),
        ("pricing_tiers",        counts["pricing_tiers"],   57,  "=="),
        ("error_codes",          counts["error_codes"],    159,  ">="),
        ("labor_rates_houston",  counts["labor_rates"],      1,  "=="),
        ("legacy_model_prefixes",counts["legacy_prefixes"], 75,  "=="),
    ]
    all_pass = True
    for table, actual, expected, op_ in checks:
        if op_ == "==" and actual != expected:
            status = f"❌ FAIL  (got {actual}, expected {expected})"
            all_pass = False
        elif op_ == ">=" and actual < expected:
            status = f"❌ FAIL  (got {actual}, expected ≥{expected})"
            all_pass = False
        else:
            status = f"✅ PASS  ({actual})"
        print(f"  {table:<26} {status}")

    print()
    if all_pass:
        print("✅ All acceptance checks passed. WS-A M1 complete.")
    else:
        print("❌ Some checks failed — review output above and re-run.")
        sys.exit(1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(dry_run=dry_run))
