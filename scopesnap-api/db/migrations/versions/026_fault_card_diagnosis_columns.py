"""fault_card_diagnosis_columns

Revision ID: 026
Revises: 025
Create Date: 2026-05-20

Track D: add action_steps, parts_needed, alternative_cards, severity, and
climate_notes columns to fault_cards and pak_fault_cards so the diagnosis
screen can display structured repair guidance without any AI runtime call.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "026"
down_revision = "025"
branch_labels = None
depends_on = None


def upgrade():
    # Columns shared by both US and PK fault card tables
    for table in ("fault_cards", "pak_fault_cards"):
        op.add_column(table, sa.Column("action_steps", JSONB, nullable=True))
        op.add_column(table, sa.Column("parts_needed", JSONB, nullable=True))
        op.add_column(table, sa.Column("alternative_cards", JSONB, nullable=True))
    # Market-specific climate notes
    op.add_column("fault_cards", sa.Column("climate_notes_us", sa.Text, nullable=True))
    op.add_column("pak_fault_cards", sa.Column("climate_notes_pk", sa.Text, nullable=True))


def downgrade():
    op.drop_column("fault_cards", "climate_notes_us")
    op.drop_column("pak_fault_cards", "climate_notes_pk")
    for table in ("fault_cards", "pak_fault_cards"):
        op.drop_column(table, "alternative_cards")
        op.drop_column(table, "parts_needed")
        op.drop_column(table, "action_steps")
