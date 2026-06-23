"""Enable RLS on processed_webhook_events (close public REST exposure)

processed_webhook_events (added in migration 042) was created WITHOUT row-level
security, so Supabase PostgREST exposed it to the anon role — flagged by the
Supabase security advisor `rls_disabled_in_public` (ERROR). Every sibling table
is RLS-enabled-no-policy (denied via the REST API; the app reads/writes via a
direct asyncpg owner connection that bypasses RLS, so this is behavior-neutral
for the app). This migration brings the table in line with that pattern.

Already applied live to staging + prod on 2026-06-24; this records it in the
Alembic chain so a rebuild-from-migrations stays consistent. Idempotent.

Revision ID: 044
Revises: 043
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "044"
down_revision: Union[str, None] = "043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(text(
        "ALTER TABLE IF EXISTS public.processed_webhook_events ENABLE ROW LEVEL SECURITY"
    ))


def downgrade() -> None:
    op.get_bind().execute(text(
        "ALTER TABLE IF EXISTS public.processed_webhook_events DISABLE ROW LEVEL SECURITY"
    ))
