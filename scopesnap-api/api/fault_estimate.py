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
import os
import re
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
from services import brand_data_loader
from services.analytics import capture_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


# -- Level 2 line-item wording + replacement breakdown ------------------------
# DEC-088-compliant copy lives in JSON data files (Codie-authored, board-reviewed
# 2026-06-18). Loaded once at module import.
REPLACEMENT_BREAKDOWN_RATIOS = {
    "equipment": 0.62,
    "refrigerant": 0.07,
    "labor": 0.20,
    "service": 0.11,
}
# Taleb safety flag: lets us disable the hardcoded replacement breakdown per
# deploy (env var) in ~5 min without a code change if a contractor's split is off.
USE_HARDCODED_REPLACEMENT_RATIOS = (
    os.environ.get("USE_HARDCODED_REPLACEMENT_RATIOS", "true").lower() == "true"
)

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_level2_json(filename: str) -> dict:
    try:
        with open(os.path.join(_DATA_DIR, filename), "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Level 2 data load failed for %s: %s", filename, exc)
        return {}


_REPAIR_LINE_ITEMS = {
    int(card["card_id"]): card
    for card in _load_level2_json("level2_repair_line_items.json").get("us_fault_cards", [])
}
_UNIVERSAL_STRINGS = _load_level2_json("level2_universal_strings.json")


def _build_line_items(tier, fc, card_id: int) -> list:
    """Per-tier line items (Bug 1 + Bug 5 fix).

    - Replacement tier: 4 distinct components split by REPLACEMENT_BREAKDOWN_RATIOS,
      summing exactly to tier.total (last line absorbs rounding remainder).
    - Repair tiers: a single line using the Level 2 Option 1 (tier A) or
      Option 2 (tier B / comprehensive C) wording, priced at tier.total so the
      line item always equals the displayed total (no markup arithmetic leak).
    """
    total = round(float(tier.total), 2)

    if getattr(tier, "is_replacement", False) and USE_HARDCODED_REPLACEMENT_RATIOS:
        comps = _UNIVERSAL_STRINGS.get("replacement_components") or {}
        # order -> ratio key mapping (installation is priced from the 'labor' ratio)
        order = [("equipment", "equipment"), ("refrigerant", "refrigerant"),
                 ("installation", "labor"), ("service", "service")]
        items = []
        running = 0.0
        for idx, (comp_key, ratio_key) in enumerate(order):
            if idx < len(order) - 1:
                amount = round(total * REPLACEMENT_BREAKDOWN_RATIOS[ratio_key], 2)
                running = round(running + amount, 2)
            else:
                amount = round(total - running, 2)  # remainder keeps the sum exact
            items.append({
                "description": comps.get(comp_key) or comp_key.title(),
                "amount": amount,
                "category": "replacement",
            })
        return items

    repair = _REPAIR_LINE_ITEMS.get(int(card_id)) or {}
    desc = repair.get("option_1") if getattr(tier, "tier", None) == "A" else repair.get("option_2")
    if not desc:
        desc = fc.card_name
    return [{"description": desc, "amount": total, "category": "repair"}]


# -- Label sets by unit age ---------------------------------------------------

_LABEL_SETS = [
    {"max_age": 5,   "good": "Fix Today",     "better": "Fix + Peace of Mind",        "best": "Full Service"},
    {"max_age": 10,  "good": "Fix Today",     "better": "Fix + Extend Life",           "best": "Consider Replacing"},
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


# -- [N] age-token resolution (Brand Decoder finding #1) ----------------------
# Seed copy in fault_cards.better_option_estimate.description_best_replacement
# (migrations 021/024) embeds a literal "[N]" placeholder, e.g.
# "At [N] years old, complete system replacement ...". This resolves it at the
# point the description is served so the user never sees the raw token.
_AGE_LEADIN_RE = re.compile(r"^\s*at\s+\[n\]\s+years?\s+old[,:]?\s*", re.IGNORECASE)
_STRAY_N_RE = re.compile(r"\s*\[n\]\s*", re.IGNORECASE)


def finalize_replacement_copy(raw: Optional[str],
                              unit_age: Optional[int],
                              reliable_age: bool) -> Optional[str]:
    """Resolve the [N] age placeholder in replacement-tier copy.

    - reliable age  -> substitute the real number for [N].
    - unreliable    -> never print a fabricated number: strip the
                       "At [N] years old, " lead-in entirely (re-capitalising
                       the new first letter) and scrub any stray [N] token.
    Passthrough when raw is falsy or contains no token. Consistent with the
    Stage 2 rule of never fabricating age.
    """
    if not raw or "[" not in raw:
        return raw
    if "[n]" not in raw.lower():
        return raw
    if reliable_age and unit_age:
        return re.sub(r"\[[Nn]\]", str(unit_age), raw)
    out = _AGE_LEADIN_RE.sub("", raw)
    if out != raw and out:
        out = out[0].upper() + out[1:]
    out = _STRAY_N_RE.sub(" ", out)
    return re.sub(r"\s{2,}", " ", out).strip()


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


# =====================================================================
# Stage 4 -- Track 2 shadow-mode weighted replace score
# =====================================================================
# Shadow-only: this score is computed alongside the live recommendation but
# NEVER drives the user-facing tier. It exists to (a) gather divergence data via
# the `replace_decision_shadow_eval` PostHog event and (b) feed the Stage 3C
# "show the math" panel. Weights come from the JSON replace_decision_logic_spec
# (falling back to the constants below); the threshold comes from an env var.

from dataclasses import dataclass, field, asdict

# Default weights -- mirror replace_decision_logic_spec.weights_initial_estimate.
_DEFAULT_REPLACE_WEIGHTS = {
    "remaining_life": 0.35,
    "refrigerant": 0.25,
    "cost_ratio": 0.20,
    "climate": 0.10,
    "repair_history": 0.10,
}

# cr_substituted (low-confidence Tier-3) records get their remaining_life weight
# halved to down-weight the least reliable signal.
_CR_SUBSTITUTED_REMAINING_LIFE_FACTOR = 0.5

# Neutral value used whenever a factor cannot be derived from the record/inputs.
_NEUTRAL_FACTOR = 0.5


def _replace_recommend_threshold() -> float:
    """RECOMMEND_REPLACE_THRESHOLD env var (default 0.6). Tunable without redeploy."""
    raw = os.environ.get("RECOMMEND_REPLACE_THRESHOLD", "")
    try:
        return float(raw) if raw.strip() else 0.6
    except (ValueError, AttributeError):
        return 0.6


def _replace_weights() -> dict:
    """Weights from replace_decision_logic_spec, else the default constants.

    The spec stores them under `weights_initial_estimate` keyed by the longer
    research names (brand_tier_remaining_life / refrigerant_compatibility /
    cost_ratio / climate_adjustment / repair_history). We map those onto our
    short factor keys; any missing key falls back to the default weight.
    """
    weights = dict(_DEFAULT_REPLACE_WEIGHTS)
    try:
        spec = brand_data_loader.get_replace_logic_spec() or {}
        raw = spec.get("weights_initial_estimate") or spec.get("weights") or {}
        key_map = {
            "remaining_life": ("remaining_life", "brand_tier_remaining_life"),
            "refrigerant": ("refrigerant", "refrigerant_compatibility"),
            "cost_ratio": ("cost_ratio",),
            "climate": ("climate", "climate_adjustment"),
            "repair_history": ("repair_history",),
        }
        for short, candidates in key_map.items():
            for c in candidates:
                if c in raw:
                    weights[short] = float(raw[c])
                    break
    except Exception:  # pragma: no cover - stay safe, fall back to defaults
        logger.debug("[replace_score] weight lookup failed; using defaults", exc_info=True)
    return weights


@dataclass
class ReplaceFactor:
    raw: float          # normalized 0..1 factor value
    weight: float       # weight actually applied (post cr_substituted adjustment)
    contribution: float # raw * weight
    sourced: bool       # True if derived from data, False if neutral default


@dataclass
class ReplaceScore:
    score: float
    recommend_replace: bool
    threshold: float
    cr_substituted: bool
    record_found: bool
    factors: dict = field(default_factory=dict)  # name -> ReplaceFactor (as dict)

    def as_dict(self) -> dict:
        return asdict(self)


def _clamp01(x: float) -> float:
    if x != x:  # NaN
        return _NEUTRAL_FACTOR
    return max(0.0, min(1.0, float(x)))


def _parse_lifespan_years(value) -> Optional[float]:
    """Parse a lifespan string/number like '12-16' or '15' into a midpoint float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value)
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if not nums:
        return None
    vals = [float(n) for n in nums]
    return sum(vals) / len(vals)


def _lookup_replace_record(
    records: list, brand: Optional[str], tier: Optional[str],
    variant: Optional[str], region: Optional[str],
) -> Optional[dict]:
    """Find the best Track 2 record for (brand, tier, variant, region).

    Matching is case-insensitive and progressively relaxed: brand is required;
    tier/variant/region narrow the match but a brand-only fallback is returned
    if no fully-qualified record exists.
    """
    if not brand:
        return None
    b = brand.strip().lower()
    t = (tier or "").strip().lower()
    v = (variant or "").strip().lower()
    r = (region or "").strip().lower()

    def _score(rec: dict) -> int:
        if (rec.get("brand") or rec.get("canonical_name") or "").strip().lower() != b:
            return -1  # brand mismatch disqualifies
        s = 8
        if t and (rec.get("tier") or "").strip().lower() == t:
            s += 4
        if v and (rec.get("variant") or "").strip().lower() == v:
            s += 2
        if r and (rec.get("market") or rec.get("region") or "").strip().lower() == r:
            s += 1
        return s

    best = None
    best_s = -1
    for rec in records:
        sc = _score(rec)
        if sc > best_s:
            best, best_s = rec, sc
    return best if best_s >= 0 else None


def _refrigerant_factor(record: Optional[dict], refrigerant: Optional[str],
                        unit_age_years: Optional[int]) -> tuple:
    """Map refrigerant generation -> replace pressure (0..1). Returns (value, sourced)."""
    rcode = (refrigerant or "").upper().replace(" ", "")
    if rcode.startswith("R-22") or rcode.startswith("R22"):
        return 1.0, True   # R-22: recharge uneconomical/illegal-for-new -> strong replace
    if rcode.startswith("R-410A") or rcode.startswith("R410A"):
        return 0.5, True   # R-410A: phase-down adds moderate weight
    if (rcode.startswith("R-454") or rcode.startswith("R-32")
            or rcode.startswith("R454") or rcode.startswith("R32")):
        return 0.1, True   # A2L: current generation, no penalty
    # Fall back: infer from record's refrigerant_compatibility by install era.
    if record and unit_age_years is not None:
        try:
            comp = record.get("refrigerant_compatibility") or {}
            install_year = datetime.now(timezone.utc).year - int(unit_age_years)
            if install_year < 2010 and comp.get("before_2010"):
                return 1.0, True
            if 2010 <= install_year < 2025 and comp.get("2010_2024"):
                return 0.5, True
            if install_year >= 2025:
                return 0.1, True
        except Exception:
            pass
    return _NEUTRAL_FACTOR, False


def _remaining_life_factor(record: Optional[dict], unit_age_years: Optional[int]) -> tuple:
    """Replace pressure from remaining service life (0..1). Returns (value, sourced).

    Uses reliability_profile.houston_climate_adjusted lifespan minus unit age.
    Less life remaining -> higher replace pressure. remaining<=3 -> ~1.0.
    """
    if not record or unit_age_years is None:
        return _NEUTRAL_FACTOR, False
    prof = record.get("reliability_profile") or {}
    expected = (
        _parse_lifespan_years(prof.get("houston_climate_adjusted"))
        or _parse_lifespan_years(prof.get("expected_lifespan_years_humid_climate"))
        or _parse_lifespan_years(prof.get("expected_lifespan_years_dry_climate"))
    )
    if not expected or expected <= 0:
        return _NEUTRAL_FACTOR, False
    remaining = expected - float(unit_age_years)
    if remaining <= 3:
        return 1.0, True
    # Linear: full life left -> 0 pressure; 3 yrs left -> ~1.0 pressure.
    return _clamp01(1.0 - (remaining - 3) / max(expected - 3, 1.0)), True


def _climate_factor(record: Optional[dict], region: Optional[str]) -> tuple:
    """Climate harshness -> replace pressure (0..1). Houston/humid -> higher."""
    if record:
        prof = record.get("reliability_profile") or {}
        humid = _parse_lifespan_years(prof.get("expected_lifespan_years_humid_climate"))
        dry = _parse_lifespan_years(prof.get("expected_lifespan_years_dry_climate"))
        if humid and dry and dry > 0:
            # Larger humid/dry shortfall -> harsher climate -> more replace pressure.
            return _clamp01((dry - humid) / dry + 0.4), True
    r = (region or "").strip().lower()
    if r in ("us", "houston"):
        return 0.6, True   # Houston humidity: moderate replace pressure
    if r == "pk":
        return 0.7, True   # PK extreme ambient: slightly higher
    return _NEUTRAL_FACTOR, False


def _cost_ratio_factor(repair_cost: Optional[float], replacement_cost: Optional[float]) -> tuple:
    """repair/replace cost ratio -> replace pressure (0..1)."""
    if repair_cost and replacement_cost and replacement_cost > 0:
        return _clamp01(float(repair_cost) / float(replacement_cost)), True
    return _NEUTRAL_FACTOR, False


def _repair_history_factor(repair_count: Optional[int]) -> tuple:
    """Past repair count -> replace pressure (0..1). 0 repairs -> 0, 3+ -> ~1.0."""
    if repair_count is None:
        return _NEUTRAL_FACTOR, False
    return _clamp01(float(repair_count) / 3.0), True


# -- Stage 3C: install-year / remaining-life band / refrigerant compatibility --
# These feed the FaultResolutionScreen "Why this recommendation?" panel via the
# recommendation dict. The band is ALWAYS a range string (never year-exact) and
# is Houston-climate adjusted. None when age is unknown (frontend hides the row).

_DEFAULT_HOUSTON_LIFESPAN_YEARS = 18  # sane default when no brand record found


def _estimated_install_year(unit_age_years: Optional[int]) -> Optional[int]:
    """Echo the unit-age-derived install year (current_year - age). None if unknown."""
    if unit_age_years is None:
        return None
    return datetime.now(timezone.utc).year - int(unit_age_years)


def _typical_lifespan_years(record: Optional[dict]) -> float:
    """Houston-adjusted typical lifespan (years) from a replace record, else default.

    Uses the midpoint of houston_climate_adjusted (e.g. "12-16" -> 14). Falls back
    to the humid-climate profile, then to a Houston-typical default.
    """
    if record:
        prof = record.get("reliability_profile") or {}
        for key in ("houston_climate_adjusted",
                    "expected_lifespan_years_humid_climate"):
            val = _parse_lifespan_years(prof.get(key))
            if val and val > 0:
                return float(val)
    return float(_DEFAULT_HOUSTON_LIFESPAN_YEARS)


def _remaining_life_band(unit_age_years: Optional[int],
                         record: Optional[dict] = None) -> Optional[str]:
    """Houston-adjusted REMAINING-life range string like "12-16 years".

    NEVER year-exact: rendered as a +/-2 band around (typical lifespan - age),
    floored at 0. Returns None when age is unknown so the frontend hides the row.
    """
    if unit_age_years is None:
        return None
    lifespan = _typical_lifespan_years(record)
    remaining = max(0.0, lifespan - float(unit_age_years))
    lo = max(0, int(round(remaining - 2)))
    hi = max(lo, int(round(remaining + 2)))
    return f"{lo}-{hi} years"


def _refrigerant_2025_compatible(refrigerant: Optional[str]) -> Optional[bool]:
    """Map a refrigerant code to 2025+ A2L compatibility.

    r22   -> False (phased out, not serviceable / not 2025+ compatible)
    r410a -> False (serviceable now but phasing down -> not the 2025+ standard)
    r32 / r454b -> True (current A2L generation)
    Unknown / None -> None (frontend hides the badge).
    """
    if not refrigerant:
        return None
    code = str(refrigerant).upper().replace("-", "").replace(" ", "")
    if code in ("R22", "R410A", "R410"):
        return False
    if code in ("R32", "R454B", "R454"):
        return True
    return None


# Constraint #8: per-brand factory refrigerant by manufacture year. The 2025+
# A2L transition splits by manufacturer (R-32 vs R-454B), so "can't recharge,
# must replace" pressure respects the actual likely charge.
_R2025_BY_BRAND = {
    # R-32 adopters
    "daikin": "R-32", "daikin mini-split": "R-32", "goodman": "R-32", "amana": "R-32",
    # R-454B adopters (majority of US OEMs)
    "carrier": "R-454B", "bryant": "R-454B", "payne": "R-454B",
    "trane": "R-454B", "american standard": "R-454B",
    "lennox": "R-454B", "rheem": "R-454B", "ruud": "R-454B",
    "york": "R-454B", "coleman": "R-454B", "luxaire": "R-454B",
    "mrcool": "R-454B",
    # Nortek family 2025+ = working hypothesis R-454B (pending v1.2 Batch 2)
    "frigidaire hvac": "R-454B", "nortek": "R-454B", "maytag hvac": "R-454B",
}
_DEFAULT_R2025 = "R-454B"


def refrigerant_for_year(brand: Optional[str], year: Optional[int]) -> Optional[str]:
    """Likely factory refrigerant for a US residential unit of (brand, year).

    <=2009  -> R-22   (pre-410A residential era)
    2010-24 -> R-410A (410A mandated for new equipment from 2010)
    >=2025  -> A2L: per-brand R-32 vs R-454B split (default R-454B).
    Returns None when year is unknown.
    """
    if year is None:
        return None
    if year <= 2009:
        return "R-22"
    if year <= 2024:
        return "R-410A"
    canon = (brand or "").strip().lower()
    return _R2025_BY_BRAND.get(canon, _DEFAULT_R2025)


def _compute_weighted_replace_score(
    brand: Optional[str],
    tier: Optional[str],
    variant: Optional[str],
    region: Optional[str],
    unit_age_years: Optional[int] = None,
    refrigerant: Optional[str] = None,
    repair_cost: Optional[float] = None,
    replacement_cost: Optional[float] = None,
    repair_count: Optional[int] = None,
    threshold: Optional[float] = None,
) -> ReplaceScore:
    """Shadow-mode weighted replace score in [0, 1] with a full factor breakdown.

    Looks up the Track 2 record for (brand, tier, variant, region). Each factor
    is normalized to 0..1 (1.0 = strong replace pressure); absent factors default
    to a neutral 0.5. The weighted sum uses the JSON-sourced weights (or the
    default constants). When the record is cr_substituted, the remaining_life
    weight is halved (down-weighting the least-reliable Tier-3 signal) and the
    weight vector is renormalized so the score stays in [0, 1].

    Returns a ReplaceScore with the recommendation flag + per-factor breakdown
    (raw value, applied weight, contribution) for the Stage 3C show-the-math panel.
    """
    records = brand_data_loader.get_replace_records()
    record = _lookup_replace_record(records, brand, tier, variant, region)
    cr_substituted = bool(record.get("cr_substituted")) if record else False

    rl_val, rl_src = _remaining_life_factor(record, unit_age_years)
    ref_val, ref_src = _refrigerant_factor(record, refrigerant, unit_age_years)
    cost_val, cost_src = _cost_ratio_factor(repair_cost, replacement_cost)
    clim_val, clim_src = _climate_factor(record, region)
    hist_val, hist_src = _repair_history_factor(repair_count)

    base_weights = _replace_weights()
    weights = dict(base_weights)

    # cr_substituted: halve the remaining_life weight, then renormalize the whole
    # vector so contributions still sum to a 0..1 score (no artificial deflation
    # of the other factors). Documented approach: down-weight + renormalize.
    if cr_substituted:
        weights["remaining_life"] = (
            base_weights["remaining_life"] * _CR_SUBSTITUTED_REMAINING_LIFE_FACTOR
        )
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

    factor_values = {
        "remaining_life": (rl_val, rl_src),
        "refrigerant": (ref_val, ref_src),
        "cost_ratio": (cost_val, cost_src),
        "climate": (clim_val, clim_src),
        "repair_history": (hist_val, hist_src),
    }

    factors = {}
    score = 0.0
    for name, (val, sourced) in factor_values.items():
        w = float(weights.get(name, 0.0))
        contribution = _clamp01(val) * w
        score += contribution
        factors[name] = asdict(ReplaceFactor(
            raw=round(_clamp01(val), 4), weight=round(w, 4),
            contribution=round(contribution, 4), sourced=bool(sourced),
        ))

    score = _clamp01(score)
    thr = _replace_recommend_threshold() if threshold is None else float(threshold)
    return ReplaceScore(
        score=round(score, 4),
        recommend_replace=(score >= thr),
        threshold=thr,
        cr_substituted=cr_substituted,
        record_found=record is not None,
        factors=factors,
    )


def _extract_brand_tier_variant(asmt) -> tuple:
    """Best-effort (brand, tier, variant) from an assessment's OCR/AI equipment data.

    Used only for the shadow-mode replace score lookup -- returns (None, None, None)
    when nothing usable is present (the score then falls back to neutral factors).
    """
    if asmt is None:
        return None, None, None
    brand = None
    for blob_name in ("ocr_nameplate", "ai_equipment_id"):
        blob = getattr(asmt, blob_name, None)
        if isinstance(blob, dict):
            b = blob.get("brand") or blob.get("canonical_name")
            if b:
                brand = str(b).strip()
                break
    # tier/variant are not reliably stored on the assessment today; leave None so
    # the lookup uses a brand-only fallback record.
    return brand, None, None


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

    # Reliable-age provenance gate (reused for [N] copy resolution + age_str).
    reliable_age = _has_reliable_age(body.age_source, body.age_confidence, unit_age)

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
        # Only state the age when it is reliable (never fabricate -- Stage 2 rule).
        age_str    = f"At {unit_age} years old, " if (reliable_age and unit_age) else ""
        tiers.append(EstimateTier(
            tier="C", label=labels["best"],
            base_amount=repl_typical, surcharges={}, subtotal=repl_typical,
            markup_amount=repl_mkup, total=repl_total,
            recommended=True, is_replacement=True,
            description=finalize_replacement_copy(
                    (better_data or {}).get("description_best_replacement"),
                    unit_age, reliable_age,
                )
                or (
                    f"{age_str}a complete system replacement covers the whole system "
                    "and runs at current efficiency standards."
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
    _shadow_brand = _shadow_tier = _shadow_variant = None
    if body.assessment_id:
        asmt_row = await db.execute(
            select(Assessment).where(
                Assessment.id == body.assessment_id,
                Assessment.company_id == auth.company_id,
            )
        )
        asmt = asmt_row.scalar_one_or_none()
        if asmt:
            _shadow_brand, _shadow_tier, _shadow_variant = _extract_brand_tier_variant(asmt)
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
                        "line_items": _build_line_items(t, fc, body.card_id),
                    }
                    for t in tiers
                ]
                # Stage 3C: stash recommendation metadata on the recommended tier
                # option so the diagnostic repair_plan (GET /api/diagnostic/{id})
                # can surface the chooser-gate banner + "Why this recommendation?"
                # panel without recomputing. Backward-compatible: an extra key on
                # an existing option dict; consumers that ignore it are unaffected.
                _persist_reliable_age = _has_reliable_age(
                    body.age_source, body.age_confidence, unit_age
                )
                try:
                    _persist_rl_record = _lookup_replace_record(
                        brand_data_loader.get_replace_records(),
                        _shadow_brand, _shadow_tier, _shadow_variant, tables.market,
                    )
                except Exception:
                    _persist_rl_record = None
                _persist_rec_meta = {
                    "recommended_tier": rec_tier,
                    "age_source": body.age_source,
                    "age_confidence": (
                        (body.age_confidence or "unknown")
                        if _persist_reliable_age else "unknown"
                    ),
                    "reliable_age": _persist_reliable_age,
                    "requires_user_chooser": replace_recommendation_gate(
                        rec_tier == "C", _persist_reliable_age
                    ),
                    "estimated_install_year": _estimated_install_year(unit_age),
                    "remaining_life_band": _remaining_life_band(
                        unit_age, _persist_rl_record
                    ),
                    "refrigerant": body.refrigerant,
                    "refrigerant_2025_compatible": _refrigerant_2025_compatible(
                        body.refrigerant
                    ),
                    "unit_age_years": unit_age,
                }
                for _opt in options_payload:
                    if _opt.get("recommended"):
                        _opt["recommendation_meta"] = _persist_rec_meta
                        break
                else:
                    if options_payload:
                        options_payload[0]["recommendation_meta"] = _persist_rec_meta
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

                # Stage 5: stamp brand-decoder / replace-logic data versions on
                # the assessment row (migration 040 columns). New estimates carry
                # the live JSON data versions; historical rows keep "pre-v1.2".
                try:
                    asmt.decoder_version = brand_data_loader.BRAND_DATA_VERSION
                    _rl_spec = brand_data_loader.get_replace_logic_spec() or {}
                    asmt.replace_logic_version = str(
                        _rl_spec.get("version") or brand_data_loader.BRAND_DATA_VERSION
                    )
                except Exception:
                    logger.warning("[fault_estimate] version stamping failed", exc_info=True)

                await db.flush()
                estimate_id = str(new_estimate.id)
                logger.info("[fault_estimate v2] Saved estimate %s for assessment %s card %d age=%s",
                            estimate_id, body.assessment_id, body.card_id, unit_age)

    # Stage 2: reliable-age gate + replacement chooser gate
    _reliable_age = _has_reliable_age(body.age_source, body.age_confidence, unit_age)
    _requires_chooser = replace_recommendation_gate(rec_tier == "C", _reliable_age)
    _age_confidence_out = (body.age_confidence or "unknown") if _reliable_age else "unknown"

    # Stage 3C: install-year echo, Houston-adjusted remaining-life band, and
    # refrigerant 2025+ compatibility for the "Why this recommendation?" panel.
    try:
        _rl_record = _lookup_replace_record(
            brand_data_loader.get_replace_records(),
            _shadow_brand, _shadow_tier, _shadow_variant, tables.market,
        )
    except Exception:
        _rl_record = None
    _estimated_install_year_out = _estimated_install_year(unit_age)
    _remaining_life_band_out = _remaining_life_band(unit_age, _rl_record)
    # Constraint #8: if the tech didn't enter a refrigerant, infer it per-brand
    # from the (estimated) manufacture year so the 2025+ A2L split is respected.
    _eff_refrigerant = body.refrigerant or refrigerant_for_year(_shadow_brand, _estimated_install_year_out)
    _refrigerant_2025_out = _refrigerant_2025_compatible(_eff_refrigerant)

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
        # Stage 3C show-the-math / why-panel fields:
        "estimated_install_year": _estimated_install_year_out,
        "remaining_life_band": _remaining_life_band_out,
        "refrigerant": _eff_refrigerant,
        "refrigerant_2025_compatible": _refrigerant_2025_out,
    }

    # Stage 4: Track 2 shadow-mode weighted replace score.
    # SHADOW ONLY -- never changes the user-facing rec_tier above. Recorded in the
    # response meta for the Stage 3C "show the math" panel + fired to PostHog.
    try:
        _shadow = _compute_weighted_replace_score(
            brand=_shadow_brand,
            tier=_shadow_tier,
            variant=_shadow_variant,
            region=tables.market,
            unit_age_years=unit_age,
            refrigerant=_eff_refrigerant,
            repair_cost=float(fc.price_list_typical or 0) or None,
            replacement_cost=float(repl_typical or 0) or None,
            repair_count=None,
        )
        _old_recommends_replace = (rec_tier == "C")
        _did_diverge = _shadow.recommend_replace != _old_recommends_replace
        _rec_meta["shadow_replace_score"] = _shadow.as_dict()

        try:
            capture_event(
                "replace_decision_shadow_eval",
                {
                    "brand": _shadow_brand,
                    "tier": _shadow_tier,
                    "variant": _shadow_variant,
                    "region": tables.market,
                    "unit_age_years": unit_age,
                    "refrigerant": body.refrigerant,
                    "card_id": body.card_id,
                    "factors": _shadow.factors,
                    "record_found": _shadow.record_found,
                    "old_recommended_tier": rec_tier,
                    "old_recommends_replace": _old_recommends_replace,
                    "new_score": _shadow.score,
                    "new_threshold": _shadow.threshold,
                    "new_recommends_replace": _shadow.recommend_replace,
                    "did_diverge": _did_diverge,
                    "cr_substituted": _shadow.cr_substituted,
                    "age_source": body.age_source,
                    "age_confidence": _age_confidence_out,
                },
                distinct_id=f"company:{auth.company_id}",
            )
        except Exception:
            logger.debug("[fault_estimate] shadow_eval analytics failed", exc_info=True)
    except Exception:
        logger.warning("[fault_estimate] shadow replace-score computation failed",
                       exc_info=True)

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
