"""WS-B — Step Zero OCR: add ocr_nameplate to assessments

Revision ID: 009
Revises: 008
Create Date: 2026-04-30

Adds:
  assessments.ocr_nameplate  JSONB  — stores the structured OCR result from
    the nameplate photo capture step (Step Zero).

Schema of the stored JSON:
  {
    "outdoor": {
      "model_number": "24ACC636A003",
      "serial_number": "4816E12345",
      "tonnage": 3.0,
      "refrigerant": "R-410A",
      "factory_charge_oz": 94,
      "rla": 14.2,
      "lra": 82.0,
      "capacitor_uf": "45/5",
      "mca": 17.6,
      "mocp": 25,
      "voltage": "208/230",
      "year_of_manufacture": 2016,
      "brand_id": "carrier",
      "series_id": "carrier_performance",
      "charging_method": "subcooling",
      "metering_device": "TXV",
      "is_legacy": false,
      "confidence": 92,
      "gemini_raw": "..."        // raw Gemini response for debugging
    },
    "indoor": { ... },          // same shape, nullable fields
    "captured_at": "2026-04-30T20:00:00Z",
    "capture_method": "photo"   // "photo" | "manual"
  }
"""

from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assessments",
        sa.Column(
            "ocr_nameplate",
            postgresql.JSONB,
            nullable=True,
            comment=(
                "Step Zero OCR result: {outdoor:{model_number,serial_number,tonnage,"
                "refrigerant,factory_charge_oz,rla,lra,capacitor_uf,mca,mocp,voltage,"
                "year_of_manufacture,brand_id,series_id,charging_method,metering_device,"
                "is_legacy,confidence}, indoor:{...}, captured_at, capture_method}"
            ),
        ),
    )

    # Index for quickly finding assessments that have been through Step Zero
    op.create_index(
        "ix_assessments_ocr_nameplate_notnull",
        "assessments",
        ["ocr_nameplate"],
        postgresql_where=sa.text("ocr_nameplate IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_assessments_ocr_nameplate_notnull", table_name="assessments")
    op.drop_column("assessments", "ocr_nameplate")
