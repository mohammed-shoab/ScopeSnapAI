"""
WS-F — Training Feedback Loop
POST /api/feedback/card  — record YES/NO tech feedback for AI model retraining

Acceptance criteria (WS-F M8):
  YES on Card #1 from tech X writes a row to card_feedback with assessment_id,
  photo IDs, and any readings entered.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db
from api.auth import get_current_user, AuthContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feedback", tags=["feedback"])

VALID_ANSWERS = {"yes", "no"}

class CardFeedbackRequest(BaseModel):
    card_id: int = Field(..., ge=1, le=19)
    answer: str = Field(..., pattern="^(yes|no)$")
    assessment_id: Optional[str] = None
    photo_ids: Optional[list[str]] = None
    readings: Optional[dict] = None

class CardFeedbackResponse(BaseModel):
    ok: bool
    feedback_id: str
    message: str

@router.post("/card", response_model=CardFeedbackResponse)
async def record_card_feedback(
    body: CardFeedbackRequest,
    request: Request,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-F — Record YES/NO feedback from tech on AI fault card diagnosis.
    Used to build training dataset for YOLO and XGBoost model retraining.

    YES = "AI diagnosis was correct, I fixed this fault"
    NO  = "AI was wrong, actual fault was different"
    """
    result = await db.execute(
        text("""
            INSERT INTO card_feedback
                (card_id, answer, assessment_id, company_id, technician_id,
                 photo_ids, readings)
            VALUES
                (:card_id, :answer, :assessment_id, :company_id, :tech_id,
                 :photo_ids, CAST(:readings AS jsonb))
            RETURNING id::text
        """),
        {
            "card_id": body.card_id,
            "answer": body.answer,
            "assessment_id": body.assessment_id,
            "company_id": str(auth.company_id),
            "tech_id": auth.user_id,
            "photo_ids": body.photo_ids,
            "readings": __import__("json").dumps(body.readings or {}),
        },
    )
    row = result.fetchone()
    await db.commit()

    feedback_id = row[0] if row else "unknown"
    logger.info(f"[Feedback] card={body.card_id} answer={body.answer} company={auth.company_id}")

    return CardFeedbackResponse(
        ok=True,
        feedback_id=feedback_id,
        message=f"Feedback recorded. Card #{body.card_id}: {body.answer.upper()}. Thank you!"
    )

@router.get("/card/{card_id}/stats")
async def get_feedback_stats(
    card_id: int,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get YES/NO stats for a card (for display in AI accuracy dashboard)."""
    row = await db.execute(
        text("""
            SELECT
                COUNT(*) FILTER (WHERE answer='yes') as yes_count,
                COUNT(*) FILTER (WHERE answer='no')  as no_count,
                COUNT(*) as total
            FROM card_feedback
            WHERE card_id = :card_id AND company_id = :company_id
        """),
        {"card_id": card_id, "company_id": str(auth.company_id)},
    )
    r = row.fetchone()
    total = r.total or 0
    accuracy_pct = round((r.yes_count / total) * 100) if total > 0 else None
    return {
        "card_id": card_id,
        "yes": r.yes_count,
        "no": r.no_count,
        "total": total,
        "accuracy_pct": accuracy_pct,
    }
