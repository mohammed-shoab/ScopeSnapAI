"""Quarantine legacy pricing_rules — fault_estimate.py uses pricing_tiers now.

Revision ID: 020
Revises: 019
Create Date: 2026-05-19

See DEC-016 in DECISIONS.md — the new fault_estimate.py engine queries
pricing_tiers (indexed by card_id), never pricing_rules. These rows are kept
for audit purposes but marked deprecated so future engineers know they are
not authoritative.
"""
from alembic import op
import sqlalchemy as sa

revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'pricing_rules',
        sa.Column('deprecated', sa.Boolean(), nullable=False, server_default='false')
    )
    op.execute("UPDATE pricing_rules SET deprecated = true")
    op.execute(
        "COMMENT ON TABLE pricing_rules IS "
        "'DEPRECATED — engine uses pricing_tiers (indexed by card_id) instead. "
        "See DEC-016 in DECISIONS.md. Do not add new rows here.'"
    )


def downgrade():
    op.drop_column('pricing_rules', 'deprecated')
