"""Add trusted server-side market to companies (authed market-trust fix #4)

Authenticated requests must resolve market-dependent reference/pricing tables
from a TRUSTED server-side source, not the spoofable X-Market header. This adds
companies.market ('US' | 'PK'). Authed routes use this column (via
get_company_tables) so a US company can no longer pull PK pak_* tables (or
vice-versa) by spoofing the header.

Backfill: existing rows default to 'US'. PK is a test market; any existing PK
company must be set manually:  UPDATE companies SET market='PK' WHERE id='<uuid>';
New companies are stamped from the request host at provision time.

Idempotent: ADD/DROP COLUMN IF [NOT] EXISTS (same style as 039-042).

Revision ID: 043
Revises: 042
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "043"
down_revision: Union[str, None] = "042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(text(
        'ALTER TABLE "companies" '
        "ADD COLUMN IF NOT EXISTS \"market\" VARCHAR(2) NOT NULL DEFAULT 'US'"
    ))


def downgrade() -> None:
    op.get_bind().execute(text(
        'ALTER TABLE "companies" DROP COLUMN IF EXISTS "market"'
    ))
