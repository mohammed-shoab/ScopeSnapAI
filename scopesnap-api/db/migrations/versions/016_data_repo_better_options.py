"""016 — Data Repo Better Options + Defaults + Replacement Costs

Adds:
  - better_option_estimate JSONB column to fault_cards
  - data_defaults table (market-level defaults from ac_data_repo)
  - replacement_cost_estimates table (cost by tonnage)

Safe to re-run (IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).

Revision ID: 016
Revises: 015
Create Date: 2026-05-13
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Add better_option_estimate to fault_cards
    bind.execute(text("""
        ALTER TABLE fault_cards
            ADD COLUMN IF NOT EXISTS better_option_estimate JSONB
    """))

    # 2. Create data_defaults table
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS data_defaults (
            id                    SERIAL PRIMARY KEY,
            market                TEXT,
            refrigerant_by_year   JSONB,
            cap_uf_by_tonnage      JSONB,
            electrical_by_tonnage  JSONB,
            tech_warning          TEXT,
            inverter_note         TEXT,
            created_at            TIMESTAMPTZ DEFAULT NOW()
        )
    """))

    # 3. Create replacement_cost_estimates table
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS replacement_cost_estimates (
            id            SERIAL PRIMARY KEY,
            tonnage       NUMERIC,
            price_min     INTEGER,
            price_max     INTEGER,
            price_typical INTEGER,
            notes         TEXT,
            created_at    TIMESTAMPTZ DEFAULT NOW()
        )
    """))


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("DROP TABLE IF EXISTS replacement_cost_estimates"))
    bind.execute(text("DROP TABLE IF EXISTS data_defaults"))
    bind.execute(text("ALTER TABLE fault_cards DROP COLUMN IF EXISTS better_option_estimate"))
