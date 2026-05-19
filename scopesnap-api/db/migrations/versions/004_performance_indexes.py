"""Add performance indexes for common query patterns

Revision ID: 004
Revises: 003
Create Date: 2026-04-14

Performance fix: adds composite and single-column indexes for the queries
that run on every dashboard load and every assessment list fetch.
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Most common query: list assessments for a company, newest first
    op.create_index(
        "ix_assessments_company_created",
        "assessments",
        ["company_id", "created_at"],
        postgresql_ops={"created_at": "DESC"},
    )

    # Dashboard status filter (pending / completed / sent)
    op.create_index(
        "ix_estimates_status",
        "estimates",
        ["status"],
    )

    # Homeowner lookup by email (send report, dedup check)
    op.create_index(
        "ix_properties_customer_email",
        "properties",
        ["customer_email"],
    )

    # Assessment lookup by company + status
    op.create_index(
        "ix_assessments_company_status",
        "assessments",
        ["company_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_assessments_company_created", table_name="assessments")
    op.drop_index("ix_estimates_status", table_name="estimates")
    op.drop_index("ix_properties_customer_email", table_name="properties")
    op.drop_index("ix_assessments_company_status", table_name="assessments")
