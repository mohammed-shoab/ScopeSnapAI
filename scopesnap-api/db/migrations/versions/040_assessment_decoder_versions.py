"""Stamp decoder + replace-logic versions on assessments (v1.2, Stage 5).

Adds two nullable provenance columns to ``assessments`` so every estimate can
record which brand-decoder / replace-logic data version produced it:

  * ``decoder_version``       -- serial/brand decoder data version (e.g. "1.2")
  * ``replace_logic_version`` -- replace-decision logic spec version (e.g. "1.2")

Historical rows predate v1.2 version stamping, so both columns carry a
``server_default`` of ``"pre-v1.2"``: existing assessments are NOT recomputed or
backfilled -- they keep the sentinel that marks them as pre-stamping.

Idempotent: columns are added with raw ``ADD COLUMN IF NOT EXISTS`` guards (same
style as migration 039). Safe to re-run.

Revision ID: 040
Revises: 039
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "040"
down_revision: Union[str, None] = "039"
branch_labels = None
depends_on = None

_NEW_COLS = ("decoder_version", "replace_logic_version")


def upgrade() -> None:
    bind = op.get_bind()
    # Nullable; historical rows default to the "pre-v1.2" sentinel so they are
    # never confused with freshly-stamped v1.2 estimates.
    bind.execute(text(
        'ALTER TABLE "assessments" '
        "ADD COLUMN IF NOT EXISTS \"decoder_version\" VARCHAR(20) DEFAULT 'pre-v1.2', "
        "ADD COLUMN IF NOT EXISTS \"replace_logic_version\" VARCHAR(20) DEFAULT 'pre-v1.2'"
    ))


def downgrade() -> None:
    bind = op.get_bind()
    for col in _NEW_COLS:
        bind.execute(text(f'ALTER TABLE "assessments" DROP COLUMN IF EXISTS "{col}"'))
