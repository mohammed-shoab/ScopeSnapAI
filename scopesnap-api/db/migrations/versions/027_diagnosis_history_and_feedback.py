"""diagnosis_history_and_feedback

Revision ID: 027
Revises: 026
Create Date: 2026-05-20

Track D: add history/share/confidence columns to diagnostic_sessions,
and create diagnosis_feedback table for Mark-as-Solved / Different-fault-found.

Note: all diagnostic sessions (US + PK) share the single diagnostic_sessions
table — PK market routing is handled via X-Market header at the query level,
not via a separate pak_diagnostic_sessions table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "027"
down_revision = "026"
branch_labels = None
depends_on = None


def upgrade():
    # -- Add Track D columns to diagnostic_sessions --
    op.add_column("diagnostic_sessions",
        sa.Column("customer_label", sa.Text, nullable=True))
    op.add_column("diagnostic_sessions",
        sa.Column("customer_address", sa.Text, nullable=True))
    op.add_column("diagnostic_sessions",
        sa.Column("share_token", sa.String(64), nullable=True))
    op.add_column("diagnostic_sessions",
        sa.Column("confidence_level", sa.String(10), nullable=True))
    op.add_column("diagnostic_sessions",
        sa.Column("reasoning_chain", JSONB, nullable=True))
    op.add_column("diagnostic_sessions",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Unique index on share_token (partial — only non-NULL rows)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_ds_share_token
        ON diagnostic_sessions (share_token)
        WHERE share_token IS NOT NULL
    """)

    # Composite index for the list query (company_id + created_at DESC)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ds_company_created
        ON diagnostic_sessions (company_id, created_at DESC)
        WHERE resolved_card_id IS NOT NULL AND deleted_at IS NULL
    """)

    # -- Create diagnosis_feedback table (single table, both markets) --
    op.create_table(
        "diagnosis_feedback",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.UUID(as_uuid=False),
                  sa.ForeignKey("diagnostic_sessions.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("tech_user_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("agreement", sa.String(20), nullable=False),
        sa.Column("real_fault_text", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
    )
    op.create_index("ix_diagnosis_feedback_session", "diagnosis_feedback",
                    ["session_id"])
    op.execute("ALTER TABLE diagnosis_feedback ENABLE ROW LEVEL SECURITY")


def downgrade():
    op.drop_index("ix_diagnosis_feedback_session",
                  table_name="diagnosis_feedback")
    op.drop_table("diagnosis_feedback")
    op.execute("DROP INDEX IF EXISTS ix_ds_company_created")
    op.execute("DROP INDEX IF EXISTS ix_ds_share_token")
    for col in ("deleted_at", "reasoning_chain", "confidence_level",
                "share_token", "customer_address", "customer_label"):
        op.drop_column("diagnostic_sessions", col)
