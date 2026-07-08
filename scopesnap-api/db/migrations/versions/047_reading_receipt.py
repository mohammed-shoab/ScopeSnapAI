"""047 -- add reading_receipt jsonb to diagnostic_sessions (GATE-5 Reading Receipt).

Stores the resolving reading + target snapshot captured at card resolution so the
FaultResolutionScreen can render the inline Reading Receipt (reading vs target,
result, why, confidence, Layer-4). Nullable: only reading/multi resolutions set it.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "047"
down_revision: Union[str, None] = "046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "diagnostic_sessions",
        sa.Column("reading_receipt", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("diagnostic_sessions", "reading_receipt")
