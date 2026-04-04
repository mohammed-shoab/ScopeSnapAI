"""
SnapAI — Pricing Rules Seed Script
Populates pricing_rules with national defaults for common HVAC job types.
All amounts are in USD.

Run once: python scripts/seed_pricing.py
WP-04 deliverable.
"""

import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import AsyncSessionLocal
from db.models import PricingRule
from sqlalchemy import select


NATIONAL_PRICING = [
    # ── AC Unit jobs ──────────────────────────────────────────────────────────

    {
        "equipment_type": "ac_unit",
        "job_type": "coil_cleaning",
        "region": "national",
        "parts_cost": {"min": 50, "max": 150, "avg": 80, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 2.5, "avg": 1.5},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 0.0,
        "additional_costs": {"coil_cleaner_chemicals": 35, "disposal": 0},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "coil_replacement",
        "region": "national",
        "parts_cost": {"min": 800, "max": 2200, "avg": 1400, "source": "distributor_list"},
        "labor_hours": {"min": 3, "max": 6, "avg": 4.5},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"disposal_fee": 75, "refrigerant_lbs": 4},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "full_system",
        "region": "national",
        "parts_cost": {"min": 2800, "max": 5500, "avg": 3800, "source": "distributor_list"},
        "labor_hours": {"min": 6, "max": 10, "avg": 8},
        "labor_rate": 95.0,
        "permit_cost": 250.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"disposal_old_unit": 150, "refrigerant_lbs": 5, "misc": 100},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "full_system_premium",
        "region": "national",
        "parts_cost": {"min": 4500, "max": 8000, "avg": 6000, "source": "distributor_list"},
        "labor_hours": {"min": 8, "max": 12, "avg": 10},
        "labor_rate": 95.0,
        "permit_cost": 250.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"disposal_old_unit": 150, "refrigerant_lbs": 5, "smart_thermostat": 250, "misc": 150},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "compressor_replacement",
        "region": "national",
        "parts_cost": {"min": 800, "max": 1800, "avg": 1200, "source": "distributor_list"},
        "labor_hours": {"min": 3, "max": 5, "avg": 4},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"refrigerant_lbs": 5, "misc": 50},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "refrigerant_recharge",
        "region": "national",
        "parts_cost": {"min": 0, "max": 0, "avg": 0, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 2, "avg": 1.5},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"refrigerant_lbs": 3, "leak_seal_treatment": 75},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "maintenance",
        "region": "national",
        "parts_cost": {"min": 20, "max": 80, "avg": 40, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 2, "avg": 1.5},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 0.0,
        "additional_costs": {"filter": 25},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "repair",
        "region": "national",
        "parts_cost": {"min": 50, "max": 500, "avg": 200, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 3, "avg": 2},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {},
    },

    # ── Furnace jobs ──────────────────────────────────────────────────────────
    {
        "equipment_type": "furnace",
        "job_type": "full_system",
        "region": "national",
        "parts_cost": {"min": 1800, "max": 4000, "avg": 2600, "source": "distributor_list"},
        "labor_hours": {"min": 4, "max": 8, "avg": 6},
        "labor_rate": 95.0,
        "permit_cost": 150.0,
        "refrigerant_cost_per_lb": 0.0,
        "additional_costs": {"disposal_old_unit": 100, "flue_modification": 100},
    },
    {
        "equipment_type": "furnace",
        "job_type": "maintenance",
        "region": "national",
        "parts_cost": {"min": 30, "max": 100, "avg": 55, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 2, "avg": 1.5},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 0.0,
        "additional_costs": {"filter": 30},
    },
    {
        "equipment_type": "furnace",
        "job_type": "repair",
        "region": "national",
        "parts_cost": {"min": 50, "max": 600, "avg": 250, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 3, "avg": 2},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 0.0,
        "additional_costs": {},
    },

    # ── Heat pump jobs ─────────────────────────────────────────────────────────
    {
        "equipment_type": "heat_pump",
        "job_type": "full_system",
        "region": "national",
        "parts_cost": {"min": 3500, "max": 7000, "avg": 5000, "source": "distributor_list"},
        "labor_hours": {"min": 8, "max": 12, "avg": 10},
        "labor_rate": 95.0,
        "permit_cost": 300.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"disposal_old_unit": 150, "refrigerant_lbs": 6, "misc": 100},
    },
    {
        "equipment_type": "heat_pump",
        "job_type": "refrigerant_recharge",
        "region": "national",
        "parts_cost": {"min": 0, "max": 0, "avg": 0, "source": "distributor_list"},
        "labor_hours": {"min": 1, "max": 2.5, "avg": 1.5},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 28.0,
        "additional_costs": {"refrigerant_lbs": 4},
    },
    {
        "equipment_type": "heat_pump",
        "job_type": "maintenance",
        "region": "national",
        "parts_cost": {"min": 20, "max": 80, "avg": 40, "source": "distributor_list"},
        "labor_hours": {"min": 1.5, "max": 2.5, "avg": 2},
        "labor_rate": 95.0,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 0.0,
        "additional_costs": {"filter": 25},
    },
]


async def seed_pricing():
    async with AsyncSessionLocal() as db:
        created = 0
        skipped = 0

        for pricing in NATIONAL_PRICING:
            # Check if exists
            result = await db.execute(
                select(PricingRule).where(
                    PricingRule.company_id == None,
                    PricingRule.equipment_type == pricing["equipment_type"],
                    PricingRule.job_type == pricing["job_type"],
                    PricingRule.region == pricing["region"],
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            rule = PricingRule(
                id=str(uuid.uuid4()),
                company_id=None,  # NULL = global default
                equipment_type=pricing["equipment_type"],
                job_type=pricing["job_type"],
                region=pricing["region"],
                parts_cost=pricing["parts_cost"],
                labor_hours=pricing["labor_hours"],
                labor_rate=pricing["labor_rate"],
                permit_cost=pricing["permit_cost"],
                refrigerant_cost_per_lb=pricing["refrigerant_cost_per_lb"],
                additional_costs=pricing.get("additional_costs", {}),
            )
            db.add(rule)
            created += 1

        await db.commit()
        print(f"Pricing seed complete: {created} created, {skipped} skipped")


if __name__ == "__main__":
    asyncio.run(seed_pricing())
