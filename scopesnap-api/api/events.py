"""
ScopeSnap — Events API
SOW Task 1.10: POST /api/events — record behavioral analytics events.

Design:
- Always returns 200 (even on DB error) to ensure tracking never blocks UX
- Validates event_name whitelist to prevent junk data ingestion
- Extracts IP from X-Forwarded-For (Railway/Vercel proxy) or Request
- Truncates long strings to prevent DB overflow
- No auth required — events come from both authenticated and anonymous users
  (homeowner report views have no user_id)
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
import logging
import time
from collections import defaultdict

from sqlalchemy import text
from db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["events"])

# ── In-memory rate limiter (SOW Task 1.10 acceptance criterion) ───────────────
# Sliding window: max 100 events per user/IP per 60 seconds.
# Safe for single-worker async FastAPI (one event loop — no race conditions).
# Will reset on redeploy, which is acceptable for beta.
_rate_cache: Dict[str, List[float]] = defaultdict(list)
_RATE_LIMIT = 100   # max events per window
_RATE_WINDOW = 60   # window size in seconds


def _is_rate_limited(identifier: str) -> bool:
    """
    Sliding window check. Returns True if identifier has exceeded the limit.
    Side effect: records current timestamp if not limited.
    """
    now = time.monotonic()
    cutoff = now - _RATE_WINDOW
    # Trim timestamps outside the current window
    _rate_cache[identifier] = [t for t in _rate_cache[identifier] if t > cutoff]
    if len(_rate_cache[identifier]) >= _RATE_LIMIT:
        return True
    _rate_cache[identifier].append(now)
    return False

# ── Allowed event names (whitelist) ───────────────────────────────────────────
VALID_EVENTS = {
    "assessment_started",
    "assessment_photo_added",
    "assessment_submitted",
    "assessment_completed",
    "assessment_queued_offline",
    "estimate_generated",
    "report_viewed",
    "report_approved",
    "email_sent",
    "email_failed",
    "user_signed_up",
    "page_view",
    "waitlist_signup",
    "feedback_submitted",
}


# ── Request schema ────────────────────────────────────────────────────────────
class EventPayload(BaseModel):
    event_name: str
    event_data: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = None
    page_url: Optional[str] = None
    user_agent: Optional[str] = None

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        v = v.strip().lower()[:100]
        # Allow known events; silently remap unknown ones to "unknown_event"
        # (don't raise — we never want tracking to fail a request)
        return v if v in VALID_EVENTS else "unknown_event"

    @field_validator("page_url", "user_agent", "session_id", mode="before")
    @classmethod
    def truncate_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v[:2000]
        return v


# ── Helper: extract IP ────────────────────────────────────────────────────────
def get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()[:45]
    if request.client:
        return str(request.client.host)[:45]
    return None


# ── POST /api/events ──────────────────────────────────────────────────────────
@router.post("/events", status_code=200)
async def record_event(payload: EventPayload, request: Request):
    """
    Record a behavioral event.
    Always returns 200 — tracking errors must never fail user-facing requests.
    """
    try:
        ip = get_client_ip(request)

        # Extract user_id from Clerk header (optional — homeowner views won't have it)
        user_id = request.headers.get("X-Dev-Clerk-User-Id") or None

        # Rate limiting — silently drop if exceeded (never expose to client)
        identifier = user_id or ip or "anonymous"
        if _is_rate_limited(identifier):
            return {"ok": True}

        async with AsyncSessionLocal() as db:
            await db.execute(
                text("""
                INSERT INTO app_events
                    (event_name, event_data, session_id, page_url, user_agent, ip_address, user_id)
                VALUES
                    (:event_name, :event_data::jsonb, :session_id, :page_url, :user_agent, :ip_address, :user_id)
                """),
                {
                    "event_name": payload.event_name,
                    "event_data": __import__("json").dumps(payload.event_data or {}),
                    "session_id": payload.session_id,
                    "page_url": payload.page_url,
                    "user_agent": payload.user_agent,
                    "ip_address": ip,
                    "user_id": user_id,
                },
            )
            await db.commit()

    except Exception as e:
        # Log but never propagate — tracking must be invisible to the user
        logger.warning(f"[events] Failed to record event '{payload.event_name}': {e}")

    return {"ok": True}


# ── POST /api/waitlist ─────────────────────────────────────────────────────────
class WaitlistPayload(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()[:200]
        if "@" not in v or len(v) < 5:
            raise ValueError("Invalid email address")
        return v


@router.post("/waitlist", status_code=200)
async def join_waitlist(payload: WaitlistPayload, request: Request):
    """
    Join the early-access waitlist.
    Called from the landing page email capture form.
    SOW Task 1.11: waitlist_signups table.
    """
    ip = get_client_ip(request)
    referrer = request.headers.get("Referer", "")[:2000]

    try:
        async with AsyncSessionLocal() as db:
            # Upsert — silently ignore duplicate emails
            await db.execute(
                text("""
                INSERT INTO waitlist_signups (email, source, referrer_url, ip_address)
                VALUES (:email, 'landing_page', :referrer, :ip)
                ON CONFLICT (email) DO NOTHING
                """),
                {
                    "email": payload.email,
                    "referrer": referrer,
                    "ip": ip,
                },
            )
            await db.commit()

        # Also record an analytics event
        await record_event(
            EventPayload(
                event_name="waitlist_signup",
                event_data={"email_domain": payload.email.split("@")[-1]},
                page_url=referrer,
            ),
            request,
        )

    except Exception as e:
        logger.warning(f"[waitlist] Failed to save {payload.email}: {e}")
        return {"ok": False, "detail": "Could not save email. Please try again."}

    return {"ok": True, "message": "You're on the list! We'll be in touch soon."}
