"""031 — add photo_skipped to diagnostic_sessions

Revision ID: 031
Revises: 030
Create Date: 2026-05-21

Adds a boolean flag to track when the tech skipped the on-site photo step.
Used by reports.py to render a disclosure on the homeowner report (B.6).
"""
from alembic import op
import sqlalchemy as sa

revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "diagnostic_sessions",
        sa.Column("photo_skipped", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("diagnostic_sessions", "photo_skipped")
