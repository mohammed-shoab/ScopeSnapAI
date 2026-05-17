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
from api.dependencies import get_tables, MarketTables
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
        candidate = "rpt-" + "".join(secrets.choice(_string.digits) for _ in range(4))
        clash = await db.execute(
            text("SELECT id FROM estimates WHERE report_short_id = :sid LIMIT 1"),
            {"sid": candidate},
        )
        if not clash.fetchone():
            short_id = candidate
            break
    if not short_id:
        short_id = f"rpt-{uuid.uuid4().hex[:4]}"

    report_token = secrets.token_urlsafe(32)[:32]
    now = datetime.now(timezone.utc)

    await db.execute(
        text(
            "INSERT INTO estimates"
            "  (id, assessment_id, company_id, report_token, report_short_id,"
            "   options, markup_percent, status, created_at, updated_at)"
            " VALUES"
            "  (:id, :aid, :cid, :token, :short_id,"
            "   :options::jsonb, :markup, 'draft', :now, :now)"
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
        },
    )

    # Mark assessment as having an estimate (non-critical; ignore errors)
    try:
        await db.execute(
            text("UPDATE assessments SET est_status = 'estimated', updated_at = :now WHERE id = :aid"),
            {"now": now, "aid": assessment_id},
        )
    except Exception as exc:
        logger.warning("[diagnostic] could not update assessment est_status: %s", exc)

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

    For PK market, PSI reading questions get localised pressure-range hints
    instead of the US-centric defaults stored in the database.
    """
    hint = row.hint_text
    if market == "PK" and isinstance(row.reading_spec, dict) and row.reading_spec.get("type") == "psi":
        subtype = row.reading_spec.get("subtype", "suction")
        hint = _PK_PSI_HINTS.get(subtype, hint)

    return QuestionOut(
        step_id=row.step_id,
        question_text=row.question_text,
        hint_text=hint,
        input_type=row.input_type,
        # options_jsonb serves dual purpose:
        #   visual_select → [{value, label, icon}]
        #   multi         → [{kind, spec}]  (frontend casts)
        options=row.options_jsonb,
        reading_spec=row.reading_spec,
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
        # Top-level branch_key (simple reading / photo answers)
        bk = answer.get("branch_key")
        if bk:
            return str(bk).strip().lower()

        # BUG-005: Multi-input bundled answer — readings keyed as reading_0, reading_1 …
        # The first reading's branch_key is the primary routing key.
        r0 = answer.get("reading_0")
        if isinstance(r0, dict):
            bk = r0.get("branch_key")
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


async def _pk_evaluate_pressure(
    db: AsyncSession,
    value: float,
    subtype: str,           # "suction" | "discharge"
    refrigerant: str,       # "R-32" | "R-410A" | "R-22" | "not_sure"
    ambient_c: int = 40,    # default mid-summer Pakistan
) -> str:
    """
    Look up pak_operating_targets and return "low" | "ok" | "high".
    "not_sure" defaults to R-410A.
    Falls back to US thresholds (60/110 PSI suction) if table lookup fails.
    """
    ref = refrigerant if refrigerant != "not_sure" else "R-410A"

    # Find the nearest ambient row (floor to nearest available step)
    try:
        row = await db.execute(
            text(
                "SELECT suction_min_psi, suction_max_psi, discharge_min_psi, discharge_max_psi "
                "FROM pak_operating_targets "
                "WHERE refrigerant = :ref AND ambient_c <= :amb "
                "ORDER BY ambient_c DESC LIMIT 1"
            ),
            {"ref": ref, "amb": ambient_c},
        )
        targets = row.fetchone()
    except Exception as e:
        logger.warning("[diagnostic] pak_operating_targets lookup failed: %s", e)
        targets = None

    if not targets:
        # Fallback: US thresholds
        lo, hi = (60, 110) if subtype == "suction" else (200, 400)
    elif subtype == "suction":
        lo, hi = float(targets.suction_min_psi), float(targets.suction_max_psi)
    else:
        lo, hi = float(targets.discharge_min_psi), float(targets.discharge_max_psi)

    if value < lo:
        return "low"
    if value > hi:
        return "high"
    return "ok"


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
        # BUG-009 fix: generate estimate before marking session done
        # BUG-010 fix: wrap in try/except so step-8 photo never 503s
        if branch.get("generate_estimate") and assessment_id and company_id:
            try:
                await _generate_service_estimate(db, assessment_id, company_id)
            except Exception as exc:
                logger.error(
                    "[diagnostic] service estimate creation failed (non-fatal): %s", exc
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
    tables: MarketTables = Depends(get_tables),
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
    tables: MarketTables = Depends(get_tables),
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
        if isinstance(body.answer, dict) and body.answer.get("branch_key") == "skipped":
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

    # ── PK pressure override: server-side evaluation against pak_operating_targets ─
    if (
        tables.market == "PK"
        and q_row.input_type == "reading"
        and isinstance(q_row.reading_spec, dict)
        and q_row.reading_spec.get("type") == "psi"
        and isinstance(body.answer, dict)
        and body.answer.get("value") is not None
    ):
        subtype = q_row.reading_spec.get("subtype", "suction")
        raw_psi = float(body.answer["value"])
        refrigerant = body.refrigerant_type or "not_sure"
        ambient = body.ambient_c or 40
        branch_key = await _pk_evaluate_pressure(db, raw_psi, subtype, refrigerant, ambient)
        logger.info(
            "[diagnostic] PK pressure override: %.1f PSI %s → %s (ref=%s, amb=%d°C)",
            raw_psi, subtype, branch_key, refrigerant, ambient,
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
            "FROM pak_operating_targets "
            "WHERE refrigerant = :ref AND ambient_c <= :amb "
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
    tables: MarketTables = Depends(get_tables),
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
    session_id: str =