"""
ScopeSnap — Clerk Webhook Handler
WP-11: Auto-provisions users and companies when they sign up via Clerk.

Clerk sends a webhook POST to /api/webhooks/clerk on these events:
- user.created  → create Company + User record in ScopeSnap DB
- user.updated  → update email/name in ScopeSnap DB
- user.deleted  → (soft) deactivate user

Security: Webhook signature verified via svix (Clerk's delivery provider).
Dev mode: Accepts unsigned webhooks if CLERK_WEBHOOK_SECRET is not set.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
import string

from db.database import get_db
from db.models import Company, User
from config import get_settings

settings = get_settings()
router = APIRouter(tags=["webhooks"])


def _make_slug(company_name: str) -> str:
    """Converts company name to URL-safe slug."""
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower().strip())
    slug = slug.strip("-")[:40]
    suffix = "".join(secrets.choice(string.digits) for _ in range(4))
    return f"{slug}-{suffix}" if slug else f"company-{suffix}"


async def _ensure_unique_slug(slug: str, db: AsyncSession) -> str:
    """Ensures slug is unique in DB, appending random suffix if needed."""
    result = await db.execute(select(Company).where(Company.slug == slug))
    if not result.scalar_one_or_none():
        return slug
    # Conflict: add more randomness
    suffix = "".join(secrets.choice(string.digits) for _ in range(4))
    return f"{slug}-{suffix}"


async def _provision_user(clerk_user_id: str, email: str, name: str, db: AsyncSession) -> dict:
    """
    Creates Company + User records for a new Clerk user.
    Idempotent: if user already exists, returns existing records.
    """
    # Check if user already exists
    existing = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    existing_user = existing.scalar_one_or_none()
    if existing_user:
        return {"action": "already_exists", "user_id": str(existing_user.id)}

    # Create Company (auto-generated from user's name)
    company_name = f"{name}'s HVAC" if name else "My HVAC Company"
    base_slug = _make_slug(company_name)
    slug = await _ensure_unique_slug(base_slug, db)

    company = Company(
        name=company_name,
        slug=slug,
        email=email,
        plan="trial",
        monthly_estimate_limit=10,
        monthly_estimate_count=0,
        settings={},
    )
    db.add(company)
    await db.flush()  # Get company.id

    # Create User linked to Company
    user = User(
        company_id=company.id,
        clerk_user_id=clerk_user_id,
        email=email,
        name=name,
        role="owner",  # First user is always owner
    )
    db.add(user)
    await db.commit()

    print(f"[clerk-webhook] Provisioned: user={clerk_user_id}, company={slug}")
    return {
        "action": "created",
        "user_id": str(user.id),
        "company_id": str(company.id),
        "company_slug": slug,
    }


# ── POST /api/webhooks/clerk ──────────────────────────────────────────────────

@router.post("/api/webhooks/clerk")
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    WP-11: Handles Clerk webhook events for user lifecycle.

    Events handled:
    - user.created  → provision Company + User in ScopeSnap DB
    - user.updated  → sync email/name changes
    - user.deleted  → no-op (data retained for billing)
    """
    payload = await request.body()

    # ── Verify webhook signature ───────────────────────────────────────────────
    clerk_webhook_secret = getattr(settings, "clerk_webhook_secret", "")
    if clerk_webhook_secret and not clerk_webhook_secret.startswith("whsec_placeholder"):
        # Production: verify svix signature
        try:
            from svix.webhooks import Webhook, WebhookVerificationError
            wh = Webhook(clerk_webhook_secret)
            svix_id = request.headers.get("svix-id", "")
            svix_ts = request.headers.get("svix-timestamp", "")
            svix_sig = request.headers.get("svix-signature", "")
            headers_dict = {"svix-id": svix_id, "svix-timestamp": svix_ts, "svix-signature": svix_sig}
            event = wh.verify(payload, headers_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {e}")
    else:
        # Dev mode: parse without verification
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    event_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
    event_data = event.get("data", {}) if isinstance(event, dict) else getattr(event, "data", {})

    # ── user.created ─────────────────────────────────────────────────────────
    if event_type == "user.created":
        clerk_user_id = event_data.get("id")
        email_list = event_data.get("email_addresses", [])
        primary_email_id = event_data.get("primary_email_address_id")
        email = ""
        for e in email_list:
            if e.get("id") == primary_email_id:
                email = e.get("email_address", "")
                break
        if not email and email_list:
            email = email_list[0].get("email_address", "")

        first_name = event_data.get("first_name") or ""
        last_name = event_data.get("last_name") or ""
        name = f"{first_name} {last_name}".strip() or email.split("@")[0]

        if not clerk_user_id:
            raise HTTPException(status_code=400, detail="Missing user ID in webhook payload.")

        result = await _provision_user(clerk_user_id, email, name, db)
        return {"received": True, "event": event_type, **result}

    # ── user.updated ─────────────────────────────────────────────────────────
    elif event_type == "user.updated":
        clerk_user_id = event_data.get("id")
        email_list = event_data.get("email_addresses", [])
        primary_email_id = event_data.get("primary_email_address_id")
        email = ""
        for e in email_list:
            if e.get("id") == primary_email_id:
                email = e.get("email_address", "")
                break

        first_name = event_data.get("first_name") or ""
        last_name = event_data.get("last_name") or ""
        name = f"{first_name} {last_name}".strip()

        if clerk_user_id:
            result = await db.execute(
                select(User).where(User.clerk_user_id == clerk_user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                if email:
                    user.email = email
                if name:
                    user.name = name
                await db.commit()
                return {"received": True, "event": event_type, "action": "updated"}

        return {"received": True, "event": event_type, "action": "no_action"}

    # ── user.deleted ─────────────────────────────────────────────────────────
    elif event_type == "user.deleted":
        # Retain data for billing/audit. Log only.
        clerk_user_id = event_data.get("id")
        print(f"[clerk-webhook] user.deleted: {clerk_user_id} (data retained)")
        return {"received": True, "event": event_type, "action": "retained"}

    # ── Other events ─────────────────────────────────────────────────────────
    return {"received": True, "event": event_type, "action": "ignored"}


# ── POST /api/auth/me — Current User Info ────────────────────────────────────

from api.auth import get_current_user, AuthContext

me_router = APIRouter(prefix="/api/auth", tags=["auth"])


@me_router.get("/me")
async def get_me(
    auth: AuthContext = Depends(get_current_user),
):
    """Returns the authenticated user's profile and company info."""
    return {
        "user": {
            "id": str(auth.user.id),
            "clerk_user_id": auth.user.clerk_user_id,
            "email": auth.user.email,
            "name": auth.user.name,
            "role": auth.user.role,
            "accuracy_score": float(auth.user.accuracy_score) if auth.user.accuracy_score else None,
            "total_estimates": auth.user.total_estimates or 0,
        },
        "company": {
            "id": str(auth.company.id),
            "name": auth.company.name,
            "slug": auth.company.slug,
            "plan": auth.company.plan,
            "monthly_estimate_count": auth.company.monthly_estimate_count or 0,
            "monthly_estimate_limit": auth.company.monthly_estimate_limit or 10,
            "logo_url": auth.company.logo_url,
            "phone": auth.company.phone,
            "email": auth.company.email,
            "license_number": auth.company.license_number,
        },
    }


@me_router.patch("/me/company")
async def update_company(
    request: Request,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Owner updates their company profile (name, phone, license, etc.).
    Used during onboarding (WP-16) and settings.
    """
    if not auth.is_owner:
        raise HTTPException(status_code=403, detail="Owner access required.")

    body = await request.json()
    company = auth.company

    # Allowed fields to update
    if "name" in body:
        company.name = body["name"]
    if "phone" in body:
        company.phone = body["phone"]
    if "email" in body:
        company.email = body["email"]
    if "license_number" in body:
        company.license_number = body["license_number"]
    if "address_line1" in body:
        company.address_line1 = body["address_line1"]
    if "city" in body:
        company.city = body["city"]
    if "state" in body:
        company.state = body["state"]
    if "zip" in body:
        company.zip = body["zip"]

    await db.commit()

    return {
        "success": True,
        "company": {
            "id": str(company.id),
            "name": company.name,
            "phone": company.phone,
            "email": company.email,
            "license_number": company.license_number,
        }
    }
