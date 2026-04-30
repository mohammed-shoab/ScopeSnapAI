"""WS-A — Data Foundation

Revision ID: 007
Revises: 006
Create Date: 2026-04-30

Creates 9 new reference tables that back the ac_data_repo.json v2.0 and the
SnapAI_HVAC_Master_Price_List_2026.xlsx.  All tables have RLS enabled —
service_role (the backend) bypasses RLS automatically; no anon/authenticated
access is needed for these internal reference tables.

New tables:
  data_repo_versions    — JSON load history + row-count manifest
  brands                — 15 brand records  (id = text slug, e.g. "carrier")
  parts_catalog         — 40 parts
  fault_cards           — 19 diagnostic cards  (card_id = 1–19)
  error_codes           — 159 error codes across 8 brand families
  pricing_tiers         — A/B/C estimate tiers per fault card (from price list)
  labor_rates_houston   — 1 row of Houston labour-rate targets
  legacy_model_prefixes — 75 pre-2010 model prefixes
  lifecycle_rules       — per-component age → recommended A/B/C tier

Schema extensions:
  equipment_models      — adds brand_id FK + refrigerant / compressor metadata
  assessments           — adds complaint_type (TEXT, nullable) for Tab H (WS-J)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ── Helper: enable RLS ─────────────────────────────────────────────────────────
def _enable_rls(table: str) -> None:
    op.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')


def upgrade() -> None:

    # ── TABLE: data_repo_versions ─────────────────────────────────────────────
    op.create_table(
        "data_repo_versions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("version", sa.String(20), nullable=False),          # "2.0"
        sa.Column("source_file", sa.Text, nullable=True),             # "ac_data_repo.json"
        sa.Column("row_counts", postgresql.JSONB, nullable=True),     # {brands:15, parts:40, …}
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    _enable_rls("data_repo_versions")

    # ── TABLE: brands ─────────────────────────────────────────────────────────
    # Primary key is a text slug matching ac_data_repo.json brand.id ("carrier",
    # "trane", …).  This makes FK references human-readable.
    op.create_table(
        "brands",
        sa.Column("id", sa.String(50), primary_key=True),             # "carrier"
        sa.Column("name", sa.String(100), nullable=False),            # "Carrier"
        sa.Column("parent_company", sa.String(200), nullable=True),
        sa.Column("sister_brands", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("houston_prevalence", sa.String(20), nullable=True),# "very_high"
        sa.Column("manufactured_in_tx", sa.Boolean, nullable=True, server_default="false"),
        sa.Column("series", postgresql.JSONB, nullable=True),         # full series array
        sa.Column("legacy_model_prefixes", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("legacy_years", sa.String(20), nullable=True),
        sa.Column("legacy_refrigerant", sa.String(50), nullable=True),
        sa.Column("legacy_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    _enable_rls("brands")

    # ── TABLE: parts_catalog ──────────────────────────────────────────────────
    op.create_table(
        "parts_catalog",
        sa.Column("id", sa.String(100), primary_key=True),            # "cap_run_dual"
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("category", sa.String(50), nullable=True),          # "electrical"
        sa.Column("fault_cards", postgresql.ARRAY(sa.Integer), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("part_cost_wholesale", postgresql.JSONB, nullable=True),
        sa.Column("part_cost_retail", postgresql.JSONB, nullable=True),
        sa.Column("total_installed_houston", postgresql.JSONB, nullable=True),
        sa.Column("labor_hours", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    _enable_rls("parts_catalog")

    # ── TABLE: fault_cards ────────────────────────────────────────────────────
    # card_id 1–19 matches the JSON / Price List / HTML numbering (Decision D-1).
    op.create_table(
        "fault_cards",
        sa.Column("card_id", sa.Integer, primary_key=True),           # 1–19
        sa.Column("card_name", sa.String(200), nullable=False),
        sa.Column("houston_frequency_pct", sa.Integer, nullable=True),
        sa.Column("primary_parts", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("optional_parts", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("labor_hours_min", sa.Numeric(5, 2), nullable=True),
        sa.Column("labor_hours_max", sa.Numeric(5, 2), nullable=True),
        sa.Column("labor_hours_avg", sa.Numeric(5, 2), nullable=True),
        # JSON source estimate values
        sa.Column("estimate_min", sa.Integer, nullable=True),
        sa.Column("estimate_typical", sa.Integer, nullable=True),
        sa.Column("estimate_max", sa.Integer, nullable=True),
        # Price list values (source-of-truth per Decision D-8)
        sa.Column("price_list_min", sa.Integer, nullable=True),
        sa.Column("price_list_typical", sa.Integer, nullable=True),
        sa.Column("price_list_max", sa.Integer, nullable=True),
        sa.Column("price_list_primary_parts", sa.Text, nullable=True),
        sa.Column("price_list_optional_parts", sa.Text, nullable=True),
        sa.Column("price_list_labor_hours", sa.String(20), nullable=True),
        sa.Column("marks_field_notes", sa.Text, nullable=True),
        sa.Column("phase", sa.String(30), nullable=True),             # "Phase 1" / "Phase 2"
        sa.Column("difficulty", sa.String(30), nullable=True),
        sa.Column("tech_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    _enable_rls("fault_cards")

    # ── TABLE: error_codes ────────────────────────────────────────────────────
    # 159 codes across 8 brand families. brand_family = key in error_code_db.brands
    # (e.g. "carrier_bryant_payne").  subsystem = the nested section name inside
    # each brand family dict (e.g. "led_flash_system", "communicating_infinity").
    # Standalone mini-split brands (lg, samsung, etc.) store subsystem = "mini_split".
    op.create_table(
        "error_codes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("brand_family", sa.String(100), nullable=False),
        sa.Column("brand_family_members", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("subsystem", sa.String(100), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=False),
        sa.Column("meaning", sa.Text, nullable=True),
        sa.Column("severity", sa.String(30), nullable=True),
        sa.Column("action", sa.Text, nullable=True),
        sa.Column("decision_tree_card", sa.Integer,
                  sa.ForeignKey("fault_cards.card_id", ondelete="SET NULL"),
                  nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ix_error_codes_brand_family", "error_codes", ["brand_family"])
    op.create_index("ix_error_codes_error_code", "error_codes", ["error_code"])
    op.create_index("ix_error_codes_decision_tree_card", "error_codes", ["decision_tree_card"])
    _enable_rls("error_codes")

    # ── TABLE: pricing_tiers ──────────────────────────────────────────────────
    # A = Min (Good), B = Typical (Better), C = Max (Best) — per Decision D-8.
    # Source of truth = price list sheet "13. FAULT CARDS".
    op.create_table(
        "pricing_tiers",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("card_id", sa.Integer,
                  sa.ForeignKey("fault_cards.card_id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("tier", sa.String(1), nullable=False),              # 'A', 'B', 'C'
        sa.Column("estimate_amount", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("card_id", "tier", name="uq_pricing_tier_card_tier"),
    )
    op.create_index("ix_pricing_tiers_card_id", "pricing_tiers", ["card_id"])
    _enable_rls("pricing_tiers")

    # ── TABLE: labor_rates_houston ────────────────────────────────────────────
    # Single-row table (or one row per version).  load_repo.py inserts/upserts.
    op.create_table(
        "labor_rates_houston",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("version", sa.String(20), nullable=False, server_default="2.0"),
        sa.Column("standard_hourly_min", sa.Integer, nullable=True),
        sa.Column("standard_hourly_max", sa.Integer, nullable=True),
        sa.Column("flat_rate_note", sa.Text, nullable=True),
        sa.Column("after_hours_premium", sa.String(50), nullable=True),
        sa.Column("emergency_weekend_premium", sa.String(50), nullable=True),
        sa.Column("attic_premium_min", sa.Integer, nullable=True),
        sa.Column("attic_premium_max", sa.Integer, nullable=True),
        sa.Column("attic_premium_note", sa.Text, nullable=True),
        sa.Column("r22_surcharge_min", sa.Integer, nullable=True),
        sa.Column("r22_surcharge_max", sa.Integer, nullable=True),
        sa.Column("effective_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    _enable_rls("labor_rates_houston")

    # ── TABLE: legacy_model_prefixes ──────────────────────────────────────────
    op.create_table(
        "legacy_model_prefixes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("prefix", sa.String(50), nullable=False),
        sa.Column("brand_id", sa.String(50),
                  sa.ForeignKey("brands.id", ondelete="SET NULL"), nullable=True),
        sa.Column("brand_name", sa.String(100), nullable=True),
        sa.Column("years", sa.String(30), nullable=True),             # "2000-2010"
        sa.Column("refrigerant", sa.String(30), nullable=True),       # "R-22 (pre-2010)"
        sa.Column("series_name", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ix_legacy_model_prefixes_prefix", "legacy_model_prefixes", ["prefix"])
    op.create_index("ix_legacy_model_prefixes_brand_id", "legacy_model_prefixes", ["brand_id"])
    _enable_rls("legacy_model_prefixes")

    # ── TABLE: lifecycle_rules ────────────────────────────────────────────────
    # Powers the WS-H Recommended-badge engine.  One row per component / card /
    # condition combination.  "recommended_tier" is 'A', 'B', or 'C'.
    op.create_table(
        "lifecycle_rules",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("component_name", sa.String(100), nullable=False),
        sa.Column("card_id", sa.Integer,
                  sa.ForeignKey("fault_cards.card_id", ondelete="SET NULL"), nullable=True),
        sa.Column("age_threshold_years", sa.Integer, nullable=True),
        sa.Column("condition_signal", sa.String(100), nullable=True),
        sa.Column("recommended_tier", sa.String(1), nullable=False,
                  server_default="B"),                                # 'A', 'B', or 'C'
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ix_lifecycle_rules_card_id", "lifecycle_rules", ["card_id"])
    _enable_rls("lifecycle_rules")

    # ── EXTEND: equipment_models ──────────────────────────────────────────────
    # Add FK to new brands table + compressor / charging metadata for WS-B / WS-D.
    op.add_column("equipment_models", sa.Column(
        "brand_id", sa.String(50),
        sa.ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to brands.id — e.g. 'carrier'",
    ))
    op.add_column("equipment_models", sa.Column(
        "refrigerant", sa.String(20), nullable=True,
        comment="Primary refrigerant — R-410A / R-22 / R-32 / R-454B",
    ))
    op.add_column("equipment_models", sa.Column(
        "metering_device", sa.String(20), nullable=True,
        comment="piston / TXV / EEV",
    ))
    op.add_column("equipment_models", sa.Column(
        "compressor_type", sa.String(20), nullable=True,
        comment="single_stage / two_stage / variable_speed",
    ))
    op.add_column("equipment_models", sa.Column(
        "charging_method", sa.String(20), nullable=True,
        comment="superheat / subcooling",
    ))
    op.add_column("equipment_models", sa.Column(
        "dual_fuel_capable", sa.Boolean, nullable=False,
        server_default=sa.text("false"),
        comment="True if unit can pair with a gas furnace for dual-fuel operation",
    ))
    op.add_column("equipment_models", sa.Column(
        "is_legacy", sa.Boolean, nullable=False,
        server_default=sa.text("false"),
        comment="True for pre-2010 / R-22 units identified via legacy prefix lookup",
    ))

    # ── EXTEND: assessments ───────────────────────────────────────────────────
    # complaint_type drives the Tab H branch (WS-J).  Nullable so existing rows
    # are unaffected.  CHECK constraint is advisory — new types added by migration.
    op.add_column("assessments", sa.Column(
        "complaint_type", sa.String(40), nullable=True,
        comment=(
            "Complaint chip selected by tech: not_cooling | not_heating | "
            "not_running | noisy | water_leak | high_bill | intermittent_shutdown"
        ),
    ))
    op.execute("""
        ALTER TABLE assessments
        ADD CONSTRAINT chk_assessments_complaint_type
        CHECK (complaint_type IN (
            'not_cooling', 'not_heating', 'not_running',
            'noisy', 'water_leak', 'high_bill', 'intermittent_shutdown'
        ) OR complaint_type IS NULL)
    """)


def downgrade() -> None:
    # Remove assessments extension
    op.execute("ALTER TABLE assessments DROP CONSTRAINT IF EXISTS chk_assessments_complaint_type")
    op.drop_column("assessments", "complaint_type")

    # Remove equipment_models extensions
    op.drop_column("equipment_models", "is_legacy")
    op.drop_column("equipment_models", "dual_fuel_capable")
    op.drop_column("equipment_models", "charging_method")
    op.drop_column("equipment_models", "compressor_type")
    op.drop_column("equipment_models", "metering_device")
    op.drop_column("equipment_models", "refrigerant")
    op.drop_column("equipment_models", "brand_id")

    # Drop new tables in reverse FK order
    op.drop_index("ix_lifecycle_rules_card_id", table_name="lifecycle_rules")
    op.drop_table("lifecycle_rules")

    op.drop_index("ix_legacy_model_prefixes_brand_id", table_name="legacy_model_prefixes")
    op.drop_index("ix_legacy_model_prefixes_prefix", table_name="legacy_model_prefixes")
    op.drop_table("legacy_model_prefixes")

    op.drop_table("labor_rates_houston")

    op.drop_index("ix_pricing_tiers_card_id", table_name="pricing_tiers")
    op.drop_table("pricing_tiers")

    op.drop_index("ix_error_codes_decision_tree_card", table_name="error_codes")
    op.drop_index("ix_error_codes_error_code", table_name="error_codes")
    op.drop_index("ix_error_codes_brand_family", table_name="error_codes")
    op.drop_table("error_codes")

    op.drop_table("fault_cards")
    op.drop_table("parts_catalog")
    op.drop_table("brands")
    op.drop_table("data_repo_versions")
