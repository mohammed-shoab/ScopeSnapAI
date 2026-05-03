"""
WS-A3 Phase 3 — Job Confirmation API (training loop)
POST /api/job-confirmation         — tech submits post-job feedback
GET  /api/job-confirmation/stats   — diagnosis accuracy stats per company
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.database import get_db
from api.auth import get_current_user, AuthContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/job-confirmation", tags=["phase3-training"])


# ── Request / Response ─────────────────────────────────────────────────────────

class JobConfirmationCreate(BaseModel):
    assessment_id: str
    diagnosed_card_id: int = Field(..., ge=1, le=19)
    actual_card_id: int = Field(..., ge=1, le=19)
    complaint_resolved: bool
    final_invoice_amount: Optional[float] = None
    tech_notes: Optional[str] = None
    consent_given: bool = True


class JobConfirmationResponse(BaseModel):
    ok: bool
    training_signal: str   # 'positive' | 'negative'
    diagnosis_correct: bool


class CardStats(BaseModel):
    card_id: int
    diagnosed_n: int
    correct_n: int
    accuracy_pct: float


class JobConfirmationStats(BaseModel):
    total_jobs: int
    confirmed_jobs: int
    diagnosis_accuracy_pct: float
    resolution_rate_pct: float
    per_card: list[CardStats]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("", response_model=JobConfirmationResponse, status_code=status.HTTP_201_CREATED)
async def create_job_confirmation(
    body: JobConfirmationCreate,
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    """Submit post-job training feedback (30-second 3-question card)."""
    # Verify assessment ownership
    row = await db.execute(
        text("SELECT company_id FROM assessments WHERE id = :id"),
        {"id": body.assessment_id},
    )
    assessment = row.fetchone()
    if not assessment or str(assessment.company_id) != str(auth.company_id):
        raise HTTPException(status_code=404, detail="assessment_not_found")

    diagnosis_correct = body.diagnosed_card_id == body.actual_card_id

    await db.execute(
        text("""
            INSERT INTO job_confirmations
              (assessment_id, company_id, technician_id, diagnosed_card_id,
               actual_card_id, diagnosis_correct, complaint_resolved,
               final_invoice_amount, tech_notes, consent_given)
            VALUES
              (:assessment_id, :company_id, :technician_id, :diagnosed_card_id,
               :actual_card_id, :diagnosis_correct, :complaint_resolved,
               :final_invoice_amount, :tech_notes, :consent_given)
            ON CONFLICT (assessment_id) DO UPDATE SET
              actual_card_id = EXCLUDED.actual_card_id,
              diagnosis_correct = EXCLUDED.diagnosis_correct,
              complaint_resolved = EXCLUDED.complaint_resolved,
              final_invoice_amount = EXCLUDED.final_invoice_amount,
              tech_notes = EXCLUDED.tech_notes,
              confirmed_at = now()
        """),
        {
            "assessment_id": body.assessment_id,
            "company_id": auth.company_id,
            "technician_id": auth.user_id,
            "diagnosed_card_id": body.diagnosed_card_id,
            "actual_card_id": body.actual_card_id,
            "diagnosis_correct": diagnosis_correct,
            "complaint_resolved": body.complaint_resolved,
            "final_invoice_amount": body.final_invoice_amount,
            "tech_notes": body.tech_notes,
            "consent_given": body.consent_given,
        },
    )
    await db.commit()

    return JobConfirmationResponse(
        ok=True,
        training_signal="positive" if diagnosis_correct else "negative",
        diagnosis_correct=diagnosis_correct,
    )


@router.get("/stats", response_model=JobConfirmationStats)
async def get_job_confirmation_stats(
    since: Optional[str] = Query(None, description="ISO8601 datetime — filter confirmations after this date"),
    db: AsyncSession = Depends(get_db),
    auth: AuthContext = Depends(get_current_user),
):
    """Diagnosis accuracy stats for this company."""
    since_clause = "AND confirmed_at > :since::timestamptz" if since else ""

    # Overall stats
    overall = await db.execute(
        text(f"""
            SELECT
                COUNT(*) AS confirmed_jobs,
                SUM(CASE WHEN diagnosis_correct THEN 1 ELSE 0 END) AS correct_count,
                SUM(CASE WHEN complaint_resolved THEN 1 ELSE 0 END) AS resolved_count
            FROM job_confirmations
            WHERE company_id = :company_id {since_clause}
        """),
        {"company_id": auth.company_id, "since": since},
    )
    ov = overall.fetchone()
    confirmed = ov.confirmed_jobs or 0
    correct = ov.correct_count or 0
    resolved = ov.resolved_count or 0

    # Total assessments (all, not just confirmed)
    total_row = await db.execute(
        text("SELECT COUNT(*) AS n FROM assessments WHERE company_id = :company_id"),
        {"company_id": auth.company_id},
    )
    total = total_row.fetchone().n or 0

    # Per-card breakdown
    per_card_rows = await db.execute(
        text(f"""
            SELECT
                diagnosed_card_id AS card_id,
                COUNT(*) AS diagnosed_n,
                SUM(CASE WHEN diagnosis_correct THEN 1 ELSE 0 END) AS correct_n
            FROM job_confirmations
            WHERE company_id = :company_id {since_clause}
            GROUP BY diagnosed_card_id
            ORDER BY diagnosed_card_id
        """),
        {"company_id": auth.company_id, "since": since},
    )

    per_card = [
        CardStats(
            card_id=r.card_id,
            diagnosed_n=r.diagnosed_n,
            correct_n=r.correct_n or 0,
            accuracy_pct=round((r.correct_n or 0) / r.diagnosed_n * 100, 1),
        )
        for r in per_card_rows.fetchall()
    ]

    return JobConfirmationStats(
        total_jobs=total,
        confirmed_jobs=confirmed,
        diagnosis_accuracy_pct=round(correct / confirmed * 100, 1) if confirmed else 0.0,
        resolution_rate_pct=round(resolved / confirmed * 100, 1) if confirmed else 0.0,
        per_card=per_card,
    )
