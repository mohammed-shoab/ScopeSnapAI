"""
ScopeSnap — Stripe Payment API Endpoints
WP-10: Deposit collection flow.

Endpoints:
- POST /api/estimates/{id}/checkout  — Create Stripe Checkout session (20% deposit)
- GET  /api/estimates/{id}/payment   — Get payment status for an estimate
- POST /api/webhooks/stripe          — Stripe webhook (payment_intent.succeeded)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from db.database import get_db
from db.models import Assessment, Company, Estimate, Property
from api.auth import get_current_user, AuthContext
from services.payment import get_payment_service

router = APIRouter(tags=["payments"])
webhook_router = APIRouter(tags=["webhooks"])


# ── POST /api/estimates/{id}/checkout ─────────────────────────────────────────

class CheckoutRequest(BaseModel):
    success_url: Optional[str] = None  # Override redirect URL
    cancel_url: Optional[str] = None   # Override cancel URL


@router.post("/api/estimates/{estimate_id}/checkout")
async def create_checkout(
    estimate_id: str,
    body: CheckoutRequest = CheckoutRequest(),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-10: Creates a Stripe Checkout session for the 20% deposit.

    Returns:
    - checkout_url: URL to redirect homeowner to (or mock URL in dev)
    - session_id: Stripe session ID (stored on estimate)
    - amount_cents: deposit amount in cents
    """
    # Load estimate
    result = await db.execute(
        select(Estimate).where(
            Estimate.id == estimate_id,
            Estimate.company_id == auth.company_id,
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found.")

    # Must be approved before paying deposit
    if estimate.status not in ("approved", "sent", "estimated"):
        raise HTTPException(
            status_code=400,
            detail=f"Estimate must be approved before collecting deposit. Current status: {estimate.status}",
        )

    # Calculate deposit amount
    if not estimate.deposit_amount:
        raise HTTPException(
            status_code=400,
            detail="No deposit amount set. Approve an option first.",
        )

    deposit_cents = int(float(estimate.deposit_amount) * 100)

    # Load company for branding
    company_result = await db.execute(
        select(Company).where(Company.id == auth.company_id)
    )
    company = company_result.scalar_one_or_none()
    company_name = company.name if company else "ScopeSnap HVAC"

    # Load customer email from property
    customer_email = None
    if estimate.assessment_id:
        assess_result = await db.execute(
            select(Assessment).where(Assessment.id == estimate.assessment_id)
        )
        assessment = assess_result.scalar_one_or_none()
        if assessment and assessment.property_id:
            prop_result = await db.execute(
                select(Property).where(Property.id == assessment.property_id)
            )
            prop = prop_result.scalar_one_or_none()
            if prop:
                customer_email = prop.customer_email

    # Build redirect URLs
    base = "http://localhost:3000"
    success_url = body.success_url or f"{base}/payment-success?estimate={estimate_id}&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = body.cancel_url or f"{base}/r/hvac/{estimate.report_short_id}"

    # Create Stripe Checkout session
    payment_service = get_payment_service()
    session_data = await payment_service.create_checkout_session(
        estimate_id=estimate_id,
        amount_cents=deposit_cents,
        description=f"{company_name} — HVAC Service Deposit ({estimate.report_short_id})",
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email,
        metadata={"estimate_id": estimate_id, "report_short_id": estimate.report_short_id},
    )

    # Store session ID on estimate
    estimate.stripe_payment_intent_id = session_data["session_id"]
    await db.commit()

    return {
        "checkout_url": session_data["checkout_url"],
        "session_id": session_data["session_id"],
        "amount_cents": deposit_cents,
        "deposit_amount": float(estimate.deposit_amount),
        "report_short_id": estimate.report_short_id,
        "mode": session_data.get("mode", "stripe"),
    }


# ── GET /api/estimates/{id}/payment ───────────────────────────────────────────

@router.get("/api/estimates/{estimate_id}/payment")
async def get_payment_status(
    estimate_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the payment status for an estimate."""
    result = await db.execute(
        select(Estimate).where(
            Estimate.id == estimate_id,
            Estimate.company_id == auth.company_id,
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found.")

    return {
        "estimate_id": estimate_id,
        "status": estimate.status,
        "deposit_amount": float(estimate.deposit_amount) if estimate.deposit_amount else None,
        "deposit_paid": estimate.status == "deposit_paid",
        "stripe_session_id": estimate.stripe_payment_intent_id,
    }


# ── POST /api/webhooks/stripe ─────────────────────────────────────────────────

@webhook_router.post("/api/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    WP-10: Stripe webhook handler.
    Handles: checkout.session.completed → marks estimate as deposit_paid.

    In dev mode (no STRIPE_WEBHOOK_SECRET): accepts unsigned events for testing.
    In prod: verifies Stripe-Signature header.
    """
    from config import get_settings
    settings = get_settings()

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    # ── Parse event ───────────────────────────────────────────────────────────
    if settings.stripe_webhook_secret and sig_header:
        # Production: verify signature
        payment_service = get_payment_service()
        try:
            event = await payment_service.verify_webhook(payload, sig_header)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook signature invalid: {e}")
    else:
        # Dev mode: parse raw JSON without signature verification
        import json
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    event_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
    event_data = event.get("data", {}) if isinstance(event, dict) else getattr(event, "data", {})

    # ── Handle checkout.session.completed ─────────────────────────────────────
    if event_type == "checkout.session.completed":
        session_obj = event_data.get("object", {}) if isinstance(event_data, dict) else {}
        payment_status = session_obj.get("payment_status")
        metadata = session_obj.get("metadata", {})
        session_id = session_obj.get("id")
        estimate_id = metadata.get("estimate_id")

        if estimate_id and payment_status == "paid":
            result = await db.execute(
                select(Estimate).where(Estimate.id == estimate_id)
            )
            estimate = result.scalar_one_or_none()
            if estimate and estimate.status != "deposit_paid":
                estimate.status = "deposit_paid"
                estimate.stripe_payment_intent_id = session_id
                await db.commit()
                print(f"[webhook] Deposit paid for estimate {estimate_id} (session: {session_id})")
                return {"received": True, "action": "deposit_marked_paid", "estimate_id": estimate_id}

        return {"received": True, "action": "no_action", "payment_status": payment_status}

    # ── Handle payment_intent.succeeded (fallback) ────────────────────────────
    elif event_type == "payment_intent.succeeded":
        pi_obj = event_data.get("object", {}) if isinstance(event_data, dict) else {}
        pi_id = pi_obj.get("id")
        if pi_id:
            result = await db.execute(
                select(Estimate).where(Estimate.stripe_payment_intent_id == pi_id)
            )
            estimate = result.scalar_one_or_none()
            if estimate and estimate.status != "deposit_paid":
                estimate.status = "deposit_paid"
                await db.commit()
                return {"received": True, "action": "deposit_marked_paid", "estimate_id": str(estimate.id)}

        return {"received": True, "action": "no_action"}

    # ── Ignore other events ───────────────────────────────────────────────────
    return {"received": True, "action": "ignored", "event_type": event_type}
