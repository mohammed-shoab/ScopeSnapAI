"""Phase 3 — Diagnostic Engine — Migration 011

Revision ID: 011
Revises: 010
Create Date: 2026-05-03

Creates 5 new Phase 3 tables:
  - diagnostic_questions  (question library, seeded via Monaco)
  - diagnostic_sessions   (live per-assessment diagnostic state)
  - reading_inputs        (every numeric reading entered during diagnostic)
  - photo_labels          (photos with label + AI grade, set by tree)
  - job_confirmations     (post-job training feedback)

DDL applied directly in Supabase (same technique as WS-C migration 008).
This file is a no-op so Railway alembic upgrade head skips cleanly.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # DDL applied directly in Supabase SQL editor on 2026-05-03.
    # alembic_version already set to '011' via Monaco.
    pass


def downgrade() -> None:
    pass
