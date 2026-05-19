"""017 — Service checklist: add "any" wildcard + "photo_submitted" branches to photo steps

Revision ID: 017
Revises: 016
Create Date: 2026-05-16

Problem
-------
Service checklist photo steps (svc-2-cap, svc-3-coil, svc-5-terminals)
have no branch for the key the frontend now sends ("photo_submitted") and
no "any" wildcard fallback.

When a photo was submitted:
  1. _compute_branch_key returned a garbage stringified-dict key (old) or
     "photo_submitted" (after frontend fix in Task 4).
  2. _follow_branch found no matching branch → escalated the session.
  3. ServiceChecklist.tsx had no escalation handler → UI stalled.

Fix (DB side)
-------------
For every service/* step that has input_type='photo' or input_type='multi',
add both:
  "photo_submitted": {"next_step_id": "<next>"}
  "any":             {"next_step_id": "<next>"}

This ensures ANY answer value (photo_submitted, AI grade, or empty) advances
to the next step.  Matches SOW Task-6 requirement: photos must never block routing.

Step ordering (inferred from STEP_LABELS in ServiceChecklist.tsx):
  svc-1-filter  → svc-2-cap
  svc-2-cap     → svc-3-coil
  svc-3-coil    → svc-4-drain
  svc-4-drain   → svc-5-terminals
  svc-5-terminals → svc-6-amps
  svc-6-amps    → svc-7-deltaT
  svc-7-deltaT  → svc-8-run
  svc-8-run     → (terminal — service_complete)
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


# Mapping: photo/multi step_id → next step_id
_PHOTO_STEP_NEXT: dict[str, str] = {
    "svc-2-cap":       "svc-3-coil",
    "svc-3-coil":      "svc-4-drain",
    "svc-5-terminals": "svc-6-amps",
}


def upgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    for step_id, next_step_id in _PHOTO_STEP_NEXT.items():
        patch = (
            f'{{"photo_submitted": {{"next_step_id": "{next_step_id}"}}, '
            f'"any": {{"next_step_id": "{next_step_id}"}}}}'
        )

        if pg:
            bind.execute(text(f"""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb = branch_logic_jsonb || '{patch}'::jsonb
                WHERE complaint_type = 'service'
                  AND step_id = '{step_id}'
                  AND input_type IN ('photo', 'multi')
            """))
        else:
            bind.execute(text(f"""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb = json_patch(branch_logic_jsonb, '{patch}')
                WHERE complaint_type = 'service'
                  AND step_id = '{step_id}'
                  AND input_type IN ('photo', 'multi')
            """))

    # svc-1-filter also gets a photo fallback (filter photo is optional pre-read)
    filter_patch = (
        '{"photo_submitted": {"next_step_id": "svc-2-cap"}, '
        '"any": {"next_step_id": "svc-2-cap"}}'
    )
    if pg:
        bind.execute(text(f"""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = branch_logic_jsonb || '{filter_patch}'::jsonb
            WHERE complaint_type = 'service'
              AND step_id = 'svc-1-filter'
              AND input_type IN ('photo', 'multi')
        """))
    else:
        bind.execute(text(f"""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(branch_logic_jsonb, '{filter_patch}')
            WHERE complaint_type = 'service'
              AND step_id = 'svc-1-filter'
              AND input_type IN ('photo', 'multi')
        """))


def downgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    all_steps = list(_PHOTO_STEP_NEXT.keys()) + ["svc-1-filter"]
    for step_id in all_steps:
        if pg:
            bind.execute(text(f"""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb =
                    branch_logic_jsonb - 'photo_submitted' - 'any'
                WHERE complaint_type = 'service'
                  AND step_id = '{step_id}'
            """))
        else:
            bind.execute(text(f"""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb =
                    json_remove(json_remove(branch_logic_jsonb, '$.photo_submitted'), '$.any')
                WHERE complaint_type = 'service'
                  AND step_id = '{step_id}'
            """))
