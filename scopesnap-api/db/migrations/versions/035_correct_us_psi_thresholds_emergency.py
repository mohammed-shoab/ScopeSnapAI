"""035 — Emergency patch: correct R-410A US PSI thresholds (Priority 0)

Revision ID: 035
Revises: 034
Create Date: 2026-05-24

Problem
-------
Migration 013 set q2-nc-suction low_threshold=60, high_threshold=110 and
hint_text "R-410A typical: 65-85 PSI at normal charge". Those numbers are
R-22 suction pressures, not R-410A. Later migration raised high_threshold
to 145 but left the wrong low_threshold (60) and wrong hint_text.

Effect: a tech reading 80 PSI on an R-410A system (genuinely low charge)
was routed to "ok" (TXV/Metering), not "low" (Refrigerant Leak). This is
a clinical error that could lead to a wrong diagnosis.

Authoritative values (sourced 2026-05-24 from 4 industry references:
AC Direct, Inspectapedia, HVAC-Talk, AristotleAir):
  R-410A US suction at 95F ambient: 115-140 PSI normal; 141+ = high
  R-410A US discharge at 95F ambient: 225-275 PSI normal; 276+ = high

Fix
---
All US-market suction rows updated: low_threshold=115, high_threshold=141
All US-market discharge rows updated: low_threshold=225, high_threshold=276
Hint texts corrected to show accurate R-410A reference values.

Rows affected:
  - not_cooling / q2-nc-suction   (was 60/145 hint wrong)
  - not_cooling / q2-nc-discharge (was 250/350)
  - making_noise / q2-hiss-suction (was 60/145 hint wrong)
  - water_dripping / q2-wd-suction (was 60/145)

DEC reference: Priority 0 emergency patch. Architectural rewrite
(ambient-aware dynamic lookup) is Phase 2.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "035"
down_revision: Union[str, None] = "034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # ── q2-nc-suction: correct thresholds + hint ─────────────────────────────
    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '115'),
                '{high_threshold}', '141'
            ),
            hint_text = 'Connect to suction service port. R-410A normal: 115-140 PSI at 95°F outdoor ambient. R-22 normal: 55-78 PSI. Add ~5-8 PSI per 5°F above 95°F.'
        WHERE complaint_type = 'not_cooling'
          AND step_id = 'q2-nc-suction';
    """))

    # ── q2-nc-discharge: correct thresholds + hint ───────────────────────────
    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '225'),
                '{high_threshold}', '276'
            ),
            hint_text = 'R-410A normal discharge: 225-275 PSI at 95°F outdoor ambient. Above 275 suggests dirty condenser or overcharge.'
        WHERE complaint_type = 'not_cooling'
          AND step_id = 'q2-nc-discharge';
    """))

    # ── q2-hiss-suction: correct thresholds + hint ───────────────────────────
    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '115'),
                '{high_threshold}', '141'
            ),
            hint_text = 'Hissing often indicates refrigerant leak or TXV chatter. R-410A normal suction: 115-140 PSI at 95°F ambient.'
        WHERE complaint_type = 'making_noise'
          AND step_id = 'q2-hiss-suction';
    """))

    # ── q2-wd-suction: correct thresholds ────────────────────────────────────
    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '115'),
                '{high_threshold}', '141'
            ),
            hint_text = 'Connect to suction service port. R-410A normal: 115-140 PSI at 95°F ambient. Low reading = refrigerant undercharge = ice formation = dripping.'
        WHERE complaint_type = 'water_dripping'
          AND step_id = 'q2-wd-suction';
    """))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # Restore prior values (pre-035 state)
    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '60'),
                '{high_threshold}', '145'
            ),
            hint_text = 'Connect to suction service port. R-410A typical: 65-85 PSI at normal charge.'
        WHERE complaint_type = 'not_cooling'
          AND step_id = 'q2-nc-suction';
    """))

    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '250'),
                '{high_threshold}', '350'
            ),
            hint_text = 'R-410A typical: 225-250 PSI normal. Above 350 PSI suggests overcharge or non-condensables.'
        WHERE complaint_type = 'not_cooling'
          AND step_id = 'q2-nc-discharge';
    """))

    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '60'),
                '{high_threshold}', '145'
            ),
            hint_text = 'Hissing often indicates refrigerant leak or TXV chatter. R-410A normal suction: 60-110 PSI.'
        WHERE complaint_type = 'making_noise'
          AND step_id = 'q2-hiss-suction';
    """))

    op.execute(text("""
        UPDATE diagnostic_questions
        SET
            reading_spec = jsonb_set(
                jsonb_set(reading_spec::jsonb, '{low_threshold}', '60'),
                '{high_threshold}', '145'
            ),
            hint_text = 'Connect to suction service port. Outdoor drip often signals refrigerant charge issue.'
        WHERE complaint_type = 'water_dripping'
          AND step_id = 'q2-wd-suction';
    """))
