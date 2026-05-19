"""
Pakistan Data Repo Loader
=========================
Ingests ac_data_repo_pakistan_v2_merged.json into pak_ prefixed Supabase tables.

This is a SEPARATE script from load_repo.py. It NEVER touches Houston tables.
Houston tables (brands, fault_cards, parts_catalog, etc.) are not modified.

Usage (from the scopesnap-api directory):
    python scripts/load_repo_pakistan.py
    python scripts/load_repo_pakistan.py --dry-run

Idempotent: each pak_ table is truncated and re-seeded on every run.

Target table counts (Phase 1):
  pak_brands             — 15 rows
  pak_parts_catalog      — 13 rows
  pak_fault_cards        — 15 rows
  pak_error_codes        — varies (Gree, Haier, Dawlance, Orient)
  pak_labor_rates        — 1 row
  pak_lifecycle_rules    — 5 rows (one per top-level key)
  pak_data_defaults      — 1 row
  pak_replacement_costs  — 4 rows (1.0, 1.5, 2.0 ton + default)
"""

import asyncio
import json
import sys
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from db.database import AsyncSessionLocal

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_DIR = Path(__file__).parent.parent.parent.parent   # ScopeSnapAI/..
PERSONAL_CLAUDE = REPO_DIR.parent / "Personal Claude"

_PAK_JSON_CANDIDATES = [
    Path("/app/data/ac_data_repo_pakistan_v2_merged.json"),              # Railway container
    PERSONAL_CLAUDE / "marketing" / "ac_data_repo_pakistan_v2_merged.json",  # Local (Windows)
    Path("/sessions/youthful-nifty-faraday/mnt/Personal Claude/marketing/ac_data_repo_pakistan_v2_merged.json"),
    Path(__file__).parent.parent.parent / "ac_data_repo_pakistan.json",  # Fallback
]


def _find_file(candidates):
    for p in candidates:
        if Path(p).exists():
            return Path(p)
    raise FileNotFoundError(
        "Pakistan data file not found. Tried:\n" + "\n".join(str(c) for c in candidates)
    )


def _pg_text_array(lst) -> str | None:
    """['a', 'b'] → '{"a","b"}' for CAST(:x AS text[])"""
    if not lst:
        return None
    items = []
    for item in lst:
        if item is None:
            items.append("NULL")
        else:
            escaped = str(item).replace("\\", "\\\\").replace('"', '\\"')
            items.append(f'"{escaped}"')
    return "{" + ",".join(items) + "}"


# ── Migrations: Create all pak_ tables ────────────────────────────────────────
async def run_migrations(db) -> None:
    """Create all pak_ prefixed tables if they don't exist. Safe to re-run."""
    print("Running Pakistan table migrations...")

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_brands (
            id                       TEXT PRIMARY KEY,
            name                     TEXT NOT NULL,
            country_of_origin        TEXT,
            pakistan_prevalence      TEXT,
            service_network_pakistan TEXT,
            pakistan_notes           TEXT,
            series                   JSONB,
            created_at               TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_parts_catalog (
            id                  TEXT PRIMARY KEY,
            name                TEXT NOT NULL,
            category            TEXT,
            pkr_part            INTEGER,
            pkr_installed       INTEGER,
            usd_part_approx     NUMERIC,
            usd_installed_approx NUMERIC,
            availability        TEXT,
            applies_to          TEXT,
            notes               TEXT,
            created_at          TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_fault_cards (
            id                   SERIAL PRIMARY KEY,
            card_id              INTEGER UNIQUE,
            card_name            TEXT,
            fault_category       TEXT,
            applies_to           TEXT,
            primary_parts        TEXT[],
            optional_parts       TEXT[],
            labor_hours_min      NUMERIC,
            labor_hours_max      NUMERIC,
            labor_hours_avg      NUMERIC,
            pkr_est_min          INTEGER,
            pkr_est_max          INTEGER,
            pkr_est_typical      INTEGER,
            pakistan_frequency_pct INTEGER,
            tech_notes           TEXT,
            pakistan_notes       TEXT,
            better_option_estimate JSONB,
            created_at           TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_error_codes (
            id             SERIAL PRIMARY KEY,
            brand_id       TEXT,
            code           TEXT,
            description    TEXT,
            fault_category TEXT,
            severity       TEXT,
            created_at     TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_labor_rates (
            id                          SERIAL PRIMARY KEY,
            currency                    TEXT DEFAULT 'PKR',
            diagnostic_visit_pkr        INTEGER,
            gas_charging_r22_per_kg_pkr INTEGER,
            gas_charging_r410a_per_kg_pkr INTEGER,
            gas_charging_r32_per_kg_pkr INTEGER,
            capacitor_replacement_pkr   INTEGER,
            pcb_inverter_board_pkr      INTEGER,
            compressor_1ton_pkr         INTEGER,
            compressor_1_5ton_pkr       INTEGER,
            full_system_1ton_pkr        INTEGER,
            full_system_1_5ton_pkr      INTEGER,
            usd_exchange_rate           NUMERIC,
            notes                       TEXT,
            raw_data                    JSONB,
            created_at                  TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_lifecycle_rules (
            id         SERIAL PRIMARY KEY,
            rule_key   TEXT UNIQUE,
            rule_value JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_data_defaults (
            id                    SERIAL PRIMARY KEY,
            market                TEXT,
            refrigerant_by_year   JSONB,
            cap_uf_by_tonnage     JSONB,
            electrical_by_tonnage JSONB,
            tech_warning          TEXT,
            inverter_note         TEXT,
            created_at            TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS pak_replacement_costs (
            id               SERIAL PRIMARY KEY,
            tonnage          NUMERIC,
            pkr_min          INTEGER,
            pkr_max          INTEGER,
            pkr_typical      INTEGER,
            usd_typical_approx NUMERIC,
            notes            TEXT,
            created_at       TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    print("  ✓ All pak_ tables ready")


# ── Loader: pak_brands ─────────────────────────────────────────────────────────
async def load_pak_brands(db, data: dict) -> int:
    await db.execute(text("TRUNCATE pak_brands CASCADE"))
    brands = data.get("brands", [])
    if not brands:
        print("  ⚠ pak_brands: no brands found in JSON")
        return 0

    for b in brands:
        await db.execute(
            text("""
                INSERT INTO pak_brands
                    (id, name, country_of_origin, pakistan_prevalence,
                     service_network_pakistan, pakistan_notes, series)
                VALUES
                    (:id, :name, :country, :prevalence, :service, :notes,
                     CAST(:series AS jsonb))
            """),
            {
                "id": b["id"],
                "name": b["name"],
                "country": b.get("country_of_origin"),
                "prevalence": b.get("pakistan_prevalence"),
                "service": b.get("service_network_pakistan"),
                "notes": b.get("pakistan_notes"),
                "series": json.dumps(b.get("series", [])),
            }
        )

    print(f"  ✓ pak_brands: {len(brands)} rows")
    return len(brands)


# ── Loader: pak_parts_catalog ──────────────────────────────────────────────────
async def load_pak_parts(db, data: dict) -> int:
    parts = data.get("parts_catalog", [])
    if not parts:
        print("  ⚠ pak_parts_catalog: empty array in JSON — skipping")
        return 0

    await db.execute(text("TRUNCATE pak_parts_catalog"))
    for p in parts:
        await db.execute(
            text("""
                INSERT INTO pak_parts_catalog
                    (id, name, category, pkr_part, pkr_installed,
                     usd_part_approx, usd_installed_approx,
                     availability, applies_to, notes)
                VALUES
                    (:id, :name, :cat, :pkr_part, :pkr_inst,
                     :usd_part, :usd_inst,
                     :avail, :applies, :notes)
            """),
            {
                "id": p["id"],
                "name": p["name"],
                "cat": p.get("category"),
                "pkr_part": p.get("pkr_part"),
                "pkr_inst": p.get("pkr_installed"),
                "usd_part": p.get("usd_part_approx"),
                "usd_inst": p.get("usd_installed_approx"),
                "avail": p.get("availability"),
                "applies": p.get("applies_to"),
                "notes": p.get("notes") or p.get("note"),
            }
        )

    print(f"  ✓ pak_parts_catalog: {len(parts)} rows")
    return len(parts)


# ── Loader: pak_fault_cards ────────────────────────────────────────────────────
async def load_pak_fault_cards(db, data: dict) -> int:
    cards = data.get("fault_card_estimates", [])
    if not cards:
        print("  ⚠ pak_fault_cards: no cards found in JSON")
        return 0

    await db.execute(text("TRUNCATE pak_fault_cards RESTART IDENTITY CASCADE"))
    count = 0
    for c in cards:
        # Estimate figures — the Pakistan file uses pkr_estimate.{min, max, typical}
        est = c.get("pkr_estimate", {})
        lh = c.get("labor_hours", {})
        lo = lh.get("min")
        hi = lh.get("max")
        avg = lh.get("average")

        await db.execute(
            text("""
                INSERT INTO pak_fault_cards
                    (card_id, card_name, fault_category, applies_to,
                     primary_parts, optional_parts,
                     labor_hours_min, labor_hours_max, labor_hours_avg,
                     pkr_est_min, pkr_est_max, pkr_est_typical,
                     pakistan_frequency_pct, tech_notes, pakistan_notes,
                     better_option_estimate)
                VALUES
                    (:cid, :name, :cat, :applies,
                     CAST(:primary AS text[]), CAST(:optional AS text[]),
                     :lmin, :lmax, :lavg,
                     :emin, :emax, :etypical,
                     :freq, :tech_notes, :pak_notes,
                     CAST(:better_est AS jsonb))
            """),
            {
                "cid": c.get("card_id"),
                "name": c.get("card_name") or c.get("name", ""),
                "cat": c.get("fault_category") or c.get("category"),
                "applies": c.get("applies_to", "all"),
                "primary": _pg_text_array(c.get("primary_parts", [])),
                "optional": _pg_text_array(c.get("optional_parts", [])),
                "lmin": lo,
                "lmax": hi,
                "lavg": avg,
                "emin": est.get("min"),
                "emax": est.get("max"),
                "etypical": est.get("typical"),
                "freq": c.get("pakistan_frequency_pct"),
                "tech_notes": c.get("tech_notes"),
                "pak_notes": c.get("pakistan_notes"),
                "better_est": json.dumps(c.get("better_option_estimate") or {}),
            }
        )
        count += 1

    print(f"  ✓ pak_fault_cards: {count} rows")
    return count


# ── Loader: pak_error_codes ────────────────────────────────────────────────────
async def load_pak_error_codes(db, data: dict) -> int:
    """
    The Pakistan error_code_db structure is:
      { "gree": { "E1": "High Pressure", "E3": "Low Pressure", ... },
        "haier": { "E7": "...", ... }, ... }
    Each brand maps to a dict of code → description_string.
    """
    error_db = data.get("error_code_db", {})
    if not error_db:
        print("  ⚠ pak_error_codes: not found in JSON")
        return 0

    await db.execute(text("TRUNCATE pak_error_codes"))
    count = 0

    for brand_id, codes in error_db.items():
        if not isinstance(codes, dict):
            continue
        for code_str, description in codes.items():
            # Description may be a string or a dict with more fields
            if isinstance(description, str):
                desc_text = description
                fault_cat = None
                severity = None
            elif isinstance(description, dict):
                desc_text = description.get("description") or description.get("meaning", "")
                fault_cat = description.get("fault_category") or description.get("category")
                severity = description.get("severity")
            else:
                continue

            await db.execute(
                text("""
                    INSERT INTO pak_error_codes
                        (brand_id, code, description, fault_category, severity)
                    VALUES
                        (:brand, :code, :desc, :cat, :severity)
                """),
                {
                    "brand": brand_id,
                    "code": code_str,
                    "desc": desc_text,
                    "cat": fault_cat,
                    "severity": severity,
                }
            )
            count += 1

    print(f"  ✓ pak_error_codes: {count} rows")
    return count


# ── Loader: pak_labor_rates ────────────────────────────────────────────────────
async def load_pak_labor_rates(db, data: dict) -> int:
    """
    labor_rates_pakistan has nested dicts:
      { "diagnostic_visit": { "pkr": 500, ... },
        "gas_charging_r22_per_kg": { "pkr": 2500, ... }, ... }
    """
    lr = data.get("labor_rates_pakistan") or {}
    if not lr:
        print("  ⚠ pak_labor_rates: not found in JSON — skipping")
        return 0

    def _pkr(key):
        val = lr.get(key, {})
        if isinstance(val, dict):
            return val.get("pkr")
        return None

    await db.execute(text("TRUNCATE pak_labor_rates"))
    await db.execute(
        text("""
            INSERT INTO pak_labor_rates
                (currency,
                 diagnostic_visit_pkr,
                 gas_charging_r22_per_kg_pkr,
                 gas_charging_r410a_per_kg_pkr,
                 gas_charging_r32_per_kg_pkr,
                 capacitor_replacement_pkr,
                 pcb_inverter_board_pkr,
                 compressor_1ton_pkr,
                 compressor_1_5ton_pkr,
                 full_system_1ton_pkr,
                 full_system_1_5ton_pkr,
                 usd_exchange_rate,
                 notes,
                 raw_data)
            VALUES
                ('PKR',
                 :visit, :r22, :r410a, :r32,
                 :cap, :pcb,
                 :comp1, :comp1_5,
                 :sys1, :sys1_5,
                 280.0,
                 :notes,
                 CAST(:raw AS jsonb))
        """),
        {
            "visit":  _pkr("diagnostic_visit"),
            "r22":    _pkr("gas_charging_r22_per_kg"),
            "r410a":  _pkr("gas_charging_r410a_per_kg"),
            "r32":    _pkr("gas_charging_r32_per_kg"),
            "cap":    _pkr("capacitor_replacement"),
            "pcb":    _pkr("pcb_inverter_board"),
            "comp1":  _pkr("compressor_replacement_1ton"),
            "comp1_5": _pkr("compressor_replacement_1_5ton"),
            "sys1":   _pkr("full_system_replacement_1ton"),
            "sys1_5": _pkr("full_system_replacement_1_5ton"),
            "notes":  lr.get("usd_exchange_note", "Approximately 280 PKR = 1 USD as of 2026"),
            "raw":    json.dumps(lr),
        }
    )
    print("  ✓ pak_labor_rates: 1 row")
    return 1


# ── Loader: pak_lifecycle_rules ────────────────────────────────────────────────
async def load_pak_lifecycle_rules(db, data: dict) -> int:
    """
    lifecycle_rules is a flat dict:
      { "avg_lifespan_years_by_brand": {...},
        "replacement_trigger_age_years": 7,
        "replacement_trigger_cost_ratio": 0.5,
        "label_sets": {...},
        "pakistan_note": "..." }
    Each top-level key becomes one row.
    """
    rules = data.get("lifecycle_rules", {})
    if not rules:
        print("  ⚠ pak_lifecycle_rules: not found in JSON")
        return 0

    await db.execute(text("TRUNCATE pak_lifecycle_rules"))
    count = 0
    for key, value in rules.items():
        await db.execute(
            text("""
                INSERT INTO pak_lifecycle_rules (rule_key, rule_value)
                VALUES (:key, CAST(:val AS jsonb))
            """),
            {"key": key, "val": json.dumps(value)}
        )
        count += 1

    print(f"  ✓ pak_lifecycle_rules: {count} rows")
    return count


# ── Loader: pak_data_defaults ──────────────────────────────────────────────────
async def load_pak_defaults(db, data: dict) -> int:
    defaults = data.get("defaults", {})
    if not defaults:
        print("  ⚠ pak_data_defaults: not found in JSON")
        return 0

    await db.execute(text("TRUNCATE pak_data_defaults"))
    await db.execute(
        text("""
            INSERT INTO pak_data_defaults
                (market, refrigerant_by_year, cap_uf_by_tonnage,
                 electrical_by_tonnage, tech_warning, inverter_note)
            VALUES
                (:market, CAST(:ref_by_year AS jsonb), CAST(:cap_uf AS jsonb),
                 CAST(:electrical AS jsonb), :warning, :inverter_note)
        """),
        {
            "market": data.get("metadata", {}).get("market", "Pakistan"),
            "ref_by_year": json.dumps(
                defaults.get("refrigerant_by_install_year") or
                defaults.get("refrigerant_by_year", {})
            ),
            "cap_uf": json.dumps(
                defaults.get("cap_uf_by_tonnage_non_inverter_only") or
                defaults.get("cap_uf_by_tonnage", {})
            ),
            "electrical": json.dumps(defaults.get("electrical_by_tonnage", {})),
            "warning": defaults.get("tech_warning"),
            "inverter_note": defaults.get("inverter_note"),
        }
    )
    print("  ✓ pak_data_defaults: 1 row")
    return 1


# ── Loader: pak_replacement_costs ─────────────────────────────────────────────
async def load_pak_replacement_costs(db, data: dict) -> int:
    """
    replacement_cost_estimates.by_tonnage uses pkr_min / pkr_max / pkr_typical
    (different from Houston which uses min / max / typical in USD).
    """
    rce = data.get("replacement_cost_estimates", {})
    if not rce:
        print("  ⚠ pak_replacement_costs: not found in JSON")
        return 0

    await db.execute(text("TRUNCATE pak_replacement_costs"))
    count = 0
    by_tonnage = rce.get("by_tonnage", {})
    for tonnage_key, costs in by_tonnage.items():
        pkr_typ = costs.get("pkr_typical") or costs.get("typical")
        await db.execute(
            text("""
                INSERT INTO pak_replacement_costs
                    (tonnage, pkr_min, pkr_max, pkr_typical, usd_typical_approx, notes)
                VALUES (:ton, :pmin, :pmax, :ptyp, :usd, :notes)
            """),
            {
                "ton": float(tonnage_key),
                "pmin": costs.get("pkr_min") or costs.get("min"),
                "pmax": costs.get("pkr_max") or costs.get("max"),
                "ptyp": pkr_typ,
                "usd": costs.get("usd_typical") or (round(pkr_typ / 280, 2) if pkr_typ else None),
                "notes": rce.get("includes") or rce.get("notes"),
            }
        )
        count += 1

    default = rce.get("default_if_tonnage_unknown", {})
    if default:
        pkr_def = default.get("pkr_typical") or default.get("typical")
        await db.execute(
            text("""
                INSERT INTO pak_replacement_costs
                    (tonnage, pkr_min, pkr_max, pkr_typical, notes)
                VALUES (0, :pmin, :pmax, :ptyp, 'default when tonnage unknown')
            """),
            {
                "pmin": default.get("pkr_min") or default.get("min"),
                "pmax": default.get("pkr_max") or default.get("max"),
                "ptyp": pkr_def,
            }
        )
        count += 1

    print(f"  ✓ pak_replacement_costs: {count} rows")
    return count


# ── Dry-run summary ────────────────────────────────────────────────────────────
def _dry_run_summary(data: dict, json_path: Path) -> None:
    print("[DRY RUN] File found. No DB writes will be made.")
    print(f"  Source : {json_path}")
    print(f"  Version: {data.get('metadata', {}).get('version', '?')}")
    print(f"  Status : {data.get('metadata', {}).get('completion_status', '?')}")
    print()

    brands = data.get("brands", [])
    parts = data.get("parts_catalog", [])
    cards = data.get("fault_card_estimates", [])
    edb = data.get("error_code_db", {})
    total_codes = sum(
        len(v) for v in edb.values() if isinstance(v, dict)
    )
    lr = data.get("labor_rates_pakistan", {})
    lifecycle = data.get("lifecycle_rules", {})
    defaults = data.get("defaults", {})
    rce = data.get("replacement_cost_estimates", {})
    rce_rows = len(rce.get("by_tonnage", {}))
    if rce.get("default_if_tonnage_unknown"):
        rce_rows += 1

    print("  Table                    Rows to insert")
    print("  ─────────────────────────────────────────")
    print(f"  pak_brands               {len(brands)}")
    print(f"  pak_parts_catalog        {len(parts)}")
    print(f"  pak_fault_cards          {len(cards)}")
    print(f"  pak_error_codes          {total_codes}")
    print(f"  pak_labor_rates          {'1' if lr else '0 (missing!)'}")
    print(f"  pak_lifecycle_rules      {len(lifecycle)}")
    print(f"  pak_data_defaults        {'1' if defaults else '0 (missing!)'}")
    print(f"  pak_replacement_costs    {rce_rows}")
    print()

    # Spot-check: verify all fault cards have better_option_estimate
    missing_better = [
        f"  Card {c.get('card_id')}: {c.get('card_name', '')}"
        for c in cards if not c.get("better_option_estimate")
    ]
    if missing_better:
        print("  ⚠ Cards missing better_option_estimate:")
        for m in missing_better:
            print(m)
    else:
        print(f"  ✓ All {len(cards)} fault cards have better_option_estimate")

    print()
    print("[DRY RUN COMPLETE] Run without --dry-run to write to database.")


# ── Main ───────────────────────────────────────────────────────────────────────
async def main(dry_run: bool = False) -> None:
    print("=" * 50)
    print("  SnapAI Pakistan Data Repo Loader v1.0")
    print("=" * 50)
    print()

    json_path = _find_file(_PAK_JSON_CANDIDATES)

    with open(json_path) as f:
        data = json.load(f)

    if dry_run:
        _dry_run_summary(data, json_path)
        return

    print(f"JSON : {json_path}")
    print(f"Date : {date.today().isoformat()}")
    print()
    print("Loading into database...")

    try:
        async with AsyncSessionLocal() as db:
            counts = {}

            await run_migrations(db)

            counts["brands"]            = await load_pak_brands(db, data)
            counts["parts"]             = await load_pak_parts(db, data)
            counts["fault_cards"]       = await load_pak_fault_cards(db, data)
            counts["error_codes"]       = await load_pak_error_codes(db, data)
            counts["labor_rates"]       = await load_pak_labor_rates(db, data)
            counts["lifecycle_rules"]   = await load_pak_lifecycle_rules(db, data)
            counts["defaults"]          = await load_pak_defaults(db, data)
            counts["replacement_costs"] = await load_pak_replacement_costs(db, data)

            await db.commit()

    except Exception:
        print("\n❌ FATAL ERROR — full traceback:")
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 50)
    print("  Pakistan Load Complete")
    print("=" * 50)
    for key, count in counts.items():
        status = "✓" if count > 0 else "⚠"
        print(f"  {status} {key}: {count} rows")

    print()
    print("Validation queries to run in Supabase:")
    print("  SELECT COUNT(*) FROM pak_brands;           -- expect 15")
    print("  SELECT COUNT(*) FROM pak_fault_cards;      -- expect 15")
    print("  SELECT COUNT(*) FROM pak_parts_catalog;    -- expect 13")
    print("  SELECT COUNT(*) FROM pak_error_codes;      -- varies")
    print("  SELECT COUNT(*) FROM pak_labor_rates;      -- expect 1")
    print("  SELECT COUNT(*) FROM pak_lifecycle_rules;  -- expect 5")
    print("  SELECT COUNT(*) FROM pak_data_defaults;    -- expect 1")
    print("  SELECT COUNT(*) FROM pak_replacement_costs;-- expect 4")
    print()
    print("Safety check:")
    print("  SELECT b.name FROM pak_brands b")
    print("    WHERE b.name IN ('Carrier','Trane','Lennox','Goodman');")
    print("  -- expect 0 rows (no Houston data in Pakistan tables)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(dry_run))
