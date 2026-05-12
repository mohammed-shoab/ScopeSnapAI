"""015 — Fix BUG #13: patch options_jsonb for not_heating/q4-flame-sensor

Revision ID: 015
Revises: 014
Create Date: 2026-05-11

Root cause of lingering BUG #13
---------------------------------
Migration 014 attempted to fix the flame-sensor micro-amps type mismatch by
patching the ``reading_spec`` column:

    UPDATE diagnostic_questions
    SET reading_spec = jsonb_set(reading_spec, '{type}', '"microamps"')
    WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'

However, q4-flame-sensor uses ``input_type = 'multi'``, which means the
reading spec is NOT stored in the standalone ``reading_spec`` column — it
lives inside ``options_jsonb`` as an array element:

    [
      {"kind": "photo", "spec": {...}},
      {"kind": "reading", "spec": {"type": "micro_amps", "unit": "uA", ...}}
    ]

The ``reading_spec`` column for this row is NULL, so migration 014's UPDATE
was a no-op.  The frontend ``classifyReading()`` function checks
``spec.type === "microamps"`` (no underscore) and never matched — falling
through to the generic branchKey:"ok" path, which the backend routes to
``{escalate: true}``.

Fix
---
Update the ``options_jsonb`` array for ``not_heating/q4-flame-sensor``:
change the reading element's ``spec.type`` from ``"micro_amps"`` to
``"microamps"`` (matching all other microamps steps and the frontend handler).

After this migration, entering 0.5 µA will produce branchKey "low" → Card #11
(Ignitor/Flame Sensor replacement), and 3 µA will produce branchKey "ok" →
escalate (sensor good, investigate gas pressure/valve).
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    if pg:
        # Walk options_jsonb array; for the element where kind='reading' and
        # spec.type='micro_amps', rewrite spec.type to 'microamps'.
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = (
                SELECT jsonb_agg(
                    CASE
                        WHEN (elem->>'kind') = 'reading'
                             AND (elem->'spec'->>'type') = 'micro_amps'
                        THEN jsonb_set(elem, '{spec,type}', '"microamps"'::jsonb)
                        ELSE elem
                    END
                )
                FROM jsonb_array_elements(options_jsonb) AS elem
            )
            WHERE complaint_type = 'not_heating'
              AND step_id = 'q4-flame-sensor'
        """))
    else:
        # SQLite: replace the full options_jsonb with the corrected array.
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = '[
                {"kind": "photo", "spec": {
                    "ai_prompt": "Detect oxide coating on flame sensor. Classes: clean / light_oxide / heavy_oxide.",
                    "slot_name": "flame_sensor_rod",
                    "photo_type": "diagnostic",
                    "instruction": "Flame sensor rod - show full surface."
                }},
                {"kind": "reading", "spec": {
                    "type": "microamps",
                    "unit": "uA",
                    "placeholder": ">2 uA healthy, <1 uA replace"
                }}
            ]'
            WHERE complaint_type = 'not_heating'
              AND step_id = 'q4-flame-sensor'
        """))


def downgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = (
                SELECT jsonb_agg(
                    CASE
                        WHEN (elem->>'kind') = 'reading'
                             AND (elem->'spec'->>'type') = 'microamps'
                        THEN jsonb_set(elem, '{spec,type}', '"micro_amps"'::jsonb)
                        ELSE elem
                    END
                )
                FROM jsonb_array_elements(options_jsonb) AS elem
            )
            WHERE complaint_type = 'not_heating'
              AND step_id = 'q4-flame-sensor'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = '[
                {"kind": "photo", "spec": {
                    "ai_prompt": "Detect oxide coating on flame sensor. Classes: clean / light_oxide / heavy_oxide.",
                    "slot_name": "flame_sensor_rod",
                    "photo_type": "diagnostic",
                    "instruction": "Flame sensor rod - show full surface."
                }},
                {"kind": "reading", "spec": {
                    "type": "micro_amps",
                    "unit": "uA",
                    "placeholder": ">2 uA healthy, <1 uA replace"
                }}
            ]'
            WHERE complaint_type = 'not_heating'
              AND step_id = 'q4-flame-sensor'
        """))
