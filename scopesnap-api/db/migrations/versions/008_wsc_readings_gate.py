"""WS-C: Phase 2 Readings Gate — add pressure readings columns to assessments

Revision ID: 008
Revises: 007
Create Date: 2026-05-01

NOTE: This migration was applied DIRECTLY in Supabase on 2026-05-01 (bypass Railway).
alembic_version was manually updated to '008'. Railway will skip this on next boot.
"""

from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add pressure readings + gate columns to assessments table
    op.add_column("assessments", sa.Column("suction_psig", sa.Numeric(), nullable=True))
    op.add_column("assessments", sa.Column("discharge_psig", sa.Numeric(), nullable=True))
    op.add_column("assessments", sa.Column("ambient_temp_f", sa.Numeric(), nullable=True))
    op.add_column("assessments", sa.Column("supply_air_temp_f", sa.Numeric(), nullable=True))
    # Optional — enables auto-calc of superheat / subcooling
    op.add_column("assessments", sa.Column("suction_line_temp_f", sa.Numeric(), nullable=True))
    op.add_column("assessments", sa.Column("liquid_line_temp_f", sa.Numeric(), nullable=True))
    # From Step Zero OCR or manual entry
    op.add_column("assessments", sa.Column("refrigerant_type", sa.String(10), nullable=True))
    op.add_column("assessments", sa.Column("metering_device", sa.String(10), nullable=True))
    # Computed and stored
    op.add_column("assessments", sa.Column("superheat_f", sa.Numeric(), nullable=True))
    op.add_column("assessments", sa.Column("subcooling_f", sa.Numeric(), nullable=True))
    op.add_column("assessments", sa.Column("delta_t_f", sa.Numeric(), nullable=True))
    # Gate flags
    op.add_column("assessments", sa.Column(
        "readings_gate_triggered", sa.Boolean(), server_default="false", nullable=False
    ))
    op.add_column("assessments", sa.Column(
        "readings_completed", sa.Boolean(), server_default="false", nullable=False
    ))

    op.execute("""
        ALTER TABLE assessments
        ADD CONSTRAINT chk_assessments_refrigerant_type
        CHECK (refrigerant_type IN ('R-410A', 'R-22', 'R-32', 'R-454B') OR refrigerant_type IS NULL)
    """)
    op.execute("""
        ALTER TABLE assessments
        ADD CONSTRAINT chk_assessments_metering_device
        CHECK (metering_device IN ('piston', 'txv', 'eev') OR metering_device IS NULL)
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE assessments DROP CONSTRAINT IF EXISTS chk_assessments_metering_device")
    op.execute("ALTER TABLE assessments DROP CONSTRAINT IF EXISTS chk_assessments_refrigerant_type")
    for col in [
        "readings_completed", "readings_gate_triggered", "delta_t_f",
        "subcooling_f", "superheat_f", "metering_device", "refrigerant_type",
        "liquid_line_temp_f", "suction_line_temp_f", "supply_air_temp_f",
        "ambient_temp_f", "discharge_psig", "suction_psig",
    ]:
        op.drop_column("assessments", col)
