"""Tier A schema: 10 threshold tables + fault_cards homeowner-copy columns

DRAFT ONLY -- NOT applied to any database, NOT deployed. Authored as a
READ-ONLY spec-to-code pass; no DB command has been run to produce this file.

DEC-111 CAVEAT (re-confirm before this is ever applied): live Alembic head was
confirmed as "045" via read-only SELECT against BOTH prod and staging
`alembic_version` on 2026-07-07 (see step1/B3_B1_schema_and_migration_spec.md,
"DEC-111 reconfirmation" section). Before applying this file to any environment,
re-run `SELECT version_num FROM alembic_version;` against that target AND
check origin/main for db/migrations/versions/ for anything merged as "046"
or later in the interim -- if head has moved, renumber this revision and
update down_revision first. Do not apply as-is if head != 045 at apply time.

DEC-070 (staging-first): when authorized, apply to STAGING FIRST, verify,
then promote to prod per the existing per-environment process. Authoring
this file performs neither.

DEC-005 / DEC-027 (ASCII-clean): no em-dash, no degree symbol, no emoji.
'F' used for degrees; '->' used in place of arrows in comments/docstrings.

Scope (see migration_046_tierA_schema.sql for the full annotated DDL and
migration_046_NOTES.md for the per-table rationale / deviations from the
literal seed_*.sql drafts):
  1. CREATE 10 new threshold tables (6 already-drafted + 3 net-new + 1 Card 25
     liquid-line-restriction table, added in this revision -- see Section 2.4
     below and migration_046_NOTES.md).
  2. ALTER fault_cards: ADD 5 homeowner-copy columns (B1 locked decision).
  3. card_id constraint check (D1 / Cards 25+26): NO ALTER -- see NOTE below.
     fault_cards.card_id is a plain sa.Integer primary_key with no CHECK/enum
     anywhere in migrations 007/016/026 (independently verified). Nothing to
     widen. This migration adds nothing for that item by design.
  4. Card 25 (Liquid-Line Restriction): liquid_line_restriction_thresholds
     table (Section 2.4) added for the three provisional LOW-confidence
     checks identified in RESEARCH_card25_liquidline_threshold_compute.md.
     Schema only -- no seed rows inserted here; values remain provisional/
     GATE-1, seeding is a follow-up step. The head/discharge-pressure
     reference item is CONFIRMED as already covered by the existing
     operating_targets table (migration 036) -- no schema change needed for
     that item. See migration_046_NOTES.md.

Revision ID: 046
Revises: 045
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "046"
down_revision: Union[str, None] = "045"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Standardized confidence CHECK clause reused across all 10 new tables in this
# migration. Normalizes casing that was inconsistent across the underlying
# draft seed files (some used 'HIGH'/'MEDIUM'/'LOW' uppercase, some 'High'/
# 'Medium'/'Low' title case) to a single 'High'/'Medium'/'Low'/'Deferred' set,
# per this task's explicit column spec. See migration_046_NOTES.md Section 2.
_CONFIDENCE_VALUES = ("High", "Medium", "Low", "Deferred")


def upgrade() -> None:
    bind = op.get_bind()

    # ------------------------------------------------------------------
    # SECTION 1 -- six already-drafted tables (seed_*.sql), column sets
    # confirmed against research_reconciled/RECONCILED_MASTER.md before
    # writing. Raw SQL via bind.execute(text(...)) mirrors the CREATE TABLE
    # statements in migration_046_tierA_schema.sql exactly (kept in one raw
    # SQL block per table so the .sql and .py stay byte-comparable during
    # review; see migration 016 for precedent on this raw-SQL DDL style).
    # ------------------------------------------------------------------

    # 1.1 superheat_subcool_targets -- 2-D grid (LOCKED DECISION: indoor_wetbulb_f
    # added; not present in the literal seed_superheat_subcool_targets.sql draft).
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS superheat_subcool_targets (
            id                          SERIAL PRIMARY KEY,
            market                      VARCHAR(2)   NOT NULL DEFAULT 'US',
            refrigerant                 VARCHAR(20)  NOT NULL,
            metering_device             VARCHAR(20)  NOT NULL
                                        CHECK (metering_device IN ('TXV', 'fixed_orifice')),
            ambient_c                   NUMERIC(5,1) NOT NULL,
            indoor_wetbulb_f            NUMERIC(5,1),
            target_superheat_min_f      NUMERIC(5,1),
            target_superheat_max_f      NUMERIC(5,1),
            target_subcool_min_f        NUMERIC(5,1),
            target_subcool_max_f        NUMERIC(5,1),
            source                      TEXT         NOT NULL,
            confidence                  VARCHAR(10)  NOT NULL
                                        CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes                       TEXT,
            created_at                  TIMESTAMPTZ  NOT NULL DEFAULT now(),
            CONSTRAINT superheat_subcool_targets_market_ref_dev_amb_wb_key
                UNIQUE (market, refrigerant, metering_device, ambient_c, indoor_wetbulb_f)
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_superheat_subcool_targets_lookup
            ON superheat_subcool_targets (market, refrigerant, metering_device, ambient_c)
    """))
    bind.execute(text("""
        COMMENT ON COLUMN superheat_subcool_targets.indoor_wetbulb_f IS
            'Indoor wet-bulb temperature (F), second grid axis for fixed-orifice superheat targets (outdoor DB x indoor WB). NULL for TXV rows. Locked decision -- see migration_046_NOTES.md.'
    """))

    # 1.2 static_pressure_targets -- matches seed_static_pressure_targets.sql draft
    # (confidence CHECK values normalized only).
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS static_pressure_targets (
          id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          system_type         VARCHAR(30) NOT NULL,
          design_budget_inwc  NUMERIC(4,2) NOT NULL,
          measurement_point   VARCHAR(20) NOT NULL,
          drop_threshold_inwc NUMERIC(4,2),
          interpretation      TEXT NOT NULL,
          routes_to_card      VARCHAR(60),
          source              TEXT NOT NULL,
          confidence          VARCHAR(10) NOT NULL
                              CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
          notes               TEXT,
          created_at          TIMESTAMPTZ DEFAULT now(),
          CHECK (measurement_point IN ('before_filter','after_filter','before_coil','after_coil','total_external'))
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_spt_system_point
            ON static_pressure_targets(system_type, measurement_point)
    """))

    # 1.3 delta_t_targets -- matches seed_delta_t_targets.sql draft
    # (confidence CHECK values normalized only).
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS delta_t_targets (
          id                      SERIAL PRIMARY KEY,
          indoor_rh_min_pct       NUMERIC(4,1) NOT NULL,
          indoor_rh_max_pct       NUMERIC(4,1) NOT NULL,
          target_delta_t_min_f    NUMERIC(4,1) NOT NULL,
          target_delta_t_max_f    NUMERIC(4,1) NOT NULL,
          low_interpretation      TEXT NOT NULL,
          high_interpretation     TEXT NOT NULL,
          source                  TEXT NOT NULL,
          confidence              VARCHAR(10) NOT NULL DEFAULT 'Medium'
                                  CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
          notes                   TEXT,
          created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
          CONSTRAINT chk_delta_t_rh_range CHECK (indoor_rh_min_pct < indoor_rh_max_pct),
          CONSTRAINT chk_delta_t_range CHECK (target_delta_t_min_f < target_delta_t_max_f)
        )
    """))

    # 1.4 latent_targets -- matches seed_latent_targets.sql draft
    # (confidence CHECK values normalized, column widened SERIAL->VARCHAR(10)).
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS latent_targets (
            id                          SERIAL PRIMARY KEY,
            metric                      VARCHAR(32) NOT NULL
                                            CHECK (metric IN ('indoor_rh', 'return_wet_bulb', 'grain_depression', 'latent_split')),
            target_min                  NUMERIC(6,2),
            target_max                  NUMERIC(6,2),
            unit                        VARCHAR(16) NOT NULL,
            out_of_range_interpretation TEXT NOT NULL,
            source                      TEXT NOT NULL,
            confidence                  VARCHAR(10) NOT NULL DEFAULT 'Low'
                                            CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes                       TEXT,
            created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_latent_targets_metric ON latent_targets (metric)
    """))

    # 1.5 sizing_rules -- matches seed_sizing_rules.sql draft (confidence CHECK
    # values normalized; 'Deferred' is load-bearing here per RECONCILED_MASTER
    # Sec 1.5 -- the sensible sub-check row ships at status DEFERRED).
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS sizing_rules (
          id                        SERIAL PRIMARY KEY,
          indicator                 VARCHAR(40) NOT NULL,
          climate_zone              VARCHAR(40) NOT NULL,
          threshold_value            NUMERIC(8,2) NOT NULL,
          threshold_unit            VARCHAR(20) NOT NULL,
          comparison                VARCHAR(2) NOT NULL,
          interpretation            TEXT NOT NULL,
          source                    TEXT NOT NULL,
          confidence                VARCHAR(10) NOT NULL DEFAULT 'Medium'
                                    CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
          requires_manual_j         BOOLEAN NOT NULL DEFAULT TRUE,
          notes                     TEXT,
          created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
          CONSTRAINT chk_sizing_rules_indicator CHECK (
            indicator IN ('sqft_per_ton', 'runtime_pct', 'cycles_per_hour', 'manual_j_vs_installed_delta')
          ),
          CONSTRAINT chk_sizing_rules_comparison CHECK (comparison IN ('<', '>')),
          CONSTRAINT chk_sizing_rules_requires_manual_j CHECK (requires_manual_j = TRUE)
        )
    """))

    # 1.6 compressor_test_thresholds -- LOCKED DECISION (D1): sub_mode_card
    # enum is POST-SPLIT ('26a'..'26e'), not the literal draft's '10a'..'10e'.
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS compressor_test_thresholds (
            id                  SERIAL PRIMARY KEY,
            test                VARCHAR(40)  NOT NULL
                                 CHECK (test IN (
                                     'winding_to_ground_resistance',
                                     'lra_rla_ratio',
                                     'compression_ratio',
                                     'start_component',
                                     'crankcase_heater_check'
                                 )),
            sub_mode_card       VARCHAR(3)   NOT NULL
                                 CHECK (sub_mode_card IN ('26a', '26b', '26c', '26d', '26e')),
            threshold_value     NUMERIC(10,2),
            threshold_value_max NUMERIC(10,2),
            unit                VARCHAR(20)  NOT NULL,
            comparison           VARCHAR(10)  NOT NULL
                                 CHECK (comparison IN ('below', 'above', 'between', 'equals')),
            interpretation      TEXT         NOT NULL,
            source              TEXT         NOT NULL,
            confidence          VARCHAR(10)  NOT NULL DEFAULT 'Low'
                                 CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes               TEXT,
            created_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
            CONSTRAINT chk_compressor_thresholds_between
                CHECK (comparison <> 'between' OR threshold_value_max IS NOT NULL)
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_compressor_test_thresholds_lookup
            ON compressor_test_thresholds (test, sub_mode_card)
    """))

    # ------------------------------------------------------------------
    # SECTION 2 -- four net-new tables (2.1-2.3 have no v1 counterpart;
    # 2.4 is new in this revision). Schemas for 2.1-2.3 derived from
    # research_v2/A6, B5, B6 and cross-checked against RECONCILED_MASTER
    # Section 1.7-1.9 (row counts 12 / 12 / 18). 2.4's column set is the
    # exact spec given for this migration.
    # ------------------------------------------------------------------

    # 2.1 cfm_per_ton_targets (research_v2/A6) -- schema derived here; A6 did
    # not propose an explicit DDL block. 12 indicator rows per RECONCILED_MASTER
    # Sec 1.7 (static-pressure "context rows" in A6 Sec 2 are out of scope --
    # already covered by static_pressure_targets).
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS cfm_per_ton_targets (
            id                  SERIAL PRIMARY KEY,
            indicator           VARCHAR(50) NOT NULL,
            cfm_per_ton_min     NUMERIC(6,1),
            cfm_per_ton_max     NUMERIC(6,1),
            unit                VARCHAR(20) NOT NULL DEFAULT 'CFM/ton',
            interpretation      TEXT        NOT NULL,
            source              TEXT        NOT NULL,
            confidence          VARCHAR(10) NOT NULL
                                CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes               TEXT,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_cfm_per_ton_indicator UNIQUE (indicator)
        )
    """))

    # 2.2 thermostat_low_voltage_targets (research_v2/B5) -- table schema per
    # B5 Section 3; the two "reading intake" columns B5 also lists
    # (measured_under_load, meter_impedance) are intentionally NOT added here
    # -- they belong on diagnostic_questions/reading_inputs, not this
    # threshold table. See migration_046_NOTES.md.
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS thermostat_low_voltage_targets (
            id              SERIAL PRIMARY KEY,
            check_name      VARCHAR(50) NOT NULL
                            CHECK (check_name IN (
                                'control_voltage_nominal',
                                'control_voltage_acceptable_range',
                                'control_voltage_brownout',
                                'r_to_c',
                                'r_to_c_zero',
                                'c_wire_present',
                                'transformer_va',
                                'control_fuse_amps',
                                'phantom_voltage_flag'
                            )),
            value_min       NUMERIC(6,2),
            value_max       NUMERIC(6,2),
            unit            VARCHAR(20) NOT NULL,
            interpretation  TEXT        NOT NULL,
            source          TEXT        NOT NULL,
            confidence      VARCHAR(10) NOT NULL
                            CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes           TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_thermostat_low_voltage_check
            ON thermostat_low_voltage_targets (check_name)
    """))

    # 2.3 vacuum_validation_targets (research_v2/B6) -- check_name enum widened
    # to 10 values to match B6 Section 4's actual 18-row data table (Section
    # 3's schema sketch only listed 6; Section 4 is authoritative per
    # RECONCILED_MASTER Sec 1.9, "Final rows: 18").
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS vacuum_validation_targets (
            id              SERIAL PRIMARY KEY,
            check_name      VARCHAR(40) NOT NULL
                            CHECK (check_name IN (
                                'target_vacuum',
                                'decay_pass_hold',
                                'decay_pass_rise',
                                'decay_fail_rise',
                                'decay_test_duration',
                                'moisture_leveloff',
                                'ice_leveloff',
                                'nitrogen_sweep_setpoint',
                                'epa608_recovery_lowpressure',
                                'epa608_recovery_veryhigh'
                            )),
            value_min       NUMERIC(10,2),
            value_max       NUMERIC(10,2),
            unit            VARCHAR(20) NOT NULL,
            oil_refrigerant VARCHAR(30),
            interpretation  TEXT        NOT NULL,
            source          TEXT        NOT NULL,
            confidence      VARCHAR(10) NOT NULL
                            CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes           TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_vacuum_validation_check
            ON vacuum_validation_targets (check_name)
    """))

    # 2.4 liquid_line_restriction_thresholds (NEW in this revision) -- Card 25
    # (Liquid-Line Restriction). Source: RESEARCH_card25_liquidline_threshold_
    # compute.md Sections 3-4. Column set is the exact 10-column spec given
    # for this migration (id, refrigerant, check_type, threshold_value, unit,
    # comparison, interpretation, source, confidence, notes) -- no `market`
    # and no `created_at` column, unlike the other 9 tables, per that same
    # explicit spec. `comparison` is left as free TEXT (no CHECK) since the
    # spec did not enumerate values for it. Schema only -- NOT seeded here;
    # see migration_046_NOTES.md for the three provisional LOW-confidence
    # rows (ambient_floor / drier_temp_drop / subcool_proxy) to be seeded in
    # a follow-up step.
    bind.execute(text("""
        CREATE TABLE IF NOT EXISTS liquid_line_restriction_thresholds (
            id                  SERIAL PRIMARY KEY,
            refrigerant         TEXT        NOT NULL,
            check_type          TEXT        NOT NULL
                                CHECK (check_type IN ('ambient_floor', 'drier_temp_drop', 'subcool_proxy')),
            threshold_value     NUMERIC(6,2) NOT NULL,
            unit                TEXT        NOT NULL,
            comparison          TEXT        NOT NULL,
            interpretation      TEXT        NOT NULL,
            source              TEXT        NOT NULL,
            confidence          TEXT        NOT NULL
                                CHECK (confidence IN ('High', 'Medium', 'Low', 'Deferred')),
            notes               TEXT
        )
    """))
    bind.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_liquid_line_restriction_thresholds_lookup
            ON liquid_line_restriction_thresholds (refrigerant, check_type)
    """))

    # ------------------------------------------------------------------
    # SECTION 3 -- fault_cards: 5 homeowner-copy columns (B1 locked decision).
    # Style follows migration 026 (plain op.add_column per column) per the
    # companion spec's explicit recommendation, not migration 016's raw-SQL
    # "IF NOT EXISTS" re-run-safe style -- this is a one-time clean change.
    # ------------------------------------------------------------------
    op.add_column("fault_cards", sa.Column("homeowner_header", sa.Text, nullable=True))
    op.add_column("fault_cards", sa.Column("homeowner_body", sa.Text, nullable=True))
    op.add_column("fault_cards", sa.Column("layer4_disclaimer", sa.Text, nullable=True))
    op.add_column("fault_cards", sa.Column("layer5_note", sa.Text, nullable=True))
    op.add_column(
        "fault_cards",
        sa.Column(
            "company_attribution",
            sa.Boolean,
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # ------------------------------------------------------------------
    # SECTION 4 -- card_id constraint check (D1 / Cards 25 + 26): NO ALTER.
    # FINDING: fault_cards.card_id is sa.Integer, primary_key=True, with no
    # CHECK constraint / enum / range limit / trigger anywhere in migrations
    # 007, 016, or 026 (independently verified by reading all three; only a
    # code COMMENT says "card_id 1-19", not an enforced constraint). Cards 25
    # and 26 (D1 locked) can be inserted as plain integers with NO schema
    # change. Nothing is added in this section by design -- this is the
    # documented negative finding, not an omission.
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # SECTION 5 -- Card 25 (Liquid-Line Restriction) schema gap: RESOLVED
    # (schema only) via Section 2.4's liquid_line_restriction_thresholds
    # table above. Per D1_10c_split_spec.md Sec 2.3, Card 25 needed (a) a
    # liquid-line temperature-drop/ambient-floor threshold -- now added in
    # Section 2.4 -- and (b) a head/discharge-pressure "normal-to-low after
    # runtime" reference -- CONFIRMED as already covered by the existing
    # operating_targets table (migration 036), no schema change needed. See
    # migration_046_tierA_schema.sql Section 5 and migration_046_NOTES.md.
    # ------------------------------------------------------------------


def downgrade() -> None:
    # Reverse order of upgrade().

    # Section 3 reversal -- drop the 5 homeowner-copy columns, reverse order.
    op.drop_column("fault_cards", "company_attribution")
    op.drop_column("fault_cards", "layer5_note")
    op.drop_column("fault_cards", "layer4_disclaimer")
    op.drop_column("fault_cards", "homeowner_body")
    op.drop_column("fault_cards", "homeowner_header")

    # Section 2 reversal -- drop the 4 net-new tables, reverse creation order
    # (2.4 was created last, so it is dropped first).
    bind = op.get_bind()
    bind.execute(text("DROP TABLE IF EXISTS liquid_line_restriction_thresholds"))
    bind.execute(text("DROP TABLE IF EXISTS vacuum_validation_targets"))
    bind.execute(text("DROP TABLE IF EXISTS thermostat_low_voltage_targets"))
    bind.execute(text("DROP TABLE IF EXISTS cfm_per_ton_targets"))

    # Section 1 reversal -- drop the 6 already-drafted tables.
    bind.execute(text("DROP TABLE IF EXISTS compressor_test_thresholds"))
    bind.execute(text("DROP TABLE IF EXISTS sizing_rules"))
    bind.execute(text("DROP TABLE IF EXISTS latent_targets"))
    bind.execute(text("DROP TABLE IF EXISTS delta_t_targets"))
    bind.execute(text("DROP TABLE IF EXISTS static_pressure_targets"))
    bind.execute(text("DROP TABLE IF EXISTS superheat_subcool_targets"))
