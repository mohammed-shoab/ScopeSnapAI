"""Add seasonal modifier columns to companies and estimates.

Track R.9 — seasonal labor surcharge.
  companies.peak_season_surcharge_percent  INT nullable
      NULL  = use market default (25 in peak months, 0 off-peak)
      0     = company has disabled seasonal surcharge
      1-100 = company's custom override percent

  estimates.seasonal_modifier_pct  INT not-null default 0
      Snapshot of the pct actually applied at generation time.
      Frozen per generation-time-freeze rule (QA Decision doc SS15.2 Q4).

Revision: 029
Down-revision: 028
"""
from alembic import op
import sqlalchemy as sa

revision = '029'
down_revision = '028'
branch_labels = None
depends_on = None


def upgrade():
    # companies -- nullable so NULL means "use market default"
    op.add_column(
        'companies',
        sa.Column(
            'peak_season_surcharge_percent',
            sa.Integer(),
            nullable=True,
            comment=(
                'NULL=use market default (25% peak / 0 off-peak), '
                '0=disabled, 1-100=custom override'
            ),
        ),
    )

    # estimates -- not-null with default 0; set to actual pct at generation time
    op.add_column(
        'estimates',
        sa.Column(
            'seasonal_modifier_pct',
            sa.Integer(),
            nullable=False,
            server_default='0',
            comment='Seasonal labor surcharge % applied at generation time (generation-time freeze)',
        ),
    )


def downgrade():
    op.drop_column('estimates', 'seasonal_modifier_pct')
    op.drop_column('companies', 'peak_season_surcharge_percent')
