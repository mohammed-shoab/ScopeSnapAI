"""Add contractor onboarding-gate columns to companies (gate C3)

The contractor onboarding GATE ensures a homeowner can't just sign up with a
Gmail and reach the app. Two nullable columns back it:

  * ``attestation_accepted_at`` -- TIMESTAMPTZ, NULL by default. Stamped with
    now() when the owner ticks the "I'm a licensed HVAC contractor…" attestation
    on the onboarding form. The frontend guard treats a NULL value (or a blank
    ``license_number``) as "onboarding incomplete" and redirects to /onboarding.
  * ``terms_ack_version`` -- VARCHAR(20), NULL by default. Records which version
    of the ToS / decision-support acknowledgement the owner accepted (e.g. "v1").

Both nullable with no server_default, so existing companies are unaffected until
their owner completes the gate.

Idempotent: ADD/DROP COLUMN IF [NOT] EXISTS guards (same style as 041/043).

Revision ID: 045
Revises: 044
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "045"
down_revision: Union[str, None] = "044"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text(
        'ALTER TABLE "companies" '
        'ADD COLUMN IF NOT EXISTS "attestation_accepted_at" TIMESTAMPTZ'
    ))
    bind.execute(text(
        'ALTER TABLE "companies" '
        'ADD COLUMN IF NOT EXISTS "terms_ack_version" VARCHAR(20)'
    ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text(
        'ALTER TABLE "companies" DROP COLUMN IF EXISTS "terms_ack_version"'
    ))
    bind.execute(text(
        'ALTER TABLE "companies" DROP COLUMN IF EXISTS "attestation_accepted_at"'
    ))
