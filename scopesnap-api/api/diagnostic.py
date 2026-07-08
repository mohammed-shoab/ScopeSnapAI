"""
WS-A3 — Phase 3 Diagnostic Engine

POST /api/diagnostic/session              — start a new session
GET  /api/diagnostic/session/{session_id} — resume (get current step)
POST /api/diagnostic/session/{session_id}/answer — submit answer to current step

Bug fixes in this implementation
---------------------------------
BUG-003  : _compute_branch_key reads pre-computed branch_key from frontend
           (avoids str(dict) coercion for reading/photo answer dicts)
BUG-003b : _get_fault_card_name uses  SELECT card_name AS name  so .name works
BUG-004  : not_heating auto Q1 — null-safe read of ocr_nameplate.system_type;
           defaults to gas_furnace when field is absent
BUG-005  : error_code call_error_code_lookup — null-safe read of
           ocr_nameplate.brand; routes to nuisance_or_unknown when absent
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import AuthContext, get_current_user
from api.dependencies import get_tables, get_company_tables, MarketTables
from db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])

# ── Pydantic schemas ───────────────────────────────────────────────────────────


class StartSessionRequest(BaseModel):
    assessment_id: str
    complaint_type: str


class AnswerRequest(BaseModel):
    answer: Any
    # PK-only: refrigerant type for server-side pressure evaluation
    refrigerant_type: Optional[str] = None   # "R-32" | "R-410A" | "R-22" | "not_sure"
    ambient_c: Optional[int] = None          # outdoor ambient °C; defaults to 40


class QuestionOut(BaseModel):
    step_id: str
    question_text: str
    hint_text: Optional[str] = None
    input_type: str
    # For visual_select: [{value, label, icon}]
    # For multi:         [{kind, spec}]  (frontend casts via `as unknown as MultiInputItem[]`)
    options: Optional[List[Any]] = None
    reading_spec: Optional[dict] = None
    photo_spec: Optional[dict] = None
    is_terminal: bool = False


class StartSessionResponse(BaseModel):
    session_id: str
    current_step: QuestionOut


class AnswerResponse(BaseModel):
    resolved: bool = False
    card_id: Optional[int] = None
    card_name: Optional[str] = None
    photo_slots: Optional[List[dict]] = None
    next_step: Optional[QuestionOut] = None
    phase_2_gate: bool = False
    gate_continuation: Optional[dict] = None
    escalated: bool = False
    escalation_reason: Optional[str] = None
    service_step_complete: bool = False
    finding: Optional[dict] = None


# ── DB helpers ─────────────────────────────────────────────────────────────────

_QUESTION_COLS = """
    step_id, question_text, hint_text, input_type,
    options_jsonb, reading_spec, photo_spec,
    branch_logic_jsonb, is_terminal
"""


async def _load_question(
    db: AsyncSession, complaint_type: str, step_id: str
) -> Any:
    result = await db.execute(
        text(
            f"SELECT {_QUESTION_COLS} FROM diagnostic_questions"
            " WHERE complaint_type = :ct AND step_id = :sid LIMIT 1"
        ),
        {"ct": complaint_type, "sid": step_id},
    )
    return result.fetchone()


async def _load_first_question(db: AsyncSession, complaint_type: str) -> Any:
    result = await db.execute(
        text(
            f"SELECT {_QUESTION_COLS} FROM diagnostic_questions"
            " WHERE complaint_type = :ct ORDER BY step_order ASC LIMIT 1"
        ),
        {"ct": complaint_type},
    )
    return result.fetchone()


async def _load_assessment(
    db: AsyncSession, assessment_id: str, company_id: str
) -> Any:
    result = await db.execute(
        text(
            "SELECT id, company_id, user_id, ocr_nameplate"
            " FROM assessments WHERE id = :aid AND company_id = :cid LIMIT 1"
        ),
        {"aid": assessment_id, "cid": company_id},
    )
    return result.fetchone()


async def _get_fault_card_name(db: AsyncSession, card_id: int, tables: MarketTables = None) -> Optional[str]:
    """BUG-003b: alias column so .name resolves correctly."""
    fc_table = tables.fault_cards if tables else "fault_cards"
    result = await db.execute(
        text(f"SELECT card_name AS name FROM {fc_table} WHERE card_id = :cid LIMIT 1"),
        {"cid": card_id},
    )
    row = result.fetchone()
    return row.name if row else None


async def _load_session(
    db: AsyncSession, session_id: str, company_id: str
) -> Any:
    result = await db.execute(
        text(
            "SELECT id, assessment_id, company_id, technician_id,"
            "       complaint_type, current_step_id, status"
            " FROM diagnostic_sessions"
            " WHERE id = :sid AND company_id = :cid LIMIT 1"
        ),
        {"sid": session_id, "cid": company_id},
    )
    return result.fetchone()


async def _create_session(
    db: AsyncSession,
    assessment_id: str,
    company_id: str,
    technician_id: str,
    complaint_type: str,
    first_step_id: str,
) -> str:
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    await db.execute(
        text(
            "INSERT INTO diagnostic_sessions"
            "  (id, assessment_id, company_id, technician_id, complaint_type,"
            "   current_step_id, answers_jsonb, status, created_at, updated_at)"
            " VALUES"
            "  (:sid, :aid, :cid, :tid, :ct,"
            "   :step, :empty, 'active', :now, :now)"
        ),
        {
            "sid": session_id,
            "aid": assessment_id,
            "cid": company_id,
            "tid": technician_id,
            "ct": complaint_type,
            "step": first_step_id,
            "empty": "{}",
            "now": now,
        },
    )
    return session_id


async def _set_session_step(
    db: AsyncSession, session_id: str, step_id: str
) -> None:
    await db.execute(
        text(
            "UPDATE diagnostic_sessions"
            " SET current_step_id = :step, updated_at = :now"
            " WHERE id = :sid"
        ),
        {"step": step_id, "now": datetime.now(timezone.utc), "sid": session_id},
    )


async def _resolve_session(
    db: AsyncSession, session_id: str, card_id: int
) -> None:
    now = datetime.now(timezone.utc)
    await db.execute(
        text(
            "UPDATE diagnostic_sessions"
            " SET status = 'resolved', resolved_card_id = :cid,"
            "     resolved_at = :now, updated_at = :now"
            " WHERE id = :sid"
        ),
        {"cid": card_id, "now": now, "sid": session_id},
    )


async def _escalate_session(db: AsyncSession, session_id: str) -> None:
    await db.execute(
        text(
            "UPDATE diagnostic_sessions"
            " SET status = 'escalated', updated_at = :now WHERE id = :sid"
        ),
        {"now": datetime.now(timezone.utc), "sid": session_id},
    )


async def _complete_service_session(db: AsyncSession, session_id: str) -> None:
    """Mark a service/tune-up session as complete (distinct from 'escalated')."""
    await db.execute(
        text(
            "UPDATE diagnostic_sessions"
            " SET status = 'service_complete', updated_at = :now WHERE id = :sid"
        ),
        {"now": datetime.now(timezone.utc), "sid": session_id},
    )


async def _build_service_estimate_options(markup_percent: float) -> list:
    """
    BUG-009: Build standard Good/Better/Best tiers for a service/tune-up job.

    Tiers are fixed for all service calls:
      Good   — base inspection only
      Better — inspection + drain flush treatment  (recommended)
      Best   — inspection + drain flush + filter replacement
    """
    BASE   = 110.0   # Service / Tune-Up Inspection
    DRAIN  =  20.0   # Drain Flush Treatment (tablet)
    FILTER =  40.0   # Filter Replacement (1-inch standard)

    def tier(name, t, items, recommended=False):
        subtotal = sum(i["amount"] for i in items)
        total    = round(subtotal * (1 + markup_percent / 100), 2)
        return {
            "name": name, "tier": t,
            "total": total, "subtotal": subtotal,
            "line_items": items,
            "recommended": recommended,
            "markup_percent": markup_percent,
        }

    return [
        tier("Good", "A", [
            {"amount": BASE,  "category": "service", "description": "Service / Tune-Up Inspection"},
        ]),
        tier("Better", "B", [
            {"amount": BASE,  "category": "service", "description": "Service / Tune-Up Inspection"},
            {"amount": DRAIN, "category": "service", "description": "Drain Flush Treatment (tablet)"},
        ], recommended=True),
        tier("Best", "C", [
            {"amount": BASE,   "category": "service", "description": "Service / Tune-Up Inspection"},
            {"amount": DRAIN,  "category": "service", "description": "Drain Flush Treatment (tablet)"},
            {"amount": FILTER, "category": "parts",   "description": "Filter Replacement (1-inch standard)"},
        ]),
    ]


async def _generate_service_estimate(
    db: AsyncSession,
    assessment_id: str,
    company_id: str,
    market: str = "US",  # BUG-037: stamp market at creation
) -> None:
    """
    BUG-009 fix: create a service/tune-up estimate in the DB so the frontend's
    GET /api/estimates/{assessment_uuid} lookup succeeds.

    CRITICAL: estimate.id is set to assessment_id so that the frontend URL
    pattern /assessment/{uuid} → GET /api/estimates/{uuid} resolves correctly.
    This matches the convention used throughout the estimates API.
    """
    import json as _json
    import secrets
    import string as _string

    # Idempotent: do nothing if estimate already exists for this assessment
    # BUG-010-fix: check both id=assessment_id AND assessment_id column to
    # avoid duplicate-key failure when a fault estimate was created earlier.
    existing = await db.execute(
        text("SELECT id FROM estimates WHERE id = :aid OR assessment_id = :aid LIMIT 1"),
        {"aid": assessment_id},
    )
    if existing.fetchone():
        logger.info("[diagnostic] service estimate already exists for %s", assessment_id)
        return

    # Fetch company markup (falls back to 35 %)
    markup_percent = 35.0
    try:
        comp_row = await db.execute(
            text("SELECT default_markup_pct FROM companies WHERE id = :cid LIMIT 1"),
            {"cid": company_id},
        )
        row = comp_row.fetchone()
        if row and row.default_markup_pct is not None:
            markup_percent = float(row.default_markup_pct)
    except Exception as exc:
        logger.warning("[diagnostic] could not load company markup: %s", exc)

    options = await _build_service_estimate_options(markup_percent)

    # Unique report short ID (retry on collision)
    short_id = None
    for _ in range(10):
        candidate = "rpt-" + "".join(secrets.choice(_string.digits) for _ in range(6))
        clash = await db.execute(
            text("SELECT id FROM estimates WHERE report_short_id = :sid LIMIT 1"),
            {"sid": candidate},
        )
        if not clash.fetchone():
            short_id = candidate
            break
    if not short_id:
        short_id = f"rpt-{uuid.uuid4().hex[:6]}"

    report_token = secrets.token_urlsafe(32)[:32]
    now = datetime.now(timezone.utc)

    await db.execute(
        text(
            "INSERT INTO estimates"
            "  (id, assessment_id, company_id, report_token, report_short_id,"
            "   options, markup_percent, status, created_at, market)"
            " VALUES"
            "  (:id, :aid, :cid, :token, :short_id,"
            "   CAST(:options AS jsonb), :markup, 'draft', :now, :market)"
        ),
        {
            "id":       assessment_id,   # id == assessment_id → frontend URL routing
            "aid":      assessment_id,
            "cid":      company_id,
            "token":    report_token,
            "short_id": short_id,
            "options":  _json.dumps(options),
            "markup":   markup_percent,
            "now":      now,
            "market":   market,
        },
    )

    # NOTE: est_status column was removed from assessments table (BUG-039 fix).
    # Do not update assessments here — would abort the transaction on missing column.

    logger.info(
        "[diagnostic] service estimate created: assessment=%s short_id=%s markup=%.0f%%",
        assessment_id, short_id, markup_percent,
    )


# ── Question row → response schema ────────────────────────────────────────────


_PK_PSI_HINTS: dict[str, str] = {
    "suction":   "PK typical — R-32: 120–140 PSI | R-410A: 125–145 PSI | R-22: 65–88 PSI (at 40 °C ambient)",
    "discharge":  "PK typical — R-32: 365–410 PSI | R-410A: 325–370 PSI | R-22: 250–310 PSI (at 40 °C ambient)",
}


def _row_to_question_out(row: Any, market: str = "US") -> QuestionOut:
    """Convert a diagnostic_questions DB row to the API response schema.

    For PK market:
    - PSI reading questions get localised pressure-range hints
    - Voltage reading questions get PK-specific low_threshold (190 V)
      so the frontend routes < 190 V as "no_power" / low voltage
    """
    hint = row.hint_text
    reading_spec = row.reading_spec

    if market == "PK" and isinstance(reading_spec, dict):
        spec_type = reading_spec.get("type")
        if spec_type == "psi":
            subtype = reading_spec.get("subtype", "suction")
            hint = _PK_PSI_HINTS.get(subtype, hint)
        elif spec_type == "voltage":
            # PK nominal voltage: 190–260 V single phase 50 Hz.
            # Override US default low_threshold (100 V) so readings below
            # 190 V are classified as "no_power" (under-voltage condition).
            reading_spec = {**reading_spec, "low_threshold": 190}

    return QuestionOut(
        step_id=row.step_id,
        question_text=row.question_text,
        hint_text=hint,
        input_type=row.input_type,
        # options_jsonb serves dual purpose:
        #   visual_select → [{value, label, icon}]
        #   multi         → [{kind, spec}]  (frontend casts)
        options=row.options_jsonb,
        reading_spec=reading_spec,
        photo_spec=row.photo_spec,
        is_terminal=bool(row.is_terminal),
    )


# ── Branch-key extraction ──────────────────────────────────────────────────────


def _compute_branch_key(answer: Any, input_type: str) -> str:
    """
    BUG-003: extract the routing branch_key from the frontend answer.

    - yesno / visual_select  → answer is a plain string
    - reading / photo / multi → answer is a dict; prefer explicit branch_key field
    - multi (bundled)        → answer has reading_0, reading_1, etc.; use reading_0.branch_key
    - fallback               → str(answer)
    """
    if isinstance(answer, str):
        return answer.strip().lower()

    if isinstance(answer, dict):
        # Top-level branch_key — accept snake_case (backend) and camelCase (frontend ReadingResult)
        # BUG-021: frontend ReadingInput sends branchKey (camelCase), not branch_key (snake_case)
        bk = answer.get("branch_key") or answer.get("branchKey")
        if bk:
            return str(bk).strip().lower()

        # BUG-005: Multi-input bundled answer — readings keyed as reading_0, reading_1 …
        # The first reading's branch_key is the primary routing key.
        r0 = answer.get("reading_0")
        if isinstance(r0, dict):
            bk = r0.get("branch_key") or r0.get("branchKey")
            if bk:
                logger.info(
                    "[diagnostic] branch_key from reading_0: '%s'", bk
                )
                return str(bk).strip().lower()

        # Legacy fallback for older clients that sent {value, unit}
        val = answer.get("value")
        if val is not None:
            return str(val).strip().lower()

    logger.warning("[diagnostic] branch_key fallback: answer=%r input_type=%s", answer, input_type)
    return str(answer).strip().lower()


# ── Auto-question resolution — BUG-004 fix ────────────────────────────────────


def _resolve_auto_question(branch_logic: dict, ocr_nameplate: Optional[dict]) -> str:
    """
    Resolve an 'auto' question type (e.g. not_heating Q1 system_type detection).

    BUG-004 fix: safely handles None / missing ocr_nameplate values.
    When system_type is absent, defaults to 'gas_furnace' (most common Houston
    system type) so the session can continue rather than crash.
    """
    use_field: str = branch_logic.get("use_field", "")
    ocr = ocr_nameplate or {}

    # branch_logic stores field as "ocr_nameplate.system_type" — strip prefix
    field_name = use_field.split(".", 1)[-1] if "." in use_field else use_field
    value = ocr.get(field_name)

    if not value:
        # BUG-004: null safety — fall back to gas_furnace
        logger.info(
            "[diagnostic] auto Q: ocr field '%s' is None — defaulting to gas_furnace",
            field_name,
        )
        value = "gas_furnace"

    value = str(value).strip().lower()

    # Validate value has a branch; try "any" wildcard; then hard-default
    if value in branch_logic:
        return value
    if "any" in branch_logic:
        return "any"

    logger.warning(
        "[diagnostic] auto Q: no branch for '%s', no 'any' wildcard — defaulting to gas_furnace",
        value,
    )
    return "gas_furnace"


# ── Error-code lookup — BUG-005 fix ───────────────────────────────────────────


async def _call_error_code_lookup(
    db: AsyncSession,
    action_config: dict,
    ocr_nameplate: Optional[dict],
    photo_ai_output: Optional[str],
    tables: MarketTables = None,
) -> str:
    """
    Resolve the error_code Q1 action: lookup brand+code in error_codes table,
    return a branch_key from the 'after' map.

    BUG-005 fix: when ocr_nameplate.brand is absent, skip the DB lookup and
    route directly to 'nuisance_or_unknown' (→ q4-reset) instead of crashing.
    """
    after_map: dict = action_config.get("after", {})

    ocr = ocr_nameplate or {}
    brand = ocr.get("brand")

    if not brand:
        # BUG-005: no brand data — skip lookup, use generic reset path
        logger.info("[diagnostic] error_code lookup: no brand in OCR — nuisance_or_unknown")
        return "nuisance_or_unknown"

    if not photo_ai_output:
        return "nuisance_or_unknown"

    brand_clean = str(brand).strip().lower()
    code_clean = str(photo_ai_output).strip()

    try:
        ec_table = tables.error_codes if tables else "error_codes"
        result = await db.execute(
            text(f"""
                SELECT ec.subsystem, ec.meaning, ec.severity
                FROM {ec_table} ec
                WHERE (
                        LOWER(ec.brand_family) = :brand
                    OR  :brand = ANY(ec.brand_family_members::text[])
                    OR  ec.brand_family LIKE ('%' || :brand || '%')
                )
                AND (
                        LOWER(ec.error_code) = LOWER(:code)
                    OR  ec.error_code = :code
                )
                ORDER BY
                    CASE WHEN LOWER(ec.brand_family) = :brand THEN 0 ELSE 1 END,
                    CASE WHEN ec.decision_tree_card IS NOT NULL THEN 0 ELSE 1 END
                LIMIT 1
            """),
            {"brand": brand_clean, "code": code_clean},
        )
        row = result.fetchone()
    except Exception as exc:
        logger.error("[diagnostic] error_code DB lookup failed: %s", exc)
        return "nuisance_or_unknown"

    if not row:
        return "nuisance_or_unknown"

    subsystem = (row.subsystem or "").lower()
    meaning = (row.meaning or "").lower()

    # Keyword-based subsystem → branch_key mapping
    if "pressure" in subsystem or "sensor" in subsystem or "pressure" in meaning:
        bk = "pressure_sensor_fault"
    elif "refrigerant" in subsystem or "refrigerant" in meaning or ("low" in meaning and "suction" in meaning):
        bk = "refrigerant_low"
    elif "comm" in subsystem or "communication" in subsystem:
        bk = "communication_fault"
    elif "lockout" in subsystem or "lockout" in meaning or "trip" in meaning:
        bk = "lockout_trip"
    elif "capacitor" in subsystem or "capacitor" in meaning:
        bk = "capacitor"
    elif "contactor" in subsystem or "contactor" in meaning:
        bk = "contactor"
    else:
        bk = "nuisance_or_unknown"

    return bk if bk in after_map else "nuisance_or_unknown"


# ── PK pressure evaluation ────────────────────────────────────────────────────


async def _evaluate_pressure_for_market(
    db: AsyncSession,
    value: float,
    subtype: str,           # "suction" | "discharge"
    refrigerant: str,       # "R-32" | "R-410A" | "R-22" | "not_sure"
    ambient_c: int = 35,    # default "Hot" bucket (35°C ≈ 95°F) for US; 40°C for PK
    market: str = "US",     # "US" | "PK"
) -> str:
    """
    Look up operating_targets (unified table — both US and PK) and return "low" | "ok" | "high".
    "not_sure" refrigerant defaults to R-410A.

    Phase 2 (2026-05-24): renamed from _pk_evaluate_pressure. Both markets now use this path.
    PK behavior unchanged — PK rows remain in operating_targets with market='PK'.
    Falls back to _FALLBACK_SUCTION/_FALLBACK_DISCHARGE keyed by (market, refrigerant) if DB fails.
    """
    ref = refrigerant if refrigerant != "not_sure" else "R-410A"

    # ── Belt-and-suspenders fallback dicts (used only when operating_targets lookup fails) ───
    # Values match the "Hot" default-ambient row in operating_targets for each market.
    _FALLBACK_SUCTION = {
        ("US", "R-410A"): (115, 140),
        ("US", "R-22"):   (55, 78),
        ("US", "R-32"):   (110, 145),
        ("PK", "R-410A"): (125, 144),
        ("PK", "R-22"):   (78, 88),
        ("PK", "R-32"):   (120, 140),
    }
    _FALLBACK_DISCHARGE = {
        ("US", "R-410A"): (225, 275),
        ("US", "R-22"):   (150, 275),
        ("US", "R-32"):   (225, 290),
        ("PK", "R-410A"): (325, 370),
        ("PK", "R-22"):   (200, 320),
        ("PK", "R-32"):   (365, 410),
    }

    # Find the nearest ambient row (floor to nearest available step)
    try:
        row = await db.execute(
            text(
                "SELECT suction_min_psi, suction_max_psi, discharge_min_psi, discharge_max_psi "
                "FROM operating_targets "
                "WHERE market = :mkt AND refrigerant = :ref AND ambient_c <= :amb "
                "ORDER BY ambient_c DESC LIMIT 1"
            ),
            {"mkt": market, "ref": ref, "amb": ambient_c},
        )
        targets = row.fetchone()
    except Exception as e:
        logger.warning("[diagnostic] operating_targets lookup failed (market=%s): %s", market, e)
        targets = None

    if not targets:
        if subtype == "suction":
            lo, hi = _FALLBACK_SUCTION.get((market, ref), (65, 145))
        else:
            lo, hi = _FALLBACK_DISCHARGE.get((market, ref), (200, 400))
    elif subtype == "suction":
        lo, hi = float(targets.suction_min_psi), float(targets.suction_max_psi)
    else:
        lo, hi = float(targets.discharge_min_psi), float(targets.discharge_max_psi)

    if value < lo:
        return "low"
    if value > hi:
        return "high"
    return "ok"


async def _evaluate_static_pressure_inwc(
    db: AsyncSession,
    value: float,
    system_type: str = "residential_split",
) -> str:
    """
    Tier A -- mirrors _evaluate_pressure_for_market. Look up static_pressure_targets
    (total_external design budget) and return "over_budget" | "within_budget".
    Server-side deterministic classification against the DB threshold table, with a
    belt-and-suspenders fallback (NCI residential 0.50 in.w.c. routing max) if the
    lookup fails.
    """
    _FALLBACK_TESP_BUDGET = 0.50
    try:
        row = await db.execute(
            text(
                "SELECT design_budget_inwc FROM static_pressure_targets "
                "WHERE measurement_point = 'total_external' "
                "AND drop_threshold_inwc IS NOT NULL "
                "ORDER BY design_budget_inwc ASC LIMIT 1"
            )
        )
        target = row.fetchone()
    except Exception as e:
        logger.warning("[diagnostic] static_pressure_targets lookup failed: %s", e)
        target = None
    budget = float(target.design_budget_inwc) if target else _FALLBACK_TESP_BUDGET
    if value > budget:
        return "over_budget"
    return "within_budget"


async def _evaluate_clammy_rh(
    db: AsyncSession,
    indoor_rh: float,
    return_wet_bulb: Optional[float],
) -> str:
    """
    Tier A Card #22 (comfort / clammy) step q2-clammy-rh. Mirrors
    _evaluate_pressure_for_market / _evaluate_static_pressure_inwc: DB-driven bands
    from latent_targets, deterministic (GATE-4), hard fallbacks if lookup fails.
    Composes TWO readings into one semantic branch_key:
      rh_low  |  in_band  |  rh_or_wetbulb_high
    """
    _FALLBACK_RH = (45.0, 55.0)          # latent_targets.indoor_rh design band
    _FALLBACK_WB_MAX = 69.0              # return_wet_bulb upper band (spec 63-69)
    rh_min, rh_max = _FALLBACK_RH
    try:
        rh_row = await db.execute(
            text(
                "SELECT target_min, target_max FROM latent_targets "
                "WHERE metric = 'indoor_rh' LIMIT 1"
            )
        )
        r = rh_row.fetchone()
        if r and r.target_min is not None and r.target_max is not None:
            rh_min, rh_max = float(r.target_min), float(r.target_max)
    except Exception as e:
        logger.warning("[diagnostic] latent_targets indoor_rh lookup failed: %s", e)

    wb_max = _FALLBACK_WB_MAX
    try:
        wb_row = await db.execute(
            text(
                "SELECT target_max FROM latent_targets "
                "WHERE metric = 'return_wet_bulb' LIMIT 1"
            )
        )
        wr = wb_row.fetchone()
        # latent_targets stores return_wet_bulb as a 67F point-target; only adopt the
        # DB value as an upper band when it exceeds that point, else keep 69F fallback.
        if wr and wr.target_max is not None and float(wr.target_max) > 67.0:
            wb_max = float(wr.target_max)
    except Exception as e:
        logger.warning("[diagnostic] latent_targets return_wet_bulb lookup failed: %s", e)

    if indoor_rh < rh_min:
        return "rh_low"
    if indoor_rh > rh_max or (return_wet_bulb is not None and return_wet_bulb > wb_max):
        return "rh_or_wetbulb_high"
    return "in_band"


async def _evaluate_clammy_airflow(
    db: AsyncSession,
    cfm_per_ton: float,
    tolerance_pct: float = 15.0,
) -> str:
    """
    Tier A Card #22 step q3-clammy-airflow. Humid-climate anchored (Houston default):
    low floor from cfm_per_ton_targets.low_airflow_fault_threshold, high limit from
    humid_target*(1+tolerance). Deterministic (GATE-4) with fallbacks. Returns:
      low_airflow  |  cfm_high  |  cfm_in_spec_no_load_calc
    """
    _FALLBACK_FLOOR = 350.0
    _FALLBACK_TARGET = 350.0
    floor = _FALLBACK_FLOOR
    target = _FALLBACK_TARGET
    try:
        frow = await db.execute(
            text(
                "SELECT cfm_per_ton_max FROM cfm_per_ton_targets "
                "WHERE indicator = 'low_airflow_fault_threshold' LIMIT 1"
            )
        )
        fr = frow.fetchone()
        if fr and fr.cfm_per_ton_max is not None:
            floor = float(fr.cfm_per_ton_max)
        trow = await db.execute(
            text(
                "SELECT cfm_per_ton_max FROM cfm_per_ton_targets "
                "WHERE indicator = 'humid_target' LIMIT 1"
            )
        )
        tr = trow.fetchone()
        if tr and tr.cfm_per_ton_max is not None:
            target = float(tr.cfm_per_ton_max)
    except Exception as e:
        logger.warning("[diagnostic] cfm_per_ton_targets lookup failed: %s", e)

    high_limit = target * (1.0 + tolerance_pct / 100.0)
    if cfm_per_ton < floor:
        return "low_airflow"
    if cfm_per_ton > high_limit:
        return "cfm_high"
    return "cfm_in_spec_no_load_calc"


async def _evaluate_shortcycle_static(
    db: AsyncSession,
    tesp_inwc: float,
    subcool_f: Optional[float],
) -> str:
    """
    Tier A comfort/short-cycle step q2-short-cycle-static. Discriminates the
    short-cycling root cause BEFORE the sizing gate (deterministic, GATE-4):
      subcool_abnormal (-> #17 overcharge)  |  static_above_budget (-> #20 airflow)
      | static_within_budget_and_subcool_normal (-> q3-short-cycle-runtime)
    Subcool band from superheat_subcool_targets (TXV default 7-12F). TESP budget
    reuses _evaluate_static_pressure_inwc (static_pressure_targets).
    """
    _FALLBACK_SC = (7.0, 12.0)
    sc_min, sc_max = _FALLBACK_SC
    try:
        row = await db.execute(
            text(
                "SELECT target_subcool_min_f, target_subcool_max_f "
                "FROM superheat_subcool_targets "
                "WHERE market = 'US' AND metering_device = 'TXV' "
                "AND target_subcool_min_f IS NOT NULL "
                "ORDER BY id LIMIT 1"
            )
        )
        r = row.fetchone()
        if r and r.target_subcool_min_f is not None and r.target_subcool_max_f is not None:
            sc_min, sc_max = float(r.target_subcool_min_f), float(r.target_subcool_max_f)
    except Exception as e:
        logger.warning("[diagnostic] superheat_subcool_targets subcool lookup failed: %s", e)

    if subcool_f is not None and (subcool_f < sc_min or subcool_f > sc_max):
        return "subcool_abnormal"
    tesp_key = await _evaluate_static_pressure_inwc(db, tesp_inwc)
    if tesp_key == "over_budget":
        return "static_above_budget"
    return "static_within_budget_and_subcool_normal"


async def _evaluate_shortcycle_runtime(
    db: AsyncSession,
    cycles_per_hour: float,
) -> str:
    """
    Tier A comfort/short-cycle step q3-short-cycle-runtime. runtime_pct is
    record-only (HARD-DISABLED); only cycles_per_hour drives the branch, compared
    against sizing_rules.cycles_per_hour (default 3/hr). Deterministic (GATE-4):
      short_cycle_signature_present (-> q4-sizing-gate)  |  cycle_pattern_normal (escalate)
    """
    _FALLBACK_CPH = 3.0
    thr = _FALLBACK_CPH
    try:
        row = await db.execute(
            text(
                "SELECT threshold_value FROM sizing_rules "
                "WHERE indicator = 'cycles_per_hour' LIMIT 1"
            )
        )
        r = row.fetchone()
        if r and r.threshold_value is not None:
            thr = float(r.threshold_value)
    except Exception as e:
        logger.warning("[diagnostic] sizing_rules cycles_per_hour lookup failed: %s", e)

    if cycles_per_hour > thr:
        return "short_cycle_signature_present"
    return "cycle_pattern_normal"


async def _evaluate_four_point_static(
    db: AsyncSession,
    before_filter: float,
    after_filter: float,
    before_coil: float,
    after_coil: float,
) -> str:
    """
    Tier A airflow_assessment step aa-q2-four-point. Localizes an over-budget TESP
    across the 4-point static profile (deterministic, GATE-4):
      coil_drop_dominant (-> #14)  |  filter_drop_dominant (-> #2)
      | system_wide_no_dominant_point (-> #20 catch-all)
    The distributed_duct_signature (#13) branch is LOW-confidence / flagged for
    review, so the no-dominant case folds into the #20 catch-all here.
    Drop thresholds from static_pressure_targets (after_filter, after_coil).
    """
    _FB_FILTER_THR = 0.10
    _FB_COIL_THR = 0.20
    filter_thr = _FB_FILTER_THR
    coil_thr = _FB_COIL_THR
    try:
        frow = await db.execute(
            text(
                "SELECT max(drop_threshold_inwc) AS thr FROM static_pressure_targets "
                "WHERE measurement_point = 'after_filter' AND drop_threshold_inwc IS NOT NULL"
            )
        )
        fr = frow.fetchone()
        if fr and fr.thr is not None:
            filter_thr = float(fr.thr)
        crow = await db.execute(
            text(
                "SELECT max(drop_threshold_inwc) AS thr FROM static_pressure_targets "
                "WHERE measurement_point = 'after_coil' AND system_type = 'residential_split' "
                "AND drop_threshold_inwc IS NOT NULL"
            )
        )
        cr = crow.fetchone()
        if cr and cr.thr is not None:
            coil_thr = float(cr.thr)
    except Exception as e:
        logger.warning("[diagnostic] static_pressure_targets drop-threshold lookup failed: %s", e)

    filter_delta = abs(after_filter - before_filter)
    coil_delta = abs(after_coil - before_coil)
    coil_exceeds = coil_delta > coil_thr
    filter_exceeds = filter_delta > filter_thr

    if coil_exceeds and coil_delta >= filter_delta:
        return "coil_drop_dominant"
    if filter_exceeds and filter_delta > coil_delta:
        return "filter_drop_dominant"
    return "system_wide_no_dominant_point"


async def _evaluate_shsc_discrimination(
    db: AsyncSession,
    superheat_f: float,
    subcool_f: Optional[float],
    oscillating: bool = False,
) -> str:
    """
    Tier A not_cooling step q2-sh-sc (Card #8 leak / #15 TXV variants / restriction gate).
    Deterministic SH/SC discrimination (GATE-4):
      txv_hunting(#15/15c) | txv_bulb_loss(#15/15b) | restriction_check(-> q3)
      | confirmed_leak(#8) | inconclusive(escalate)
    Subcool band from superheat_subcool_targets (TXV 7-12F). TXV target_superheat is
    NULL in DB (a TXV modulates superheat), so a clinical upper fallback (14F) gates
    the starved/leak case.
    """
    sc_min, sc_max = 7.0, 12.0
    _FALLBACK_SH_MAX = 14.0
    sh_max = _FALLBACK_SH_MAX
    try:
        row = await db.execute(
            text(
                "SELECT target_subcool_min_f, target_subcool_max_f "
                "FROM superheat_subcool_targets "
                "WHERE market = 'US' AND metering_device = 'TXV' "
                "AND target_subcool_min_f IS NOT NULL ORDER BY id LIMIT 1"
            )
        )
        r = row.fetchone()
        if r and r.target_subcool_min_f is not None and r.target_subcool_max_f is not None:
            sc_min, sc_max = float(r.target_subcool_min_f), float(r.target_subcool_max_f)
    except Exception as e:
        logger.warning("[diagnostic] superheat_subcool_targets SH/SC lookup failed: %s", e)

    if oscillating:
        return "txv_hunting"
    if superheat_f <= 3.0:
        return "txv_bulb_loss"
    if subcool_f is not None and subcool_f > sc_max:
        return "restriction_check"
    if superheat_f > sh_max and subcool_f is not None and subcool_f < sc_min:
        return "confirmed_leak"
    return "inconclusive"


async def _evaluate_ll_restriction(
    db: AsyncSession,
    drier_inlet_f: float,
    drier_outlet_f: float,
    ambient_f: Optional[float],
) -> str:
    """
    Tier A not_cooling step q3-restriction-lldrop. Confirms a liquid-line/drier
    restriction (deterministic, GATE-4) via drier temp drop OR colder-than-ambient
    check against liquid_line_restriction_thresholds:
      drop_confirmed(-> q4-restriction-head)  |  no_drop_confirmed(escalate)
    """
    drop_floor = 3.0
    ambient_floor = 1.0
    try:
        d = await db.execute(
            text(
                "SELECT threshold_value FROM liquid_line_restriction_thresholds "
                "WHERE check_type = 'drier_temp_drop' AND refrigerant = 'ALL' LIMIT 1"
            )
        )
        dr = d.fetchone()
        if dr and dr.threshold_value is not None:
            drop_floor = float(dr.threshold_value)
        a = await db.execute(
            text(
                "SELECT threshold_value FROM liquid_line_restriction_thresholds "
                "WHERE check_type = 'ambient_floor' LIMIT 1"
            )
        )
        ar = a.fetchone()
        if ar and ar.threshold_value is not None:
            ambient_floor = float(ar.threshold_value)
    except Exception as e:
        logger.warning("[diagnostic] liquid_line_restriction_thresholds lookup failed: %s", e)

    drier_drop = drier_inlet_f - drier_outlet_f
    colder_than_ambient = (
        ambient_f is not None and drier_outlet_f <= (ambient_f - ambient_floor)
    )
    if drier_drop > drop_floor or colder_than_ambient:
        return "drop_confirmed"
    return "no_drop_confirmed"


async def _evaluate_restriction_head(
    db: AsyncSession,
    discharge_psi: float,
    refrigerant: str,
    ambient_c: int,
    market: str = "US",
) -> str:
    """
    Tier A not_cooling step q4-restriction-head. No head-pressure table exists (D1
    Sec 2.3 GAP), so reuse the existing discharge-PSI evaluator against
    operating_targets: HIGH head -> head_high (escalate; overcharge/dirty condenser,
    NOT restriction); normal-to-low head -> head_normal_to_low (-> Card #25 confirmed
    restriction). Deterministic (GATE-4).
    """
    disch_key = await _evaluate_pressure_for_market(
        db, discharge_psi, "discharge", refrigerant, ambient_c, market=market
    )
    if disch_key == "high":
        return "head_high"
    return "head_normal_to_low"


def _evaluate_tstat_24v(voltage: float) -> str:
    """
    Tier A not_turning_on step q6-tstat-24v (Card #23 thermostat / low-voltage).
    24V nominal control voltage, +/-10% tolerance (spec.control_voltage_24v).
    Deterministic (GATE-4):
      present_but_call_not_passing (-> #23)  |  absent_or_call_passing (escalate)
    24V present at R-to-C but equipment not energizing => thermostat/wiring fault (#23).
    Below-tolerance (absent/phantom) => upstream transformer/wiring -> tech judgment.
    """
    _NOMINAL_24V = 24.0
    _TOLERANCE_PCT = 10.0
    present_floor = _NOMINAL_24V * (1.0 - _TOLERANCE_PCT / 100.0)  # 21.6 V
    if voltage >= present_floor:
        return "present_but_call_not_passing"
    return "absent_or_call_passing"


async def _evaluate_megohm(db: AsyncSession, megohm: float) -> str:
    """
    Tier A not_cooling #26 chain step q7-compressor-megohm. Winding-to-ground
    resistance vs compressor_test_thresholds (26a; Copeland default anchor 0.5 megohm).
    Deterministic (GATE-4):
      below_condemn_limit (-> #26 grounded/shorted winding)  |  above_condemn_limit (-> q8)
    """
    _FALLBACK_CONDEMN = 0.50
    limit = _FALLBACK_CONDEMN
    try:
        row = await db.execute(
            text(
                "SELECT min(threshold_value) AS lim FROM compressor_test_thresholds "
                "WHERE sub_mode_card = '26a' AND test = 'winding_to_ground_resistance' "
                "AND unit = 'megohm' AND comparison = 'below'"
            )
        )
        r = row.fetchone()
        if r and r.lim is not None:
            limit = float(r.lim)
    except Exception as e:
        logger.warning("[diagnostic] compressor_test_thresholds 26a lookup failed: %s", e)

    if megohm < limit:
        return "below_condemn_limit"
    return "above_condemn_limit"


async def _evaluate_locked_rotor(db: AsyncSession, duration_s: float) -> str:
    """
    Tier A not_cooling #26 chain step q8-compressor-locked-rotor. Sustained no-spin
    LRA-level draw duration vs compressor_test_thresholds (26b; >=2s). Upstream steps
    (q5 charge / q6 start-assist / q7 megohm) have already excluded charge, start
    components, and grounded windings. Deterministic (GATE-4):
      seizure_confirmed (-> #26 mechanical seizure, 26b)  |  not_confirmed (escalate)
    """
    _FALLBACK_DURATION_S = 2.0
    thr = _FALLBACK_DURATION_S
    try:
        row = await db.execute(
            text(
                "SELECT min(threshold_value) AS thr FROM compressor_test_thresholds "
                "WHERE sub_mode_card = '26b' AND unit = 'seconds'"
            )
        )
        r = row.fetchone()
        if r and r.thr is not None:
            thr = float(r.thr)
    except Exception as e:
        logger.warning("[diagnostic] compressor_test_thresholds 26b lookup failed: %s", e)

    if duration_s >= thr:
        return "seizure_confirmed"
    return "not_confirmed"


# ── GATE-5 Reading Receipt ──────────────────────────────────────────────────────

_HIGH_EXPOSURE_CARDS = {10, 22, 24, 26}  # >$5K exposure -> enhanced Layer-4 (Guidelines Sec 10)


def _reading_result_label(branch_key: str) -> str:
    b = (branch_key or "").lower()
    if any(x in b for x in ("high", "over", "above", "abnormal", "excess", "confirmed_leak", "seizure", "below_condemn")):
        return "high"
    if any(x in b for x in ("_low", "low_", "below", "under", "deficit", "cfm_high")):
        return "low"
    if "cfm_high" in b:
        return "high"
    return "within range"


def _build_reading_receipt(q_row, answer, branch: dict, branch_key: str, card_id: int) -> Optional[dict]:
    """
    GATE-5 Reading Receipt snapshot captured when a reading/multi step resolves a
    card. Generic: pulls the primary reading value + the step's target band + a
    result label so FaultResolutionScreen can render reading-vs-target inline.
    Returns None for non-reading resolutions (visual_select / photo).
    """
    spec = None
    value = None
    if q_row.input_type == "reading" and isinstance(q_row.reading_spec, dict):
        spec = q_row.reading_spec
        if isinstance(answer, dict):
            value = answer.get("value")
    elif q_row.input_type == "multi" and isinstance(q_row.options_jsonb, list):
        for item in q_row.options_jsonb:
            if isinstance(item, dict) and item.get("kind") == "reading":
                spec = item.get("spec")
                break
        if isinstance(answer, dict):
            r0 = answer.get("reading_0")
            if isinstance(r0, dict):
                value = r0.get("value")
    if not isinstance(spec, dict) or value is None:
        return None

    why = (branch.get("reason") or branch.get("note") or "").strip()
    for sep in (" -- ", ". "):
        if sep in why:
            why = why.split(sep, 1)[0].strip()
            break

    conf_raw = str(branch.get("confidence") or "Medium").strip().lower()
    confidence = {"low": "Low", "medium": "Medium", "high": "High"}.get(conf_raw, "Medium")

    return {
        "reading_value": value,
        "unit": spec.get("unit"),
        "target_low": spec.get("band_min"),
        "target_high": spec.get("band_max"),
        "target_source": spec.get("compare_to") or "reference targets",
        "result": _reading_result_label(branch_key),
        "why_line": why,
        "ruled_out": [],
        "confidence": confidence,
        "high_exposure": int(card_id) in _HIGH_EXPOSURE_CARDS,
    }


# ── Branch following ───────────────────────────────────────────────────────────


def _follow_branch(branch_logic: dict, branch_key: str) -> Optional[dict]:
    """
    Look up branch_key in branch_logic.

    Resolution order:
      1. Exact key match
      2. photo_branch_map translation (AI photo grades → compound keys)
      3. 'any' wildcard fallback
    Returns None if no match found (caller should escalate).
    """
    branch = branch_logic.get(branch_key)

    if branch is None:
        # BUG-011-fix: translate AI photo grade via photo_branch_map
        # e.g. {"photo_branch_map": {"pitted": "pitted_or_arced", "_default": "clean"}, ...}
        pmap = branch_logic.get("photo_branch_map")
        if isinstance(pmap, dict):
            mapped_key = pmap.get(branch_key) or pmap.get("_default")
            if mapped_key:
                branch = branch_logic.get(mapped_key)
                if branch:
                    logger.info(
                        "[diagnostic] photo_branch_map: '%s' → '%s'", branch_key, mapped_key
                    )

    if branch is None:
        branch = branch_logic.get("any")

    return branch


# ── Branch result → AnswerResponse ────────────────────────────────────────────


async def _process_branch(
    db: AsyncSession,
    session_id: str,
    complaint_type: str,
    branch: dict,
    assessment_id: str = "",
    company_id: str = "",
    tables: MarketTables = None,
) -> AnswerResponse:
    """
    Translate a branch dict into an AnswerResponse.

    Handles all branch action types:
      service_complete, escalate, phase_2_gate, resolve_card, next_step_id,
      jump_to_complaint

    assessment_id / company_id are required for service_complete+generate_estimate.
    """
    finding = branch.get("finding")

    # ── service_complete ───────────────────────────────────────────────────────
    if branch.get("service_complete"):
        # BUG-008 fix: failure must propagate as HTTP 503; do NOT silently
        # return service_step_complete=True while the estimate row is missing.
        # Sentry receives the full exception via logger.error(exc_info=True).
        if branch.get("generate_estimate") and assessment_id and company_id:
            try:
                await _generate_service_estimate(db, assessment_id, company_id, tables.market)
            except Exception as exc:
                logger.error(
                    "[diagnostic] service estimate creation failed: %s", exc,
                    exc_info=True,
                )
                try:
                    await db.rollback()
                except Exception:
                    pass
                raise HTTPException(
                    status_code=503,
                    detail="Estimate creation failed — please retry.",
                )
        await _complete_service_session(db, session_id)
        return AnswerResponse(service_step_complete=True, finding=finding)

    # ── escalate ───────────────────────────────────────────────────────────────
    if branch.get("escalate"):
        reason = branch.get("reason", "Manual diagnosis required.")
        await _escalate_session(db, session_id)
        return AnswerResponse(escalated=True, escalation_reason=reason, finding=finding)

    # ── phase_2_gate ───────────────────────────────────────────────────────────
    if branch.get("phase_2_gate"):
        continuation = branch.get("after", {})
        return AnswerResponse(
            phase_2_gate=True,
            gate_continuation={"session_id": session_id, **continuation},
        )

    # ── resolve_card ───────────────────────────────────────────────────────────
    if "resolve_card" in branch:
        card_id: int = branch["resolve_card"]
        card_name = await _get_fault_card_name(db, card_id, tables)
        photo_slots: List[dict] = branch.get("photo_slots") or []
        await _resolve_session(db, session_id, card_id)
        return AnswerResponse(
            resolved=True,
            card_id=card_id,
            card_name=card_name or f"Card #{card_id}",
            photo_slots=photo_slots,
            finding=finding,
        )

    # ── next_step_id ───────────────────────────────────────────────────────────
    if "next_step_id" in branch:
        next_step_id: str = branch["next_step_id"]
        next_row = await _load_question(db, complaint_type, next_step_id)
        if not next_row:
            await _escalate_session(db, session_id)
            return AnswerResponse(
                escalated=True,
                escalation_reason=f"Question '{next_step_id}' not found in database.",
            )
        await _set_session_step(db, session_id, next_step_id)
        return AnswerResponse(next_step=_row_to_question_out(next_row, tables.market), finding=finding)

    # ── jump_to_complaint (error_code q4-reset "no" branch) ───────────────────
    if "jump_to_complaint" in branch:
        new_ct: str = branch["jump_to_complaint"]
        first_row = await _load_first_question(db, new_ct)
        if not first_row:
            await _escalate_session(db, session_id)
            return AnswerResponse(
                escalated=True,
                escalation_reason=f"No questions found for complaint type '{new_ct}'.",
            )
        await db.execute(
            text(
                "UPDATE diagnostic_sessions"
                " SET current_step_id = :step, complaint_type = :ct, updated_at = :now"
                " WHERE id = :sid"
            ),
            {
                "step": first_row.step_id,
                "ct": new_ct,
                "now": datetime.now(timezone.utc),
                "sid": session_id,
            },
        )
        return AnswerResponse(next_step=_row_to_question_out(first_row, tables.market))

    # ── unrecognised branch structure ──────────────────────────────────────────
    logger.error("[diagnostic] branch has no recognised action key: %s", branch)
    await _escalate_session(db, session_id)
    return AnswerResponse(
        escalated=True,
        escalation_reason="Internal: branch has no recognised action.",
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────


@router.post("/session", response_model=StartSessionResponse)
async def start_session(
    body: StartSessionRequest,
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_company_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new diagnostic session for an assessment.

    - Verifies assessment belongs to the caller's company.
    - Loads the first question for the given complaint_type.
    - Auto-resolves 'auto' type Q1 from OCR nameplate data (BUG-004 fix).
    - Returns session_id + first question (or second, for auto-advance).
    """
    # Ownership check
    assessment = await _load_assessment(db, body.assessment_id, auth.company_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    # Load first question
    first_row = await _load_first_question(db, body.complaint_type)
    if not first_row:
        raise HTTPException(
            status_code=400,
            detail=f"No diagnostic questions found for complaint type '{body.complaint_type}'.",
        )

    # ── 'auto' type Q1 (e.g. not_heating system_type) ────────────────────────
    if first_row.input_type == "auto":
        branch_logic = first_row.branch_logic_jsonb or {}
        branch_key = _resolve_auto_question(branch_logic, assessment.ocr_nameplate)
        branch = _follow_branch(branch_logic, branch_key)

        if not branch:
            raise HTTPException(
                status_code=500,
                detail=f"Auto-question: no branch for resolved key '{branch_key}'.",
            )

        # Create session pointing at Q1 (will advance immediately below)
        session_id = await _create_session(
            db,
            body.assessment_id,
            auth.company_id,
            auth.user_id,
            body.complaint_type,
            first_row.step_id,
        )

        # Auto-advance to next_step_id if present
        if "next_step_id" in branch:
            next_row = await _load_question(db, body.complaint_type, branch["next_step_id"])
            if next_row:
                await _set_session_step(db, session_id, next_row.step_id)
                return StartSessionResponse(
                    session_id=session_id,
                    current_step=_row_to_question_out(next_row, tables.market),
                )

        # phase_2_gate / escalate from Q1 auto — rare, surface to caller
        return StartSessionResponse(
            session_id=session_id,
            current_step=_row_to_question_out(first_row, tables.market),
        )

    # ── Normal (non-auto) first question ─────────────────────────────────────
    session_id = await _create_session(
        db,
        body.assessment_id,
        auth.company_id,
        auth.user_id,
        body.complaint_type,
        first_row.step_id,
    )
    return StartSessionResponse(
        session_id=session_id,
        current_step=_row_to_question_out(first_row, tables.market),
    )


@router.post("/session/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: str,
    body: AnswerRequest,
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_company_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit an answer to the current diagnostic step.

    Computes the branch_key from the answer payload, follows branch_logic_jsonb,
    and returns the next question or a resolution/escalation/gate response.

    Special handling:
      - error_code Q1 'extract_then_lookup' action (BUG-005 fix)
    """
    # Load & validate session
    session = await _load_session(db, session_id, auth.company_id)
    if not session:
        raise HTTPException(status_code=404, detail="Diagnostic session not found.")
    if session.status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Session is already '{session.status}' and cannot accept new answers.",
        )

    # Load current question
    q_row = await _load_question(db, session.complaint_type, session.current_step_id)
    if not q_row:
        raise HTTPException(
            status_code=500,
            detail=f"Current step '{session.current_step_id}' not found in diagnostic_questions.",
        )

    branch_logic: dict = q_row.branch_logic_jsonb or {}

    # ── Special: error_code photo Q1 with 'extract_then_lookup' action ────────
    # The entire branch_logic for this step is wrapped under one key:
    # {"extract_then_lookup": {"action": "call_error_code_lookup", "brand_from": ..., "after": {...}}}
    if "extract_then_lookup" in branch_logic:
        action_config = branch_logic["extract_then_lookup"]
        assessment = await _load_assessment(db, session.assessment_id, auth.company_id)
        ocr = assessment.ocr_nameplate if assessment else None

        # WS-A4: tech used the code_input photo-skip — honour the "skipped" branch
        # directly instead of running OCR lookup (no photo was taken).
        # B.6: also set photo_skipped flag on session for report disclosure
        if isinstance(body.answer, dict) and body.answer.get("branch_key") == "skipped":
            from datetime import datetime, timezone
            await db.execute(
                text(
                    "UPDATE diagnostic_sessions SET photo_skipped = TRUE, updated_at = :now WHERE id = :sid"
                ),
                {"now": datetime.now(timezone.utc), "sid": session_id},
            )
            logger.info(
                "[diagnostic] photo step '%s' skipped — photo_skipped flag set on session %s",
                session.current_step_id, session_id,
            )
            skip_branch = branch_logic.get("skipped") or branch_logic.get("any")
            if skip_branch:
                logger.info("[diagnostic] error_code q1: skipped photo — routing via 'skipped' branch")
                return await _process_branch(
                    db, session_id, session.complaint_type, skip_branch,
                    assessment_id=session.assessment_id, company_id=auth.company_id,
                    tables=tables,
                )

        # Extract AI-read code from answer (may be None when branch_key injection is used)
        photo_ai_output: Optional[str] = None
        if isinstance(body.answer, dict):
            photo_ai_output = body.answer.get("ai_output") or body.answer.get("code")

        # BUG-005 fix embedded in _call_error_code_lookup
        resolved_bk = await _call_error_code_lookup(db, action_config, ocr, photo_ai_output, tables=tables)
        after_map: dict = action_config.get("after", {})
        branch = after_map.get(resolved_bk) or after_map.get("nuisance_or_unknown")

        if not branch:
            await _escalate_session(db, session_id)
            return AnswerResponse(
                escalated=True,
                escalation_reason="Error code lookup produced no matching branch.",
            )
        return await _process_branch(
            db, session_id, session.complaint_type, branch,
            assessment_id=session.assessment_id, company_id=auth.company_id,
            tables=tables,
        )

    # ── Compute branch_key (BUG-003 fix) ─────────────────────────────────
    branch_key = _compute_branch_key(body.answer, q_row.input_type)

    # ── Ambient-aware pressure evaluation: both US and PK use operating_targets ──
    # Phase 2 (2026-05-24): PK-only gate removed. Both markets use _evaluate_pressure_for_market.
    # US routing is now dynamic per ambient bucket selected in Step Zero UI.
    # PK behavior unchanged — PK rows in operating_targets, ambient_c from request or market default.
    if (
        q_row.input_type == "reading"
        and isinstance(q_row.reading_spec, dict)
        and q_row.reading_spec.get("type") == "psi"
        and isinstance(body.answer, dict)
        and body.answer.get("value") is not None
    ):
        subtype = q_row.reading_spec.get("subtype", "suction")
        raw_psi = float(body.answer["value"])
        refrigerant = body.refrigerant_type or "not_sure"
        # US default: 35°C ("Hot" bucket ≈ 95°F Houston summer). PK default: 40°C mid-summer.
        default_ambient = 40 if tables.market == "PK" else 35
        ambient = body.ambient_c or default_ambient
        branch_key = await _evaluate_pressure_for_market(
            db, raw_psi, subtype, refrigerant, ambient, market=tables.market
        )
        logger.info(
            "[diagnostic] pressure eval: %.1f PSI %s → %s (market=%s, ref=%s, amb=%d°C)",
            raw_psi, subtype, branch_key, tables.market, refrigerant, ambient,
        )

    # Static-pressure evaluation (Tier A -- mirrors PSI). Additive: only fires for
    # the new static_pressure_inwc reading type; never affects existing flows.
    if (
        q_row.input_type == "reading"
        and isinstance(q_row.reading_spec, dict)
        and q_row.reading_spec.get("type") == "static_pressure_inwc"
        and isinstance(body.answer, dict)
        and body.answer.get("value") is not None
    ):
        raw_tesp = float(body.answer["value"])
        branch_key = await _evaluate_static_pressure_inwc(db, raw_tesp)
        logger.info(
            "[diagnostic] static-pressure eval: %.3f in.w.c. -> %s", raw_tesp, branch_key,
        )

    # ── Tier A Card #22 comfort/clammy multi steps (server-side eval) ────────
    # Mirrors the PSI / static-pressure overrides. Multi readings arrive in
    # options order as answer.reading_0 / reading_1; recompute the semantic
    # branch_key deterministically from the threshold tables (GATE-4). Additive:
    # fires only for the two clammy step_ids, never affects existing multi flows.
    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q2-clammy-rh"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")
        _r1 = body.answer.get("reading_1")
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            _rh = float(_r0["value"])
            _wb = (
                float(_r1["value"])
                if isinstance(_r1, dict) and _r1.get("value") is not None
                else None
            )
            branch_key = await _evaluate_clammy_rh(db, _rh, _wb)
            logger.info(
                "[diagnostic] clammy-rh eval: RH=%.1f WB=%s -> %s", _rh, _wb, branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q3-clammy-airflow"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            _cfm = float(_r0["value"])
            _tol = 15.0
            if isinstance(q_row.options_jsonb, list) and q_row.options_jsonb:
                _spec = q_row.options_jsonb[0].get("spec") or {}
                _tol = float(_spec.get("tolerance_pct", 15.0))
            branch_key = await _evaluate_clammy_airflow(db, _cfm, _tol)
            logger.info(
                "[diagnostic] clammy-airflow eval: CFM/ton=%.1f -> %s", _cfm, branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q2-short-cycle-static"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")  # static_pressure (TESP)
        _r1 = body.answer.get("reading_1")  # subcool
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            _tesp = float(_r0["value"])
            _sc = (
                float(_r1["value"])
                if isinstance(_r1, dict) and _r1.get("value") is not None
                else None
            )
            branch_key = await _evaluate_shortcycle_static(db, _tesp, _sc)
            logger.info(
                "[diagnostic] short-cycle static eval: TESP=%.3f subcool=%s -> %s",
                _tesp, _sc, branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q3-short-cycle-runtime"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")  # cycles_per_hour
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            _cph = float(_r0["value"])
            branch_key = await _evaluate_shortcycle_runtime(db, _cph)
            logger.info(
                "[diagnostic] short-cycle runtime eval: cycles/hr=%.1f -> %s",
                _cph, branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "aa-q2-four-point"
        and isinstance(body.answer, dict)
    ):
        # options order: before_filter, after_filter, before_coil, after_coil
        _rs = [body.answer.get(f"reading_{i}") for i in range(4)]
        if all(isinstance(r, dict) and r.get("value") is not None for r in _rs):
            _v = [float(r["value"]) for r in _rs]
            branch_key = await _evaluate_four_point_static(db, _v[0], _v[1], _v[2], _v[3])
            logger.info(
                "[diagnostic] four-point static eval: bf=%.3f af=%.3f bc=%.3f ac=%.3f -> %s",
                _v[0], _v[1], _v[2], _v[3], branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q2-sh-sc"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")  # superheat_F
        _r1 = body.answer.get("reading_1")  # subcool_F
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            _sh = float(_r0["value"])
            _sc = (
                float(_r1["value"])
                if isinstance(_r1, dict) and _r1.get("value") is not None
                else None
            )
            _osc = bool(
                _r0.get("oscillating")
                or _r0.get("stability") == "oscillating"
                or _r0.get("branch_key") == "oscillating"
            )
            branch_key = await _evaluate_shsc_discrimination(db, _sh, _sc, _osc)
            logger.info(
                "[diagnostic] SH/SC eval: SH=%.1f SC=%s osc=%s -> %s",
                _sh, _sc, _osc, branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q3-restriction-lldrop"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")  # drier inlet
        _r1 = body.answer.get("reading_1")  # drier outlet
        _r2 = body.answer.get("reading_2")  # outdoor ambient
        if (
            isinstance(_r0, dict) and _r0.get("value") is not None
            and isinstance(_r1, dict) and _r1.get("value") is not None
        ):
            _in = float(_r0["value"])
            _out = float(_r1["value"])
            _amb = (
                float(_r2["value"])
                if isinstance(_r2, dict) and _r2.get("value") is not None
                else None
            )
            branch_key = await _evaluate_ll_restriction(db, _in, _out, _amb)
            logger.info(
                "[diagnostic] LL-restriction eval: in=%.1f out=%.1f amb=%s -> %s",
                _in, _out, _amb, branch_key,
            )

    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q4-restriction-head"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")  # discharge_pressure_psi
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            _disch = float(_r0["value"])
            _ref = body.refrigerant_type or "not_sure"
            _amb_c = body.ambient_c or (40 if tables.market == "PK" else 35)
            branch_key = await _evaluate_restriction_head(
                db, _disch, _ref, _amb_c, market=tables.market
            )
            logger.info(
                "[diagnostic] restriction-head eval: discharge=%.1f PSI -> %s",
                _disch, branch_key,
            )

    # ── Tier A Card #23 thermostat 24V (not_turning_on q6-tstat-24v) ─────────
    if (
        q_row.input_type == "reading"
        and isinstance(q_row.reading_spec, dict)
        and q_row.reading_spec.get("type") == "voltage_24v"
        and isinstance(body.answer, dict)
        and body.answer.get("value") is not None
    ):
        branch_key = _evaluate_tstat_24v(float(body.answer["value"]))
        logger.info(
            "[diagnostic] tstat-24V eval: %.1f V -> %s", float(body.answer["value"]), branch_key,
        )

    # ── Tier A #26 chain: megohm winding-to-ground (q7-compressor-megohm) ────
    if (
        q_row.input_type == "reading"
        and isinstance(q_row.reading_spec, dict)
        and q_row.reading_spec.get("type") == "megohm_winding_to_ground"
        and isinstance(body.answer, dict)
        and body.answer.get("value") is not None
    ):
        branch_key = await _evaluate_megohm(db, float(body.answer["value"]))
        logger.info(
            "[diagnostic] megohm eval: %.2f megohm -> %s", float(body.answer["value"]), branch_key,
        )

    # ── Tier A #26 chain: locked-rotor duration (q8-compressor-locked-rotor) ─
    if (
        q_row.input_type == "multi"
        and session.current_step_id == "q8-compressor-locked-rotor"
        and isinstance(body.answer, dict)
    ):
        _r0 = body.answer.get("reading_0")
        if isinstance(_r0, dict) and _r0.get("value") is not None:
            branch_key = await _evaluate_locked_rotor(db, float(_r0["value"]))
            logger.info(
                "[diagnostic] locked-rotor eval: %.1f s -> %s", float(_r0["value"]), branch_key,
            )

    # ── BUG-016: PK ok suction → discharge PSI step (not US Card 13) ─────────
    # US q2-nc-suction maps "ok" → Card 13 (TXV/Metering Device).
    # For PK at 40°C ambient, "ok" means 125-145 PSI (normal operating range).
    # Routing to Card 13 is wrong — instead continue to discharge PSI to
    # differentiate dirty condenser (Card 14) vs. overcharge (Card 17).
    if (
        tables.market == "PK"
        and branch_key == "ok"
        and isinstance(q_row.reading_spec, dict)
        and q_row.reading_spec.get("subtype") == "suction"
    ):
        pk_ok_branch: dict = {"next_step_id": "q2-nc-discharge"}
        logger.info("[diagnostic] BUG-016: PK normal suction → routing to discharge PSI step")
        return await _process_branch(
            db, session_id, session.complaint_type, pk_ok_branch,
            assessment_id=session.assessment_id, company_id=auth.company_id,
            tables=tables,
        )

    # ── Follow branch ─────────────────────────────────────────────────────────
    branch = _follow_branch(branch_logic, branch_key)

    if branch is None:
        logger.warning(
            "[diagnostic] ESCALATED unhandled_answer: step='%s' complaint='%s' branch_key='%s'",
            session.current_step_id,
            session.complaint_type,
            branch_key,
        )
        await _escalate_session(db, session_id)
        return AnswerResponse(
            escalated=True,
            escalation_reason=(
                f"No branch for answer '{branch_key}' at step '{session.current_step_id}'. "
                "Manual diagnosis required."
            ),
        )

    # ── GATE-5 Reading Receipt: snapshot the resolving reading + target ──────
    if "resolve_card" in branch:
        try:
            _rr = _build_reading_receipt(q_row, body.answer, branch, branch_key, branch["resolve_card"])
            if _rr is not None:
                await db.execute(
                    text("UPDATE diagnostic_sessions SET reading_receipt = CAST(:rr AS JSONB) WHERE id = :sid"),
                    {"rr": json.dumps(_rr), "sid": session_id},
                )
        except Exception as e:
            logger.warning("[diagnostic] reading_receipt capture failed: %s", e)

    return await _process_branch(
        db, session_id, session.complaint_type, branch,
        assessment_id=session.assessment_id, company_id=auth.company_id,
        tables=tables,
    )


@router.get("/pk/pressure-targets")
async def pk_pressure_targets(
    refrigerant: str = "not_sure",
    ambient_c: int = 40,
    db: AsyncSession = Depends(get_db),
):
    """
    PK-only: return expected suction/discharge PSI ranges for a given
    refrigerant type and outdoor ambient temperature.

    Used by the frontend to display target ranges on the pressure reading step.

    GET /api/diagnostic/pk/pressure-targets?refrigerant=R-32&ambient_c=40

    Response:
      {
        "refrigerant_used": "R-32",
        "ambient_c": 40,
        "suction": {"min": 120, "max": 140},
        "discharge": {"min": 365, "max": 410}
      }
    """
    ref = refrigerant if refrigerant != "not_sure" else "R-410A"
    row = await db.execute(
        text(
            "SELECT suction_min_psi, suction_max_psi, discharge_min_psi, discharge_max_psi, ambient_c "
            "FROM operating_targets "
            "WHERE market = 'PK' AND refrigerant = :ref AND ambient_c <= :amb "
            "ORDER BY ambient_c DESC LIMIT 1"
        ),
        {"ref": ref, "amb": ambient_c},
    )
    targets = row.fetchone()
    if not targets:
        return {"error": "No targets found", "refrigerant_used": ref, "ambient_c": ambient_c}
    return {
        "refrigerant_used": ref,
        "ambient_c": targets.ambient_c,
        "suction":   {"min": float(targets.suction_min_psi),   "max": float(targets.suction_max_psi)},
        "discharge":  {"min": float(targets.discharge_min_psi), "max": float(targets.discharge_max_psi)},
    }


@router.get("/questions/{complaint_type}")
async def list_questions(
    complaint_type: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-N3: Return ordered question list for a complaint type.
    Used by the frontend to set the progress-bar total step count.
    GET /api/diagnostic/questions/{complaint_type}
    """
    result = await db.execute(
        text(
            "SELECT step_id, step_order, question_text, input_type"
            " FROM diagnostic_questions"
            " WHERE complaint_type = :ct"
            " ORDER BY step_order ASC"
        ),
        {"ct": complaint_type},
    )
    rows = result.fetchall()
    return [
        {
            "step_id": r.step_id,
            "step_order": r.step_order,
            "question_text": r.question_text,
            "input_type": r.input_type,
        }
        for r in rows
    ]


@router.post("/session/{session_id}/undo", response_model=StartSessionResponse)
async def undo_step(
    session_id: str = Path(...),
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_company_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-N3: Step back to the previous question in the current complaint_type tree.
    """
    session = await _load_session(db, session_id, auth.company_id)
    if not session:
        raise HTTPException(status_code=404, detail="Diagnostic session not found.")
    if session.status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot undo — session is already '{session.status}'.",
        )

    current_row = await _load_question(db, session.complaint_type, session.current_step_id)
    if not current_row:
        raise HTTPException(status_code=500, detail="Current step not found.")

    prev_result = await db.execute(
        text(
            f"SELECT {_QUESTION_COLS} FROM diagnostic_questions"
            " WHERE complaint_type = :ct AND step_order < :order"
            " ORDER BY step_order DESC LIMIT 1"
        ),
        {"ct": session.complaint_type, "order": current_row.step_order},
    )
    prev_row = prev_result.fetchone()
    if not prev_row:
        raise HTTPException(status_code=400, detail="Already at the first step.")

    await _set_session_step(db, session_id, prev_row.step_id)
    return StartSessionResponse(
        session_id=session_id,
        current_step=_row_to_question_out(prev_row, tables.market),
    )


@router.get("/session/{session_id}", response_model=StartSessionResponse)
async def resume_session(
    session_id: str = Path(...),
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_company_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    Resume a diagnostic session — return session_id + current question.
    Used when the tech navigates back to an in-progress assessment.
    """
    session = await _load_session(db, session_id, auth.company_id)
    if not session:
        raise HTTPException(status_code=404, detail="Diagnostic session not found.")

    q_row = await _load_question(db, session.complaint_type, session.current_step_id)
    if not q_row:
        raise HTTPException(
            status_code=500,
            detail=f"Current step '{session.current_step_id}' not found.",
        )

    return StartSessionResponse(
        session_id=session_id,
        current_step=_row_to_question_out(q_row, tables.market),
    )

@router.get("/result/{session_id}")
async def get_diagnostic_result(
    session_id: str = Path(...),
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_company_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    Track D D.7 -- GET /api/diagnostic/result/{session_id}
    Returns the full DiagnosticResult for a resolved diagnostic session.
    Used by /diagnoses/[session_id] to render FaultResolutionScreen.
    """
    # Load session with all Track D columns
    sess_result = await db.execute(
        text(
            "SELECT id, assessment_id, company_id, resolved_card_id, created_at,"
            "       reasoning_chain, confidence_level, share_token, reading_receipt,"
            "       customer_label, customer_address"
            " FROM diagnostic_sessions"
            " WHERE id = :sid AND company_id = :cid AND deleted_at IS NULL LIMIT 1"
        ),
        {"sid": session_id, "cid": auth.company_id},
    )
    session = sess_result.fetchone()

    if not session:
        raise HTTPException(status_code=404, detail="Diagnosis not found.")

    if not session.resolved_card_id:
        raise HTTPException(status_code=409, detail="Diagnosis not yet resolved.")

    # Load fault card data (market-aware table + climate notes column)
    climate_col = "climate_notes_pk" if tables.market == "PK" else "climate_notes_us"
    # BUG-023: use base table directly to avoid pak_fault_cards_v stale-statement issues
    _fc_table = "pak_fault_cards" if tables.market == "PK" else tables.fault_cards
    fc_result = await db.execute(
        text(
            "SELECT card_id, card_name, action_steps, parts_needed, alternative_cards,"
            " " + climate_col
            + " FROM " + _fc_table + " WHERE card_id = :cid LIMIT 1"
        ),
        {"cid": session.resolved_card_id},
    )
    fc = fc_result.fetchone()

    if not fc:
        raise HTTPException(status_code=404, detail="Fault card not found.")

    # Build share URL from share_token if present
    share_url = ""
    if session.share_token:
        base_url = (
            "https://pk.snapai.mainnov.tech"
            if tables.market == "PK"
            else "https://snapai.mainnov.tech"
        )
        share_url = base_url + "/d/" + session.share_token

    # Build alternative_diagnoses from alternative_cards JSONB
    alt_cards = fc.alternative_cards or []
    alt_diagnoses = []
    for alt in alt_cards:
        if isinstance(alt, dict):
            alt_diagnoses.append(
                {"name": alt.get("name", ""), "confidence": alt.get("confidence", "low")}
            )

    climate_note = getattr(fc, climate_col, None)

    # DX.3: pull repair_plan from existing estimate (created at diagnosis resolution)
    repair_plan = None
    if session.assessment_id:
        try:
            est_res = await db.execute(
                text("SELECT options, markup_percent FROM estimates WHERE assessment_id = :aid LIMIT 1"),
                {"aid": str(session.assessment_id)},
            )
            est_row = est_res.fetchone()
            if est_row and est_row.options:
                raw_opts = est_row.options if isinstance(est_row.options, list) else []
                # Identify recommended tier
                rec_tier = next((o.get("tier") for o in raw_opts if o.get("recommended")), "B")
                tiers = []
                _rec_meta = None
                for opt in raw_opts:
                    tier_key = opt.get("tier", "B")
                    tiers.append({
                        "key": tier_key,
                        "name": opt.get("name", tier_key),
                        "total": float(opt.get("total", 0)),
                        "line_items": opt.get("line_items", []),
                        "recommended": bool(opt.get("recommended", False)),
                    })
                    # Stage 3C: recommendation metadata is stashed on whichever
                    # option carries it (the recommended tier at persist time).
                    if _rec_meta is None and opt.get("recommendation_meta"):
                        _rec_meta = opt.get("recommendation_meta")
                if tiers:
                    # Stage 3C: surface chooser-gate flag + unit age + the
                    # "Why this recommendation?" metadata to FaultResolutionScreen.
                    _requires_chooser = bool(
                        (_rec_meta or {}).get("requires_user_chooser", False)
                    )
                    _unit_age = (_rec_meta or {}).get("unit_age_years")
                    repair_plan = {
                        "recommended_tier": rec_tier,
                        "tiers": tiers,
                        "requires_user_chooser": _requires_chooser,
                        "unit_age_years": _unit_age,
                        "recommendation": _rec_meta,
                    }
        except Exception as _rp_exc:
            logger.warning("[diagnostic] repair_plan fetch failed (non-fatal): %s", _rp_exc)

    return {
        "session_id": session_id,
        "assessment_id": str(session.assessment_id) if session.assessment_id else None,
        "fault": {
            "card_id": session.resolved_card_id,
            "name": fc.card_name,
            "confidence": session.confidence_level or "high",
        },
        "reasoning_chain": session.reasoning_chain or [],
        "reading_receipt": session.reading_receipt,
        "action_steps": fc.action_steps or [],
        "parts_needed": fc.parts_needed or [],
        "time_estimate_minutes": None,
        "common_cause_climate": climate_note,
        "photo_evidence": [],
        "alternative_diagnoses": alt_diagnoses,
        "customer": {
            "label": session.customer_label,
            "address": session.customer_address,
        },
        "share_url": share_url,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "repair_plan": repair_plan,
    }


# =============================================================================
# Track D: remaining endpoints (D.2, D.3, D.4, D.9)
# GET  /list                       -- paginated company history
# POST /feedback                   -- tech feedback on a diagnosis
# POST /finalize/{session_id}      -- set share_token + confidence_level
# GET  /public/{share_token}       -- unauthenticated public share
# Added: 2026-05-20  DEC-025 / DEC-026
# =============================================================================

import base64
import uuid as _uuid_mod


def _cursor_encode(dt) -> str:
    """Encode a datetime to an opaque base64 cursor."""
    return base64.urlsafe_b64encode(dt.isoformat().encode()).decode()


def _cursor_decode(cursor: str):
    """Decode a base64 cursor back to a datetime."""
    from datetime import datetime
    return datetime.fromisoformat(base64.urlsafe_b64decode(cursor.encode()).decode())


def _generate_share_token() -> str:
    """32-char hex token for URL sharing."""
    import secrets as _secrets
    return _secrets.token_hex(16)


# -- D.2: GET /list -----------------------------------------------------------

@router.get("/list")
async def list_diagnoses(
    limit: int = 20,
    cursor: Optional[str] = None,
    auth: AuthContext = Depends(get_current_user),
    tables: MarketTables = Depends(get_company_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    D.2 -- Paginated list of resolved diagnoses for the company.
    Uses opaque base64 cursor on created_at DESC.
    """
    limit = min(max(1, limit), 50)
    params: dict = {"cid": auth.company_id, "limit": limit + 1}
    cursor_clause = ""
    if cursor:
        try:
            cursor_dt = _cursor_decode(cursor)
            cursor_clause = " AND ds.created_at < :cursor_dt"
            params["cursor_dt"] = cursor_dt
        except Exception:
            pass

    # BUG-023: use base table directly to avoid pak_fault_cards_v stale-statement issues
    fc_table = "pak_fault_cards" if tables.market == "PK" else tables.fault_cards

    rows_res = await db.execute(
        text(
            "SELECT ds.id AS session_id, ds.created_at, ds.resolved_card_id,"
            "       ds.confidence_level, ds.customer_label, ds.assessment_id,"
            "       ds.share_token,"
            "       fc.card_name,"
            "       a.photo_urls[1] AS nameplate_photo_url,"
            "       p.address_line1 AS customer_address"
            " FROM diagnostic_sessions ds"
            " JOIN " + fc_table + " fc ON fc.card_id = ds.resolved_card_id"
            " JOIN assessments a ON a.id = ds.assessment_id"
            " LEFT JOIN properties p ON p.id = a.property_id"
            " WHERE ds.company_id = :cid"
            "   AND ds.status = 'resolved'"
            "   AND ds.deleted_at IS NULL"
            "   AND ds.resolved_card_id IS NOT NULL"
            + cursor_clause +
            " ORDER BY ds.created_at DESC"
            " LIMIT :limit"
        ),
        params,
    )
    rows = rows_res.fetchall()

    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor = None
    if has_more and items:
        next_cursor = _cursor_encode(items[-1].created_at)

    return {
        "items": [
            {
                "session_id": str(r.session_id),
                "assessment_id": str(r.assessment_id) if r.assessment_id else None,
                "fault_name": r.card_name,
                "confidence": r.confidence_level or "high",
                "customer_label": r.customer_label,
                "nameplate_photo_url": r.nameplate_photo_url,
                "share_token": getattr(r, "share_token", None),
                "customer_address": getattr(r, "customer_address", None),
                "created_at": r.created_at.isoformat(),
            }
            for r in items
        ],
        "next_cursor": next_cursor,
        "has_more": has_more,
    }


# -- D.3: POST /feedback ------------------------------------------------------

class DiagnosisFeedbackRequest(BaseModel):
    session_id: str
    agreement: str
    real_fault_text: Optional[str] = None
    alternative_fault_id: Optional[int] = None  # DX.6: structured picker result


@router.post("/feedback", status_code=201)
async def submit_diagnosis_feedback(
    body: DiagnosisFeedbackRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    D.3 -- Tech submits agree/disagree feedback on a diagnosis.
    Single shared diagnosis_feedback table (DEC-025).
    """
    sess_check = await db.execute(
        text(
            "SELECT id FROM diagnostic_sessions"
            " WHERE id = :sid AND company_id = :cid LIMIT 1"
        ),
        {"sid": body.session_id, "cid": auth.company_id},
    )
    if not sess_check.fetchone():
        raise HTTPException(status_code=404, detail="Session not found.")

    await db.execute(
        text(
            "INSERT INTO diagnosis_feedback"
            " (id, session_id, tech_user_id, agreement, real_fault_text, alternative_fault_id, created_at)"
            " VALUES (:id, :sid, :uid, :agr, :rft, :afi, :now)"
        ),
        {
            "id":  str(_uuid_mod.uuid4()),
            "sid": body.session_id,
            "uid": auth.user_id,
            "agr": body.agreement,
            "rft": body.real_fault_text,
            "afi": body.alternative_fault_id,
            "now": datetime.now(timezone.utc),
        },
    )
    await db.commit()
    return {"status": "ok"}


# -- D.4: POST /finalize/{session_id} -----------------------------------------

class FinalizeRequest(BaseModel):
    customer_label: Optional[str] = None


@router.post("/finalize/{session_id}")
async def finalize_diagnosis(
    session_id: str = Path(...),
    body: FinalizeRequest = FinalizeRequest(),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    D.4 -- Idempotent. Generates share_token + sets confidence_level.
    Called fire-and-forget from frontend on diagnostic resolve (DEC-026).
    """
    sess_res = await db.execute(
        text(
            "SELECT id, company_id, status, share_token"
            " FROM diagnostic_sessions"
            " WHERE id = :sid AND company_id = :cid LIMIT 1"
        ),
        {"sid": session_id, "cid": auth.company_id},
    )
    session = sess_res.fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.share_token:
        return {"share_token": session.share_token, "status": "already_finalized"}

    share_token = _generate_share_token()
    confidence = "high"

    updates: dict = {
        "sid": session_id,
        "token": share_token,
        "confidence": confidence,
        "now": datetime.now(timezone.utc),
    }
    label_set = ""
    if body.customer_label:
        label_set = ", customer_label = :label"
        updates["label"] = body.customer_label

    await db.execute(
        text(
            "UPDATE diagnostic_sessions"
            " SET share_token = :token,"
            "     confidence_level = :confidence,"
            "     updated_at = :now"
            + label_set +
            " WHERE id = :sid"
        ),
        updates,
    )
    await db.commit()
    return {"share_token": share_token, "status": "finalized"}


# -- D.9: GET /public/{share_token} -------------------------------------------

@router.get("/public/{share_token}")
async def get_public_diagnosis(
    share_token: str = Path(...),
    tables: MarketTables = Depends(get_tables),
    db: AsyncSession = Depends(get_db),
):
    """
    D.9 -- Unauthenticated public share. Customer PII always null.
    Market from X-Market header sent by frontend detectMarket().
    """
    sess_res = await db.execute(
        text(
            "SELECT id, assessment_id, status, resolved_card_id,"
            "       created_at, share_token, confidence_level, reasoning_chain, reading_receipt,"
            "       customer_label, customer_address"
            " FROM diagnostic_sessions"
            " WHERE share_token = :token AND deleted_at IS NULL LIMIT 1"
        ),
        {"token": share_token},
    )
    session = sess_res.fetchone()
    if not session or session.status != "resolved" or not session.resolved_card_id:
        raise HTTPException(status_code=404, detail="Diagnosis not found.")

    fc_table = tables.fault_cards
    if tables.market == "US":
        climate_col = "climate_notes_us"
    else:
        climate_col = "climate_notes_pk"

    fc_sql = (
        "SELECT card_id, card_name, action_steps, parts_needed, alternative_cards, "
        + climate_col
        + " FROM " + fc_table + " WHERE card_id = :cid LIMIT 1"
    )
    fc_res = await db.execute(text(fc_sql), {"cid": session.resolved_card_id})
    fc_row = fc_res.fetchone()
    if not fc_row:
        raise HTTPException(status_code=404, detail="Fault card not found.")

    alt_cards = fc_row.alternative_cards or []
    alt_diagnoses = [
        {"name": a.get("name", ""), "confidence": a.get("confidence", "low")}
        for a in alt_cards if isinstance(a, dict)
    ]

    climate_note = getattr(fc_row, climate_col, None)

    share_url = ""
    if session.share_token:
        base = (
            "https://pk.snapai.mainnov.tech"
            if tables.market == "PK"
            else "https://snapai.mainnov.tech"
        )
        share_url = base + "/d/" + session.share_token

    return {
        "session_id": str(session.id),
        "assessment_id": str(session.assessment_id) if session.assessment_id else None,
        "fault": {
            "card_id": session.resolved_card_id,
            "name": fc_row.card_name,
            "confidence": session.confidence_level or "high",
        },
        "reasoning_chain": session.reasoning_chain or [],
        "reading_receipt": session.reading_receipt,
        "action_steps": fc_row.action_steps or [],
        "parts_needed": fc_row.parts_needed or [],
        "time_estimate_minutes": None,
        "common_cause_climate": climate_note,
        "photo_evidence": [],
        "alternative_diagnoses": alt_diagnoses,
        "customer": {"label": None, "address": None},
        "share_url": share_url,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


# -- DX.9: PATCH /session/{session_id}/cancel ---------------------------------

@router.patch("/session/{session_id}/cancel", status_code=200)
async def cancel_diagnosis_session(
    session_id: str = Path(...),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    DX.9 -- Soft-delete a diagnostic session (sets deleted_at).
    Called when the tech taps Cancel diagnosis from the ... menu.
    """
    sess_check = await db.execute(
        text(
            "SELECT id FROM diagnostic_sessions"
            " WHERE id = :sid AND company_id = :cid AND deleted_at IS NULL LIMIT 1"
        ),
        {"sid": session_id, "cid": auth.company_id},
    )
    if not sess_check.fetchone():
        raise HTTPException(status_code=404, detail="Session not found.")

    await db.execute(
        text(
            "UPDATE diagnostic_sessions"
            " SET deleted_at = :now, updated_at = :now WHERE id = :sid"
        ),
        {"now": datetime.now(timezone.utc), "sid": session_id},
    )
    await db.commit()
    return {"status": "cancelled"}

# BUG-020 fix verified: card_id (not id)