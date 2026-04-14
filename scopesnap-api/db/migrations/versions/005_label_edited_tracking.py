"""Add label_edited tracking to assessments

Revision ID: 005
Revises: 004
Create Date: 2026-04-15

Adds:
- label_edited (bool): True whenever a tech changes the AI-generated fault
  diagnosis. Used to flag assessments for the retraining pipeline.
- issue_change_count (int): Number of times the label has been changed on
  this assessment. Quick metric for AI accuracy without querying JSON.

The full change history (original label, new label, timestamp, tech_id) is
stored in assessments.tech_overrides._issue_change_log as a JSON array.
"""

from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Flag for retraining pipeline — easy to query vs parsing JSON
    op.add_column(
        "assessments",
        sa.Column(
            "label_edited",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Count of label changes — product metric for AI accuracy tracking
    op.add_column(
        "assessments",
        sa.Column(
            "issue_change_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )

    # Index for retraining pipeline: quickly find all edited assessments
    op.create_index(
        "ix_assessments_label_edited",
        "assessments",
        ["label_edited"],
        postgresql_where=sa.text("label_edited = true"),
    )


def downgrade() -> None:
    op.drop_index("ix_assessments_label_edited", table_name="assessments")
    op.drop_column("assessments", "issue_change_count")
    op.drop_column("assessments", "label_edited")
