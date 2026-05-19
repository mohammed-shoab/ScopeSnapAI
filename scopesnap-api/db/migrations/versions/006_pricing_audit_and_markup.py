"""Add pricing audit trail and per-contractor markup setting

Revision ID: 006
Revises: 005
Create Date: 2026-04-15

Changes:
  pricing_rules:
    - changed_by_user_id  — who last edited this price
    - changed_at          — when it was last changed
    - previous_value      — previous price before the edit (JSON snapshot)
    - change_note         — optional reason for change

  companies:
    - default_markup_pct  — per-contractor markup % (replaces hardcoded 35%)
    - markup_updated_at   — when the markup was last changed
"""
from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── pricing_rules audit columns ───────────────────────────────────────────
    op.add_column("pricing_rules", sa.Column(
        "changed_by_user_id", sa.String(36), nullable=True,
        comment="User ID who last edited this price",
    ))
    op.add_column("pricing_rules", sa.Column(
        "changed_at", sa.DateTime(timezone=True), nullable=True,
        comment="Timestamp of last manual price edit",
    ))
    op.add_column("pricing_rules", sa.Column(
        "previous_value", sa.JSON(), nullable=True,
        comment="JSON snapshot of price before last edit {good, better, best, labor_rate}",
    ))
    op.add_column("pricing_rules", sa.Column(
        "change_note", sa.Text(), nullable=True,
        comment="Optional reason for price change (e.g. 'Customer negotiated')",
    ))

    # ── companies markup setting ──────────────────────────────────────────────
    op.add_column("companies", sa.Column(
        "default_markup_pct", sa.Numeric(5, 2), nullable=False,
        server_default=sa.text("35.00"),
        comment="Default markup % applied to all estimates for this contractor",
    ))
    op.add_column("companies", sa.Column(
        "markup_updated_at", sa.DateTime(timezone=True), nullable=True,
        comment="When the contractor last changed their markup setting",
    ))


def downgrade() -> None:
    op.drop_column("companies", "markup_updated_at")
    op.drop_column("companies", "default_markup_pct")
    op.drop_column("pricing_rules", "change_note")
    op.drop_column("pricing_rules", "previous_value")
    op.drop_column("pricing_rules", "changed_at")
    op.drop_column("pricing_rules", "changed_by_user_id")
