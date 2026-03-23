"""
ScopeSnap — Estimate Generation Engine
Pure math + DB lookups. ZERO AI calls. All deterministic.

Implements the 9-step pipeline from Tech Spec §05:
1. Get AI analysis results from assessment
2. Determine job types from condition → options mapping
3. Look up pricing (cascade: company → region → national)
4. Calculate line items (parts + labor + permit + refrigerant + disposal)
5. Apply markup
6. Calculate energy savings (SEER comparison)
7. Check rebate eligibility
8. Build Good/Better/Best options array
9. Calculate 5-year total cost per option

WP-04 deliverable.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from db.models import PricingRule


# ── EIA State Average Annual Cooling Costs (USD) ──────────────────────────────
# Source: EIA Residential Energy Consumption Survey 2020
EIA_COOLING_COST_BY_STATE = {
    "TX": 700, "FL": 680, "LA": 620, "MS": 580, "GA": 540,
    "AL": 520, "SC": 500, "AR": 480, "AZ": 650, "NM": 400,
    "OK": 430, "NC": 440, "TN": 420, "CA": 380, "NV": 550,
    "DEFAULT": 380,
}

# ── Condition → Job Type Mapping (the "intelligence" layer) ───────────────────
# Maps AI condition findings to recommended job options.
# Each entry: (condition_trigger, job_type_good, job_type_better, job_type_best)
CONDITION_TO_OPTIONS = {
    # Coil issues
    ("evaporator_coil", "minor_issue"): {
        "good": "coil_cleaning",
        "better": "coil_cleaning",
        "best": "coil_replacement",
    },
    ("evaporator_coil", "moderate_issue"): {
        "good": "coil_cleaning",
        "better": "coil_replacement",
        "best": "full_system",
    },
    ("evaporator_coil", "severe_issue"): {
        "good": "coil_replacement",
        "better": "full_system",
        "best": "full_system_premium",
    },
    # Compressor
    ("compressor", "moderate_issue"): {
        "good": "repair",
        "better": "compressor_replacement",
        "best": "full_system",
    },
    ("compressor", "severe_issue"): {
        "good": "compressor_replacement",
        "better": "full_system",
        "best": "full_system_premium",
    },
    # Refrigerant
    ("refrigerant_lines", "minor_issue"): {
        "good": "refrigerant_recharge",
        "better": "refrigerant_recharge",
        "best": "repair",
    },
    ("refrigerant_lines", "moderate_issue"): {
        "good": "refrigerant_recharge",
        "better": "repair",
        "best": "coil_replacement",
    },
    # General / maintenance
    ("overall", "excellent"): {
        "good": "maintenance",
        "better": "maintenance",
        "best": "maintenance",
    },
    ("overall", "good"): {
        "good": "maintenance",
        "better": "maintenance",
        "best": "repair",
    },
    ("overall", "fair"): {
        "good": "maintenance",
        "better": "repair",
        "best": "coil_replacement",
    },
    ("overall", "poor"): {
        "good": "repair",
        "better": "full_system",
        "best": "full_system_premium",
    },
    ("overall", "critical"): {
        "good": "full_system",
        "better": "full_system",
        "best": "full_system_premium",
    },
}

# Display names for job types
JOB_TYPE_NAMES = {
    "coil_cleaning": "Clean & Treat Coil",
    "coil_replacement": "Replace Evaporator Coil",
    "full_system": "New System Installation",
    "full_system_premium": "Premium High-Efficiency System",
    "compressor_replacement": "Compressor Replacement",
    "refrigerant_recharge": "Refrigerant Recharge",
    "maintenance": "Preventive Maintenance",
    "repair": "Diagnostic & Repair",
}

TIER_DESCRIPTIONS = {
    "good": {
        "label": "Good",
        "badge": "Budget",
        "description": "Addresses the immediate issue at the lowest cost."
    },
    "better": {
        "label": "Better",
        "badge": "Recommended",
        "description": "Best value — resolves the root cause with durable parts."
    },
    "best": {
        "label": "Best",
        "badge": "Premium",
        "description": "Long-term solution with maximum efficiency and warranty."
    },
}


# ── Pricing Lookup ─────────────────────────────────────────────────────────────

async def get_pricing_rule(
    equipment_type: str,
    job_type: str,
    company_id: Optional[str],
    state: Optional[str],
    db: AsyncSession,
) -> Optional[PricingRule]:
    """
    Pricing cascade: company-specific → regional → national default.
    Returns the most specific pricing rule found.
    """
    # Company-specific pricing (highest priority)
    if company_id:
        result = await db.execute(
            select(PricingRule).where(
                PricingRule.company_id == company_id,
                PricingRule.equipment_type == equipment_type,
                PricingRule.job_type == job_type,
            )
        )
        rule = result.scalars().first()
        if rule:
            return rule

    # Regional pricing (if state available)
    if state:
        state_region_map = {
            "TX": "south_central", "LA": "south_central", "OK": "south_central",
            "FL": "southeast", "GA": "southeast", "SC": "southeast",
            "CA": "west", "AZ": "west", "NV": "west",
            "NY": "northeast", "MA": "northeast", "PA": "northeast",
        }
        region = state_region_map.get(state)
        if region:
            result = await db.execute(
                select(PricingRule).where(
                    PricingRule.company_id == None,
                    PricingRule.equipment_type == equipment_type,
                    PricingRule.job_type == job_type,
                    PricingRule.region == region,
                )
            )
            rule = result.scalars().first()
            if rule:
                return rule

    # National default (fallback)
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.company_id == None,
            PricingRule.equipment_type == equipment_type,
            PricingRule.job_type == job_type,
            PricingRule.region == "national",
        )
    )
    return result.scalars().first()


# ── Line Item Calculation ──────────────────────────────────────────────────────

def calculate_line_items(
    rule: PricingRule,
    markup_percent: float,
    tier: str = "avg",
) -> tuple[list[dict], Decimal]:
    """
    Calculates line items for a pricing rule at the given tier (min/avg/max).
    Returns (line_items, total_before_markup).

    Line items: parts, labor, permit, refrigerant, additional costs.
    """
    line_items = []
    subtotal = Decimal("0.00")

    # Parts
    if rule.parts_cost:
        parts_val = Decimal(str(rule.parts_cost.get(tier, rule.parts_cost.get("avg", 0))))
        if parts_val > 0:
            line_items.append({
                "category": "parts",
                "description": f"Parts and materials ({JOB_TYPE_NAMES.get(rule.job_type, rule.job_type)})",
                "quantity": 1.0,
                "unit_cost": float(parts_val),
                "total": float(parts_val),
                "source": "pricing_db",
            })
            subtotal += parts_val

    # Labor
    if rule.labor_hours and rule.labor_rate:
        labor_h = Decimal(str(rule.labor_hours.get(tier, rule.labor_hours.get("avg", 0))))
        labor_rate = Decimal(str(rule.labor_rate))
        labor_cost = (labor_h * labor_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)
        if labor_cost > 0:
            line_items.append({
                "category": "labor",
                "description": f"Labor ({float(labor_h)} hours @ ${float(labor_rate)}/hr)",
                "quantity": float(labor_h),
                "unit_cost": float(labor_rate),
                "total": float(labor_cost),
                "source": "pricing_db",
            })
            subtotal += labor_cost

    # Permit
    if rule.permit_cost and float(rule.permit_cost) > 0:
        permit = Decimal(str(rule.permit_cost))
        line_items.append({
            "category": "permits",
            "description": "Permit and inspection fees",
            "quantity": 1.0,
            "unit_cost": float(permit),
            "total": float(permit),
            "source": "pricing_db",
        })
        subtotal += permit

    # Refrigerant
    if rule.refrigerant_cost_per_lb and rule.additional_costs:
        ref_lbs = Decimal(str(rule.additional_costs.get("refrigerant_lbs", 0)))
        ref_rate = Decimal(str(rule.refrigerant_cost_per_lb))
        ref_cost = (ref_lbs * ref_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)
        if ref_cost > 0:
            line_items.append({
                "category": "refrigerant",
                "description": f"Refrigerant ({float(ref_lbs)} lbs)",
                "quantity": float(ref_lbs),
                "unit_cost": float(ref_rate),
                "total": float(ref_cost),
                "source": "pricing_db",
            })
            subtotal += ref_cost

    # Additional costs (disposal, etc.)
    if rule.additional_costs:
        for key, val in rule.additional_costs.items():
            if key == "refrigerant_lbs":
                continue  # Already handled
            if val and float(val) > 0:
                name = key.replace("_", " ").title()
                cost = Decimal(str(val)).quantize(Decimal("0.01"), ROUND_HALF_UP)
                line_items.append({
                    "category": "disposal" if "disposal" in key else "parts",
                    "description": name,
                    "quantity": 1.0,
                    "unit_cost": float(cost),
                    "total": float(cost),
                    "source": "pricing_db",
                })
                subtotal += cost

    return line_items, subtotal


def apply_markup(subtotal: Decimal, markup_percent: float) -> Decimal:
    """Apply markup percentage to subtotal. Returns total with markup."""
    markup = Decimal(str(markup_percent)) / Decimal("100")
    return (subtotal * (1 + markup)).quantize(Decimal("0.01"), ROUND_HALF_UP)


# ── Energy Savings Calculation ─────────────────────────────────────────────────

def calculate_energy_savings(
    current_seer: Optional[float],
    new_seer: Optional[float],
    state: Optional[str] = None,
) -> dict:
    """
    Calculates annual energy savings when replacing equipment.
    Uses EIA state average cooling cost as baseline.

    Returns dict with annual_savings, 5yr_savings, seer_improvement_pct.
    """
    if not current_seer or not new_seer or new_seer <= current_seer:
        return {"annual_savings": 0, "five_year_savings": 0, "seer_improvement_pct": 0}

    annual_cooling_cost = EIA_COOLING_COST_BY_STATE.get(state or "DEFAULT", 380)
    # Savings = base_cost × (1 - old_seer / new_seer)
    savings_pct = 1 - (current_seer / new_seer)
    annual_savings = round(annual_cooling_cost * savings_pct, 0)
    five_year_savings = annual_savings * 5
    seer_improvement = round((new_seer - current_seer) / current_seer * 100, 1)

    return {
        "annual_savings": int(annual_savings),
        "five_year_savings": int(five_year_savings),
        "seer_improvement_pct": seer_improvement,
        "current_seer": current_seer,
        "new_seer": new_seer,
    }


# ── Five-Year Total Cost ───────────────────────────────────────────────────────

def calculate_five_year_cost(
    upfront: float,
    annual_energy_cost: float,
    condition: str,
    equipment_age: Optional[int],
) -> float:
    """
    5-year total = upfront + (annual_energy × 5) + estimated_future_repairs.
    Future repairs estimated from condition + age.
    """
    # Estimate future repairs based on condition
    repair_probability_cost = {
        "excellent": 200,
        "good": 400,
        "fair": 800,
        "poor": 1800,
        "critical": 3000,
    }
    future_repairs = repair_probability_cost.get(condition, 500)

    # Age multiplier — older = more likely to fail again
    age = equipment_age or 10
    age_multiplier = min(2.0, 1.0 + (age - 10) * 0.05) if age > 10 else 1.0
    future_repairs = round(future_repairs * age_multiplier, -1)

    return round(upfront + (annual_energy_cost * 5) + future_repairs, 2)


# ── Main Estimate Generation Function ────────────────────────────────────────

async def generate_estimate(
    assessment_id: str,
    assessment: object,  # Assessment ORM model
    company_id: str,
    company_state: Optional[str],
    markup_percent: float,
    db: AsyncSession,
) -> dict:
    """
    Generates Good/Better/Best estimate options from AI analysis results.
    Pure math + DB lookups. NO AI calls.

    Returns the complete estimate dict ready to store.
    """
    # ── Step 1: Get AI analysis ──────────────────────────────────────────────
    equipment_type = "ac_unit"  # Default
    if assessment.ai_equipment_id:
        equipment_type = assessment.ai_equipment_id.get("equipment_type", "ac_unit")
        if equipment_type == "unknown":
            equipment_type = "ac_unit"

    overall_condition = "fair"
    if assessment.ai_condition:
        overall_condition = assessment.ai_condition.get("overall", "fair")

    components = []
    if assessment.ai_condition:
        components = assessment.ai_condition.get("components", [])

    estimated_age = None
    if assessment.ai_equipment_id:
        estimated_age = assessment.ai_equipment_id.get("estimated_age_years")
    if not estimated_age and assessment.ai_equipment_id:
        decoded = assessment.ai_equipment_id.get("serial_decoded", {})
        if decoded and decoded.get("year"):
            import datetime
            estimated_age = datetime.datetime.now().year - decoded["year"]

    # ── Step 2: Determine job types ──────────────────────────────────────────
    # Find worst component issue
    job_types_for_tiers = None
    for comp in components:
        comp_name = comp.get("name", "")
        comp_cond = comp.get("condition", "normal")
        key = (comp_name, comp_cond)
        if key in CONDITION_TO_OPTIONS:
            job_types_for_tiers = CONDITION_TO_OPTIONS[key]
            break

    # Fall back to overall condition
    if not job_types_for_tiers:
        key = ("overall", overall_condition)
        job_types_for_tiers = CONDITION_TO_OPTIONS.get(key, {
            "good": "maintenance",
            "better": "repair",
            "best": "full_system",
        })

    # ── Steps 3-8: Calculate options ────────────────────────────────────────
    tiers = ["good", "better", "best"]
    price_levels = {"good": "min", "better": "avg", "best": "max"}
    options = []

    for tier in tiers:
        job_type = job_types_for_tiers.get(tier, "maintenance")
        price_level = price_levels[tier]

        # Step 3: Look up pricing
        rule = await get_pricing_rule(
            equipment_type=equipment_type,
            job_type=job_type,
            company_id=company_id,
            state=company_state,
            db=db,
        )

        if not rule:
            # Fallback to any matching job type
            rule = await get_pricing_rule(
                equipment_type=equipment_type,
                job_type="maintenance",
                company_id=company_id,
                state=company_state,
                db=db,
            )

        if not rule:
            # If still no rule, use defaults
            line_items = []
            subtotal = Decimal("450.00")  # Default floor
        else:
            # Step 4: Calculate line items
            line_items, subtotal = calculate_line_items(rule, markup_percent, price_level)

        # Step 5: Apply markup
        total_with_markup = apply_markup(subtotal, markup_percent)

        # Step 6: Energy savings (only for full_system options)
        energy_savings = {}
        current_seer = None
        if assessment.ai_equipment_id:
            # Try to get SEER from known model
            from services.equipment_matcher import match_equipment_model
            try:
                model = await match_equipment_model(
                    assessment.ai_equipment_id.get("brand", ""),
                    assessment.ai_equipment_id.get("model", ""),
                    db
                )
                if model and model.seer_rating:
                    current_seer = float(model.seer_rating)
            except Exception:
                pass

        if "full_system" in job_type and current_seer:
            new_seer = 18.0 if "premium" in job_type else 16.0
            energy_savings = calculate_energy_savings(
                current_seer=current_seer,
                new_seer=new_seer,
                state=company_state,
            )

        # Step 7: Rebate check (simplified — check for high SEER)
        rebate_available = 0
        if "premium" in job_type or job_type == "full_system_premium":
            rebate_available = 500  # Simplified IRA/ENERGYSTAR rebate estimate

        # Build option
        tier_info = TIER_DESCRIPTIONS[tier]
        option = {
            "tier": tier,
            "label": tier_info["label"],
            "badge": tier_info["badge"],
            "job_type": job_type,
            "name": JOB_TYPE_NAMES.get(job_type, job_type.replace("_", " ").title()),
            "description": tier_info["description"],
            "line_items": line_items,
            "subtotal": float(subtotal),
            "total": float(total_with_markup),
            "markup_percent": markup_percent,
            "energy_savings": energy_savings,
            "rebate_available": rebate_available,
            "total_after_rebate": float(total_with_markup) - rebate_available,
        }

        # Step 9: 5-year total cost
        annual_energy = EIA_COOLING_COST_BY_STATE.get(company_state or "DEFAULT", 380)
        if energy_savings:
            post_install_annual = annual_energy - energy_savings.get("annual_savings", 0)
        else:
            post_install_annual = annual_energy

        option["five_year_total"] = calculate_five_year_cost(
            upfront=float(total_with_markup),
            annual_energy_cost=post_install_annual,
            condition=overall_condition,
            equipment_age=estimated_age,
        )

        options.append(option)

    # Deduplicate if tiers happen to select same job type
    seen_jobs = set()
    unique_options = []
    for opt in options:
        key = opt["job_type"]
        if key not in seen_jobs:
            seen_jobs.add(key)
            unique_options.append(opt)
        else:
            # If duplicate, adjust the total slightly to differentiate
            opt["total"] = float(Decimal(str(opt["total"])) * Decimal("1.15"))
            opt["five_year_total"] = calculate_five_year_cost(
                opt["total"], post_install_annual, overall_condition, estimated_age
            )
            unique_options.append(opt)

    return {
        "options": unique_options,
        "equipment_type": equipment_type,
        "overall_condition": overall_condition,
        "estimated_age_years": estimated_age,
    }
