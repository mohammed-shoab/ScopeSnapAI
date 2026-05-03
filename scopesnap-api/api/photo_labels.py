"""
WS-A3 Phase 3 — Photo Label API
POST /api/photo-labels/       — save a labeled photo from the diagnostic flow
GET  /api/photo-labels/{assessment_id} — list all labeled photos for an assessment
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.database import get_db
from api.auth import get_current_user, AuthContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/photo-labels", tags=["phase3-diagnostic"])


# ── Request / Response ─────────────────────────────────────────────────────────

class PhotoLabelCreate(BaseModel):
    assessment_id: str = Field(..., description="Assessment UUID")
    session_id: Optional[str] = Field(None, description="Diagnostic session UUID")
    step_id: Optional[str] = Field(None, description="Question step_id that triggered this photo")
    photo_url: str = Field(..., description="R2 storage URL for the uploaded photo")
    photo_type: str = Field(..., description="'diagnostic' | 'evidence'")
    slot_name: Optional[str] = Field(None, description="e.g. 'capacitor_can', 'contactor_face'")
    card_id: Optional[int] = Field(None, description="Fault card resolved (if known at upload time)")
    ai_prompt_used: Optional[str] = Field(None)
    ai_grade: Optional[str] = Field(None, description="Grade returned by Gemini / YOLO")
    ai_confidence: Optional[float] = Field(None, ge=0, le=1)
    is_for_pdf: bool = Field(True)


class PhotoLabelResponse(BaseModel):
    id: str
    assessment_id: str
    session_id: Optional[str]
    step_id: Optional[str]
    photo_url: str
    photo_type: str
    slot_name: Optional[str]
    card_id: Optional[int]
    ai_grade: Optional[str]
    ai_confidence: Optional[float]
    is_for_pdf: bool
    created_at: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("", response_model=PhotoLabelResponse, status_code=status.HTTP_201_CREATED)
async def create_photo_label(
    body: PhotoLabelCreate,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    """Save a labeled diagnostic or evidence photo from the Phase 3 diagnostic flow."""
    # Verify assessment belongs to this company
    row = await db.execute(
        text("SELECT company_id FROM assessments WHERE id = :id"),
        {"id": body.assessment_id},
    )
    assessment = row.fetchone()
    if not assessment:
        raise HTTPException(status_code=404, detail="assessment_not_found")
    if str(assessment.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="assessment_not_found")

    result = await db.execute(
        text("""
            INSERT INTO photo_labels
              (assessment_id, session_id, step_id, photo_url, photo_type,
               slot_name, card_id, ai_prompt_used, ai_grade, ai_confidence, is_for_pdf)
            VALUES
              (:assessment_id, :session_id, :step_id, :photo_url, :photo_type,
               :slot_name, :card_id, :ai_prompt_used, :ai_grade, :ai_confidence, :is_for_pdf)
            RETURNING id, assessment_id, session_id, step_id, photo_url, photo_type,
                      slot_name, card_id, ai_grade, ai_confidence, is_for_pdf, created_at
        """),
        {
            "assessment_id": body.assessment_id,
            "session_id": body.session_id,
            "step_id": body.step_id,
            "photo_url": body.photo_url,
            "photo_type": body.photo_type,
            "slot_name": body.slot_name,
            "card_id": body.card_id,
            "ai_prompt_used": body.ai_prompt_used,
            "ai_grade": body.ai_grade,
            "ai_confidence": body.ai_confidence,
            "is_for_pdf": body.is_for_pdf,
        },
    )
    await db.commit()
    rec = result.fetchone()

    return PhotoLabelResponse(
        id=str(rec.id),
        assessment_id=str(rec.assessment_id),
        session_id=str(rec.session_id) if rec.session_id else None,
        step_id=rec.step_id,
        photo_url=rec.photo_url,
        photo_type=rec.photo_type,
        slot_name=rec.slot_name,
        card_id=rec.card_id,
        ai_grade=rec.ai_grade,
        ai_confidence=float(rec.ai_confidence) if rec.ai_confidence else None,
        is_for_pdf=rec.is_for_pdf,
        created_at=rec.created_at.isoformat() if rec.created_at else "",
    )


@router.get("/{assessment_id}", response_model=list[PhotoLabelResponse])
async def list_photo_labels(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    """List all labeled photos for an assessment (ordered by creation time)."""
    # Verify company isolation
    row = await db.execute(
        text("SELECT company_id FROM assessments WHERE id = :id"),
        {"id": assessment_id},
    )
    assessment = row.fetchone()
    if not assessment or str(assessment.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="assessment_not_found")

    result = await db.execute(
        text("""
            SELECT id, assessment_id, session_id, step_id, photo_url, photo_type,
                   slot_name, card_id, ai_grade, ai_confidence, is_for_pdf, created_at
            FROM photo_labels
            WHERE assessment_id = :assessment_id
            ORDER BY created_at ASC
        """),
        {"assessment_id": assessment_id},
    )
    rows = result.fetchall()
    return [
        PhotoLabelResponse(
            id=str(r.id),
            assessment_id=str(r.assessment_id),
            session_id=str(r.session_id) if r.session_id else None,
            step_id=r.step_id,
            photo_url=r.photo_url,
            photo_type=r.photo_type,
            slot_name=r.slot_name,
            card_id=r.card_id,
            ai_grade=r.ai_grade,
            ai_confidence=float(r.ai_confidence) if r.ai_confidence else None,
            is_for_pdf=r.is_for_pdf,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in rows
    ]
