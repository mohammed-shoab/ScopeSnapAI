# coding: utf-8
"""Seed pak_pricing_tiers with 45 rows (15 PK cards x 3 tiers x metering_type=any).

Revision ID: 023
Revises: 022
Create Date: 2026-05-19

Prices in PKR. Source: Karachi/Lahore market research verified 2026-05-19.
metering_type='any' is the v1 default. Inverter-specific rows can be added later.
"""
from alembic import op

revision = '023'
down_revision = '022'
branch_labels = None
depends_on = None

_ROWS = [
    # (card_id, tier, amount_pkr, metering_type)
    (1, 'A', 1500, 'any'),
    (1, 'B', 3500, 'any'),
    (1, 'C', 6500, 'any'),
    (2, 'A', 800, 'any'),
    (2, 'B', 1800, 'any'),
    (2, 'C', 4500, 'any'),
    (3, 'A', 8000, 'any'),
    (3, 'B', 12000, 'any'),
    (3, 'C', 28000, 'any'),
    (4, 'A', 3500, 'any'),
    (4, 'B', 6500, 'any'),
    (4, 'C', 14000, 'any'),
    (5, 'A', 500, 'any'),
    (5, 'B', 1500, 'any'),
    (5, 'C', 3500, 'any'),
    (6, 'A', 1200, 'any'),
    (6, 'B', 3500, 'any'),
    (6, 'C', 8500, 'any'),
    (7, 'A', 1800, 'any'),
    (7, 'B', 3200, 'any'),
    (7, 'C', 7500, 'any'),
    (8, 'A', 3500, 'any'),
    (8, 'B', 6500, 'any'),
    (8, 'C', 18000, 'any'),
    (9, 'A', 1500, 'any'),
    (9, 'B', 3500, 'any'),
    (9, 'C', 9500, 'any'),
    (10, 'A', 13000, 'any'),
    (10, 'B', 22000, 'any'),
    (10, 'C', 110000, 'any'),
    (11, 'A', 1500, 'any'),
    (11, 'B', 3500, 'any'),
    (11, 'C', 8500, 'any'),
    (13, 'A', 1500, 'any'),
    (13, 'B', 3500, 'any'),
    (13, 'C', 8500, 'any'),
    (14, 'A', 2000, 'any'),
    (14, 'B', 4500, 'any'),
    (14, 'C', 9500, 'any'),
    (16, 'A', 2500, 'any'),
    (16, 'B', 5500, 'any'),
    (16, 'C', 16000, 'any'),
    (18, 'A', 85000, 'any'),
    (18, 'B', 110000, 'any'),
    (18, 'C', 220000, 'any')
]


def upgrade():
    for card_id, tier, amount, mt in _ROWS:
        op.execute(
            f"INSERT INTO pak_pricing_tiers (card_id, tier, estimate_amount, metering_type) "
            f"VALUES ({card_id}, '{tier}', {amount}, '{mt}') "
            f"ON CONFLICT ON CONSTRAINT uq_pak_pricing_tier DO UPDATE "
            f"SET estimate_amount = EXCLUDED.estimate_amount"
        )


def downgrade():
    op.execute("DELETE FROM pak_pricing_tiers WHERE metering_type = 'any'")
