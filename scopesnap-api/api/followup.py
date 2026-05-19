"""
WS-I — Follow-up Emails + Lifecycle Reminders
POST /api/followup/schedule  — schedule follow-up emails after assessment
GET  /api/followup/opt-out/{token}  — one-click opt-out

The email service (Resend) is already wired in services/email.py.
This endpoint queues follow-ups at 24h, 48h, 7-day intervals.

Acceptance criteria (WS-I M11):
  - Test assessment fires 3 emails on schedule
  - Opt-out link disables future sends
"""
import logging, secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db
from api.auth import get_current_user, AuthContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/followup", tags=["followup"])

FOLLOWUP_DELAYS = [
    ("followup_24h",  timedelta(hours=24)),
    ("followup_48h",  timedelta(hours=48)),
    ("followup_7day", timedelta(days=7)),
]

class FollowupScheduleRequest(BaseModel):
    assessment_id: str
    homeowner_email: str
    homeowner_name: str
    report_url: str
    company_name: str

class FollowupScheduleResponse(BaseModel):
    ok: bool
    scheduled_count: int
    opt_out_token: str
    message: str

@router.post("/schedule", response_model=FollowupScheduleResponse)
async def schedule_followups(
    body: FollowupScheduleRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule 3 follow-up emails for a completed assessment.
    Creates FollowUp records in DB; a background job (or cron) sends them.
    """
    now = datetime.now(timezone.utc)
    opt_out_token = secrets.token_urlsafe(24)
    scheduled = 0

    for template, delay in FOLLOWUP_DELAYS:
        scheduled_at = now + delay
        try:
            await db.execute(
                text("""
                    INSERT INTO follow_ups
                        (assessment_id, company_id, type, scheduled_at,
                         metadata, status)
                    VALUES
                        (:assessment_id, :company_id, :type, :scheduled_at,
                         CAST(:metadata AS jsonb), 'pending')
                    ON CONFLICT DO NOTHING
                """),
                {
                    "assessment_id": body.assessment_id,
                    "company_id": str(auth.company_id),
                    "type": template,
                    "scheduled_at": scheduled_at.isoformat(),
                    "metadata": __import__("json").dumps({
                        "homeowner_email": body.homeowner_email,
                        "homeowner_name": body.homeowner_name,
                        "report_url": body.report_url,
                        "company_name": body.company_name,
                        "opt_out_token": opt_out_token,
                    }),
                },
            )
            scheduled += 1
        except Exception as e:
            logger.warning(f"[Followup] Failed to schedule {template}: {e}")

    await db.commit()
    logger.info(f"[Followup] Scheduled {scheduled} emails for assessment {body.assessment_id}")

    return FollowupScheduleResponse(
        ok=True,
        scheduled_count=scheduled,
        opt_out_token=opt_out_token,
        message=f"Scheduled {scheduled} follow-up emails (24h, 48h, 7-day)."
    )

@router.get("/opt-out/{token}")
async def opt_out(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """One-click opt-out — cancels all pending follow-ups for this token."""
    await db.execute(
        text("""
            UPDATE follow_ups
            SET status = 'cancelled'
            WHERE status = 'pending'
              AND metadata->>'opt_out_token' = :token
        """),
        {"token": token},
    )
    await db.commit()
    return {"ok": True, "message": "You have been unsubscribed from all future follow-up emails."}

@router.get("/pending")
async def list_pending_followups(
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List pending follow-ups for this company (for admin/debug)."""
    rows = await db.execute(
        text("""
            SELECT id, assessment_id, type, scheduled_at, status
            FROM follow_ups
            WHERE company_id = :company_id AND status = 'pending'
              AND scheduled_at <= now() + interval '8 days'
            ORDER BY scheduled_at
            LIMIT 50
        """),
        {"company_id": str(auth.company_id)},
    )
    return [
        {"id": str(r.id), "assessment_id": str(r.assessment_id),
         "type": r.type, "scheduled_at": r.scheduled_at.isoformat(), "status": r.status}
        for r in rows.fetchall()
    ]
