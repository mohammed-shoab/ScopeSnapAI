"""
ScopeSnap — Stripe Payment Service
WP-10: Deposit collection via Stripe Checkout.

Dev mode (no STRIPE_SECRET_KEY): returns mock checkout URL + fake session ID.
Prod mode: creates real Stripe Checkout session.

Design: 20% deposit collected via Stripe Checkout before work begins.
On payment_intent.succeeded webhook → estimate.status = 'deposit_paid'.
"""

from config import get_settings

settings = get_settings()


class MockPaymentService:
    """
    Development payment service — returns mock checkout URLs.
    Zero setup, zero cost. Mirrors the real Stripe interface.
    """

    async def create_checkout_session(
        self,
        estimate_id: str,
        amount_cents: int,
        description: str,
        success_url: str,
        cancel_url: str,
        customer_email: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Returns a mock checkout session for development."""
        mock_session_id = f"cs_mock_{estimate_id[:8]}"
        mock_checkout_url = (
            f"http://localhost:3000/mock-payment"
            f"?session_id={mock_session_id}"
            f"&amount={amount_cents}"
            f"&estimate_id={estimate_id}"
            f"&success_url={success_url}"
        )
        print(f"\n{'=' * 60}")
        print(f"💳 STRIPE CHECKOUT (Mock Mode — not a real charge)")
        print(f"{'=' * 60}")
        print(f"  ESTIMATE:   {estimate_id}")
        print(f"  AMOUNT:     ${amount_cents / 100:.2f}")
        print(f"  DESC:       {description}")
        print(f"  SESSION ID: {mock_session_id}")
        print(f"  URL:        {mock_checkout_url}")
        print(f"{'=' * 60}\n")
        return {
            "session_id": mock_session_id,
            "checkout_url": mock_checkout_url,
            "amount_cents": amount_cents,
            "mode": "mock",
        }

    async def retrieve_session(self, session_id: str) -> dict:
        """Mock session retrieval — always returns paid status for mock IDs."""
        return {
            "id": session_id,
            "payment_status": "paid" if session_id.startswith("cs_mock_") else "unpaid",
            "amount_total": 0,
            "mode": "mock",
        }

    async def verify_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Mock webhook — not callable from outside in dev."""
        raise RuntimeError("MockPaymentService does not process webhooks.")


class StripePaymentService:
    """
    Production Stripe payment service.
    Requires: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET in .env
    """

    def __init__(self):
        import stripe
        if not settings.stripe_secret_key:
            raise RuntimeError("STRIPE_SECRET_KEY not set. Use MockPaymentService in development.")
        stripe.api_key = settings.stripe_secret_key
        self._stripe = stripe

    async def create_checkout_session(
        self,
        estimate_id: str,
        amount_cents: int,
        description: str,
        success_url: str,
        cancel_url: str,
        customer_email: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Creates a Stripe Checkout session and returns session_id + url."""
        import asyncio
        loop = asyncio.get_event_loop()

        session_params: dict = {
            "payment_method_types": ["card"],
            "mode": "payment",
            "line_items": [
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": description,
                            "description": "Deposit for HVAC service — 20% of approved estimate",
                        },
                    },
                    "quantity": 1,
                }
            ],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "estimate_id": estimate_id,
                **(metadata or {}),
            },
        }
        if customer_email:
            session_params["customer_email"] = customer_email

        session = await loop.run_in_executor(
            None,
            lambda: self._stripe.checkout.Session.create(**session_params),
        )
        return {
            "session_id": session.id,
            "checkout_url": session.url,
            "amount_cents": amount_cents,
            "mode": "stripe",
        }

    async def retrieve_session(self, session_id: str) -> dict:
        """Retrieves a Stripe Checkout session."""
        import asyncio
        loop = asyncio.get_event_loop()
        session = await loop.run_in_executor(
            None,
            lambda: self._stripe.checkout.Session.retrieve(session_id),
        )
        return {
            "id": session.id,
            "payment_status": session.payment_status,
            "amount_total": session.amount_total,
            "mode": "stripe",
        }

    async def verify_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Verifies webhook signature and returns the event object."""
        import asyncio
        loop = asyncio.get_event_loop()
        event = await loop.run_in_executor(
            None,
            lambda: self._stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            ),
        )
        return event


def _is_real_stripe_key(key: str) -> bool:
    """
    Returns True only if the key looks like a real Stripe key.
    Rejects empty strings and placeholder values from .env templates.
    """
    if not key:
        return False
    if "placeholder" in key.lower():
        return False
    # Real Stripe keys: sk_test_... (>30 chars) or sk_live_... (>30 chars)
    if not (key.startswith("sk_test_") or key.startswith("sk_live_")):
        return False
    return len(key) > 20


def get_payment_service():
    """
    Returns the correct payment service based on STRIPE_SECRET_KEY presence.
    Falls back to MockPaymentService if key is empty or a placeholder.
    """
    if _is_real_stripe_key(settings.stripe_secret_key):
        return StripePaymentService()
    else:
        return MockPaymentService()
