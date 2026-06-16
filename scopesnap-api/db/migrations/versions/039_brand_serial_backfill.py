"""Brand table serial-decode backfill (v1.2 brand-decoder, Stage 1).

Adds nullable serial-decode metadata columns to ``brands`` and backfills them
from ``data/serial_decoder_data_v1.2.json`` so brand decode rules are queryable
in SQL (the runtime decoder reads the JSON directly, so this table is a
convenience/reporting mirror — the app does not depend on it).

Idempotent: columns are added with IF-NOT-EXISTS guards, and the backfill is an
UPSERT keyed on the brand slug. Safe to re-run. If the data file is missing at
migration time (e.g. minimal deploy), the column add still succeeds and the
backfill is skipped with a warning.

Revision ID: 039
Revises: 038
"""
from __future__ import annotations

import json
import os
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision: str = "039"
down_revision: Union[str, None] = "038"
branch_labels = None
depends_on = None

_NEW_COLS = ("serial_format", "serial_decodable", "serial_market", "oem_siblings")


def _data_file() -> str:
    # <repo>/scopesnap-api/db/migrations/versions/ -> up 3 to scopesnap-api/ then data/
    override = os.getenv("BRAND_DATA_DIR")
    if override:
        return os.path.join(override, "serial_decoder_data_v1.2.json")
    here = os.path.dirname(os.path.abspath(__file__))
    api_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    return os.path.join(api_root, "data", "serial_decoder_data_v1.2.json")


def upgrade() -> None:
    bind = op.get_bind()

    # 1) Add columns (idempotent).
    bind.execute(text(
        'ALTER TABLE "brands" '
        'ADD COLUMN IF NOT EXISTS "serial_format" JSONB, '
        'ADD COLUMN IF NOT EXISTS "serial_decodable" BOOLEAN, '
        'ADD COLUMN IF NOT EXISTS "serial_market" VARCHAR(10), '
        'ADD COLUMN IF NOT EXISTS "oem_siblings" TEXT[]'
    ))

    # 2) Backfill from the v1.2 JSON (skip gracefully if absent).
    path = _data_file()
    if not os.path.exists(path):
        print(f"[migration 039] data file not found at {path}; skipping backfill")
        return

    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)

    brands = payload.get("brands", [])
    upserted = 0
    for rec in brands:
        canon = (rec.get("canonical_name") or "").strip()
        if not canon:
            continue
        slug = canon.lower().replace(" ", "_")
        siblings = [s for s in (rec.get("oem_siblings") or []) if s]
        market = rec.get("market") or "US"
        # decodable = the brand has at least one variant with a modern regex
        variants = rec.get("variants") or {}
        decodable = any(
            (v or {}).get("modern_regex") or (v or {}).get("modern_pattern")
            for v in variants.values()
        )
        serial_format = json.dumps(
            {k: {"pattern": (v or {}).get("modern_pattern"),
                 "regex": (v or {}).get("modern_regex"),
                 "year_position": (v or {}).get("year_position"),
                 "month_position": (v or {}).get("month_position")}
             for k, v in variants.items()}
        )

        bind.execute(
            text(
                'INSERT INTO "brands" ("id", "name", "serial_format", '
                '"serial_decodable", "serial_market", "oem_siblings") '
                "VALUES (:id, :name, CAST(:fmt AS JSONB), :dec, :mkt, :sib) "
                'ON CONFLICT ("id") DO UPDATE SET '
                '"serial_format" = EXCLUDED."serial_format", '
                '"serial_decodable" = EXCLUDED."serial_decodable", '
                '"serial_market" = EXCLUDED."serial_market", '
                '"oem_siblings" = EXCLUDED."oem_siblings"'
            ),
            {"id": slug, "name": canon, "fmt": serial_format,
             "dec": decodable, "mkt": market, "sib": siblings},
        )
        upserted += 1

    print(f"[migration 039] backfilled serial metadata for {upserted} brands")


def downgrade() -> None:
    bind = op.get_bind()
    for col in _NEW_COLS:
        bind.execute(text(f'ALTER TABLE "brands" DROP COLUMN IF EXISTS "{col}"'))
