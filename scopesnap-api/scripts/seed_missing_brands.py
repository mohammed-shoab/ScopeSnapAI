"""
SnapAI — Seed Missing 10 Brands
Adds York, Daikin, Bryant, American Standard, Amana, Ruud,
Heil, Coleman, Payne, and Mitsubishi Electric to equipment_models.

Data source: data/ac_data_repo.json (v3)
Run: python scripts/seed_missing_brands.py

Safe to re-run — skips existing brand+model_series combos.
"""

import asyncio
import sys
import os
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import AsyncSessionLocal
from db.models import EquipmentModel
from sqlalchemy import select


# ─────────────────────────────────────────────────────────────────────────────
# 10 missing brands — 3 series each (30 new rows)
# Mapped from ac_data_repo.json v3
# ─────────────────────────────────────────────────────────────────────────────
MISSING_BRAND_MODELS = [

    # ── YORK (Johnson Controls) ───────────────────────────────────────────────
    {
        "brand": "York",
        "model_series": "LX",
        "model_pattern": r"(YXC|YCC|LX14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.5,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "capacitor",
                "issue": "premature_failure",
                "onset_year": 5,
                "frequency": "15%",
                "regions": ["all"],
                "description": "Run capacitor fails early in Houston heat — same JCI-family pattern as Heil/Coleman"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
            "example": "2314A12345 → 2023, week 14"
        },
        "replacement_models": [],
    },
    {
        "brand": "York",
        "model_series": "Affinity",
        "model_pattern": r"(YXF|YFF|AFFINITY)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 17.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },
    {
        "brand": "York",
        "model_series": "YXV",
        "model_pattern": r"YXV20?\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 20.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "inverter_board",
                "issue": "surge_damage",
                "onset_year": 5,
                "frequency": "8%",
                "regions": ["all"],
                "description": "Variable-speed inverter board sensitive to power spikes"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── DAIKIN (Manufactured in Waller TX) ────────────────────────────────────
    {
        "brand": "Daikin",
        "model_series": "DN Series",
        "model_pattern": r"(DN14|DN16|DX14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 15.0,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "capacitor",
                "issue": "failure",
                "onset_year": 4,
                "frequency": "14%",
                "regions": ["all"],
                "description": "Run capacitor failure — common Daikin/Goodman/Amana shared platform issue"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYWWXXXXXX",
            "letter_pos": 0,
            "year_pos": 1,
            "week_chars": [2, 3],
            "note": "Same serial format as Goodman/Amana (sister brands, same Daikin factory)"
        },
        "replacement_models": [],
    },
    {
        "brand": "Daikin",
        "model_series": "DX Series",
        "model_pattern": r"(DX17|DX20|DX20VC)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 18.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2017-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYWWXXXXXX",
            "letter_pos": 0,
            "year_pos": 1,
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },
    {
        "brand": "Daikin",
        "model_series": "Daikin Fit",
        "model_pattern": r"(DZ|FT|SkyAir)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 21.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2019-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "inverter_drive",
                "issue": "control_board_failure",
                "onset_year": 6,
                "frequency": "7%",
                "regions": ["all"],
                "description": "Side-discharge slim cabinet — inverter control board failure. Proprietary parts required."
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYWWXXXXXX",
            "letter_pos": 0,
            "year_pos": 1,
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── BRYANT (Carrier sister brand — identical internals) ───────────────────
    {
        "brand": "Bryant",
        "model_series": "Legacy",
        "model_pattern": r"(LCA|CA14|913S)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.0,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "evap_coil",
                "issue": "formicary_corrosion",
                "onset_year": 5,
                "frequency": "28%",
                "regions": ["gulf_coast", "southeast"],
                "description": "Same Carrier copper coil — formicary corrosion pinholes common in Houston humidity"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "WWYYXXXXXXX",
            "week_chars": [0, 1],
            "year_chars": [2, 3],
            "note": "Same as Carrier (sister brand)"
        },
        "replacement_models": [],
    },
    {
        "brand": "Bryant",
        "model_series": "Preferred",
        "model_pattern": r"(127B|127A|226B)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 16.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "WWYYXXXXXXX",
            "week_chars": [0, 1],
            "year_chars": [2, 3],
        },
        "replacement_models": [],
    },
    {
        "brand": "Bryant",
        "model_series": "Evolution",
        "model_pattern": r"(180B|186B|189B)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 20.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2014-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "inverter_board",
                "issue": "surge_damage",
                "onset_year": 5,
                "frequency": "9%",
                "regions": ["all"],
                "description": "Variable-speed drive board sensitive to power spikes — same as Carrier Infinity"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "WWYYXXXXXXX",
            "week_chars": [0, 1],
            "year_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── AMERICAN STANDARD (Trane sister brand — identical internals) ──────────
    {
        "brand": "American Standard",
        "model_series": "Gold",
        "model_pattern": r"(4A7A|4A6A|GOLD14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.5,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "TXV_valve",
                "issue": "hunting",
                "onset_year": 5,
                "frequency": "9%",
                "regions": ["all"],
                "description": "Same Trane TXV issue — hunting causes temperature swings. Equivalent to Trane XR."
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYYWNN",
            "letter_pos": 0,
            "year_chars": [1, 2],
            "week_chars": [4, 5],
            "note": "Same as Trane (sister brand)"
        },
        "replacement_models": [],
    },
    {
        "brand": "American Standard",
        "model_series": "Silver",
        "model_pattern": r"(4A7B|4A6B)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 17.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYYWNN",
            "letter_pos": 0,
            "year_chars": [1, 2],
            "week_chars": [4, 5],
        },
        "replacement_models": [],
    },
    {
        "brand": "American Standard",
        "model_series": "Platinum",
        "model_pattern": r"(4A7V|4A6V)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 21.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2014-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYYWNN",
            "letter_pos": 0,
            "year_chars": [1, 2],
            "week_chars": [4, 5],
        },
        "replacement_models": [],
    },

    # ── AMANA (Daikin/Goodman sister brand — lifetime compressor warranty) ────
    {
        "brand": "Amana",
        "model_series": "ASX",
        "model_pattern": r"(ASX14|ASX16|ASXN)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.5,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 14,
        "known_issues": [
            {
                "component": "capacitor",
                "issue": "failure",
                "onset_year": 4,
                "frequency": "18%",
                "regions": ["all"],
                "description": "Run capacitor failure — identical to Goodman GSX platform (same factory)"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYWWXXXXXX",
            "letter_pos": 0,
            "year_pos": 1,
            "week_chars": [2, 3],
            "note": "Same serial format as Goodman/Daikin"
        },
        "replacement_models": [],
    },
    {
        "brand": "Amana",
        "model_series": "ASXC",
        "model_pattern": r"ASXC1[68]\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 17.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 14,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYWWXXXXXX",
            "letter_pos": 0,
            "year_pos": 1,
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },
    {
        "brand": "Amana",
        "model_series": "ASXV",
        "model_pattern": r"ASXV9\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 20.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2019-2024",
        "avg_lifespan_years": 14,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "LYWWXXXXXX",
            "letter_pos": 0,
            "year_pos": 1,
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── RUUD (Rheem sister brand — identical internals) ───────────────────────
    {
        "brand": "Ruud",
        "model_series": "EcoNet Select",
        "model_pattern": r"(UA14|UP14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.0,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "condenser_fan_motor",
                "issue": "failure",
                "onset_year": 5,
                "frequency": "10%",
                "regions": ["all"],
                "description": "Condenser fan motor failure — same Rheem platform (identical internal components)"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "FYYWNNNNN",
            "prefix": "F",
            "year_chars": [1, 2],
            "week_chars": [3, 4],
            "note": "Same as Rheem (sister brand)"
        },
        "replacement_models": [],
    },
    {
        "brand": "Ruud",
        "model_series": "EcoNet Achiever",
        "model_pattern": r"(UA17|UP17)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 17.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "FYYWNNNNN",
            "prefix": "F",
            "year_chars": [1, 2],
            "week_chars": [3, 4],
        },
        "replacement_models": [],
    },
    {
        "brand": "Ruud",
        "model_series": "EcoNet Ultra",
        "model_pattern": r"(UA20|UP20)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 20.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "FYYWNNNNN",
            "prefix": "F",
            "year_chars": [1, 2],
            "week_chars": [3, 4],
        },
        "replacement_models": [],
    },

    # ── HEIL (Johnson Controls / ICP family) ──────────────────────────────────
    {
        "brand": "Heil",
        "model_series": "QuietComfort",
        "model_pattern": r"(HCA|HSA|QC14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.0,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "capacitor",
                "issue": "failure",
                "onset_year": 5,
                "frequency": "15%",
                "regions": ["all"],
                "description": "Run capacitor failure — shared JCI family (York/Coleman/Heil) component issue"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },
    {
        "brand": "Heil",
        "model_series": "QuietComfort Deluxe",
        "model_pattern": r"(HCA18|HPA18)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 18.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── COLEMAN (Johnson Controls budget end) ─────────────────────────────────
    {
        "brand": "Coleman",
        "model_series": "Echelon",
        "model_pattern": r"(TCA|TC14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.0,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "capacitor",
                "issue": "failure",
                "onset_year": 5,
                "frequency": "15%",
                "regions": ["all"],
                "description": "Run capacitor failure — shared JCI family component issue (York/Heil/Coleman)"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },
    {
        "brand": "Coleman",
        "model_series": "Echelon Deluxe",
        "model_pattern": r"(TCA18|TPA)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 18.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYWWXXXXXXX",
            "year_chars": [0, 1],
            "week_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── PAYNE (Carrier budget brand — identical internals) ────────────────────
    {
        "brand": "Payne",
        "model_series": "Payne Entry",
        "model_pattern": r"(PA14|PA16|PH14)\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 14.0,
        "tonnage_range": "1.5-5",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 15,
        "known_issues": [
            {
                "component": "evap_coil",
                "issue": "formicary_corrosion",
                "onset_year": 5,
                "frequency": "28%",
                "regions": ["gulf_coast", "southeast"],
                "description": "Same Carrier copper coil — formicary corrosion pinholes. Identical to Carrier Comfort."
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "WWYYXXXXXXX",
            "week_chars": [0, 1],
            "year_chars": [2, 3],
            "note": "Same as Carrier (sister brand)"
        },
        "replacement_models": [],
    },
    {
        "brand": "Payne",
        "model_series": "Payne Mid",
        "model_pattern": r"PA16B\d{3}[A-Z]?",
        "equipment_type": "ac_unit",
        "seer_rating": 16.0,
        "tonnage_range": "2-5",
        "manufacture_years": "2016-2024",
        "avg_lifespan_years": 15,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "WWYYXXXXXXX",
            "week_chars": [0, 1],
            "year_chars": [2, 3],
        },
        "replacement_models": [],
    },

    # ── MITSUBISHI ELECTRIC (mini-splits / multi-zone) ────────────────────────
    {
        "brand": "Mitsubishi Electric",
        "model_series": "M-Series / MSZ",
        "model_pattern": r"(MSZ|MXZ|MUZ)[A-Z0-9]{2,6}",
        "equipment_type": "mini_split",
        "seer_rating": 17.5,
        "tonnage_range": "0.75-4",
        "manufacture_years": "2015-2024",
        "avg_lifespan_years": 20,
        "known_issues": [
            {
                "component": "drain_pan",
                "issue": "clogging",
                "onset_year": 3,
                "frequency": "20%",
                "regions": ["all"],
                "description": "Indoor head drain pan clogs in humidity — causes water overflow onto wall/ceiling"
            },
            {
                "component": "control_board",
                "issue": "error_codes",
                "onset_year": 6,
                "frequency": "12%",
                "regions": ["all"],
                "description": "Proprietary control board failures — requires Mitsubishi-certified technician"
            }
        ],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYYYMMXXXXXX",
            "year_chars": [0, 3],
            "month_chars": [4, 5],
            "note": "Serial format varies by production run. Year embedded in first 4 digits."
        },
        "replacement_models": [],
    },
    {
        "brand": "Mitsubishi Electric",
        "model_series": "Hyper-Heat / H2i",
        "model_pattern": r"(MSZ-FH|MSZ-GL|SUZ-KA)[A-Z0-9]{2,6}",
        "equipment_type": "mini_split",
        "seer_rating": 22.0,
        "tonnage_range": "0.75-3",
        "manufacture_years": "2018-2024",
        "avg_lifespan_years": 20,
        "known_issues": [],
        "recalls": [],
        "serial_decode_pattern": {
            "format": "YYYYMMXXXXXX",
            "year_chars": [0, 3],
            "month_chars": [4, 5],
        },
        "replacement_models": [],
    },
]


async def seed_missing_brands():
    """Insert all missing brand models. Skip existing ones (by brand + model_series)."""
    async with AsyncSessionLocal() as db:
        created = 0
        skipped = 0

        for model_data in MISSING_BRAND_MODELS:
            result = await db.execute(
                select(EquipmentModel).where(
                    EquipmentModel.brand == model_data["brand"],
                    EquipmentModel.model_series == model_data["model_series"],
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                skipped += 1
                print(f"  SKIP  {model_data['brand']} / {model_data['model_series']}")
                continue

            model = EquipmentModel(
                id=str(uuid.uuid4()),
                brand=model_data["brand"],
                model_series=model_data["model_series"],
                model_pattern=model_data.get("model_pattern"),
                equipment_type=model_data["equipment_type"],
                seer_rating=model_data.get("seer_rating"),
                tonnage_range=model_data.get("tonnage_range"),
                manufacture_years=model_data.get("manufacture_years"),
                avg_lifespan_years=model_data.get("avg_lifespan_years"),
                known_issues=model_data.get("known_issues", []),
                recalls=model_data.get("recalls", []),
                serial_decode_pattern=model_data.get("serial_decode_pattern"),
                replacement_models=model_data.get("replacement_models", []),
                total_assessments=0,
            )
            db.add(model)
            created += 1
            print(f"  ADD   {model_data['brand']} / {model_data['model_series']}")

        await db.commit()
        print(f"\n✓ Done: {created} added, {skipped} skipped")
        return created


if __name__ == "__main__":
    asyncio.run(seed_missing_brands())
