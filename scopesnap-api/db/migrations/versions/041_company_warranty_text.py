"""Add contractor-controlled warranty terms to companies.

Adds a single nullable column to ``companies``:

  * ``warranty_text`` -- VARCHAR(500), NULL by default. Free-text warranty
    terms the contractor enters in Settings (e.g. "30-day labor, 1-year parts").
    When populated it appears on the homeowner report under the contractor's
    name; when NULL/blank, no warranty language appears anywhere (DEC-088).

Nullable with no server_default, so existing companies are unaffected and show
no warranty language until an owner fills the field in.

Idempotent: ADD/DROP COLUMN IF [NOT] EXISTS guards (same style as 039/040).

Revision ID: 041
Revises: 040
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "041"
down_revision: Union[str, None] = "040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text(
        'ALTER TABLE "companies" '
        'ADD COLUMN IF NOT EXISTS "warranty_text" VARCHAR(500)'
    ))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text(
        'ALTER TABLE "companies" DROP COLUMN IF EXISTS "warranty_text"'
    ))
