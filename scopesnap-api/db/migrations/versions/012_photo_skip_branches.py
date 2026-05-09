"""WS-A4 — Photo skip branches: thermal reroute + error_code manual entry

Revision ID: 012
Revises: 011
Create Date: 2026-05-09

Adds two branch_logic entries so the frontend skip handlers can route
without requiring photos:

  intermittent_shutdown / q2-thermal-photo
    "skip" → {"next_step_id": "q3-visual-photo"}
    Allows tech to skip thermal camera and fall to the 4-step Path B.

  error_code / q1
    "skipped" → {"next_step_id": "q4-reset"}
    Allows tech to type the error code manually; routes to nuisance-reset
    fallback (same as lockout_trip / nuisance_or_unknown).

All other photo skips are handled via frontend branch_key overrides that
hit existing "any" wildcards — no DB change needed for those.
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers
revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    if _is_postgres():
        # PostgreSQL: native JSONB merge operator
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb =
                branch_logic_jsonb || '{"skip": {"next_step_id": "q3-visual-photo"}}'::jsonb
            WHERE complaint_type = 'intermittent_shutdown'
              AND step_id = 'q2-thermal-photo'
        """))
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb =
                branch_logic_jsonb || '{"skipped": {"next_step_id": "q4-reset"}}'::jsonb
            WHERE complaint_type = 'error_code'
              AND step_id = 'q1'
        """))
    else:
        # SQLite: json_patch() merges two JSON objects (available since SQLite 3.38)
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb =
                json_patch(branch_logic_jsonb, '{"skip": {"next_step_id": "q3-visual-photo"}}')
            WHERE complaint_type = 'intermittent_shutdown'
              AND step_id = 'q2-thermal-photo'
        """))
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb =
                json_patch(branch_logic_jsonb, '{"skipped": {"next_step_id": "q4-reset"}}')
            WHERE complaint_type = 'error_code'
              AND step_id = 'q1'
        """))


def downgrade() -> None:
    if _is_postgres():
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = branch_logic_jsonb - 'skip'
            WHERE complaint_type = 'intermittent_shutdown'
              AND step_id = 'q2-thermal-photo'
        """))
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = branch_logic_jsonb - 'skipped'
            WHERE complaint_type = 'error_code'
              AND step_id = 'q1'
        """))
    else:
        # SQLite: rebuild without the key via json_remove()
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_remove(branch_logic_jsonb, '$.skip')
            WHERE complaint_type = 'intermittent_shutdown'
              AND step_id = 'q2-thermal-photo'
        """))
        op.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_remove(branch_logic_jsonb, '$.skipped')
            WHERE complaint_type = 'error_code'
              AND step_id = 'q1'
        """))
