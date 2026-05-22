# coding: utf-8
"""Add market column to estimates table (BUG-037).

Revision ID: 034
Revises: 033
Create Date: 2026-05-22

Problem: estimates table has no market tag.  PK estimates and US estimates
sit in the same table.  The public report page (/r/...) fetches without an
X-Market header — market defaults to US — so a PK estimate viewed on the
Houston domain displays PKR amounts formatted as USD.

Fix: Add market VARCHAR(2) NOT NULL DEFAULT 'US'.
     All existing rows backfill to 'US' (safe: PK market is new; any PK
     estimates that exist are test data and will be re-created correctly).
     Going forward fault_estimate.py and _generate_service_estimate() stamp
     the market at creation time.

NOTE: Column was pre-applied directly via Supabase SQL (ALTER TABLE ADD COLUMN
IF NOT EXISTS).  upgrade() uses IF NOT EXISTS — safe to re-run on Railway deploy.
"""
import sqlalchemy as sa
from alembic import op

revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None


def upgrade():
    # IF NOT EXISTS guard: column already added via direct SQL on 2026-05-22
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='estimates' AND column_name='market'"
        )
    )
    if not result.fetchone():
        op.add_column(
            "estimates",
            sa.Column("market", sa.String(2), nullable=False, server_default="US"),
        )
    else:
        print("034: market column already exists — skip")


def downgrade():
    op.drop_column("estimates", "market")
