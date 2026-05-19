"""WS-NC1 — Not Cooling YES: replace phase_2_gate with suction pressure step

Revision ID: 013
Revises: 012
Create Date: 2026-05-10

Problem:
  not_cooling / q1 YES branch had `{"phase_2_gate": true, "after": {4 cards...}}`.
  The frontend's handlePhase2Gate immediately POSTed to /api/estimates/fault-card
  with card_id=null (phase_2_gate response carries no single card_id), causing
  Pydantic validation to fail → "Estimate generation failed" banner.

Fix:
  1. Insert new step not_cooling / q2-nc-suction  — tech reads suction PSI.
       low  (< 60 psi)  → Card  8: Refrigerant Leak / Low Charge
       ok   (60-110 psi) → Card 13: TXV/Metering Device Restriction
       high (> 110 psi) → Card 14: Dirty Condenser Coil
  2. Update q1 YES branch: phase_2_gate → next_step_id: q2-nc-suction

Thresholds (R-410A typical):
  Suction < 60 psi  = low refrigerant / freeze / leak
  Suction 60-110    = pressures normal → likely metering/airflow
  Suction > 110 psi = high head pressure → dirty condenser / overcharge
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    # ── Step 1: insert suction-pressure question ──────────────────────────────
    branch_logic = (
        '{'
        '"low":  {"resolve_card": 8,  "photo_slots": [{"slot": "uv_dye_glow", "photo_type": "evidence", '
        '"instruction": "UV dye glow under blacklight — for homeowner PDF.", "ai_prompt": null}]},'
        '"ok":   {"resolve_card": 13, "photo_slots": []},'
        '"high": {"resolve_card": 14, "photo_slots": [{"slot": "condenser_coil_face", "photo_type": "diagnostic", '
        '"instruction": "Face-on shot of condenser coil — capture full face.", '
        '"ai_prompt": "Grade dirt density on condenser coil face: clean / dirty / heavily_blocked. Note debris like leaves or cottonwood."}]}'
        '}'
    )
    reading_spec = (
        '{"type": "psi", "unit": "PSI", "subtype": "suction", "compare_to": null, '
        '"low_threshold": 60, "high_threshold": 110, '
        '"placeholder": "e.g. 70 PSI"}'
    )

    if _is_postgres():
        op.execute(text(f"""
            INSERT INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('not_cooling', 'q2-nc-suction', 2,
               'Read suction line pressure (low-side manifold gauge).',
               'Connect to suction service port. R-410A typical: 65-85 PSI at normal charge.',
               'reading',
               NULL,
               '{reading_spec}'::jsonb,
               NULL,
               '{branch_logic}'::jsonb,
               NULL,
               FALSE)
            ON CONFLICT (complaint_type, step_id) DO NOTHING
        """))

        # ── Step 2: rewrite q1 YES branch ─────────────────────────────────────
        # Replace the phase_2_gate block with a simple next_step_id pointer.
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{yes}',
                '{"next_step_id": "q2-nc-suction"}'::jsonb
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q1'
        """))

    else:
        # SQLite fallback (local dev)
        op.execute(text(f"""
            INSERT OR IGNORE INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('not_cooling', 'q2-nc-suction', 2,
               'Read suction line pressure (low-side manifold gauge).',
               'Connect to suction service port. R-410A typical: 65-85 PSI at normal charge.',
               'reading',
               NULL,
               '{reading_spec}',
               NULL,
               '{branch_logic}',
               NULL,
               0)
        """))

        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{"yes": {"next_step_id": "q2-nc-suction"}}'
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q1'
        """))


def downgrade() -> None:
    if _is_postgres():
        # Restore original phase_2_gate YES branch
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{yes}',
                '{
                  "phase_2_gate": true,
                  "after": {
                    "low_suction_high_superheat":   {"resolve_card": 8,  "photo_slots": [{"slot": "uv_dye_glow", "photo_type": "evidence", "instruction": "UV dye glow under blacklight.", "ai_prompt": null}]},
                    "high_discharge_dirty_airflow":  {"resolve_card": 14, "photo_slots": [{"slot": "condenser_coil_face", "photo_type": "diagnostic", "instruction": "Face-on shot of condenser coil.", "ai_prompt": "Grade dirt density on condenser coil face."}]},
                    "high_pressure_high_subcooling": {"resolve_card": 17, "photo_slots": []},
                    "normal_pressures_warm_supply":  {"resolve_card": 13, "photo_slots": []}
                  }
                }'::jsonb
            )
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q1'
        """))

        op.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-suction'
        """))
    else:
        op.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'not_cooling'
              AND step_id = 'q2-nc-suction'
        """))
