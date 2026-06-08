"""037 — Recreate PK market compatibility views (pak_*_v)

Context (DEC-092): The PK market request path (api/dependencies.py -> MarketTables)
queries five VIEWS that remap pak_* base-table columns onto the US-compatible names
the shared SQL expects:

    pak_fault_cards_v       (pkr_est_* -> price_list_*, NULL phase/difficulty)
    pak_error_codes_v       (brand_id -> brand_family, code -> error_code, description -> meaning)
    pak_labor_rates_v       (PKR labor cols -> Houston col names: attic/r22)
    pak_replacement_costs_v (pkr_min/max/typical -> price_min/max/typical)
    pak_lifecycle_rules_v   (US-compatible schema, 0 rows -> falls to default)

These views were originally created OUT OF BAND (Supabase SQL editor), so they were
NOT in version control. During the Tokyo -> Virginia (us-east-1) database migration
they were lost on the staging restore (the staging dump never contained them), which
broke every PK query with "relation does not exist" -> backend 503 (no CORS headers)
-> browser "Failed to fetch". See DEC-092.

This migration puts the definitions under Alembic so any future restore/rebuild that
runs `alembic upgrade head` recreates them automatically. Definitions are copied
verbatim from the Tokyo-prod backup (backups/prod_fresh_20260608_164020.sql.gz).

Idempotent: CREATE OR REPLACE VIEW — safe whether or not the views already exist
(prod already has all 6; staging was repaired manually on 2026-06-09).

Note: pak_operating_targets_v is intentionally NOT recreated here — it is owned by
migration 036 and references the renamed `operating_targets` table.

Revises: 036
"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic
revision = "037"
down_revision = "036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        CREATE OR REPLACE VIEW public.pak_error_codes_v WITH (security_invoker = true) AS
         SELECT id,
            brand_id AS brand_family,
            ARRAY[brand_id] AS brand_family_members,
            NULL::text AS subsystem,
            code AS error_code,
            description AS meaning,
            severity,
            NULL::text AS action,
            NULL::integer AS decision_tree_card,
            created_at
           FROM public.pak_error_codes;
    """))

    op.execute(text("""
        CREATE OR REPLACE VIEW public.pak_fault_cards_v WITH (security_invoker = true) AS
         SELECT card_id,
            card_name,
            NULL::text AS phase,
            NULL::text AS difficulty,
            tech_notes,
            pkr_est_min AS price_list_min,
            pkr_est_typical AS price_list_typical,
            pkr_est_max AS price_list_max,
            better_option_estimate,
            created_at,
            action_steps,
            parts_needed,
            alternative_cards,
            climate_notes_pk
           FROM public.pak_fault_cards;
    """))

    op.execute(text("""
        CREATE OR REPLACE VIEW public.pak_labor_rates_v WITH (security_invoker = true) AS
         SELECT id,
            currency,
            0 AS attic_premium_min,
            0 AS attic_premium_max,
            COALESCE(gas_charging_r22_per_kg_pkr, 0) AS r22_surcharge_min,
            COALESCE(gas_charging_r22_per_kg_pkr, 0) AS r22_surcharge_max,
            created_at
           FROM public.pak_labor_rates;
    """))

    op.execute(text("""
        CREATE OR REPLACE VIEW public.pak_lifecycle_rules_v WITH (security_invoker = true) AS
         SELECT id,
            NULL::text AS component_name,
            NULL::integer AS card_id,
            NULL::integer AS age_threshold_years,
            NULL::text AS condition_signal,
            NULL::text AS recommended_tier,
            NULL::text AS note,
            created_at
           FROM public.pak_lifecycle_rules
          WHERE false;
    """))

    op.execute(text("""
        CREATE OR REPLACE VIEW public.pak_replacement_costs_v WITH (security_invoker = true) AS
         SELECT id,
            tonnage,
            pkr_min AS price_min,
            pkr_max AS price_max,
            pkr_typical AS price_typical,
            notes,
            created_at
           FROM public.pak_replacement_costs;
    """))


def downgrade() -> None:
    # These 5 views were not under version control before 037. Dropping them on a
    # downgrade restores the pre-037 schema state. (pak_operating_targets_v is owned
    # by migration 036 and is left untouched.)
    for v in (
        "pak_error_codes_v",
        "pak_fault_cards_v",
        "pak_labor_rates_v",
        "pak_lifecycle_rules_v",
        "pak_replacement_costs_v",
    ):
        op.execute(text(f"DROP VIEW IF EXISTS public.{v};"))
