# coding: utf-8
"""Create pak_pricing_tiers table.

Revision ID: 022
Revises: 021
Create Date: 2026-05-19

Pakistan per-card A/B/C pricing tiers in PKR.
Mirrors US pricing_tiers schema + metering_type column.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '022'
down_revision = '021'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pak_pricing_tiers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('card_id', sa.Integer, nullable=False),
        sa.Column('tier', sa.String(1), nullable=False),
        sa.Column('estimate_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('metering_type', sa.String(20), nullable=False,
                  server_default='any'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.UniqueConstraint('card_id', 'tier', 'metering_type',
                            name='uq_pak_pricing_tier'),
    )
    op.execute("ALTER TABLE pak_pricing_tiers ENABLE ROW LEVEL SECURITY")
    op.execute(
        "COMMENT ON TABLE pak_pricing_tiers IS "
        "'Pakistan per-fault-card A/B/C tier pricing in PKR. "
        "Mirrors pricing_tiers schema + metering_type for inverter vs non-inverter.'"
    )


def downgrade():
    op.drop_table('pak_pricing_tiers')
