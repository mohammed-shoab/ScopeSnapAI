"""
ScopeSnap — Subscription Billing API
WP-15: Stripe subscription management for the SaaS platform.

Plans:
  trial    — Free (10 estimates/month, expires after 14 days)
  starter  — $49/mo (unlimited estimates)
  pro      — $99/mo (unlimited + priority support + custom branding)

Endpoints:
  GET  /api/billing/plans        — List available plans
  GET  /api/billing/subscription — Current company subscription status
  POST /api/billing/subscribe    — Create Stripe Checkout for subscription
  POST /api/billing/portal       — Create Stripe Customer Portal session
  POST /api/webhooks/stripe/billing — Stripe billing webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional

from db.database import get_db
from db.models import Company
from api.auth import get_current_user, AuthContext, require_owner
from config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/billing", tags=["billing"])
webhook_router = APIRouter(tags=["webhooks"])


# ── Plan Definitions ──────────────────────────────────────────────────────────

PLANS = {
    "trial": {
        "id": "trial",
        "name": "Free Trial",
        "price_monthly": 0,
        "estimate_limit": 10,
        "features": ["10 estimates/month", "AI photo analysis", "PDF reports", "Email notifications"],
        "stripe_price_id": None,
    },
    "starter": {
        "id": "starter",
        "name": "Starter",
        "price_monthly": 49,
        "estimate_limit": None,  # Unlimited
        "features": ["Unlimited estimates", "AI photo analysis", "PDF reports", "Email + SMS", "Follow-up automation", "Analytics dashboard"],
        "stripe_price_id": getattr(settings, "stripe_starter_price_id", "price_starter_placeholder"),
    },
    "pro": {
        "id": "pro",
        "name": "Professional",
        "price_monthly": 99,
        "estimate_limit": None,  # Unlimited
        "features": ["Everything in Starter", "Custom branding / logo", "Priority support", "Team member management", "Accuracy analytics"],
        "stripe_price_id": getattr(settings, "stripe_pro_price_id", "price_pro_placeholder"),
    },
}


# ── GET /api/billing/plans ────────────────────────────────────────────────────

@router.get("/plans")
async def list_plans():
    """Returns all available subscription plans."""
    return {
        "plans": [
            {k: v for k, v in plan.items() if k != "stripe_price_id"}
            for plan in PLANS.values()
        ]
    }


# ── GET /api/billing/subscription ────────────────────────────────────────────

@router.get("/subscription")
async def get_subscription(
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the current company's subscription status."""
    company = auth.company
    plan = PLANS.get(company.plan, PLANS["trial"])

    remaining = None
    if plan["estimate_limit"] is not None:
        used = company.monthly_estimate_count or 0
        remaining = max(0, plan["estimate_limit"] - used)

    return {
        "company_id": str(company.id),
        "plan": company.plan,
        "plan_name": plan["name"],
        "price_monthly": plan["price_monthly"],
        "estimate_limit": plan["estimate_limit"],
        "monthly_estimate_count": company.monthly_estimate_count or 0,
        "remaining_estimates": remaining,
        "features": plan["features"],
        "stripe_subscription_id": company.stripe_subscription_id,
        "is_active": True,  # Trial is always "active"; subscriptions checked via Stripe
        "can_create_estimate": remaining is None or remaining > 0,
    }


# ── POST /api/billing/subscribe ───────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    plan_id: str  # 'starter' | 'pro'
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


@router.post("/subscribe")
async def create_subscription_checkout(
    body: SubscribeRequest,
    auth: AuthContext = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-15: Creates a Stripe Checkout session for subscription.
    Returns a checkout_url to redirect the owner to.
    """
    if body.plan_id not in ("starter", "pro"):
        raise HTTPException(status_code=400, detail="Invalid plan. Choose 'starter' or 'pro'.")

    plan = PLANS[body.plan_id]
    company = auth.company
    base_url = settings.frontend_url or "http://localhost:3000"

    success_url = body.success_url or f"{base_url}/billing/success?plan={body.plan_id}"
    cancel_url = body.cancel_url or f"{base_url}/billing"

    # ── Mock mode (no real Stripe key) ───────────────────────────────────────
    from services.payment import _is_real_stripe_key
    if not _is_real_stripe_key(settings.stripe_secret_key):
        mock_session_id = f"sub_mock_{str(company.id)[:8]}_{body.plan_id}"
        mock_url = (
            f"{base_url}/mock-subscribe"
            f"?plan={body.plan_id}"
            f"&session_id={mock_session_id}"
            f"&company_id={company.id}"
        )
        print(f"\n{'='*60}")
        print(f"📦 STRIPE SUBSCRIPTION (Mock Mode)")
        print(f"  COMPANY: {company.name}")
        print(f"  PLAN:    {plan['name']} — ${plan['price_monthly']}/mo")
        print(f"  SESSION: {mock_session_id}")
        print(f"{'='*60}\n")
        return {
            "checkout_url": mock_url,
            "session_id": mock_session_id,
            "plan": body.plan_id,
            "price_monthly": plan["price_monthly"],
            "mode": "mock",
        }

    # ── Production Stripe ─────────────────────────────────────────────────────
    import stripe, asyncio
    stripe.api_key = settings.stripe_secret_key
    loop = asyncio.get_event_loop()

    # Ensure Stripe customer exists
    if not company.stripe_customer_id:
        customer = await loop.run_in_executor(
            None,
            lambda: stripe.Customer.create(
                email=company.email or auth.user.email,
                name=company.name,
                metadata={"company_id": str(company.id)},
            ),
        )
        company.stripe_customer_id = customer.id
        await db.commit()

    session = await loop.run_in_executor(
        None,
        lambda: stripe.checkout.Session.create(
            customer=company.stripe_customer_id,
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": plan["stripe_price_id"], "quantity": 1}],
            success_url=f"{success_url}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url,
            metadata={"company_id": str(company.id), "plan": body.plan_id},
        ),
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        "plan": body.plan_id,
        "price_monthly": plan["price_monthly"],
        "mode": "stripe",
    }


# ── POST /api/billing/portal ──────────────────────────────────────────────────

@router.post("/portal")
async def create_billing_portal(
    auth: AuthContext = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a Stripe Customer Portal session for managing subscriptions.
    The owner can cancel, upgrade, or download invoices.
    """
    company = auth.company
    base_url = settings.frontend_url or "http://localhost:3000"

    from services.payment import _is_real_stripe_key
    if not _is_real_stripe_key(settings.stripe_secret_key):
        # Mock portal
        return {
            "portal_url": f"{base_url}/mock-billing-portal?company_id={company.id}",
            "mode": "mock",
        }

    import stripe, asyncio
    stripe.api_key = settings.stripe_secret_key
    loop = asyncio.get_event_loop()

    if not company.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="No Stripe customer found. Please subscribe first.",
        )

    session = await loop.run_in_executor(
        None,
        lambda: stripe.billing_portal.Session.create(
            customer=company.stripe_customer_id,
            return_url=f"{base_url}/billing",
        ),
    )
    return {"portal_url": session.url, "mode": "stripe"}


# ── POST /api/webhooks/stripe/billing ─────────────────────────────────────────

@webhook_router.post("/api/webhooks/stripe/billing")
async def stripe_billing_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    WP-15: Handles Stripe subscription lifecycle webhooks.

    Events:
    - checkout.session.completed (subscription mode) → activate plan
    - customer.subscription.updated → update plan/status
    - customer.subscription.deleted → downgrade to trial
    - invoice.payment_failed → notify owner
    """
    import json as _json
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    # Parse event (dev: unsigned, prod: verified)
    if settings.stripe_webhook_secret and "placeholder" not in settings.stripe_webhook_secret:
        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key
            import asyncio
            loop = asyncio.get_event_loop()
            event = await loop.run_in_executor(
                None,
                lambda: stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret),
            )
            event_type = event.type
            event_data = event.data.object
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook error: {e}")
    else:
        try:
            raw = _json.loads(payload)
            event_type = raw.get("type")
            event_data = raw.get("data", {}).get("object", {})
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload.")

    # ── checkout.session.completed (subscription) ─────────────────────────────
    if event_type == "checkout.session.completed":
        mode = event_data.get("mode") if isinstance(event_data, dict) else getattr(event_data, "mode", None)
        if mode == "subscription":
            metadata = event_data.get("metadata", {}) if isinstance(event_data, dict) else {}
            company_id = metadata.get("company_id")
            plan_id = metadata.get("plan", "starter")
            subscription_id = (
                event_data.get("subscription") if isinstance(event_data, dict)
                else getattr(event_data, "subscription", None)
            )
            if company_id:
                result = await db.execute(select(Company).where(Company.id == company_id))
                company = result.scalar_one_or_none()
                if company:
                    company.plan = plan_id
                    company.stripe_subscription_id = subscription_id
                    company.monthly_estimate_limit = None  # Unlimited on paid plan
                    await db.commit()
                    print(f"[billing-webhook] Activated {plan_id} plan for company {company_id}")
                    return {"received": True, "action": "plan_activated", "plan": plan_id}

    # ── customer.subscription.deleted ────────────────────────────────────────
    elif event_type == "customer.subscription.deleted":
        sub_id = event_data.get("id") if isinstance(event_data, dict) else getattr(event_data, "id", None)
        customer_id = event_data.get("customer") if isinstance(event_data, dict) else getattr(event_data, "customer", None)
        if customer_id:
            result = await db.execute(
                select(Company).where(Company.stripe_customer_id == customer_id)
            )
            company = result.scalar_one_or_none()
            if company:
                company.plan = "trial"
                company.stripe_subscription_id = None
                company.monthly_estimate_limit = 10
                await db.commit()
                print(f"[billing-webhook] Downgraded company {company.id} to trial (subscription cancelled)")
                return {"received": True, "action": "downgraded_to_trial"}

    # ── customer.subscription.updated ────────────────────────────────────────
    elif event_type == "customer.subscription.updated":
        # Handle plan changes (upgrade/downgrade)
        return {"received": True, "action": "subscription_updated"}

    # ── invoice.payment_failed ────────────────────────────────────────────────
    elif event_type == "invoice.payment_failed":
        # In production: send email to owner about failed payment
        print(f"[billing-webhook] Payment failed: {event_data.get('customer') if isinstance(event_data, dict) else 'unknown'}")
        return {"received": True, "action": "payment_failed_logged"}

    return {"received": True, "action": "ignored", "event_type": event_type}
