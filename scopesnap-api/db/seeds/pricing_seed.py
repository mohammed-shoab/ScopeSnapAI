"""
RW-05 — Default Pricing Rules Seed Data
National average HVAC pricing rules (company_id = NULL = global defaults).
Techs can override per-company. Regions: 'national', 'houston_metro', 'gulf_coast'.

Data sources:
  - HomeAdvisor/Angi 2024 HVAC cost reports
  - ACCA Manual J / D labor standards
  - Daikin, Carrier, Trane dealer cost guides (NDA-free summaries)
  - HARDI distribution pricing surveys

Run:  python -m db.seeds.pricing_seed
"""

import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import AsyncSessionLocal
from db.models import PricingRule

# ─────────────────────────────────────────────────────────────────────────────
# Pricing Rules
# Each rule: equipment_type × job_type × region
# labor_rate = national average HVAC tech billing rate
# parts_cost, labor_hours = ranges (min/avg/max)
# ─────────────────────────────────────────────────────────────────────────────

NATIONAL_LABOR_RATE = 110.0        # $/hr — national avg HVAC technician billing rate
HOUSTON_LABOR_RATE  = 105.0        # Houston metro (competitive market, slightly below national)
GULF_COAST_LABOR_RATE = 108.0

PRICING_RULES = [

    # ═══════════════════════════════════════════════════════════════════════════
    # AC UNIT — NATIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "ac_unit",
        "job_type": "full_system_replace",
        "region": "national",
        "parts_cost": {"min": 1800, "avg": 3200, "max": 5500,
                       "source": "Angi 2024 — includes unit + disconnect + pad + refrigerant"},
        "labor_hours": {"min": 6, "avg": 8, "max": 12},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 150.0,
        "refrigerant_cost_per_lb": 45.0,   # R-410A avg 2024
        "additional_costs": {"disposal_old_unit": 75, "crane_if_rooftop": 500,
                             "electrical_upgrade_if_needed": 450},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "evap_coil_replacement",
        "region": "national",
        "parts_cost": {"min": 600, "avg": 1100, "max": 2000,
                       "source": "AHRI coil pricing 2024"},
        "labor_hours": {"min": 4, "avg": 6, "max": 9},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"nitrogen_flush": 35, "dye_kit": 25},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "compressor_replacement",
        "region": "national",
        "parts_cost": {"min": 800, "avg": 1400, "max": 2500,
                       "source": "Copeland/Emerson scroll pricing"},
        "labor_hours": {"min": 3, "avg": 5, "max": 8},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"suction_filter_drier": 45, "capacitor_and_contactor": 90},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "refrigerant_recharge",
        "region": "national",
        "parts_cost": {"min": 150, "avg": 250, "max": 600,
                       "source": "R-410A avg $45/lb × 3-10 lbs; R-22 avg $120/lb"},
        "labor_hours": {"min": 1.5, "avg": 2, "max": 3},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,   # R-410A
        "additional_costs": {"leak_search_if_needed": 150, "UV_dye": 25},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "capacitor_replacement",
        "region": "national",
        "parts_cost": {"min": 25, "avg": 50, "max": 120,
                       "source": "OEM/aftermarket dual-run capacitor pricing"},
        "labor_hours": {"min": 0.5, "avg": 1, "max": 1.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "contactor_replacement",
        "region": "national",
        "parts_cost": {"min": 15, "avg": 35, "max": 80},
        "labor_hours": {"min": 0.5, "avg": 1, "max": 1.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "maintenance_tune_up",
        "region": "national",
        "parts_cost": {"min": 15, "avg": 30, "max": 60,
                       "source": "Coil cleaner, drain pan tablets, contactor inspection"},
        "labor_hours": {"min": 1.5, "avg": 2, "max": 2.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"filter_if_in_air_handler": 25},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "condenser_fan_motor",
        "region": "national",
        "parts_cost": {"min": 80, "avg": 175, "max": 350},
        "labor_hours": {"min": 1, "avg": 1.5, "max": 2.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },

    # ── coil_cleaning (added for estimate_engine CONDITION_TO_OPTIONS) ─────────
    {
        "equipment_type": "ac_unit",
        "job_type": "coil_cleaning",
        "region": "national",
        "parts_cost": {"min": 20, "avg": 45, "max": 90,
                       "source": "Nu-Brite / Rectorseal coil cleaner + drain pan tabs"},
        "labor_hours": {"min": 1.0, "avg": 1.5, "max": 2.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"drain_line_flush": 25},
    },
    # ── diagnostic_repair (generic repair after diagnosis) ───────────────────
    {
        "equipment_type": "ac_unit",
        "job_type": "diagnostic_repair",
        "region": "national",
        "parts_cost": {"min": 50, "avg": 150, "max": 400,
                       "source": "Misc parts — contactors, capacitors, wiring, valves"},
        "labor_hours": {"min": 1.5, "avg": 2.5, "max": 4.0},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"diagnostic_fee": 95},
    },
    # ── Houston metro equivalents ────────────────────────────────────────────
    {
        "equipment_type": "ac_unit",
        "job_type": "coil_cleaning",
        "region": "houston_metro",
        "parts_cost": {"min": 20, "avg": 40, "max": 80},
        "labor_hours": {"min": 1.0, "avg": 1.5, "max": 2.5},
        "labor_rate": HOUSTON_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"drain_line_flush": 25},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "diagnostic_repair",
        "region": "houston_metro",
        "parts_cost": {"min": 50, "avg": 140, "max": 380},
        "labor_hours": {"min": 1.5, "avg": 2.5, "max": 4.0},
        "labor_rate": HOUSTON_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"diagnostic_fee": 89},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # FURNACE — NATIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "furnace",
        "job_type": "full_system_replace",
        "region": "national",
        "parts_cost": {"min": 1200, "avg": 2200, "max": 4500,
                       "source": "Angi 2024 — 80% AFUE standard; 96% AFUE adds ~$600"},
        "labor_hours": {"min": 4, "avg": 6, "max": 9},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 125.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"gas_line_if_new_run": 350, "flue_reline_if_needed": 400,
                             "disposal_old_unit": 75, "thermostat_wire_if_upgrade": 150},
    },
    {
        "equipment_type": "furnace",
        "job_type": "heat_exchanger_replacement",
        "region": "national",
        "parts_cost": {"min": 500, "avg": 900, "max": 1800,
                       "source": "OEM exchanger 2024 pricing"},
        "labor_hours": {"min": 4, "avg": 6, "max": 10},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
        # NOTE: Many techs recommend full replacement if HX cracks — flag this
    },
    {
        "equipment_type": "furnace",
        "job_type": "draft_inducer_replacement",
        "region": "national",
        "parts_cost": {"min": 150, "avg": 300, "max": 550},
        "labor_hours": {"min": 1.5, "avg": 2.5, "max": 4},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "furnace",
        "job_type": "igniter_replacement",
        "region": "national",
        "parts_cost": {"min": 20, "avg": 45, "max": 100},
        "labor_hours": {"min": 0.5, "avg": 1, "max": 1.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "furnace",
        "job_type": "gas_valve_replacement",
        "region": "national",
        "parts_cost": {"min": 80, "avg": 200, "max": 400},
        "labor_hours": {"min": 1, "avg": 2, "max": 3},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "furnace",
        "job_type": "maintenance_tune_up",
        "region": "national",
        "parts_cost": {"min": 10, "avg": 20, "max": 40,
                       "source": "Filter, thermocouple check, burner cleaning supplies"},
        "labor_hours": {"min": 1, "avg": 1.5, "max": 2},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "furnace",
        "job_type": "control_board_replacement",
        "region": "national",
        "parts_cost": {"min": 120, "avg": 300, "max": 700},
        "labor_hours": {"min": 1, "avg": 2, "max": 3},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # HEAT PUMP — NATIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "heat_pump",
        "job_type": "full_system_replace",
        "region": "national",
        "parts_cost": {"min": 2000, "avg": 4000, "max": 7500,
                       "source": "Angi 2024 heat pump system cost"},
        "labor_hours": {"min": 6, "avg": 9, "max": 14},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 175.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"electrical_upgrade": 450, "disposal": 75,
                             "drain_line": 100},
    },
    {
        "equipment_type": "heat_pump",
        "job_type": "reversing_valve_replacement",
        "region": "national",
        "parts_cost": {"min": 150, "avg": 350, "max": 650},
        "labor_hours": {"min": 3, "avg": 5, "max": 7},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {},
    },
    {
        "equipment_type": "heat_pump",
        "job_type": "defrost_board_replacement",
        "region": "national",
        "parts_cost": {"min": 80, "avg": 175, "max": 350},
        "labor_hours": {"min": 1, "avg": 1.5, "max": 2.5},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },
    {
        "equipment_type": "heat_pump",
        "job_type": "refrigerant_recharge",
        "region": "national",
        "parts_cost": {"min": 200, "avg": 350, "max": 700},
        "labor_hours": {"min": 1.5, "avg": 2, "max": 3},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"leak_search": 150},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # DUCTWORK — NATIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "ductwork",
        "job_type": "full_duct_replace",
        "region": "national",
        "parts_cost": {"min": 1500, "avg": 3000, "max": 6000,
                       "source": "Flex duct, rigid metal, mastic sealant, R-8 insulation wrap"},
        "labor_hours": {"min": 8, "avg": 14, "max": 24},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 100.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"disposal_old_duct": 100, "attic_access_panels": 150},
    },
    {
        "equipment_type": "ductwork",
        "job_type": "duct_seal_and_repair",
        "region": "national",
        "parts_cost": {"min": 150, "avg": 400, "max": 900,
                       "source": "Mastic, Aeroseal average cost"},
        "labor_hours": {"min": 3, "avg": 5, "max": 10},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # AIR HANDLER — NATIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "air_handler",
        "job_type": "full_system_replace",
        "region": "national",
        "parts_cost": {"min": 800, "avg": 1600, "max": 3000},
        "labor_hours": {"min": 3, "avg": 5, "max": 8},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 75.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"disposal": 50},
    },
    {
        "equipment_type": "air_handler",
        "job_type": "blower_motor_replacement",
        "region": "national",
        "parts_cost": {"min": 150, "avg": 350, "max": 700},
        "labor_hours": {"min": 1.5, "avg": 2.5, "max": 4},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # THERMOSTAT — NATIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "thermostat",
        "job_type": "thermostat_upgrade",
        "region": "national",
        "parts_cost": {"min": 30, "avg": 200, "max": 450,
                       "source": "Basic: $30-80; Honeywell T6: $80; ecobee/Nest: $150-250; Carrier iComfort: $350"},
        "labor_hours": {"min": 0.5, "avg": 1, "max": 2},
        "labor_rate": NATIONAL_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"wiring_upgrade_if_needed": 150},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # HOUSTON METRO OVERRIDES
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "ac_unit",
        "job_type": "full_system_replace",
        "region": "houston_metro",
        "parts_cost": {"min": 2200, "avg": 3800, "max": 6000,
                       "source": "Houston market — premium for SEER 15+ (Texas EERS mandate)"},
        "labor_hours": {"min": 6, "avg": 8, "max": 12},
        "labor_rate": HOUSTON_LABOR_RATE,
        "permit_cost": 175.0,     # City of Houston permit fee 2024
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"disposal_old_unit": 75, "crane_if_rooftop": 500,
                             "electrical_upgrade_if_needed": 450,
                             "R22_recovery_if_old_system": 250},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "refrigerant_recharge",
        "region": "houston_metro",
        "parts_cost": {"min": 200, "avg": 350, "max": 800,
                       "source": "R-22 $120/lb; R-410A $45/lb — many older Houston systems still R-22"},
        "labor_hours": {"min": 1.5, "avg": 2, "max": 3},
        "labor_rate": HOUSTON_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"R22_surcharge_if_applicable": 200},
    },
    {
        "equipment_type": "ac_unit",
        "job_type": "evap_coil_replacement",
        "region": "houston_metro",
        "parts_cost": {"min": 700, "avg": 1200, "max": 2200,
                       "source": "Gulf coast corrosion rates mean more coil replacements — techs stock more units"},
        "labor_hours": {"min": 4, "avg": 6, "max": 9},
        "labor_rate": HOUSTON_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"nitrogen_flush": 35, "dye_kit": 25},
    },
    {
        "equipment_type": "furnace",
        "job_type": "full_system_replace",
        "region": "houston_metro",
        "parts_cost": {"min": 1400, "avg": 2400, "max": 4200,
                       "source": "Houston — most new furnaces are 96% AFUE due to mild winters"},
        "labor_hours": {"min": 4, "avg": 6, "max": 9},
        "labor_rate": HOUSTON_LABOR_RATE,
        "permit_cost": 150.0,
        "refrigerant_cost_per_lb": None,
        "additional_costs": {"gas_line": 350, "flue_reline": 400, "disposal": 75},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # GULF COAST OVERRIDES
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "equipment_type": "ac_unit",
        "job_type": "evap_coil_replacement",
        "region": "gulf_coast",
        "parts_cost": {"min": 800, "avg": 1400, "max": 2500,
                       "source": "Gulf coast formicary corrosion — coil avg 7yr replacement"},
        "labor_hours": {"min": 4, "avg": 6, "max": 9},
        "labor_rate": GULF_COAST_LABOR_RATE,
        "permit_cost": 0.0,
        "refrigerant_cost_per_lb": 45.0,
        "additional_costs": {"copper_coating_treatment": 75, "nitrogen_flush": 35, "dye_kit": 25},
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Seed runner
# ─────────────────────────────────────────────────────────────────────────────

async def seed_pricing_rules(db) -> int:
    """
    Insert all PRICING_RULES into the DB if the table is empty.
    Returns number of records inserted (0 if already seeded).
    """
    from sqlalchemy import select, func
    result = await db.execute(select(func.count()).select_from(PricingRule))
    count = result.scalar()
    if count and count > 0:
        print(f"[seed] pricing_rules already has {count} rows — skipping")
        return 0

    inserted = 0
    for rule_data in PRICING_RULES:
        rule = PricingRule(**rule_data)
        db.add(rule)
        inserted += 1

    await db.commit()
    print(f"[seed] Inserted {inserted} pricing rules")
    return inserted


if __name__ == "__main__":
    async def main():
        from db.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            n = await seed_pricing_rules(db)
            print(f"Seeded {n} pricing rules")

    asyncio.run(main())
