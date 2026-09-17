"""048 -- enable RLS on the Tier A threshold tables + ARM the rls_auto_enable event trigger

BACKGROUND (DEC-135)
Migration 046 created ten Tier A threshold tables with raw `CREATE TABLE` and did
not enable row-level security on any of them. Supabase's default grant chain gives
`anon` and `authenticated` full DML on new tables in `public`, and neither role has
BYPASSRLS -- so for roughly thirty days (2026-07-07 to 2026-08-06) those ten tables
were SELECT / INSERT / UPDATE / DELETE / TRUNCATE-able on BOTH staging and production
by anyone holding `NEXT_PUBLIC_SUPABASE_ANON_KEY`, which ships in the frontend bundle
and is public by construction.

These tables are the numeric backbone of the diagnostic engine (`api/diagnostic.py`).
A silent edit to a delta-T band or a superheat target raises no error -- it produces a
confidently wrong diagnosis and a wrong three-option quote in a homeowner's hands.
A tamper audit on 2026-08-06 came back CLEAN: row counts and per-table md5 fingerprints
matched across staging and prod, and every row still carried the original migration-046
load timestamps (2026-07-07 18:47-18:54 UTC). Nothing was written during the window.

The fix was applied live to staging and prod on 2026-08-06. This migration records it
in the Alembic chain so a rebuild-from-migrations does not reopen the hole. Idempotent.

ROOT CAUSE -- WHY THE EXISTING DEFENCE DID NOT FIRE
A function `public.rls_auto_enable()` already existed on both databases. It is a
correctly written `ddl_command_end` event-trigger function that enables RLS on any new
table in `public`. It was almost certainly added after the FIRST occurrence of this bug
(migration 042 -> `processed_webhook_events`, remediated by 044 on 2026-06-24).

But no event trigger was ever bound to it. `pg_event_trigger` contained only Supabase's
six built-ins. The guard had been written and left unarmed, so it sat inert while
migration 046 created ten unprotected tables five weeks later.

This migration therefore does three things, in increasing order of importance:
  1. Enables RLS on the ten tables (repairs the specific damage).
  2. Puts `rls_auto_enable()` into version control -- it was created out-of-band and
     existed in no repo file, i.e. undocumented infrastructure nobody could review.
  3. ARMS the event trigger, so every future `CREATE TABLE` in `public` gets RLS
     automatically regardless of what the migration author remembers.

Item 3 is the actual fix. Items 1 and 2 are cleanup. A written rule already failed to
prevent recurrence once; only a mechanical guard changes the outcome.

Revision ID: 048
Revises: 047
"""
from __future__ import annotations

from typing import Union

from alembic import op
from sqlalchemy import text

revision: str = "048"
down_revision: Union[str, None] = "047"
branch_labels = None
depends_on = None


# The ten tables created by 046 without RLS.
THRESHOLD_TABLES = (
    "superheat_subcool_targets",
    "static_pressure_targets",
    "delta_t_targets",
    "latent_targets",
    "sizing_rules",
    "compressor_test_thresholds",
    "cfm_per_ton_targets",
    "thermostat_low_voltage_targets",
    "vacuum_validation_targets",
    "liquid_line_restriction_thresholds",
)

EVENT_TRIGGER_NAME = "rls_auto_enable_trg"


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Repair: bring the ten tables in line with every sibling table --
    #    RLS enabled, no policies. The app is unaffected: it connects as
    #    `postgres`, which has rolbypassrls = true.
    for table in THRESHOLD_TABLES:
        bind.execute(text(f"ALTER TABLE IF EXISTS public.{table} ENABLE ROW LEVEL SECURITY"))

    # 2. Bring the out-of-band guard function under version control.
    bind.execute(text("""
        CREATE OR REPLACE FUNCTION public.rls_auto_enable()
          RETURNS event_trigger
          LANGUAGE plpgsql
          SECURITY DEFINER
          SET search_path TO 'pg_catalog'
        AS $rls_auto_enable$
        DECLARE
          cmd record;
        BEGIN
          FOR cmd IN
            SELECT *
            FROM pg_event_trigger_ddl_commands()
            WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
              AND object_type IN ('table', 'partitioned table')
          LOOP
            IF cmd.schema_name IS NOT NULL
               AND cmd.schema_name IN ('public')
               AND cmd.schema_name NOT IN ('pg_catalog', 'information_schema')
               AND cmd.schema_name NOT LIKE 'pg_toast%'
               AND cmd.schema_name NOT LIKE 'pg_temp%'
            THEN
              BEGIN
                EXECUTE format('alter table if exists %s enable row level security',
                               cmd.object_identity);
                RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
              EXCEPTION
                WHEN OTHERS THEN
                  RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
              END;
            ELSE
              RAISE LOG 'rls_auto_enable: skip % (system schema or not in enforced list: %.)',
                        cmd.object_identity, cmd.schema_name;
            END IF;
          END LOOP;
        END;
        $rls_auto_enable$
    """))

    # It is an event-trigger function, fired by the server -- never a REST RPC.
    # Supabase had it exposed at /rest/v1/rpc/rls_auto_enable to anon and
    # authenticated, which the security advisor flagged. Revoking EXECUTE does not
    # affect event-trigger firing; the server does not check EXECUTE for that path.
    bind.execute(text("REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC"))
    for role in ("anon", "authenticated"):
        bind.execute(text(f"""
            DO $do$
            BEGIN
              IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM {role};
              END IF;
            END
            $do$
        """))

    # 3. THE ACTUAL FIX -- arm the trigger. CREATE EVENT TRIGGER has no
    #    IF NOT EXISTS, so guard it explicitly to stay idempotent.
    bind.execute(text(f"""
        DO $do$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_event_trigger WHERE evtname = '{EVENT_TRIGGER_NAME}'
          ) THEN
            CREATE EVENT TRIGGER {EVENT_TRIGGER_NAME}
              ON ddl_command_end
              WHEN TAG IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
              EXECUTE FUNCTION public.rls_auto_enable();
          END IF;
        END
        $do$
    """))


def downgrade() -> None:
    bind = op.get_bind()

    bind.execute(text(f"DROP EVENT TRIGGER IF EXISTS {EVENT_TRIGGER_NAME}"))

    # Deliberately NOT dropping rls_auto_enable(): it predates this migration on
    # every live database, so dropping it would remove infrastructure this
    # migration did not create.

    # Deliberately NOT disabling RLS on the ten tables. Downgrading a security
    # control silently re-opens a production data exposure. If that is genuinely
    # wanted it must be an explicit, deliberate act -- not a side effect of
    # stepping the migration chain backwards.
