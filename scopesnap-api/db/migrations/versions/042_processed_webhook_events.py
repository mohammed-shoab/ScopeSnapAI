"""processed_webhook_events table - Stripe webhook idempotency / replay protection

Creates a small dedupe table keyed on the Stripe event id. Each webhook handler
(payments.stripe_webhook, billing.stripe_billing_webhook) inserts the event id
after signature verification and short-circuits with 200 if it already exists,
so a re-delivered or replayed Stripe event can't re-apply payment/subscription
state.

  * ``event_id``  - TEXT PRIMARY KEY. The Stripe event id (e.g. "evt_...").
  * ``created_at`` - TIMESTAMPTZ, defaults to now(). When the event was first seen.

Idempotent: CREATE TABLE IF NOT EXISTS guard (same style as 039/040/041).

Revision ID: 042
Revises: 041
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "042"
down_revision: Union[str, None] = "041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text(
        'CREATE TABLE IF NOT EXISTS "processed_webhook_events" ('
        '"event_id" TEXT PRIMARY KEY, '
        '"created_at" TIMESTAMPTZ NOT NULL DEFAULT now()'
        ')'
    ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text(
        'DROP TABLE IF EXISTS "processed_webhook_events"'
    ))
