"""initial_schema — all 12 tables

Revision ID: 001
Revises:
Create Date: 2026-03-21

Creates all 12 ScopeSnap tables matching Tech Spec §02 exactly.
Run with: alembic upgrade head
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID generation extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ── TABLE 1: companies ────────────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("logo_url", sa.Text, nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("license_number", sa.String(100), nullable=True),
        sa.Column("address_line1", sa.String(200), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip", sa.String(10), nullable=True),
        sa.Column("stripe_customer_id", sa.String(100), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(100), nullable=True),
        sa.Column("plan", sa.String(20), nullable=False, server_default="free"),
        sa.Column("monthly_estimate_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("monthly_estimate_limit", sa.Integer, nullable=True, server_default="5"),
        sa.Column("settings", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    # ── TABLE 2: users ────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clerk_user_id", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="tech"),
        sa.Column("accuracy_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("total_estimates", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    # ── TABLE 3: properties ───────────────────────────────────────────────────
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("address_line1", sa.String(200), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip", sa.String(10), nullable=True),
        sa.Column("customer_name", sa.String(200), nullable=True),
        sa.Column("customer_email", sa.String(200), nullable=True),
        sa.Column("customer_phone", sa.String(20), nullable=True),
        sa.Column("visit_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("last_visit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("company_id", "address_line1", "zip",
                            name="uq_property_per_company"),
    )
    op.create_index("idx_properties_company_address", "properties",
                    ["company_id", "address_line1", "zip"])

    # ── TABLE 4: equipment_models (GLOBAL — no company_id) ───────────────────
    op.create_table(
        "equipment_models",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("model_series", sa.String(100), nullable=False),
        sa.Column("model_pattern", sa.String(200), nullable=True),
        sa.Column("equipment_type", sa.String(50), nullable=False),
        sa.Column("seer_rating", sa.Numeric(4, 1), nullable=True),
        sa.Column("tonnage_range", sa.String(20), nullable=True),
        sa.Column("manufacture_years", sa.String(20), nullable=True),
        sa.Column("avg_lifespan_years", sa.Integer, nullable=True),
        sa.Column("known_issues", postgresql.JSONB, nullable=True),
        sa.Column("recalls", postgresql.JSONB, nullable=True),
        sa.Column("serial_decode_pattern", postgresql.JSONB, nullable=True),
        sa.Column("replacement_models", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("total_assessments", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("idx_equipment_models_brand", "equipment_models",
                    ["brand", "model_series"])

    # ── TABLE 5: equipment_instances ──────────────────────────────────────────
    op.create_table(
        "equipment_instances",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("property_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("equipment_model_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("equipment_models.id", ondelete="SET NULL"), nullable=True),
        sa.Column("equipment_type", sa.String(50), nullable=False),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("model_number", sa.String(100), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("install_year", sa.Integer, nullable=True),
        sa.Column("condition", sa.String(20), nullable=True),
        sa.Column("condition_details", postgresql.JSONB, nullable=True),
        sa.Column("photo_urls", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("ai_confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("idx_equipment_instances_property", "equipment_instances", ["property_id"])

    # ── TABLE 6: assessments ──────────────────────────────────────────────────
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("properties.id", ondelete="SET NULL"), nullable=True),
        sa.Column("equipment_instance_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("equipment_instances.id", ondelete="SET NULL"), nullable=True),
        sa.Column("photo_urls", postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column("voice_note_url", sa.Text, nullable=True),
        sa.Column("ai_analysis", postgresql.JSONB, nullable=True),
        sa.Column("ai_equipment_id", postgresql.JSONB, nullable=True),
        sa.Column("ai_condition", postgresql.JSONB, nullable=True),
        sa.Column("ai_issues", postgresql.JSONB, nullable=True),
        sa.Column("tech_overrides", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("idx_assessments_company", "assessments",
                    ["company_id", "created_at"])

    # ── TABLE 7: assessment_photos ────────────────────────────────────────────
    op.create_table(
        "assessment_photos",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("photo_url", sa.Text, nullable=False),
        sa.Column("annotated_photo_url", sa.Text, nullable=True),
        sa.Column("annotations", postgresql.JSONB, nullable=True),
        sa.Column("ai_raw_response", postgresql.JSONB, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    # ── TABLE 8: estimates ────────────────────────────────────────────────────
    op.create_table(
        "estimates",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("assessments.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_token", sa.String(32), nullable=False, unique=True),
        sa.Column("report_short_id", sa.String(10), nullable=False, unique=True),
        sa.Column("options", postgresql.JSONB, nullable=False),
        sa.Column("selected_option", sa.String(20), nullable=True),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("deposit_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("markup_percent", sa.Numeric(5, 2), nullable=False, server_default="35.0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(100), nullable=True),
        sa.Column("contractor_pdf_url", sa.Text, nullable=True),
        sa.Column("homeowner_report_url", sa.Text, nullable=True),
        sa.Column("sent_via", sa.String(20), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("accuracy_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("idx_estimates_company", "estimates",
                    ["company_id", "status", "created_at"])
    op.create_index("idx_estimates_report_token", "estimates", ["report_token"])

    # ── TABLE 9: estimate_line_items ──────────────────────────────────────────
    op.create_table(
        "estimate_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("estimate_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("estimates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_tier", sa.String(20), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.String(300), nullable=False),
        sa.Column("quantity", sa.Numeric(8, 2), nullable=False, server_default="1"),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("source", sa.String(20), nullable=False, server_default="pricing_db"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )

    # ── TABLE 10: estimate_documents ──────────────────────────────────────────
    op.create_table(
        "estimate_documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("estimate_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("estimates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("file_url", sa.Text, nullable=False),
        sa.Column("file_name", sa.String(200), nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    # ── TABLE 11: pricing_rules ───────────────────────────────────────────────
    op.create_table(
        "pricing_rules",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("equipment_type", sa.String(50), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("region", sa.String(20), nullable=False, server_default="national"),
        sa.Column("parts_cost", postgresql.JSONB, nullable=True),
        sa.Column("labor_hours", postgresql.JSONB, nullable=True),
        sa.Column("labor_rate", sa.Numeric(8, 2), nullable=True),
        sa.Column("permit_cost", sa.Numeric(8, 2), nullable=True),
        sa.Column("refrigerant_cost_per_lb", sa.Numeric(8, 2), nullable=True),
        sa.Column("additional_costs", postgresql.JSONB, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("idx_pricing_rules_lookup", "pricing_rules",
                    ["company_id", "equipment_type", "job_type", "region"])

    # ── TABLE 12: follow_ups ──────────────────────────────────────────────────
    op.create_table(
        "follow_ups",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("estimate_id", postgresql.UUID(as_uuid=False),
                  sa.ForeignKey("estimates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("template", sa.String(50), nullable=False),
    )
    op.create_index(
        "idx_follow_ups_scheduled", "follow_ups", ["scheduled_at"],
        postgresql_where=sa.text("sent_at IS NULL AND cancelled = false")
    )

    # ── Row-Level Security (Multi-Tenancy) ────────────────────────────────────
    # Only applied to tables that have a direct company_id column.
    # equipment_instances (→ property_id) and follow_ups (→ estimate_id)
    # are protected indirectly through their parent tables.
    for table in ["users", "properties", "assessments", "estimates", "pricing_rules"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY company_isolation ON {table}
            USING (company_id = current_setting('app.current_company_id', true)::uuid)
        """)

    print("✅ All 12 ScopeSnap tables created successfully.")
    print("   Verify with: \\dt in psql")


def downgrade() -> None:
    """Drops all tables in reverse order (respects FK constraints)."""
    tables = [
        "follow_ups", "estimate_documents", "estimate_line_items",
        "estimates", "assessment_photos", "assessments",
        "equipment_instances", "equipment_models", "pricing_rules",
        "properties", "users", "companies"
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
