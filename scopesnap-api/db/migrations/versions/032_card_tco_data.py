"""032 — add card_tco_data + pak_card_tco_data (Track G)

Revision ID: 032
Revises: 031
Create Date: 2026-05-21

Creates per-card TCO lookup tables for US (Houston) and Pakistan markets.
Tables were pre-seeded directly via Supabase MCP; this migration is idempotent
(CREATE TABLE IF NOT EXISTS) so Railway deploy will not fail on re-run.
"""
from alembic import op

revision = "032"
down_revision = "031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS card_tco_data (
            id                          SERIAL PRIMARY KEY,
            card_id                     INTEGER NOT NULL,
            tier                        VARCHAR(1) NOT NULL,
            prob_major_repair_5yr_pct   NUMERIC(5,2) NOT NULL,
            prob_range                  VARCHAR(20),
            avg_repair_cost_usd_if_event NUMERIC(10,2),
            energy_savings_5yr_usd      NUMERIC(10,2),
            source_notes                TEXT,
            created_at                  TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_card_tco_data_card_tier UNIQUE (card_id, tier)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS pak_card_tco_data (
            id                           SERIAL PRIMARY KEY,
            card_id                      INTEGER NOT NULL,
            tier                         VARCHAR(1) NOT NULL,
            prob_major_repair_5yr_pct    NUMERIC(5,2) NOT NULL,
            prob_range                   VARCHAR(20),
            avg_repair_cost_pkr_if_event NUMERIC(12,2),
            energy_savings_5yr_pkr       NUMERIC(12,2),
            source_notes                 TEXT,
            created_at                   TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_pak_card_tco_data_card_tier UNIQUE (card_id, tier)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS pak_card_tco_data")
    op.execute("DROP TABLE IF EXISTS card_tco_data")
