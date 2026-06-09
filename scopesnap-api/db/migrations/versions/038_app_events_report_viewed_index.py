"""038 — Add app_events report_viewed partial index (perf)

Codifies the index that was added out-of-band during the speed audit, so any
future DB restore/rebuild recreates it automatically. Same lesson as DEC-092 /
migration 037: out-of-band DB objects get silently lost on a pg_dump restore.

The index backs the homeowner view-count lookup in api/estimates.py
(`SELECT COUNT(*) FROM app_events WHERE event_name='report_viewed'
AND event_data->>'report_short_id' = :sid`). It is a partial expression index.

Idempotent: the index already exists on both Virginia DBs, so this is a no-op
there (CREATE INDEX IF NOT EXISTS) and only matters for fresh rebuilds.

Revises: 037
"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic
revision = "038"
down_revision = "037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_app_events_report_viewed_short_id "
        "ON public.app_events USING btree (((event_data ->> 'report_short_id'))) "
        "WHERE ((event_name)::text = 'report_viewed'::text);"
    ))


def downgrade() -> None:
    op.execute(text(
        "DROP INDEX IF EXISTS public.ix_app_events_report_viewed_short_id;"
    ))
