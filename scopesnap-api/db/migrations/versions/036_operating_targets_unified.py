"""036 — Phase 2: rename pak_operating_targets → operating_targets, add market column, insert US rows

Revision ID: 036
Revises: 035
Create Date: 2026-05-24

What this migration does:
  1. Renames pak_operating_targets → operating_targets (unified table for US + PK)
  2. Adds market VARCHAR(2) NOT NULL column; migrates existing PK rows to market='PK'
  3. Inserts US rows for R-410A and R-22 across 4 ambient buckets (25/30/35/40°C)
  4. Creates backward-compat view pak_operating_targets_v (market='PK' slice) so
     any older code paths survive during the transition window
  5. Adds composite index for fast market/refrigerant/ambient lookups

Rollback caveats:
  - downgrade() drops the view, drops the market column, and renames the table back.
  - The US rows inserted in upgrade() are removed. No PK data is lost.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic
revision = "036"
down_revision = "035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Rename table ──────────────────────────────────────────────────────
    op.execute(text("ALTER TABLE pak_operating_targets RENAME TO operating_targets;"))

    # ── 2. Add market column (default PK so existing rows are set correctly) ─
    op.execute(text(
        "ALTER TABLE operating_targets ADD COLUMN market VARCHAR(2) NOT NULL DEFAULT 'PK';"
    ))
    # Remove the default so future inserts must be explicit
    op.execute(text(
        "ALTER TABLE operating_targets ALTER COLUMN market DROP DEFAULT;"
    ))

    # ── 3. Insert US rows ─────────────────────────────────────────────────────
    # Authoritative values from Phase 1 Canonical PSI Threshold Table (PROJECT_BRAIN.md)
    # and board-reviewed ambient-aware targets for 4 ambient buckets (25/30/35/40°C).
    # "Hot" bucket (35°C) matches the static _us_suction/_us_discharge dicts in diagnostic.py.
    op.execute(text("""
        INSERT INTO operating_targets
            (market, refrigerant, ambient_c, suction_min_psi, suction_max_psi,
             discharge_min_psi, discharge_max_psi)
        VALUES
            -- R-410A US
            ('US', 'R-410A', 25, 95,  120, 200, 250),
            ('US', 'R-410A', 30, 105, 130, 215, 265),
            ('US', 'R-410A', 35, 115, 140, 225, 275),
            ('US', 'R-410A', 40, 125, 150, 240, 290),
            -- R-22 US
            ('US', 'R-22',   25, 48,  70,  130, 250),
            ('US', 'R-22',   30, 52,  75,  140, 265),
            ('US', 'R-22',   35, 55,  78,  150, 275),
            ('US', 'R-22',   40, 60,  82,  165, 290);
    """))

    # ── 4. Backward-compat view for old code referencing pak_operating_targets ─
    op.execute(text("""
        CREATE VIEW pak_operating_targets_v AS
            SELECT * FROM operating_targets WHERE market = 'PK';
    """))

    # ── 5. Composite index for unified lookups ────────────────────────────────
    op.execute(text(
        "CREATE INDEX idx_operating_targets_market_ref_amb "
        "ON operating_targets (market, refrigerant, ambient_c DESC);"
    ))

    # ── 6. Section 6: update hint_text to reflect ambient-aware design ────────
    # Thresholds remain 115/141 (suction) and 225/276 (discharge) — set by migration 035.
    # Only hint_text is updated to explain that range varies with ambient selection.
    op.execute(text("""
        UPDATE diagnostic_questions
        SET hint_text = 'Read suction PSI. We compare against the right range for the outdoor ambient you selected above. R-410A normal: 115-140 at 95°F outdoor; range shifts ~5 PSI per 5°F above 95°F.'
        WHERE step_id = 'q2-nc-suction';
    """))
    op.execute(text("""
        UPDATE diagnostic_questions
        SET hint_text = 'Read discharge PSI. R-410A normal: 225-275 at 95°F outdoor; varies with ambient. Above range → dirty condenser or overcharge.'
        WHERE step_id = 'q2-nc-discharge';
    """))
    op.execute(text("""
        UPDATE diagnostic_questions
        SET hint_text = 'Hissing often indicates refrigerant leak or TXV chatter. R-410A normal suction: 115-140 PSI at 95°F ambient; varies with outdoor temp.'
        WHERE step_id = 'q2-hiss-suction';
    """))
    op.execute(text("""
        UPDATE diagnostic_questions
        SET hint_text = 'Read suction PSI. Low reading = undercharge = ice formation = dripping. R-410A normal: 115-140 PSI at 95°F outdoor; varies with ambient.'
        WHERE step_id = 'q2-wd-suction';
    """))


def downgrade() -> None:
    # Reverse order: drop index → drop view → drop US rows → drop market col → rename back
    op.execute(text("DROP INDEX IF EXISTS idx_operating_targets_market_ref_amb;"))
    op.execute(text("DROP VIEW IF EXISTS pak_operating_targets_v;"))
    op.execute(text("DELETE FROM operating_targets WHERE market = 'US';"))
    op.execute(text("ALTER TABLE operating_targets DROP COLUMN market;"))
    op.execute(text("ALTER TABLE operating_targets RENAME TO pak_operating_targets;"))

    # Restore Phase 1 hint_text (Phase 2 wording rolled back)
    op.execute(text("""
        UPDATE diagnostic_questions
        SET hint_text = 'Connect to suction service port. R-410A normal: 115-140 PSI at 95°F outdoor ambient. R-22 normal: 55-78 PSI. Add ~5-8 PSI per 5°F above 95°F.'
        WHERE step_id = 'q2-nc-suction';
    """))
    op.execute(text("""
        UPDATE diagnostic_questions
        SET hint_text = 'R-410A normal discharge: 225-275 PSI at 95°F outdoor ambient. Above 275 suggests dirty condenser or overcharge.'
        WHERE step_id = 'q2-nc-discharge';
    """))
