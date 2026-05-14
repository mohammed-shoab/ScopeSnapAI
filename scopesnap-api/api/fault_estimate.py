"""
WS-G — Estimate Engine v2 (Fault Card / Price List + better_option_estimate)
POST /api/estimates/fault-card

Implements the full three-option estimate from SnapAI_DataRepo_CompletionPlan_AI:
  * Fix 2:  Dynamic option labels by unit age  (0-5 / 6-10 / 11-15 / 15+ yrs)
  * Fix 3:  Replacement recommendation logic (age >= 8 yrs OR repair > 50% of replace cost)
  * Fix 4:  Better option from better_option_estimate JSONB (data-driven)
  * Fix 4:  Best option from replacement_cost_estimates when replacement recommended
  * Fix 7:  Five-year cost comparison in Best option when replacement recommended
  * Fix 5:  data_defaults used when model not found (warning surfaced to tech)

Surcharges (unchanged from v1):
  - attic_premium ($25-50 per visit)
  - after_hours (+25-50%)
  - r22_handling_surcharge ($75-150 if refrigerant=R-22)

Company markup applied to all options.
"""

import json
import logging
import math
import secrets
import string
from typing import Any, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from db.database import get_db
from db.models import Estimate, Assessment
from api.auth import get_current_user, AuthContext
from api.dependencies import get_tables, MarketTables

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


# -- Label sets by unit age ---------------------------------------------------

_LABEL_SETS = [
    {"max_age": 5,   "good": "Fix Today",     "better": "Fix + Peace of Mind",        "best": "Full Service"},
    {"max_age": 10,  "good": "Fix Today",     "better": "Fix + Prevent Next Failure",  "best": "Consider Replacing"},
    {"max_age": 15,  "good": "Temporary Fix", "better": "Repair + Extend Life",        "best": "Replace Now"},
    {"max_age": 999, "good": "Emergency Fix", "better": "Last Repair",                 "best": "Replace Immediately"},
]

def _get_labels(unit_age_years: Optional[int]) -> dict:
    age = unit_age_years or 7
    for s in _LABEL_SETS:
        if age <= s["max_age"]:
            return s
    return _LABEL_SETS[-1]


# -- Replacement recommendation logic ----------------------------------------

_REPLACEMENT_TRIGGER_AGE   = 8
_REPLACEMENT_COST_RATIO    = 0.50

def _should_recommend_replacement(
    unit_age_years: Optional[int],
    better_typical: int,
    replacement_typical: int,
) -> bool:
    age = unit_age_years or 0
    if age >= _REPLACEMENT_TRIGGER_AGE:
        return True
    if replacement_typical > 0 and (better_typical / replacement_typical) >= _REPLACEMENT_COST_RATIO:
        return True
    return False


# -- Five-year cost comparison ------------------------------------------------

_REPAIR_PROB_BY_AGE = {
    8: (0.55, 850), 9: (0.60, 900), 10: (0.65, 950),
    11: (0.70, 1000), 12: (0.75, 1100), 13: (0.80, 1200),
    14: (0.85, 1300), 15: (0.90, 1400),
}

def _five_year_comparison(repair_cost: int, replacement_cost: int, unit_age_years: Optional[int]) -> dict:
    age = min(unit_age_years or 8, 15)
    prob, avg_next = _REPAIR_PROB_BY_AGE.get(age, (0.90, 1400))
    repair_path   = repair_cost + (prob * avg_next * 2)
    energy_savings = replacement_cost * 0.003 * 5
    replace_path  = replacement_cost - energy_savings
    return {
        "repair_path_5yr_total":  math.ceil(repair_path),
        "replace_path_5yr_total": math.ceil(replace_path),
        "savings_note": f"Includes ~${math.ceil(energy_savings):,} in estimated energy savings over 5 years.",
    }


# -- Surcharge helper ---------------------------------------------------------

def _apply_surcharges(
    base: int,
    attic_premium: int,
    after_hours_pct: float,
    r22_surcharge: int,
    attic_access: bool,
    after_hours: bool,
    is_r22: bool,
) -> tuple:
    breakdown: dict = {}
    total = 0
    if attic_access and attic_premium > 0:
        breakdown["attic"] = attic_premium
        total += attic_premium
    if after_hours and after_hours_pct > 0:
        ah = round(base * after_hours_pct)
        breakdown["after_hours"] = ah
        total += ah
    if is_r22 and r22_surcharge > 0:
        breakdown["r22_handling"] = r22_surcharge
        total += r22_surcharge
    return total, breakdown


# -- Request / Response models ------------------------------------------------

class FaultCardEstimateRequest(BaseModel):
    card_id:        int             = Field(..., ge=1, le=19)
    tonnage:        Optional[float] = Field(None, ge=0.75, le=6.0)
    unit_age_years: Optional[int]   = Field(None, ge=0, le=50)
    install_year:   Optional[int]   = Field(None, ge=1970, le=2030)
    attic_access:   bool            = Field(False)
    after_hours:    bool            = Field(False)
    refrigerant:    Optional[str]   = Field(None)
    assessment_id:  Optional[str]   = Field(None)


class EstimateTier(BaseModel):
    tier:                 str
    label:                str
    base_amount:          int
    surcharges:           dict
    subtotal:             int
    markup_amount:        int
    total:                int
    recommended:          bool = False
    description:          Optional[str] = None
    why_recommended:      Optional[str] = None
    is_replacement:       bool = False
    five_year_comparison: Optional[dict] = None
    parts_included:       list = []
    service_items:        list = []


class FaultCardEstimateResponse(BaseModel):
    id:                  Optional[str] = None
    card_id:             int
    card_name:           str
    phase:               Optional[str]
    difficulty:          Optional[str]
    tech_notes:          Optional[str]
    tiers:               list
    r22_alert:           bool
    attic_applied:       bool
    after_hours_applied: bool
    markup_pct:          float
    unit_age_years:      Optional[int]
    using_defaults:      bool = False
    defaults_warning:    Optional[str] = None
    generated_at:        str


# -- POST /api/estimates/fault-card ------------------------------------------

@router.post("/fault-card", status_code=200, response_model=FaultCardEstimateResponse)
async def generate_fault_card_estimate(
    body: FaultCardEstimateRequest,
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-G v2: Three-option estimate with dynamic labels, better_option_estimate,
    replacement recommendation, and five-year cost comparison.
    """

    # Resolve unit age
    unit_age = body.unit_age_years
    if unit_age is None and body.install_year:
        unit_age = datetime.now(timezone.utc).year - body.install_year

    labels = _get_labels(unit_age)

    # 1. Load fault card (includes better_option_estimate)
    fc_row = await db.execute(
        text(f"""
            SELECT card_id, card_name, phase, difficulty, tech_notes,
                   price_list_min, price_list_typical, price_list_max,
                   better_option_estimate
            FROM {tables.fault_cards}
            WHERE card_id = :card_id
        """),
        {"card_id": body.card_id},
    )
    fc = fc_row.fetchone()
    if not fc:
        raise HTTPException(status_code=404, detail=f"Fault card {body.card_id} not found.")

    # 2. Load pricing tiers A/B/C
    pt_rows = await db.execute(
        text("SELECT tier, estimate_amount FROM pricing_tiers WHERE card_id = :cid ORDER BY tier"),
        {"cid": body.card_id},
    )
    pricing = {row.tier: row.estimate_amount for row in pt_rows.fetchall()}
    if not pricing:
        raise HTTPException(status_code=404, detail=f"No pricing tiers for card {body.card_id}.")

    base_A = pricing.get("A", fc.price_list_min or 0)
    base_B = pricing.get("B", fc.price_list_typical or 0)
    base_C = pricing.get("C", fc.price_list_max or 0)

    # 3. Load surcharge config
    lr_row = await db.execute(
        text(f"""
            SELECT attic_premium_min, attic_premium_max,
                   r22_surcharge_min, r22_surcharge_max
            FROM {tables.labor_rates} LIMIT 1
        """),
    )
    lr = lr_row.fetchone()
    attic_premium   = int((lr.attic_premium_min + lr.attic_premium_max) / 2) if lr else 37
    after_hours_pct = 0.375
    r22_surcharge   = int((lr.r22_surcharge_min + lr.r22_surcharge_max) / 2) if lr else 112
    is_r22          = (body.refrigerant or "").upper().startswith("R-22")

    # 4. Get company markup
    markup_row = await db.execute(
        text("SELECT default_markup_pct FROM companies WHERE id = :cid LIMIT 1"),
        {"cid": auth.company_id},
    )
    markup_result = markup_row.fetchone()
    markup_pct  = float(markup_result.default_markup_pct) if markup_result else 35.0
    markup_mult = 1 + markup_pct / 100

    # 5. Load replacement cost
    repl_row = await db.execute(
        text("""
            SELECT price_min, price_max, price_typical
            FROM {tables.replacement_costs}
            WHERE tonnage = :t ORDER BY id LIMIT 1
        """),
        {"t": body.tonnage or 0},
    )
    repl = repl_row.fetchone()
    if not repl:
        repl_row2 = await db.execute(
            text(f"SELECT price_min, price_max, price_typical FROM {tables.replacement_costs} WHERE tonnage = 0 LIMIT 1"),
        )
        repl = repl_row2.fetchone()
    repl_typical = repl.price_typical if repl else 5500

    # 6. Check data_defaults for warning
    using_defaults = False
    defaults_warning = None
    if not body.tonnage:
        drow = await db.execute(text(f"SELECT tech_warning FROM {tables.data_defaults} LIMIT 1"))
        defs = drow.fetchone()
        if defs and defs.tech_warning:
            using_defaults = True
            defaults_warning = defs.tech_warning

    # 7. Parse better_option_estimate
    better_data = None
    raw_boe = fc.better_option_estimate
    if raw_boe:
        if isinstance(raw_boe, str):
            try:
                better_data = json.loads(raw_boe)
            except Exception:
                better_data = None
        elif isinstance(raw_boe, dict):
            better_data = raw_boe

    # 8. Determine if replacement should be recommended
    better_base = better_data.get("typical", base_B) if better_data else base_B
    recommend_replacement = _should_recommend_replacement(unit_age, better_base, repl_typical)

    tiers = []

    # Tier A: Good
    surcharge_A, bkdn_A = _apply_surcharges(base_A, attic_premium, after_hours_pct, r22_surcharge,
                                             body.attic_access, body.after_hours, is_r22)
    sub_A    = base_A + surcharge_A
    mkup_A   = round(sub_A * (markup_mult - 1))
    total_A  = sub_A + mkup_A
    tiers.append(EstimateTier(
        tier="A", label=labels["good"],
        base_amount=base_A, surcharges=bkdn_A, subtotal=sub_A,
        markup_amount=mkup_A, total=total_A, recommended=False,
        description=f"Diagnose and repair: {fc.card_name}. Gets your system running today.",
    ))

    # Tier B: Better
    if better_data:
        b_base  = better_data.get("typical", base_B)
        b_desc  = better_data.get("description", f"Enhanced repair: {fc.card_name}")
        b_why   = better_data.get("why_recommended")
        b_parts = better_data.get("parts_included", [])
        b_svc   = better_data.get("service_items", [])
    else:
        b_base  = base_B
        b_desc  = f"Enhanced repair: {fc.card_name} with preventive service."
        b_why   = None
        b_parts = []
        b_svc   = []

    surcharge_B, bkdn_B = _apply_surcharges(b_base, attic_premium, after_hours_pct, r22_surcharge,
                                             body.attic_access, body.after_hours, is_r22)
    sub_B   = b_base + surcharge_B
    mkup_B  = round(sub_B * (markup_mult - 1))
    total_B = sub_B + mkup_B
    tiers.append(EstimateTier(
        tier="B", label=labels["better"],
        base_amount=b_base, surcharges=bkdn_B, subtotal=sub_B,
        markup_amount=mkup_B, total=total_B,
        recommended=not recommend_replacement,
        description=b_desc, why_recommended=b_why,
        parts_included=b_parts, service_items=b_svc,
    ))

    # Tier C: Best
    if recommend_replacement:
        repl_mkup  = round(repl_typical * (markup_mult - 1))
        repl_total = repl_typical + repl_mkup
        fyr        = _five_year_comparison(total_B, repl_total, unit_age)
        age_str    = f"At {unit_age} years old, " if unit_age else ""
        tiers.append(EstimateTier(
            tier="C", label=labels["best"],
            base_amount=repl_typical, surcharges={}, subtotal=repl_typical,
            markup_amount=repl_mkup, total=repl_total,
            recommended=True, is_replacement=True,
            description=(
                f"{age_str}complete system replacement eliminates near-term repair risk "
                "and reduces electricity costs by approximately 30-40%."
            ),
            five_year_comparison=fyr,
        ))
    else:
        c_base = round(b_base * 1.35)
        surcharge_C, bkdn_C = _apply_surcharges(c_base, attic_premium, after_hours_pct, r22_surcharge,
                                                 body.attic_access, body.after_hours, is_r22)
        sub_C   = c_base + surcharge_C
        mkup_C  = round(sub_C * (markup_mult - 1))
        total_C = sub_C + mkup_C
        tiers.append(EstimateTier(
            tier="C", label=labels["best"],
            base_amount=c_base, surcharges=bkdn_C, subtotal=sub_C,
            markup_amount=mkup_C, total=total_C, recommended=False,
            description=f"Comprehensive repair: {fc.card_name} plus full system health check.",
        ))

    # 9. Persist estimate (BUG-011 fix)
    estimate_id = None
    if body.assessment_id:
        asmt_row = await db.execute(
            select(Assessment).where(
                Assessment.id == body.assessment_id,
                Assessment.company_id == auth.company_id,
            )
        )
        asmt = asmt_row.scalar_one_or_none()
        if asmt:
            existing = await db.execute(
                text("SELECT id FROM estimates WHERE assessment_id = :aid LIMIT 1"),
                {"aid": body.assessment_id},
            )
            existing_row = existing.fetchone()
            if existing_row:
                estimate_id = str(existing_row.id)
            else:
                options_payload = [
                    {
                        "tier": t.tier, "name": t.label,
                        "total": float(t.total), "subtotal": float(t.subtotal),
                        "markup_percent": float(markup_pct),
                        "recommended": t.recommended,
                        "is_replacement": t.is_replacement,
                        "description": t.description,
                        "why_recommended": t.why_recommended,
                        "five_year_comparison": t.five_year_comparison,
                        "line_items": [{"description": fc.card_name, "amount": float(t.base_amount), "category": "repair"}],
                    }
                    for t in tiers
                ]
                report_token    = secrets.token_urlsafe(32)[:32]
                report_short_id = "rpt-" + "".join(secrets.choice(string.digits) for _ in range(4))
                new_estimate    = Estimate(
                    assessment_id=body.assessment_id, company_id=auth.company_id,
                    report_token=report_token, report_short_id=report_short_id,
                    options=options_payload, markup_percent=markup_pct, status="draft",
                )
                db.add(new_estimate)
                await db.flush()
                estimate_id = str(new_estimate.id)
                logger.info("[fault_estimate v2] Saved estimate %s for assessment %s card %d age=%s",
                            estimate_id, body.assessment_id, body.card_id, unit_age)

    return FaultCardEstimateResponse(
        id=estimate_id, card_id=fc.card_id, card_name=fc.card_name,
        phase=fc.phase, difficulty=fc.difficulty, tech_notes=fc.tech_notes,
        tiers=tiers, r22_alert=is_r22,
        attic_applied=body.attic_access, after_hours_applied=body.after_hours,
        markup_pct=markup_pct, unit_age_years=unit_age,
        using_defaults=using_defaults, defaults_warning=defaults_warning,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
