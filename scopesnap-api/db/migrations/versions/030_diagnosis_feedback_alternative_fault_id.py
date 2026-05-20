"""diagnosis_feedback_alternative_fault_id

Revision ID: 030
Revises: 029
Create Date: 2026-05-20

Track DX (DX.6): Add alternative_fault_id column to diagnosis_feedback
so the structured fault picker modal can record which card the tech
selected instead of free text.

NOTE: Both US and PK markets share the same diagnosis_feedback table.
pak_diagnosis_feedback does not exist in prod (PK diagnostic sessions
write to the same diagnosis_feedback table). Do NOT add a pak_ variant
here.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "030"
down_revision: Union[str, None] = "029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "diagnosis_feedback",
        sa.Column("alternative_fault_id", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("diagnosis_feedback", "alternative_fault_id")
