"""WS-F — Training Feedback Loop: card_feedback table

Revision ID: 010
Revises: 009
Create Date: 2026-05-01

Adds card_feedback table for YES/NO tech feedback on AI fault cards.
Used to retrain YOLO and XGBoost models.
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "card_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("card_id", sa.Integer, nullable=False),
        sa.Column("answer", sa.String(3), nullable=False),     # "yes" | "no"
        sa.Column("assessment_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("technician_id", sa.String(100), nullable=True),
        sa.Column("photo_ids", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("readings", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ix_card_feedback_card_id", "card_feedback", ["card_id"])
    op.create_index("ix_card_feedback_company", "card_feedback", ["company_id"])
    op.execute('ALTER TABLE "card_feedback" ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    op.drop_index("ix_card_feedback_company", table_name="card_feedback")
    op.drop_index("ix_card_feedback_card_id", table_name="card_feedback")
    op.drop_table("card_feedback")
