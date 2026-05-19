"""018 — Phase 2 refrigerant fault differentiation via discharge PSI

Revision ID: 018
Revises: 017
Create Date: 2026-05-16

Problem
-------
Migration 013 routed high suction PSI (>110) directly to Card #14
(Dirty Condenser Coil).  This collapses two clinically distinct
conditions into one card:

  • Card #14  Dirty Condenser   — suction high, discharge 250–350 PSI
  • Card #17  Refrigerant Overcharge — suction high, discharge > 350 PSI

Without discharge PSI the technician can misdiagnose overcharge as a
dirty coil, leading to unnecessary cleaning rather than refrigerant
recovery.

Fix
---
1. Insert new step  not_cooling / q2-nc-discharge
     input_type = reading  (PSI, subtype = discharge)
     Branches:
       low  (< 250 PSI) → escalate  (unusual: high suction + low discharge)
       ok   (250–350 PSI) → Card #14  (Dirty Condenser — confirm with photo)
       high (> 350 PSI)   → Card #17  (Refrigerant Overcharge)

2. Update q2-nc-suction "high" branch
     FROM:  {"resolve_card": 14, "photo_slots": [...]}
     TO:    {"next_step_id": "q2-nc-discharge"}

Discharge PSI thresholds (R-410A @ 95 °F ambient, sea level):
  Normal    ~225–250 PSI
  Elevated  ~250–350 PSI  (dirty condenser, airflow restriction)
  High      > 350 PSI     (overcharge, non-condensable gases)
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


# ── Shared constants ──────────────────────────────────────────────────────────

_READING_SPEC = (
    '{"type": "psi", "unit": "PSI", "subtype": "discharge", "compare_to": null, '
    '"low_threshold": 250, "high_threshold": 350, '
    '"placeholder": "e.g. 300 PSI"}'
)

# "ok" path keeps the condenser-coil evidence photo from the original Card-14 branch.
# "high" (overcharge) gets no specific photo — refrigerant scale reading is verbal.
# "low" escalates — unusual combination warrants manual review.
_BRANCH_LOGIC = (
    '{'
    '"low":  {"escalate": true, "escalation_note": "Unexpected: high suction + low discharge. Check for compressor valve failure or blocked suction line."},'
    '"ok":   {"resolve_card": 14, "photo_slots": [{"slot": "condenser_coil_face", "photo_type": "diagnostic", '
    '"instruction": "Face-on shot of condenser coil — capture full face.", '
    '"ai_prompt": "Grade dirt density on condenser coil face: clean / dirty / heavily_blocked. Note debris like leaves or cottonwood."}]},'
    '"high": {"resolve_card": 17, "photo_slots": []}'
    '}'
)


def upgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    # ── 1. Insert discharge PSI question ──────────────────────────────────────
    if pg:
        bind.execute(text(f"""
            INSERT INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('not_cooling', 'q2-nc-discharge', 3,
               'Now read the discharge line pressure (high-side manifold gauge).',
               'R-410A typical: 225-250 PSI normal. Above 350 PSI suggests overcharge or non-condensables.',
               'reading',
               NULL,
               '{_READING_SPEC}'::jsonb,
               NULL,
               '{_BRANCH_LOGIC}'::jsonb,
               NULL,
               FALSE)
            ON CONFLICT (complaint_type, step_id) DO NOTHING
        """))

        # ── 2. Redirect q2-nc-suction "high" branch to new discharge step ────
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{high}',
                '{"next_step_id": "q2-nc-discharge"}'::jsonb
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-suction'
        """))

    else:
        # SQLite fallback (local dev / CI)
        bind.execute(text(f"""
            INSERT OR IGNORE INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('not_cooling', 'q2-nc-discharge', 3,
               'Now read the discharge line pressure (high-side manifold gauge).',
               'R-410A typical: 225-250 PSI normal. Above 350 PSI suggests overcharge or non-condensables.',
               'reading',
               NULL,
               '{_READING_SPEC}',
               NULL,
               '{_BRANCH_LOGIC}',
               NULL,
               0)
        """))

        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{"high": {"next_step_id": "q2-nc-discharge"}}'
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-suction'
        """))


def downgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    # Restore q2-nc-suction "high" branch to original Card-14 resolution
    original_high = (
        '{"resolve_card": 14, "photo_slots": [{"slot": "condenser_coil_face", '
        '"photo_type": "diagnostic", '
        '"instruction": "Face-on shot of condenser coil — capture full face.", '
        '"ai_prompt": "Grade dirt density on condenser coil face: clean / dirty / heavily_blocked. '
        'Note debris like leaves or cottonwood."}]}'
    )

    if pg:
        bind.execute(text(f"""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{{high}}',
                '{original_high}'::jsonb
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-suction'
        """))

        bind.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-discharge'
        """))

    else:
        bind.execute(text(f"""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{{"high": {original_high}}}'
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-suction'
        """))

        bind.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-discharge'
        """))
