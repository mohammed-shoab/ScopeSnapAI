"""
Migration 016 — Data Repo Better Options + Defaults + Replacement Costs
Adds:
  - better_option_estimate JSONB column to fault_cards
  - data_defaults table (market-level defaults from ac_data_repo)
  - replacement_cost_estimates table (cost by tonnage)
Safe to re-run (IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).
"""
from sqlalchemy import text
from db.database import AsyncSessionLocal
import asyncio


async def upgrade():
    async with AsyncSessionLocal() as db:
        # 1. Add better_option_estimate to fault_cards
        await db.execute(text("""
            ALTER TABLE fault_cards
                ADD COLUMN IF NOT EXISTS better_option_estimate JSONB
        """))

        # 2. Create data_defaults table
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS data_defaults (
                id                   SERIAL PRIMARY KEY,
                market               TEXT,
                refrigerant_by_year  JSONB,
                cap_uf_by_tonnage     JSONB,
                electrical_by_tonnage JSONB,
                tech_warning         TEXT,
                inverter_note        TEXT,
                created_at           TIMESTAMPTZ DEFAULT NOW()
            )
        """))

        # 3. Create replacement_cost_estimates table
        await db.execute(text("""
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

        await db.commit()
        print("Migration 016 complete.")


if __name__ == "__main__":
    asyncio.run(upgrade())
