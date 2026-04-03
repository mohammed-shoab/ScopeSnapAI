"""Add unique constraint to pricing_rules

Revision ID: 003_pricing_rule_unique
Revises: 002_app_events
Create Date: 2026-04-03

BUG-04 fix: Prevent duplicate pricing rule entries for the same
(company_id, equipment_type, job_type, region) combination.
"""

from alembic import op

# revision identifiers
revision = "003_pricing_rule_unique"
down_revision = "002_app_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove any existing duplicates before adding the constraint.
    # Keep only the most recently created row for each unique tuple.
    op.execute("""
        DELETE FROM pricing_rules
        WHERE id NOT IN (
            SELECT DISTINCT ON (
                COALESCE(company_id::text, 'NULL'),
                equipment_type,
                job_type,
                region
            ) id
            FROM pricing_rules
            ORDER BY
                COALESCE(company_id::text, 'NULL'),
                equipment_type,
                job_type,
                region,
                created_at DESC NULLS LAST
        )
    """)

    # Add the unique constraint
    op.create_unique_constraint(
        "uq_pricing_rule",
        "pricing_rules",
        ["company_id", "equipment_type", "job_type", "region"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_pricing_rule", "pricing_rules", type_="unique")
