"""app_events table — behavioral analytics

Revision ID: 002
Revises: 001
Create Date: 2026-03-23

Creates the app_events table for tracking user behavior during beta.
Tracks events from both the web app and API (assessment_created, report_viewed, etc.).

SOW Task 1.10: Event tracking system for activation funnel analysis.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── TABLE: app_events ─────────────────────────────────────────────────────
    op.create_table(
        "app_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        # Who — nullable because homeowner report views have no user_id
        sa.Column("user_id", sa.String(200), nullable=True, index=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False), nullable=True),

        # What
        sa.Column("event_name", sa.String(100), nullable=False),  # e.g. "assessment_created"
        sa.Column("event_data", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),  # arbitrary payload

        # Context
        sa.Column("session_id", sa.String(200), nullable=True),
        sa.Column("page_url", sa.Text, nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),  # IPv4 or IPv6

        # When
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            index=True,
        ),
    )

    # ── Indexes for common query patterns ─────────────────────────────────────
    # Query by event type within a time window
    op.create_index(
        "ix_app_events_event_name_created_at",
        "app_events",
        ["event_name", "created_at"],
    )
    # Query all events for a company
    op.create_index(
        "ix_app_events_company_id_created_at",
        "app_events",
        ["company_id", "created_at"],
    )

    # ── TABLE: waitlist_signups ───────────────────────────────────────────────
    # SOW Task 1.11: Early-access email capture from landing page
    op.create_table(
        "waitlist_signups",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("source", sa.String(50), nullable=False,
                  server_default="landing_page"),  # landing_page | referral | etc.
        sa.Column("referrer_url", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "ix_waitlist_signups_created_at",
        "waitlist_signups",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_waitlist_signups_created_at", table_name="waitlist_signups")
    op.drop_table("waitlist_signups")

    op.drop_index("ix_app_events_company_id_created_at", table_name="app_events")
    op.drop_index("ix_app_events_event_name_created_at", table_name="app_events")
    op.drop_index("ix_app_events_user_id", table_name="app_events")
    op.drop_index("ix_app_events_created_at", table_name="app_events")
    op.drop_table("app_events")
