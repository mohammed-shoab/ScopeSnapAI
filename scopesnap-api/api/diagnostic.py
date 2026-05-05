"""
WS-A3 Phase 3 — Diagnostic Flow API
All routes prefixed /api/diagnostic

Endpoints:
  POST   /api/diagnostic/session                         — start a new diagnostic session
  GET    /api/diagnostic/session/{session_id}            — get current state
  POST   /api/diagnostic/session/{session_id}/answer     — submit an answer
  GET    /api/diagnostic/questions/{complaint_type}      — full question list (debug/training)
  GET    /api/diagnostic/complaints                      — complaint types + first question preview
  PATCH  /api/diagnostic/session/{session_id}/cancel     — cancel / restart session

WS-D3/E3/F3 fixes (2026-05-04):
  - _compute_branch_key: multi inputs now extract reading_N.branch_key from answer dict
  - _compute_branch_key: photo inputs extract branch_key from answer if pre-computed
  - _grade_single_photo(): fetches photo URL + calls Gemini, returns AI grade
  - _grade_multi_photos(): for photo-only multi steps, grades each photo and
    uses photo_branch_map in branch_logic_jsonb to derive compound branch key
  - submit_answer: calls grading helpers when branch_key is still None after
    _compute_branch_key (photo/multi-photo-only cases)
"""

import json
import logging
from typing import Optional, Any
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.database import get_db
from api.auth import get_current_user, AuthContext
from services.diagnostic_engine import evaluate_reading, evaluate_branch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnostic", tags=["phase3-diagnostic"])


# ── Complaint type metadata ────────────────────────────────────────────────────

COMPLAINT_META = [
    {"complaint_type": "not_cooling",          "label": "Not Cooling",           "icon": "\U0001f975", "houston_pct": 38},
    {"complaint_type": "water_dripping",       "label": "Water Dripping",        "icon": "\U0001f4a7", "houston_pct": 25},
    {"complaint_type": "not_turning_on",       "label": "Not Turning On",        "icon": "❌",     "houston_pct": 12},
    {"complaint_type": "making_noise",         "label": "Making Noise",          "icon": "\U0001f50a", "houston_pct": 10},
    {"complaint_type": "high_electric_bill",   "label": "High Electric Bill",    "icon": "\U0001f4a1", "houston_pct": 8},
    {"complaint_type": "error_code",           "label": "Error Code",            "icon": "⚠️", "houston_pct": 7},
    {"complaint_type": "not_heating",          "label": "Not Heating",           "icon": "\U0001f976", "houston_pct": 5},
    {"complaint_type": "intermittent_shutdown","label": "Intermittent Shutdown", "icon": "⚡",     "houston_pct": 5},
    {"complaint_type": "service",              "label": "Regular Service",       "icon": "\U0001f527", "houston_pct": 15},
]


# ── Pydantic models ────────────────────────────────────────────────────────────

class QuestionOut(BaseModel):
    step_id: str
    question_text: str
    hint_text: Optional[str] = None
    input_type: str
    options: Optional[list] = None
    reading_spec: Optional[dict] = None
    photo_spec: Optional[dict] = None
    is_terminal: bool = False


class SessionStartRequest(BaseModel):
    assessment_id: str
    complaint_type: str


class SessionStartResponse(BaseModel):
    session_id: str
    current_step: Optional[QuestionOut] = None
    phase_2_gate: bool = False
    gate_continuation: Optional[dict] = None


class AnswerRequest(BaseModel):
    answer: Any = Field(..., description="Varies by input_type")


class AnswerResponse(BaseModel):
    resolved: bool = False
    card_id: Optional[int] = None
    card_name: Optional[str] = None
    photo_slots: Optional[list] = None
    next_step: Optional[QuestionOut] = None
    phase_2_gate: bool = False
    gate_continuation: Optional[dict] = None
    service_step_complete: bool = False
    finding: Optional[dict] = None
    escalated: bool = False
    escalation_reason: Optional[str] = None


class SessionState(BaseModel):
    session_id: str
    assessment_id: str
    complaint_type: str
    status: str
    current_step: Optional[QuestionOut]
    answers: dict
    resolution_path: list
    resolved_card_id: Optional[int] = None
    phase_used: Optional[str] = None


class CancelRequest(BaseModel):
    reason: str = "tech_cancelled"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _shape_question(row) -> QuestionOut:
    options = row.options_jsonb
    if isinstance(options, str):
        options = json.loads(options)
    reading_spec = row.reading_spec
    if isinstance(reading_spec, str):
        reading_spec = json.loads(reading_spec)
    photo_spec = row.photo_spec
    if isinstance(photo_spec, str):
        photo_spec = json.loads(photo_spec)
    return QuestionOut(
        step_id=row.step_id,
        question_text=row.question_text,
        hint_text=row.hint_text,
        input_type=row.input_type,
        options=options,
        reading_spec=reading_spec,
        photo_spec=photo_spec,
        is_terminal=bool(row.is_terminal) if hasattr(row, "is_terminal") else False,
    )


def _compute_branch_key(question_row, answer) -> Optional[str]:
    """
    Determine the branch key from an answer.
    - yesno / visual_select: raw answer string
    - reading (single): evaluate_reading via nameplate spec
    - photo: extract pre-computed branch_key from answer dict if present
    - multi: extract reading_N.branch_key from first reading sub-answer;
             fall back to None (photo grading handled in submit_answer)
    Returns None when photo grading is needed (async, done in submit_answer).
    """
    input_type = question_row.input_type
    reading_spec = question_row.reading_spec
    if isinstance(reading_spec, str):
        reading_spec = json.loads(reading_spec) if reading_spec else {}

    if input_type == "reading" and isinstance(answer, dict):
        value = answer.get("value")
        if value is None:
            return None
        rs = reading_spec or {}
        rtype = rs.get("type", "unknown")
        subtype = rs.get("subtype")
        tol = rs.get("tolerance_pct", 10)
        spec = answer.get("nameplate_spec")
        eval_result = evaluate_reading(rtype, float(value), spec, subtype, tol)
        return eval_result.get("branch_key")

    if input_type == "yesno":
        return str(answer).lower()

    if input_type == "visual_select":
        return str(answer)

    # ── multi: extract the first reading's branch_key ─────────────────────────
    if input_type == "multi" and isinstance(answer, dict):
        for key in sorted(answer.keys()):
            if key.startswith("reading_"):
                sub = answer[key]
                if isinstance(sub, dict):
                    # Frontend sends branch_key in reading sub-answer
                    bk = sub.get("branch_key")
                    if bk:
                        return bk
                    # Or compute it from value + reading_spec
                    value = sub.get("value")
                    if value is not None:
                        # Find matching reading spec from options_jsonb
                        options = question_row.options_jsonb
                        if isinstance(options, str):
                            options = json.loads(options) if options else []
                        reading_items = [
                            o for o in (options or [])
                            if isinstance(o, dict) and o.get("kind") == "reading"
                        ]
                        # Use first reading spec that matches by index
                        idx = int(key.split("_")[1])
                        if idx < len(reading_items):
                            rs = reading_items[idx].get("spec", {})
                            rtype = rs.get("type", "unknown")
                            subtype = rs.get("subtype")
                            tol = rs.get("tolerance_pct", 10)
                            spec = sub.get("nameplate_spec")
                            eval_result = evaluate_reading(rtype, float(value), spec, subtype, tol)
                            bk = eval_result.get("branch_key")
                            if bk and bk != "ok":
                                return bk
        # No reading or all readings ok — photo grading may apply
        return None

    # ── photo: extract pre-computed branch_key if frontend included it ─────────
    if input_type == "photo" and isinstance(answer, dict):
        bk = answer.get("branch_key")
        if bk:
            return bk
        # No pre-computed key — photo grading needed (async, done in submit_answer)
        return None

    return None


async def _grade_single_photo(photo_url: str, ai_prompt: str) -> Optional[str]:
    """
    Fetch photo bytes from URL and call Gemini with the ai_prompt.
    Returns the grade string (first word of the class list that Gemini outputs)
    or None on any failure.
    """
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(photo_url)
            r.raise_for_status()
            image_bytes = r.content

        from services.vision import GeminiVisionService
        vision = GeminiVisionService()
        if not vision._initialized:
            logger.warning("[diagnostic] Gemini not initialized, skipping photo grade")
            return None

        structured_prompt = (
            f"{ai_prompt}\n\n"
            "Respond with JSON only: "
            "{\"grade\": \"<exact_class_from_the_list_above>\", \"confidence\": 0.0}"
        )
        result = await vision.analyze_equipment_photos(
            image_bytes_list=[image_bytes],
            prompt=structured_prompt,
        )
        grade = result.get("grade") or result.get("classification") or result.get("result")
        if grade:
            return str(grade).lower().strip()
    except Exception as e:
        logger.warning(f"[diagnostic] Photo grading failed (non-fatal): {e}")
    return None


async def _grade_multi_photos(question_row, answer: dict) -> Optional[str]:
    """
    For multi-input questions with diagnostic photos and NO readings,
    grade each photo and use photo_branch_map from branch_logic_jsonb
    to derive the compound branch key.

    photo_branch_map structure (in branch_logic_jsonb):
      {
        "photo_branch_map": {
          "<ai_grade>": "<branch_key>",
          "_default": "<fallback_branch_key>"
        },
        "<branch_key>": { ... routing ... },
        ...
      }
    """
    branch_logic = question_row.branch_logic_jsonb
    if isinstance(branch_logic, str):
        branch_logic = json.loads(branch_logic) if branch_logic else {}

    photo_branch_map = branch_logic.get("photo_branch_map")
    if not photo_branch_map:
        return None

    # Get photo specs from options_jsonb
    options = question_row.options_jsonb
    if isinstance(options, str):
        options = json.loads(options) if options else []

    photo_items = [o for o in (options or []) if isinstance(o, dict) and o.get("kind") == "photo"]

    for item in photo_items:
        spec = item.get("spec", {})
        slot_name = spec.get("slot_name", "")
        ai_prompt = spec.get("ai_prompt")
        if not ai_prompt:
            continue

        photo_data = answer.get(slot_name, {})
        if not isinstance(photo_data, dict):
            continue
        photo_url = photo_data.get("photo_url")
        if not photo_url:
            continue

        grade = await _grade_single_photo(photo_url, ai_prompt)
        if grade and grade in photo_branch_map:
            mapped = photo_branch_map[grade]
            if mapped != "_default":
                return mapped

    # No photo matched a non-default key — use _default
    return photo_branch_map.get("_default")


async def _get_question(db, complaint_type: str, step_id: str):
    result = await db.execute(
        text("""
            SELECT step_id, step_order, question_text, hint_text, input_type,
                   options_jsonb, reading_spec, photo_spec, branch_logic_jsonb,
                   data_collect_jsonb, is_terminal
            FROM diagnostic_questions
            WHERE complaint_type = :ct AND step_id = :sid
            LIMIT 1
        """),
        {"ct": complaint_type, "sid": step_id},
    )
    return result.fetchone()


async def _get_first_question(db, complaint_type: str):
    result = await db.execute(
        text("""
            SELECT step_id, step_order, question_text, hint_text, input_type,
                   options_jsonb, reading_spec, photo_spec, branch_logic_jsonb,
                   data_collect_jsonb, is_terminal
            FROM diagnostic_questions
            WHERE complaint_type = :ct
            ORDER BY step_order ASC
            LIMIT 1
        """),
        {"ct": complaint_type},
    )
    return result.fetchone()


async def _get_fault_card_name(db, card_id: int) -> str:
    row = await db.execute(
        text("SELECT name FROM fault_cards WHERE card_id = :id"),
        {"id": card_id},
    )
    r = row.fetchone()
    return r.name if r else f"Card #{card_id}"


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/complaints")
async def list_complaints(
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    result = []
    for meta in COMPLAINT_META:
        first_q = await _get_first_question(db, meta["complaint_type"])
        result.append({
            **meta,
            "first_question_text": first_q.question_text if first_q else None,
        })
    return result


@router.post("/session", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    body: SessionStartRequest,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    row = await db.execute(
        text("SELECT company_id, ocr_nameplate FROM assessments WHERE id = :id"),
        {"id": body.assessment_id},
    )
    assessment = row.fetchone()
    if not assessment:
        raise HTTPException(status_code=404, detail="assessment_not_found")
    if str(assessment.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="assessment_not_found")
    # ocr_nameplate is optional — Step Zero scan can be skipped
    first_q = await _get_first_question(db, body.complaint_type)
    if not first_q:
        raise HTTPException(status_code=422, detail=f"no_questions_for_{body.complaint_type}")

    ins = await db.execute(
        text("""
            INSERT INTO diagnostic_sessions
              (assessment_id, company_id, technician_id, complaint_type, current_step_id)
            VALUES (:assessment_id, :company_id, :technician_id, :complaint_type, :step_id)
            RETURNING id
        """),
        {
            "assessment_id": body.assessment_id,
            "company_id": auth.company_id,
            "technician_id": auth.user_id,
            "complaint_type": body.complaint_type,
            "step_id": first_q.step_id,
        },
    )
    await db.commit()
    session_id = str(ins.fetchone().id)

    # ── Auto-advance: handle input_type='auto' (not_heating q1 reads OCR system_type) ─
    if first_q.input_type == "auto":
        ocr = assessment.ocr_nameplate
        if isinstance(ocr, str):
            try:
                import json as _json
                ocr = _json.loads(ocr)
            except Exception:
                ocr = {}
        auto_value = (ocr or {}).get("system_type", "unknown")

        branch_logic_auto = first_q.branch_logic_jsonb
        if isinstance(branch_logic_auto, str):
            branch_logic_auto = json.loads(branch_logic_auto) if branch_logic_auto else {}

        auto_q_dict = {
            "input_type": "auto",
            "reading_spec": None,
            "branch_logic_jsonb": branch_logic_auto,
        }
        auto_routing = evaluate_branch(auto_q_dict, auto_value, auto_value)

        # Persist the auto-answered first step
        await db.execute(
            text("""
                UPDATE diagnostic_sessions
                SET answers_jsonb = jsonb_set(
                        COALESCE(answers_jsonb, '{}'::jsonb),
                        :path, CAST(:val AS jsonb)
                    )
                WHERE id = :id
            """),
            {"path": [first_q.step_id], "val": json.dumps(auto_value), "id": session_id},
        )

        if auto_routing["kind"] == "next_step":
            next_q = await _get_question(db, body.complaint_type, auto_routing["next_step_id"])
            if next_q:
                await db.execute(
                    text("UPDATE diagnostic_sessions SET current_step_id = :step_id WHERE id = :id"),
                    {"step_id": auto_routing["next_step_id"], "id": session_id},
                )
                await db.commit()
                return SessionStartResponse(
                    session_id=session_id,
                    current_step=_shape_question(next_q),
                )

        elif auto_routing["kind"] == "phase_2_gate":
            await db.execute(
                text("UPDATE diagnostic_sessions SET status = 'phase_2_pending', current_step_id = NULL WHERE id = :id"),
                {"id": session_id},
            )
            await db.commit()
            return SessionStartResponse(
                session_id=session_id,
                current_step=None,
                phase_2_gate=True,
                gate_continuation=auto_routing.get("continuation", {}),
            )

        elif auto_routing["kind"] == "escalate":
            await db.execute(
                text("UPDATE diagnostic_sessions SET status = 'escalated' WHERE id = :id"),
                {"id": session_id},
            )
            await db.commit()
            return SessionStartResponse(
                session_id=session_id,
                current_step=None,
                gate_continuation={"reason": auto_routing.get("reason", "auto_escalated")},
            )

        await db.commit()
        # fallback: show the auto question itself (shouldn't normally reach here)

    return SessionStartResponse(
        session_id=session_id,
        current_step=_shape_question(first_q),
    )


@router.get("/session/{session_id}", response_model=SessionState)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    row = await db.execute(
        text("""
            SELECT id, assessment_id, company_id, complaint_type, current_step_id,
                   answers_jsonb, resolved_card_id, resolution_path, status, phase_used
            FROM diagnostic_sessions
            WHERE id = :id
        """),
        {"id": session_id},
    )
    session = row.fetchone()
    if not session or str(session.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="session_not_found")

    current_q = None
    if session.current_step_id and session.status == "active":
        q_row = await _get_question(db, session.complaint_type, session.current_step_id)
        if q_row:
            current_q = _shape_question(q_row)

    answers = session.answers_jsonb or {}
    if isinstance(answers, str):
        answers = json.loads(answers)
    resolution_path = session.resolution_path or []
    if isinstance(resolution_path, str):
        resolution_path = json.loads(resolution_path)

    return SessionState(
        session_id=str(session.id),
        assessment_id=str(session.assessment_id),
        complaint_type=session.complaint_type,
        status=session.status,
        current_step=current_q,
        answers=answers,
        resolution_path=resolution_path,
        resolved_card_id=session.resolved_card_id,
        phase_used=session.phase_used,
    )


@router.post("/session/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: str,
    body: AnswerRequest,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    # Load session
    row = await db.execute(
        text("""
            SELECT id, assessment_id, company_id, complaint_type, current_step_id,
                   answers_jsonb, resolution_path, status
            FROM diagnostic_sessions WHERE id = :id
        """),
        {"id": session_id},
    )
    session = row.fetchone()
    if not session or str(session.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="session_not_found")
    if session.status != "active":
        raise HTTPException(status_code=422, detail="session_not_active")

    q_row = await _get_question(db, session.complaint_type, session.current_step_id)
    if not q_row:
        raise HTTPException(status_code=422, detail="current_question_not_found")

    branch_logic = q_row.branch_logic_jsonb
    if isinstance(branch_logic, str):
        branch_logic = json.loads(branch_logic)

    question_dict = {
        "input_type": q_row.input_type,
        "reading_spec": q_row.reading_spec,
        "branch_logic_jsonb": branch_logic,
    }

    # Compute branch key (sync for yesno/visual_select/reading)
    branch_key = _compute_branch_key(q_row, body.answer)

    # ── Async photo grading when branch_key still None ─────────────────────────
    if branch_key is None and q_row.input_type == "photo":
        photo_spec = q_row.photo_spec
        if isinstance(photo_spec, str):
            photo_spec = json.loads(photo_spec) if photo_spec else {}
        ai_prompt = (photo_spec or {}).get("ai_prompt")
        photo_url = (body.answer or {}).get("photo_url") if isinstance(body.answer, dict) else None
        if ai_prompt and photo_url:
            branch_key = await _grade_single_photo(photo_url, ai_prompt)
            # Store AI grade back into answer for logging
            if branch_key and isinstance(body.answer, dict):
                body.answer["ai_grade"] = branch_key

    if branch_key is None and q_row.input_type == "multi":
        if isinstance(body.answer, dict):
            # Check if it's a photo-only multi (no readings, has diagnostic photos)
            has_reading = any(k.startswith("reading_") for k in body.answer)
            if not has_reading:
                branch_key = await _grade_multi_photos(q_row, body.answer)

    # ── Persist reading_inputs rows for reading/multi answers ─────────────────
    if q_row.input_type == "reading" and isinstance(body.answer, dict) and "value" in body.answer:
        reading_spec = q_row.reading_spec
        if isinstance(reading_spec, str):
            reading_spec = json.loads(reading_spec) if reading_spec else {}
        rs = reading_spec or {}
        rtype = rs.get("type", "unknown")
        subtype = rs.get("subtype")
        tol = rs.get("tolerance_pct", 10)
        val = float(body.answer["value"])
        nameplate_spec = body.answer.get("nameplate_spec")
        eval_result = evaluate_reading(rtype, val, nameplate_spec, subtype, tol)

        await db.execute(
            text("""
                INSERT INTO reading_inputs
                  (session_id, assessment_id, step_id, reading_type, reading_subtype,
                   actual_value, unit, nameplate_spec, tolerance_pct,
                   classification, passed, flag_message)
                VALUES
                  (:session_id, :assessment_id, :step_id, :rtype, :subtype,
                   :value, :unit, :spec, :tol,
                   :classification, :passed, :flag)
            """),
            {
                "session_id": session_id,
                "assessment_id": str(session.assessment_id),
                "step_id": q_row.step_id,
                "rtype": rtype,
                "subtype": subtype,
                "value": val,
                "unit": body.answer.get("unit", ""),
                "spec": nameplate_spec,
                "tol": tol,
                "classification": eval_result["classification"],
                "passed": eval_result["passed"],
                "flag": eval_result["flag_message"],
            },
        )

    # Update session answers + path
    answers = session.answers_jsonb or {}
    if isinstance(answers, str):
        answers = json.loads(answers)
    answers[q_row.step_id] = body.answer if not isinstance(body.answer, dict) else body.answer

    resolution_path = session.resolution_path or []
    if isinstance(resolution_path, str):
        resolution_path = json.loads(resolution_path)
    if q_row.step_id not in resolution_path:
        resolution_path.append(q_row.step_id)

    # ── extract_then_lookup: error-code AI output → DB lookup → route by fault_category ──
    if (branch_key is not None
            and isinstance(branch_logic, dict)
            and "extract_then_lookup" in branch_logic):
        etl = branch_logic["extract_then_lookup"]
        after_map = etl.get("after", {})

        # Fetch brand from assessment OCR nameplate
        asmt_row = await db.execute(
            text("SELECT ocr_nameplate FROM assessments WHERE id = :id"),
            {"id": str(session.assessment_id)},
        )
        asmt = asmt_row.fetchone()
        ocr_np = asmt.ocr_nameplate if asmt else {}
        if isinstance(ocr_np, str):
            try:
                ocr_np = json.loads(ocr_np)
            except Exception:
                ocr_np = {}
        brand = (ocr_np or {}).get("brand", "")
        code_text = branch_key  # AI grade = extracted code string

        # Annotate answer with extracted data
        if isinstance(body.answer, dict):
            body.answer["extracted_code"] = code_text

        # Look up error code in DB
        ec_row = await db.execute(
            text("""
                SELECT fault_category, decision_tree_card
                FROM error_codes
                WHERE brand ILIKE :brand AND code ILIKE :code
                LIMIT 1
            """),
            {"brand": brand, "code": code_text},
        )
        ec = ec_row.fetchone()

        if ec and isinstance(body.answer, dict):
            body.answer["fault_category"] = ec.fault_category

        # Persist answers + path now (early returns below won't hit the normal update)
        _answers_etl = {**answers, q_row.step_id: body.answer}
        await db.execute(
            text("""
                UPDATE diagnostic_sessions
                SET answers_jsonb = CAST(:a AS jsonb), resolution_path = CAST(:p AS jsonb)
                WHERE id = :id
            """),
            {"a": json.dumps(_answers_etl), "p": json.dumps(resolution_path), "id": session_id},
        )

        def _etl_next(rule_dict, step_id_key="next_step_id"):
            return rule_dict.get(step_id_key)

        if ec:
            # Direct card resolution via decision_tree_card
            if ec.decision_tree_card:
                _card_id = int(ec.decision_tree_card)
                _card_name = await _get_fault_card_name(db, _card_id)
                await db.execute(
                    text("""
                        UPDATE diagnostic_sessions
                        SET resolved_card_id = :cid, resolved_at = now(),
                            status = 'resolved', phase_used = 'p1'
                        WHERE id = :id
                    """),
                    {"cid": _card_id, "id": session_id},
                )
                await db.commit()
                return AnswerResponse(resolved=True, card_id=_card_id, card_name=_card_name)

            # Route by fault_category → after_map
            fc = ec.fault_category or "nuisance_or_unknown"
            after_rule = after_map.get(fc) or after_map.get("nuisance_or_unknown", {})

            if after_rule.get("phase_2_gate"):
                await db.execute(
                    text("UPDATE diagnostic_sessions SET status = 'phase_2_pending' WHERE id = :id"),
                    {"id": session_id},
                )
                await db.commit()
                return AnswerResponse(
                    resolved=False,
                    phase_2_gate=True,
                    gate_continuation=after_rule.get("after", {}),
                )

            if "resolve_card" in after_rule:
                _card_id = after_rule["resolve_card"]
                _card_name = await _get_fault_card_name(db, _card_id)
                await db.execute(
                    text("""
                        UPDATE diagnostic_sessions
                        SET resolved_card_id = :cid, resolved_at = now(),
                            status = 'resolved', phase_used = 'p1'
                        WHERE id = :id
                    """),
                    {"cid": _card_id, "id": session_id},
                )
                await db.commit()
                return AnswerResponse(
                    resolved=True, card_id=_card_id, card_name=_card_name,
                    photo_slots=after_rule.get("photo_slots", []),
                )

            if "next_step_id" in after_rule:
                _nxt_id = after_rule["next_step_id"]
                _nxt_q = await _get_question(db, session.complaint_type, _nxt_id)
                if _nxt_q:
                    await db.execute(
                        text("UPDATE diagnostic_sessions SET current_step_id = :sid WHERE id = :id"),
                        {"sid": _nxt_id, "id": session_id},
                    )
                    await db.commit()
                    return AnswerResponse(resolved=False, next_step=_shape_question(_nxt_q))

        else:
            # Code not found in DB → nuisance/unknown fallback
            fallback = after_map.get("nuisance_or_unknown", {})
            if "next_step_id" in fallback:
                _nxt_id = fallback["next_step_id"]
                _nxt_q = await _get_question(db, session.complaint_type, _nxt_id)
                if _nxt_q:
                    await db.execute(
                        text("UPDATE diagnostic_sessions SET current_step_id = :sid WHERE id = :id"),
                        {"sid": _nxt_id, "id": session_id},
                    )
                    await db.commit()
                    return AnswerResponse(resolved=False, next_step=_shape_question(_nxt_q))

        # Fall through: let normal routing handle it (branch_key already set)
        answers = _answers_etl  # use the updated answers dict for the normal path

    routing = evaluate_branch(question_dict, body.answer, branch_key)

    # ── Route ─────────────────────────────────────────────────────────────────

    if routing["kind"] == "phase_2_gate":
        await db.execute(
            text("""
                UPDATE diagnostic_sessions
                SET answers_jsonb = CAST(:answers AS jsonb),
                    resolution_path = CAST(:path AS jsonb),
                    status = 'phase_2_pending'
                WHERE id = :id
            """),
            {"answers": json.dumps(answers), "path": json.dumps(resolution_path), "id": session_id},
        )
        await db.commit()
        return AnswerResponse(
            resolved=False,
            phase_2_gate=True,
            gate_continuation=routing.get("continuation", {}),
        )

    if routing["kind"] == "resolve_card":
        card_id = routing["card_id"]
        card_name = await _get_fault_card_name(db, card_id)
        await db.execute(
            text("""
                UPDATE diagnostic_sessions
                SET answers_jsonb = CAST(:answers AS jsonb),
                    resolution_path = CAST(:path AS jsonb),
                    resolved_card_id = :card_id,
                    resolved_at = now(),
                    status = 'resolved',
                    phase_used = 'p1'
                WHERE id = :id
            """),
            {"answers": json.dumps(answers), "path": json.dumps(resolution_path),
             "card_id": card_id, "id": session_id},
        )
        await db.commit()
        return AnswerResponse(
            resolved=True,
            card_id=card_id,
            card_name=card_name,
            photo_slots=routing.get("photo_slots", []),
        )

    if routing["kind"] == "next_step":
        next_q = await _get_question(db, session.complaint_type, routing["next_step_id"])
        if not next_q:
            raise HTTPException(status_code=422, detail=f"next_question_not_found: {routing['next_step_id']}")
        await db.execute(
            text("""
                UPDATE diagnostic_sessions
                SET answers_jsonb = CAST(:answers AS jsonb),
                    resolution_path = CAST(:path AS jsonb),
                    current_step_id = :step_id
                WHERE id = :id
            """),
            {"answers": json.dumps(answers), "path": json.dumps(resolution_path),
             "step_id": routing["next_step_id"], "id": session_id},
        )
        await db.commit()
        return AnswerResponse(resolved=False, next_step=_shape_question(next_q))

    if routing["kind"] == "service_step":
        finding = routing.get("finding")
        next_step_id = routing.get("next_step_id")
        next_q = None
        if next_step_id:
            next_q_row = await _get_question(db, session.complaint_type, next_step_id)
            if next_q_row:
                next_q = _shape_question(next_q_row)

        if finding:
            await db.execute(
                text("""
                    UPDATE diagnostic_sessions
                    SET service_findings = service_findings || CAST(:finding AS jsonb),
                        answers_jsonb = CAST(:answers AS jsonb),
                        resolution_path = CAST(:path AS jsonb),
                        current_step_id = COALESCE(:next_step, current_step_id)
                    WHERE id = :id
                """),
                {"finding": json.dumps([{**finding, "step_id": q_row.step_id}]),
                 "answers": json.dumps(answers), "path": json.dumps(resolution_path),
                 "next_step": next_step_id, "id": session_id},
            )
        else:
            await db.execute(
                text("""
                    UPDATE diagnostic_sessions
                    SET answers_jsonb = CAST(:answers AS jsonb),
                        resolution_path = CAST(:path AS jsonb),
                        current_step_id = COALESCE(:next_step, current_step_id)
                    WHERE id = :id
                """),
                {"answers": json.dumps(answers), "path": json.dumps(resolution_path),
                 "next_step": next_step_id, "id": session_id},
            )
        await db.commit()

        if not next_step_id:
            await db.execute(
                text("UPDATE diagnostic_sessions SET status='resolved' WHERE id=:id"),
                {"id": session_id},
            )
            await db.commit()

        return AnswerResponse(
            resolved=not bool(next_step_id),
            service_step_complete=True,
            finding=finding,
            next_step=next_q,
        )

    # Escalate
    await db.execute(
        text("""
            UPDATE diagnostic_sessions
            SET answers_jsonb = CAST(:answers AS jsonb),
                resolution_path = CAST(:path AS jsonb),
                status = 'escalated',
                phase_used = 'tj'
            WHERE id = :id
        """),
        {"answers": json.dumps(answers), "path": json.dumps(resolution_path), "id": session_id},
    )
    await db.commit()
    return AnswerResponse(
        resolved=False,
        escalated=True,
        escalation_reason=routing.get("reason", "tech_judgment"),
    )


@router.get("/questions/{complaint_type}")
async def list_questions(
    complaint_type: str,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT step_id, step_order, question_text, hint_text, input_type,
                   options_jsonb, reading_spec, photo_spec, branch_logic_jsonb,
                   data_collect_jsonb, is_terminal
            FROM diagnostic_questions
            WHERE complaint_type = :ct
            ORDER BY step_order ASC
        """),
        {"ct": complaint_type},
    )
    rows = result.fetchall()
    return [
        {"step_id": r.step_id, "step_order": r.step_order, "question_text": r.question_text,
         "hint_text": r.hint_text, "input_type": r.input_type}
        for r in rows
    ]


@router.patch("/session/{session_id}/cancel")
async def cancel_session(
    session_id: str,
    body: CancelRequest,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    row = await db.execute(
        text("SELECT company_id FROM diagnostic_sessions WHERE id = :id"),
        {"id": session_id},
    )
    session = row.fetchone()
    if not session or str(session.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="session_not_found")

    await db.execute(
        text("""
            UPDATE diagnostic_sessions
            SET status = 'cancelled',
                answers_jsonb = answers_jsonb || CAST(:note AS jsonb)
            WHERE id = :id
        """),
        {"note": json.dumps({"_cancel_reason": body.reason}), "id": session_id},
    )
    await db.commit()
    return {"ok": True}


@router.patch("/session/{session_id}/undo")
async def undo_last_step(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    """
    WS-N3: Back button support.
    Pops the last step from resolution_path, restores current_step_id to it,
    and removes that answer from answers_jsonb.
    Returns the restored question so the frontend can re-render it.
    """
    row = await db.execute(
        text("""
            SELECT id, company_id, complaint_type, current_step_id,
                   resolution_path, answers_jsonb, status
            FROM diagnostic_sessions WHERE id = :id
        """),
        {"id": session_id},
    )
    session = row.fetchone()
    if not session or str(session.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="session_not_found")

    resolution_path = session.resolution_path or []
    if isinstance(resolution_path, str):
        resolution_path = json.loads(resolution_path)

    if not resolution_path:
        raise HTTPException(status_code=400, detail="no_history_to_undo")

    # The last entry in resolution_path is the step we just answered.
    # Pop it to go back to it.
    prev_step_id = resolution_path[-1]
    new_path = resolution_path[:-1]

    # Remove the answer for prev_step_id from answers_jsonb
    answers = session.answers_jsonb or {}
    if isinstance(answers, str):
        answers = json.loads(answers)
    answers.pop(prev_step_id, None)

    await db.execute(
        text("""
            UPDATE diagnostic_sessions
            SET current_step_id = :step_id,
                resolution_path = CAST(:path AS jsonb),
                answers_jsonb = CAST(:answers AS jsonb),
                status = 'active'
            WHERE id = :id
        """),
        {
            "step_id": prev_step_id,
            "path": json.dumps(new_path),
            "answers": json.dumps(answers),
            "id": session_id,
        },
    )
    await db.commit()

    # Return the restored question
    q_row = await _get_question(db, session.complaint_type, prev_step_id)
    if not q_row:
        raise HTTPException(status_code=404, detail="question_not_found")

    return {
        "restored_step_id": prev_step_id,
        "question": _shape_question(q_row),
        "history_depth": len(new_path),
    }
