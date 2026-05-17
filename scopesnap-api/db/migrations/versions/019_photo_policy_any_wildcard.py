"""019 — Photo policy: "photo_submitted" + "any" wildcard for all non-service photo steps

Revision ID: 019
Revises: 018
Create Date: 2026-05-16

Problem (SOW Task 6)
---------------------
Photos must never block routing.  Before this migration, any photo/multi step
that received a submitted photo with no explicit branch_key (or with the new
"photo_submitted" branch_key added to DiagnosticFlow.handlePhoto) would fail
_follow_branch, escalate the session, and terminate the diagnostic flow.

The service photo steps (svc-1-filter, svc-2-cap, svc-3-coil, svc-5-terminals)
were already handled in migration 017.  This migration covers all non-service
photo/multi steps used in the main DiagnosticFlow component.

Steps covered
-------------
The PHOTO_SKIP_CONFIG map in DiagnosticFlow.tsx is the authoritative list of
photo/multi steps.  Non-service entries (excluding error_code/q1 which uses a
special extract_then_lookup action that bypasses _follow_branch):

  Step                  Complaint type        "any" target
  ──────────────────────────────────────────────────────────────────
  q2-thermal-photo      intermittent_shutdown  next_step: q3-visual-photo
  q3-visual-photo       intermittent_shutdown  next_step: q4-ir-readings
  q4-board-photo        error_code             resolve_card: 7
  q5-contactor          making_noise           soft-escalate (choice step)
  q2-filter-photo       high_electric_bill     soft-escalate (choice step)
  q2-pan-photo          water_dripping         soft-escalate (multi/water-check)

For the three "choice" steps (contactor, filter, drain-pan), the backend
escalates with a soft reason string.  DiagnosticFlow.tsx (Task-6 frontend
fix) catches photo/multi escalation, shows a warning inline, and keeps the
current step active — the tech then uses the skip-choice buttons to route.

"photo_submitted" and "any" keys are both added so that:
  - DiagnosticFlow.handlePhoto (sends branch_key="photo_submitted") routes via
    the explicit entry if present.
  - Any other unrecognised branch_key falls to the "any" wildcard.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "019"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


# ── Step routing table ────────────────────────────────────────────────────────
#
# Each entry is (complaint_type, step_id, patch_json).
# Routing targets derived from DiagnosticFlow.tsx PHOTO_SKIP_CONFIG comments.

_SOFT_ESCALATE = (
    '{"escalate": true, '
    '"reason": "Photo submitted — condition unknown. Use manual selection below."}'
)

_PATCHES = [
    # H-YES: thermal camera — advance to 4-step visual path if photo submitted
    (
        "intermittent_shutdown",
        "q2-thermal-photo",
        (
            '{"photo_submitted": {"next_step_id": "q3-visual-photo"}, '
            '"any":             {"next_step_id": "q3-visual-photo"}}'
        ),
    ),
    # H-NO: terminal strip visual — advance to IR readings
    (
        "intermittent_shutdown",
        "q3-visual-photo",
        (
            '{"photo_submitted": {"next_step_id": "q4-ir-readings"}, '
            '"any":             {"next_step_id": "q4-ir-readings"}}'
        ),
    ),
    # C-YES-ERROR: control board LED photo → resolve Card #7 (control board trip)
    (
        "error_code",
        "q4-board-photo",
        (
            '{"photo_submitted": {"resolve_card": 7}, '
            '"any":             {"resolve_card": 7}}'
        ),
    ),
    # D-Grinding: contactor face photo — choice step; soft-escalate so skip
    # buttons remain active in DiagnosticFlow's soft photo escalation handler
    (
        "making_noise",
        "q5-contactor",
        (
            '{"photo_submitted": ' + _SOFT_ESCALATE + ', '
            '"any": ' + _SOFT_ESCALATE + '}'
        ),
    ),
    # E-YES: filter face photo (high_electric_bill) — choice step; soft-escalate
    (
        "high_electric_bill",
        "q2-filter-photo",
        (
            '{"photo_submitted": ' + _SOFT_ESCALATE + ', '
            '"any": ' + _SOFT_ESCALATE + '}'
        ),
    ),
    # B-Indoor: drain pan multi step (water_dripping) — water-check; soft-escalate
    (
        "water_dripping",
        "q2-pan-photo",
        (
            '{"photo_submitted": ' + _SOFT_ESCALATE + ', '
            '"any": ' + _SOFT_ESCALATE + '}'
        ),
    ),
]


def upgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    for complaint_type, step_id, patch in _PATCHES:
        if pg:
            bind.execute(text(f"""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb = branch_logic_jsonb || '{patch}'::jsonb
                WHERE complaint_type = :ct
                  AND step_id = :sid
            """), {"ct": complaint_type, "sid": step_id})
        else:
            bind.execute(text(f"""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb = json_patch(branch_logic_jsonb, '{patch}')
                WHERE complaint_type = :ct
                  AND step_id = :sid
            """), {"ct": complaint_type, "sid": step_id})


def downgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    for complaint_type, step_id, _ in _PATCHES:
        if pg:
            bind.execute(text("""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb =
                    branch_logic_jsonb - 'photo_submitted' - 'any'
                WHERE complaint_type = :ct
                  AND step_id = :sid
            """), {"ct": complaint_type, "sid": step_id})
        else:
            bind.execute(text("""
                UPDATE diagnostic_questions
                SET branch_logic_jsonb =
                    json_remove(
                        json_remove(branch_logic_jsonb, '$.photo_submitted'),
                        '$.any'
                    )
                WHERE complaint_type = :ct
                  AND step_id = :sid
            """), {"ct": complaint_type, "sid": step_id})
