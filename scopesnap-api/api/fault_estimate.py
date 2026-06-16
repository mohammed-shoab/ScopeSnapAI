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
from api.recommend import get_recommended_tier_internal
from api.dependencies import get_tables, MarketTables
from services.condition_signals import derive_condition_signal_from_assessment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


# -- Label sets by unit age ---------------------------------------------------

_LABEL_SETS = [
    {"max_age": 5,   "good": "Fix Today",     "better": "Fix + Peace of Mind",        "best": "Full Service"},
    {"max_age": 10,  "good": "Fix Today",     "better": "Fix + Prevent Next Failure",  "best": "Consider Replacing"},
    {"max_age": 15,  "good": "Temporary Fix", "better": "Repair + Extend Life",        "best": "Replace Now"},
    {"max_age": 999, "good": "Emergency Fix", "better": "Last Repair",                 "best": "Replace Immediately"},
]

# Stage 2: a single explicit "missing age" sentinel — no silent numeric default.
DEFAULT_UNKNOWN_AGE = None

# Neutral labels used when unit age is unknown: never imply the unit is new
# (would hide replacement) nor old (would alarm). Just repair-forward wording.
_UNKNOWN_AGE_LABELS = {
    "max_age": 0, "good": "Basic Repair",
    "better": "Repair + Maintenance", "best": "Full Service",
}

def _get_labels(unit_age_years: Optional[int]) -> dict:
    if unit_age_years is None:
        return _UNKNOWN_AGE_LABELS
    for s in _LABEL_SETS:
        if unit_age_years <= s["max_age"]:
            return s
    return _LABEL_SETS[-1]


# -- Recommendation engine: fault severity × age bucket ----------------------
# Fix: algo-bias audit 2026-05-29. Replaces pure-age trigger (_REPLACEMENT_TRIGGER_AGE=8)
# which recommended replacement for ALL mid-life units regardless of fault cost.
# Now uses a 3×3 matrix: age_bucket × fault_severity → recommended tier (A/B/C).

# Stage 2: replacement trigger age, sourced from ac_data_repo.json
# lifecycle_rules.replacement_trigger_age_years (15). The legacy hardcoded
# value of 8 was removed in the 2026-05-29 algo-bias audit; this reinstates
# a single, data-reconciled module constant used for the end_of_life boundary.
_REPLACEMENT_TRIGGER_AGE = 15

_SEVERITY_EASY_MAX_USD   = 400   # easy fault: difficulty=easy AND repair < $400
_SEVERITY_MEDIUM_MAX_USD = 800   # medium fault: repair < $800

# Maps (age_bucket, fault_severity) → recommended tier string "A"/"B"/"C"
_URGENCY_RULES: dict = {
    ("young",       "easy"):   "A",
    ("young",       "medium"): "A",
    ("young",       "major"):  "B",
    ("mid_life",    "easy"):   "A",   # KEY FIX: was always "C" due to age≥8 trigger
    ("mid_life",    "medium"): "B",
    ("mid_life",    "major"):  "C",
    ("end_of_life", "easy"):   "B",
    ("end_of_life", "medium"): "C",
    ("end_of_life", "major"):  "C",
}

# Reasoning strings for each combination (included in API response)
_URGENCY_REASONS: dict = {
    ("young",       "easy"):   "Young system with a minor fault — repair is the right call.",
    ("young",       "medium"): "Young system — repair is cost-effective.",
    ("young",       "major"):  "Young system but the fault is significant — enhanced repair protects your investment.",
    ("mid_life",    "easy"):   "Mid-life system but the fault is minor — repair is more cost-effective than replacement.",
    ("mid_life",    "medium"): "Mid-life system with a moderate fault — enhanced repair is the best value.",
    ("mid_life",    "major"):  "Mid-life system with a major fault — replacement is the better long-term value.",
    ("end_of_life", "easy"):   "End-of-life system — even minor faults are warning signs. Plan for replacement.",
    ("end_of_life", "medium"): "End-of-life system with a moderate fault — replacement is the right call.",
    ("end_of_life", "major"):  "End-of-life system with a major fault — replacement is urgent.",
}


def _get_age_bucket(unit_age_years: Optional[int]) -> str:
    """Classify unit age into young / mid_life / end_of_life / unknown.

    Stage 2: no silent default. Missing age -> "unknown" (never silently
    treated as 0). end_of_life boundary is _REPLACEMENT_TRIGGER_AGE (15),
    reconciled with ac_data_repo lifecycle_rules.replacement_trigger_age_years.
    """
    if unit_age_years is None:
        return "unknown"
    if unit_age_years <= 7:
        return "young"
    if unit_age_years < _REPLACEMENT_TRIGGER_AGE:
        return "mid_life"
    return "end_of_life"


def _compute_fault_severity(difficulty: str, repair_typical_usd: int) -> str:
    """
    Classify fault severity as easy / medium / major.
    Conservative: prefer under-calling severity (favor cheaper tier) when ambiguous.
    """
    d = (difficulty or "").lower()
    if d == "easy" and repair_typical_usd < _SEVERITY_EASY_MAX_USD:
        return "easy"
    if repair_typical_usd < _SEVERITY_MEDIUM_MAX_USD:
        return "medium"
    return "major"


def _compute_recommended_tier(
    unit_age_years: Optional[int],
    fault_difficulty: str,
    fault_repair_typical: int,
    better_typical: int,
    replacement_typical: int,
) -> tuple:
    """
    Compute the recommended tier string ("A"/"B"/"C") and a human-readable reason.
    Uses age_bucket × fault_severity matrix.
    Falls back to cost-ratio check for edge cases (very expensive repair on any unit).
    Returns (tier_str, reason_str, age_bucket, severity).
    """
    age_bucket = _get_age_bucket(unit_age_years)
    severity   = _compute_fault_severity(fault_difficulty, fault_repair_typical)

    if age_bucket == "unknown":
        # No reliable age signal -> never recommend replacement (C) from age.
        # Severity-only: easy -> A, medium/major -> B. The replace gate
        # (requires_user_chooser) surfaces the replacement option in the UI.
        tier   = "A" if severity == "easy" else "B"
        reason = "Age not confirmed — recommending repair; replacement shown as an option."
        return tier, reason, age_bucket, severity

    tier       = _URGENCY_RULES.get((age_bucket, severity), "B")
    reason     = _URGENCY_REASONS.get((age_bucket, severity), "Recommendation based on unit age and fault severity.")

    # Safety override: if repair cost > 50% of replacement on any unit, never recommend A
    _REPLACEMENT_COST_RATIO = 0.50
    if (tier == "A" and replacement_typical > 0
            and better_typical > 0
            and (better_typical / replacement_typical) >= _REPLACEMENT_COST_RATIO):
        tier   = "B"
        reason = "Repair cost is significant relative to replacement — enhanced repair is more prudent."

    return tier, reason, age_bucket, severity


def _should_recommend_replacement(
    unit_age_years: Optional[int],
    better_typical: int,
    replacement_typical: int,
    fault_difficulty: str = "medium",
    fault_repair_typical: int = 0,
) -> bool:
    """Legacy shim — returns True only when _compute_recommended_tier returns C."""
    tier, _, _, _ = _compute_recommended_tier(
        unit_age_years, fault_difficulty, fault_repair_typical,
        better_typical, replacement_typical,
    )
    return tier == "C"


# -- Stage 2: reliable-age gate + replace-recommendation gate -----------------

# Sources we trust enough to drive a replacement recommendation on age alone.
def _has_reliable_age(age_source: Optional[str],
                      age_confidence: Optional[str],
                      unit_age_years: Optional[int]) -> bool:
    """True only for trustworthy age provenance:
      - serial decoder at >= medium confidence
      - plate_date (printed manufacture date)
      - homeowner_input at >= approximate
      - legacy_brand_age_floor
    False for: no age, "unknown" confidence, or a tech-marked Unknown.
    """
    if unit_age_years is None:
        return False
    src = (age_source or "").strip().lower()
    conf = (age_confidence or "").strip().lower()
    # plate_date and legacy floors are reliable on provenance alone.
    if src in ("plate_date", "plate", "legacy_brand_age_floor", "legacy_floor"):
        return True
    # An explicit "unknown" (or blank) confidence is never reliable.
    if conf in ("unknown", "none", ""):
        return False
    if src.startswith("serial"):
        return conf in ("high", "medium")
    if src in ("homeowner_input", "homeowner", "homeowner_sure", "homeowner_approximate"):
        return conf in ("sure", "approximate", "high", "medium")
    return False


def replace_recommendation_gate(is_replacement: bool, reliable_age: bool) -> bool:
    """Returns requires_user_chooser: True when we'd recommend Full Replacement
    but the age driving it is not reliable. Drives the Stage 3C chooser-gate UI."""
    return bool(is_replacement and not reliable_age)


# -- Five-year cost comparison ------------------------------------------------

_REPAIR_PROB_BY_AGE = {
    8: (0.55, 850), 9: (0.60, 900), 10: (0.65, 950),
    11: (0.70, 1000), 12: (0.75, 1100), 13: (0.80, 1200),
    14: (0.85, 1300), 15: (0.90, 1400),
}

def _five_year_comparison(repair_cost: int, replacement_cost: int, unit_age_years: Optional[int]) -> dict:
    # Only invoked when a replacement (C) tier was reached, which requires a
    # numeric end_of_life age; fall back to the trigger age if absent.
    age = min(unit_age_years if unit_age_years is not None else _REPLACEMENT_TRIGGER_AGE, 15)
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
    seasonal_pct: float = 0.0,
) -> tuple:
    base = int(base)  # BUG-030: DB may return decimal.Decimal; cast to int
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
    if seasonal_pct > 0:
        sea = round(base * seasonal_pct)
        breakdown["seasonal"] = sea
        total += sea
    return total, breakdown



# -- Seasonal labor modifier --------------------------------------------------

def _seasonal_modifier_pct(market: str, company_override) -> int:
    """
    Return seasonal labor surcharge % for the current month.

    company_override: value of companies.peak_season_surcharge_percent
        None  = use market default (25% in peak months, 0 off-peak)
        0     = contractor has disabled seasonal surcharge
        1-100 = contractor custom override percent

    Returns integer 0-100. Caller divides by 100 before multiplying labor cost.
    R.9: Houston peak June-Sept, PK peak April-Oct. Default 25% labor surcharge.
    """
    if company_override is not None:
        return int(company_override)

    month = datetime.now(timezone.utc).month
    if market == "US":
        return 25 if 6 <= month <= 9 else 0   # Houston peak: June-Sept
    elif market == "PK":
        return 25 if 4 <= month <= 10 else 0  # PK peak: April-Oct
    return 0

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
    metering_type:  Optional[str]   = Field("any", description="inverter | non_inverter | any")
    age_source:     Optional[str]   = Field(None, description="serial_decode_high|serial_decode_medium|plate_date|homeowner_sure|homeowner_approximate|legacy_brand_age_floor|photo_estimate|unknown")
    age_confidence: Optional[str]   = Field(None, description="high|medium|low|sure|approximate|unknown")


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
    five_year_comparison:       Optional[dict] = None
    parts_included:             list = []
    service_items:              list = []
    recommendation_reason:      Optional[str] = None
    recommendation_source:      Optional[str] = None


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
    markup_pct:             float
    unit_age_years:         Optional[int]
    using_defaults:         bool = False
    defaults_warning:       Optional[str] = None
    seasonal_modifier_pct:  int = 0
    seasonal_note:          Optional[str] = None
    age_confidence:         Optional[str] = None
    requires_user_chooser:  bool = False
    generated_at:           str
    recommendation:         Optional[dict] = None   # §4C: severity×age decision metadata


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
    # BUG-022: US pricing_tiers has no metering_type column — only pak_pricing_tiers does.
    # Use market-conditional query so US estimates don't fail with UndefinedColumnError.
    if tables.market == "PK":
        pt_rows = await db.execute(
            text(
                f"SELECT tier, estimate_amount FROM {tables.pricing_tiers} "
                "WHERE card_id = :cid "
                "AND (metering_type = 'any' OR metering_type = :mt) "
                "ORDER BY tier, CASE metering_type WHEN 'any' THEN 2 ELSE 1 END "
                "LIMIT 3"
            ),
            {"cid": body.card_id, "mt": body.metering_type or "any"},
        )
    else:
        pt_rows = await db.execute(
            text(f"SELECT tier, estimate_amount FROM {tables.pricing_tiers} WHERE card_id = :cid ORDER BY tier"),
            {"cid": body.card_id},
        )
    pricing = {row.tier: int(row.estimate_amount) for row in pt_rows.fetchall()}  # BUG-030: Decimal -> int
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

    # 4. Get company markup + seasonal override (R.9)
    markup_row = await db.execute(
        text("SELECT default_markup_pct, peak_season_surcharge_percent FROM companies WHERE id = :cid LIMIT 1"),
        {"cid": auth.company_id},
    )
    markup_result = markup_row.fetchone()
    markup_pct  = float(markup_result.default_markup_pct) if markup_result else 35.0
    markup_mult = 1 + markup_pct / 100
    company_seasonal_override = (
        markup_result.peak_season_surcharge_percent if markup_result else None
    )

    # R.9 -- seasonal labor surcharge (generation-time freeze per QA Decisions SS15.2 Q4)
    seasonal_pct_int  = _seasonal_modifier_pct(tables.market, company_seasonal_override)
    seasonal_pct_frac = seasonal_pct_int / 100.0  # fraction for _apply_surcharges

    # 5. Load replacement cost
    repl_row = await db.execute(
        text(f"""
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
    rec_tier, rec_reason, rec_age_bucket, rec_severity = _compute_recommended_tier(
        unit_age, getattr(fc, 'difficulty', 'medium') or 'medium',
        int(fc.price_list_typical or 0), int(better_base), int(repl_typical),
    )
    recommend_replacement = (rec_tier == "C")

    tiers = []

    # Tier A: Good
    surcharge_A, bkdn_A = _apply_surcharges(base_A, attic_premium, after_hours_pct, r22_surcharge,
                                             body.attic_access, body.after_hours, is_r22, seasonal_pct_frac)
    sub_A    = base_A + surcharge_A
    mkup_A   = round(sub_A * (markup_mult - 1))
    total_A  = sub_A + mkup_A
    tiers.append(EstimateTier(
        tier="A", label=labels["good"],
        base_amount=base_A, surcharges=bkdn_A, subtotal=sub_A,
        markup_amount=mkup_A, total=total_A, recommended=False,
        description=(better_data or {}).get("description_good")
            or f"Diagnose and repair: {fc.card_name}. Gets your system running today.",
        why_recommended=(better_data or {}).get("why_recommended_good"),
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
                                             body.attic_access, body.after_hours, is_r22, seasonal_pct_frac)
    sub_B   = b_base + surcharge_B
    mkup_B  = round(sub_B * (markup_mult - 1))
    total_B = sub_B + mkup_B
    tiers.append(EstimateTier(
        tier="B", label=labels["better"],
        base_amount=b_base, surcharges=bkdn_B, subtotal=sub_B,
        markup_amount=mkup_B, total=total_B,
        recommended=(rec_tier == "B"),
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
            description=(better_data or {}).get("description_best_replacement")
                or (
                    f"{age_str}complete system replacement eliminates near-term repair risk "
                    "and reduces electricity costs by approximately 30-40%."
                ),
            why_recommended=(better_data or {}).get("why_recommended_best_replacement"),
            five_year_comparison=fyr,
        ))
    else:
        c_base = round(b_base * 1.35)
        surcharge_C, bkdn_C = _apply_surcharges(c_base, attic_premium, after_hours_pct, r22_surcharge,
                                                 body.attic_access, body.after_hours, is_r22, seasonal_pct_frac)
        sub_C   = c_base + surcharge_C
        mkup_C  = round(sub_C * (markup_mult - 1))
        total_C = sub_C + mkup_C
        tiers.append(EstimateTier(
            tier="C", label=labels["best"],
            base_amount=c_base, surcharges=bkdn_C, subtotal=sub_C,
            markup_amount=mkup_C, total=total_C, recommended=False,
            description=(better_data or {}).get("description_best_comprehensive")
                or f"Comprehensive repair: {fc.card_name} plus full system health check.",
            why_recommended=(better_data or {}).get("why_recommended_best_comprehensive"),
        ))

    # Q.6.5 — Apply base recommendation from severity×age matrix, then overlay lifecycle_rules
    # Base recommendation (rec_tier/rec_reason/rec_age_bucket/rec_severity) was computed above
    # via _compute_recommended_tier() using the fault severity × age matrix.
    # If condition_signals.py returns a real (non-default) signal, the lifecycle_rules DB
    # lookup can further override the recommended tier for edge-case condition patterns
    # (e.g., photo_confirmed_pitting, under_warranty, rla_over_nameplate).

    # Apply the base severity×age recommendation to all tiers
    for t in tiers:
        t.recommended = (t.tier == rec_tier)
    # Seed reason/source from matrix
    for t in tiers:
        if t.recommended:
            t.recommendation_reason = rec_reason
            t.recommendation_source = "severity_age_matrix"

    # Q.6.5 overlay: lifecycle_rules DB can override for condition-specific cases
    try:
        condition_signal = await derive_condition_signal_from_assessment(
            assessment_id=body.assessment_id,
            card_id=body.card_id,
            unit_age_years=unit_age,
            db=db,
        )
        if condition_signal != "default":
            lc_rec = await get_recommended_tier_internal(
                card_id=body.card_id,
                age_years=float(unit_age) if unit_age is not None else None,
                condition_signal=condition_signal,
                db=db, tables=tables,
            )
            for t in tiers:
                t.recommended = (t.tier == lc_rec["recommended_tier"])
            for t in tiers:
                if t.recommended:
                    t.recommendation_reason = lc_rec.get("reason")
                    t.recommendation_source = lc_rec.get("source")
    except Exception:
        logger.warning("[fault_estimate] lifecycle_rules overlay failed — using severity×age base",
                       exc_info=True)

    # R.9 -- build seasonal note for report footer
    _seasonal_note: Optional[str] = None
    if seasonal_pct_int > 0:
        if tables.market == "US":
            _seasonal_note = (
                f"Includes {seasonal_pct_int}% peak-season labor surcharge (June-Sept Houston)."
            )
        elif tables.market == "PK":
            _seasonal_note = (
                f"Includes {seasonal_pct_int}% peak-season labor surcharge (April-Oct)."
            )

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
                        "recommendation_reason": t.recommendation_reason,
                        "recommendation_source": t.recommendation_source,
                        "five_year_comparison": t.five_year_comparison,
                        "line_items": [{"description": fc.card_name, "amount": float(t.base_amount), "category": "repair"}],
                    }
                    for t in tiers
                ]
                report_token = secrets.token_urlsafe(32)[:32]
                # BUG-030b: 4-digit short ID (10k combos) causes UniqueViolation as DB grows.
                # Retry up to 5 times with 6-digit ID (1M combos) to eliminate collision.
                new_estimate = None
                for _attempt in range(5):
                    _sid = "rpt-" + "".join(secrets.choice(string.digits) for _ in range(6))
                    _chk = await db.execute(
                        text("SELECT 1 FROM estimates WHERE report_short_id = :sid LIMIT 1"),
                        {"sid": _sid},
                    )
                    if _chk.fetchone() is None:
                        new_estimate = Estimate(
                            assessment_id=body.assessment_id, company_id=auth.company_id,
                            report_token=report_token, report_short_id=_sid,
                            options=options_payload, markup_percent=markup_pct, status="draft",
                            seasonal_modifier_pct=seasonal_pct_int,
                            market=tables.market,  # BUG-037: stamp market at creation
                        )
                        db.add(new_estimate)
                        break
                if new_estimate is None:
                    raise HTTPException(status_code=500, detail="Could not allocate unique report_short_id after 5 attempts")
                await db.flush()
                estimate_id = str(new_estimate.id)
                logger.info("[fault_estimate v2] Saved estimate %s for assessment %s card %d age=%s",
                            estimate_id, body.assessment_id, body.card_id, unit_age)

    # Stage 2: reliable-age gate + replacement chooser gate
    _reliable_age = _has_reliable_age(body.age_source, body.age_confidence, unit_age)
    _requires_chooser = replace_recommendation_gate(rec_tier == "C", _reliable_age)
    _age_confidence_out = (body.age_confidence or "unknown") if _reliable_age else "unknown"

    # Build recommendation metadata (§4C)
    _rec_meta = {
        "recommended_tier": rec_tier,
        "reasoning": rec_reason,
        "severity_classification": rec_severity,
        "age_bucket": rec_age_bucket,
        "age_source": body.age_source,
        "age_confidence": _age_confidence_out,
        "reliable_age": _reliable_age,
        "requires_user_chooser": _requires_chooser,
    }

    return FaultCardEstimateResponse(
        id=estimate_id, card_id=fc.card_id, card_name=fc.card_name,
        phase=fc.phase, difficulty=fc.difficulty, tech_notes=fc.tech_notes,
        tiers=tiers, r22_alert=is_r22,
        attic_applied=body.attic_access, after_hours_applied=body.after_hours,
        markup_pct=markup_pct, unit_age_years=unit_age,
        using_defaults=using_defaults, defaults_warning=defaults_warning,
        seasonal_modifier_pct=seasonal_pct_int,
        seasonal_note=_seasonal_note,
        age_confidence=_age_confidence_out,
        requires_user_chooser=_requires_chooser,
        generated_at=datetime.now(timezone.utc).isoformat(),
        recommendation=_rec_meta,
    )
