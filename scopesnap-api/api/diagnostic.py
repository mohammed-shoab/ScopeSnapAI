"""
WS-A3 â Phase 3 Diagnostic Engine

POST /api/diagnostic/session              â start a new session
GET  /api/diagnostic/session/{session_id} â resume (get current step)
POST /api/diagnostic/session/{session_id}/answer â submit answer to current step

Bug fixes in this implementation
---------------------------------
BUG-003  : _compute_branch_key reads pre-computed branch_key from frontend
           (avoids str(dict) coercion for reading/photo answer dicts)
BUG-003b : _get_fault_card_name uses  SELECT card_name AS name  so .name works
BUG-004  : not_heating auto Q1 â null-safe read of ocr_nameplate.system_type;
           defaults to gas_furnace when field is absent
BUG-005  : error_code call_error_code_lookup â null-safe read of
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
from db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])

# ââ Pydantic schemas âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


class StartSessionRequest(BaseModel):
    assessment_id: str
    complaint_type: str


class AnswerRequest(BaseModel):
    answer: Any


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


# ââ DB helpers âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

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


async def _get_fault_card_name(db: AsyncSession, card_id: int) -> Optional[str]:
    """BUG-003b: alias column so .name resolves correctly."""
    result = await db.execute(
        text("SELECT card_name AS name FROM fault_cards WHERE card_id = :cid LIMIT 1"),
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


# ââ Question row â response schema ââââââââââââââââââââââââââââââââââââââââââââ


def _row_to_question_out(row: Any) -> QuestionOut:
    """Convert a diagnostic_questions DB row to the API response schema."""
    return QuestionOut(
        step_id=row.step_id,
        question_text=row.question_text,
        hint_text=row.hint_text,
        input_type=row.input_type,
        # options_jsonb serves dual purpose:
        #   visual_select â [{value, label, icon}]
        #   multi         â [{kind, spec}]  (frontend casts)
        options=row.options_jsonb,
        reading_spec=row.reading_spec,
        photo_spec=row.photo_spec,
        is_terminal=bool(row.is_terminal),
    )


# ââ Branch-key extraction ââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def _compute_branch_key(answer: Any, input_type: str) -> str:
    """
    BUG-003: extract the routing branch_key from the frontend answer.

    - yesno / visual_select  â answer is a plain string
    - reading / photo / multi â answer is a dict; prefer explicit branch_key field
    - multi (bundled)        â answer has reading_0, reading_1, etc.; use reading_0.branch_key
    - fallback               â str(answer)
    """
    if isinstance(answer, str):
        return answer.strip().lower()

    if isinstance(answer, dict):
        # Top-level branch_key (simple reading / photo answers)
        bk = answer.get("branch_key")
        if bk:
            return str(bk).strip().lower()

        # BUG-006: Multi-input bundled answer â readings keyed as reading_0, reading_1 â¦
        # The first readingâs branch_key is the primary routing key.
        r0 = answer.get("reading_0")
        if isinstance(r0, dict):
            bk = r0.get("branch_key")
            if bk:
                logger.info(
                    "[diagnostic] branch_key from reading_0: â%sâ", bk
                )
                return str(bk).strip().lower()

        # Legacy fallback for older clients that sent {value, unit}
        val = answer.get("value")
        if val is not None:
            return str(val).strip().lower()

    logger.warning("[diagnostic] branch_key fallback: answer=%r input_type=%s", answer, input_type)
    return str(answer).strip().lower()


# ââ Auto-question resolution â BUG-004 fix ââââââââââââââââââââââââââââââââââââ


def _resolve_auto_question(branch_logic: dict, ocr_nameplate: Optional[dict]) -> str:
    """
    Resolve an 'auto' question type (e.g. not_heating Q1 system_type detection).

    BUG-004 fix: safely handles None / missing ocr_nameplate values.
    When system_type is absent, defaults to 'gas_furnace' (most common Houston
    system type) so the session can continue rather than crash.
    """
    use_field: str = branch_logic.get("use_field", "")
    ocr = ocr_nameplate or {}

    # branch_logic stores field as "ocr_nameplate.system_type" â strip prefix
    field_name = use_field.split(".", 1)[-1] if "." in use_field else use_field
    value = ocr.get(field_name)

    if not value:
        # BUG-004: null safety â fall back to gas_furnace
        logger.info(
            "[diagnostic] auto Q: ocr field '%s' is None â defaulting to gas_furnace",
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
        "[diagnostic] auto Q: no branch for '%s', no 'any' wildcard â defaulting to gas_furnace",
        value,
    )
    return "gas_furnace"


# ââ Error-code lookup â BUG-005 fix âââââââââââââââââââââââââââââââââââââââââââ


async def _call_error_code_lookup(
    db: AsyncSession,
    action_config: dict,
    ocr_nameplate: Optional[dict],
    photo_ai_output: Optional[str],
) -> str:
    """
    Resolve the error_code Q1 action: lookup brand+code in error_codes table,
    return a branch_key from the 'after' map.

    BUG-005 fix: when ocr_nameplate.brand is absent, skip the DB lookup and
    route directly to 'nuisance_or_unknown' (â q4-reset) instead of crashing.
    """
    after_map: dict = action_config.get("after", {})

    ocr = ocr_nameplate or {}
    brand = ocr.get("brand")

    if not brand:
        # BUG-005: no brand data â skip lookup, use generic reset path
        logger.info("[diagnostic] error_code lookup: no brand in OCR â nuisance_or_unknown")
        return "nuisance_or_unknown"

    if not photo_ai_output:
        return "nuisance_or_unknown"

    brand_clean = str(brand).strip().lower()
    code_clean = str(photo_ai_output).strip()

    try:
        result = await db.execute(
            text("""
                SELECT ec.subsystem, ec.meaning, ec.severity
                FROM error_codes ec
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

    # Keyword-based subsystem â branch_key mapping
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


# ââ Branch following âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def _follow_branch(branch_logic: dict, branch_key: str) -> Optional[dict]:
    """
    Look up branch_key in branch_logic.
    Falls back to 'any' wildcard if the exact key is absent.

    BUG-007: Smart "ok" fallback â frontend ReadingInput always emits branchKey "ok"
    for non-ignitor reading types. When "ok" is not a key in branch_logic we try:
      1. Any key that CONTAINS "ok" (e.g. "elevated_or_ok", "voltage_drop_ok")
      2. All branches converge to the same next_step_id â pick first key
      3. "any" wildcard
    Returns None if nothing matches (caller should escalate).
    """
    branch = branch_logic.get(branch_key)
    if branch is not None:
        return branch

    # BUG-007 smart fallback for "ok" from ReadingInput.tsx
    if branch_key == "ok" and branch_logic:
        # 1. Key whose name contains "ok"
        ok_key = next((k for k in branch_logic if "ok" in k.lower()), None)
        if ok_key:
            logger.info(
                "[diagnostic] BUG-007 ok-fallback: mapped 'ok' â '%s'", ok_key
            )
            return branch_logic[ok_key]

        # 2. All branches point to the same next_step_id â safe to pick any
        next_steps = {
            v.get("next_step_id")
            for v in branch_logic.values()
            if isinstance(v, dict)
        }
        if len(next_steps) == 1 and None not in next_steps:
            first_key = next(iter(branch_logic))
            logger.info(
                "[diagnostic] BUG-007 ok-fallback: all branches converge to '%s', "
                "picking first key '%s'",
                next(iter(next_steps)),
                first_key,
            )
            return branch_logic[first_key]

    # 'any' wildcard
    branch = branch_logic.get("any")
    return branch


# ââ Branch result â AnswerResponse ââââââââââââââââââââââââââââââââââââââââââââ


async def _process_branch(
    db: AsyncSession,
    session_id: str,
    complaint_type: str,
    branch: dict,
    assessment_id: str = "",
    company_id: str = "",
) -> AnswerResponse:
    """
    Translate a branch dict into an AnswerResponse.

    Handles all branch action types:
      service_complete, escalate, phase_2_gate, resolve_card, next_step_id,
      jump_to_complaint
    """
    finding = branch.get("finding")

    # ââ service_complete âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    if branch.get("service_complete"):
        # BUG-009 fix: generate estimate before marking session done
        if branch.get("generate_estimate") and assessment_id and company_id:
            await _generate_service_estimate(db, assessment_id, company_id)
        await _complete_service_session(db, session_id)
        return AnswerResponse(service_step_complete=True, finding=finding)

    # ââ escalate âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    if branch.get("escalate"):
        reason = branch.get("reason", "Manual diagnosis required.")
        await _escalate_session(db, session_id)
        return AnswerResponse(escalated=True, escalation_reason=reason, finding=finding)

    # ââ phase_2_gate âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    if branch.get("phase_2_gate"):
        continuation = branch.get("after", {})
        # BUG-020: extract first resolve_card so frontend can call
        # /estimates/fault-card without card_id=null -> 422
        primary_card_id = None
        for val in continuation.values():
            if isinstance(val, dict) and "resolve_card" in val:
                primary_card_id = val["resolve_card"]
                break
        return AnswerResponse(
            phase_2_gate=True,
            card_id=primary_card_id,
            gate_continuation={"session_id": session_id, **continuation},
        )

    # ââ resolve_card âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    if "resolve_card" in branch:
        card_id: int = branch["resolve_card"]
        card_name = await _get_fault_card_name(db, card_id)
        photo_slots: List[dict] = branch.get("photo_slots") or []
        await _resolve_session(db, session_id, card_id)
        return AnswerResponse(
            resolved=True,
            card_id=card_id,
            card_name=card_name or f"Card #{card_id}",
            photo_slots=photo_slots,
            finding=finding,
        )

    # ââ next_step_id âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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
        return AnswerResponse(next_step=_row_to_question_out(next_row), finding=finding)

    # ââ jump_to_complaint (error_code q4-reset "no" branch) âââââââââââââââââââ
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
        return AnswerResponse(next_step=_row_to_question_out(first_row))

    # ââ unrecognised branch structure ââââââââââââââââââââââââââââââââââââââââââ
    logger.error("[diagnostic] branch has no recognised action key: %s", branch)
    await _escalate_session(db, session_id)
    return AnswerResponse(
        escalated=True,
        escalation_reason="Internal: branch has no recognised action.",
    )


# ââ Endpoints ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


@router.post("/session", response_model=StartSessionResponse)
async def start_session(
    body: StartSessionRequest,
    auth: AuthContext = Depends(get_current_user),
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

    # ââ 'auto' type Q1 (e.g. not_heating system_type) ââââââââââââââââââââââââ
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
                    current_step=_row_to_question_out(next_row),
                )

        # phase_2_gate / escalate from Q1 auto â rare, surface to caller
        return StartSessionResponse(
            session_id=session_id,
            current_step=_row_to_question_out(first_row),
        )

    # ââ Normal (non-auto) first question âââââââââââââââââââââââââââââââââââââ
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
        current_step=_row_to_question_out(first_row),
    )


@router.post("/session/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: str,
    body: AnswerRequest,
    auth: AuthContext = Depends(get_current_user),
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

    # ââ Special: error_code photo Q1 with 'extract_then_lookup' action ââââââââ
    # The entire branch_logic for this step is wrapped under one key:
    # {"extract_then_lookup": {"action": "call_error_code_lookup", "brand_from": ..., "after": {...}}}
    if "extract_then_lookup" in branch_logic:
        action_config = branch_logic["extract_then_lookup"]
        assessment = await _load_assessment(db, session.assessment_id, auth.company_id)
        ocr = assessment.ocr_nameplate if assessment else None

        # Extract AI-read code from answer (may be None when branch_key injection is used)
        photo_ai_output: Optional[str] = None
        if isinstance(body.answer, dict):
            photo_ai_output = body.answer.get("ai_output") or body.answer.get("code")

        # BUG-005 fix embedded in _call_error_code_lookup
        resolved_bk = await _call_error_code_lookup(db, action_config, ocr, photo_ai_output)
        after_map: dict = action_config.get("after", {})
        branch = after_map.get(resolved_bk) or after_map.get("nuisance_or_unknown")

        if not branch:
            await _escalate_session(db, session_id)
            return AnswerResponse(
                escalated=True,
                escalation_reason="Error code lookup produced no matching branch.",
            )
        return await _process_branch(db, session_id, session.complaint_type, branch)

    # ââ Compute branch_key (BUG-003 fix) âââââââââââââââââââââââââââââââââââââ
    branch_key = _compute_branch_key(body.answer, q_row.input_type)

    # ââ Follow branch âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
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
    )


@router.get("/session/{session_id}", response_model=StartSessionResponse)
async def get_session(
    session_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return current session state â used for page-reload resume."""
    session = await _load_session(db, session_id, auth.company_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    q_row = await _load_question(db, session.complaint_type, session.current_step_id)
    if not q_row:
        raise HTTPException(status_code=500, detail="Current step not found in DB.")

    return StartSessionResponse(
        session_id=session_id,
        current_step=_row_to_question_out(q_row),
    )
