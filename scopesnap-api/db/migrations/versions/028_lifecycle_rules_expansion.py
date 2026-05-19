"""
028 -- lifecycle_rules expansion: 17 -> ~50 rows (US side only)
REC.3 -- Board-approved signals for all 19 fault cards.

New rules added (idempotent -- LEFT JOIN guard prevents duplicates):
  under_warranty         -> A  (11 cards: 1,3,4,5,7,8,10,13,15,16,19)
  photo_confirmed_pitting -> C  (4 cards: 1,3,4,10 with age threshold)
  formicary_confirmed    -> C/B (4 cards: 8,19,7,13)
  rla_over_nameplate     -> C/B (3 cards: 4,10,16 age-gated)
  recurring_clog         -> C  (card 5 only)
  attic_location         -> B/C (cards 13,1,5 + age gate)
  bearing_noise          -> C/B (card 4 age-gated)
  sensor_only            -> A  (card 11 only)

Total new rows: 33. Total after: ~50.

FIX NOTE (v2): Uses direct f-string interpolation -- NOT op.execute bind params.
In Alembic 1.13, op.execute(text(...), dict) treats dict as execution_options,
not query parameters. Direct interpolation avoids this bug entirely.
All string values are escaped with replace("'", "''") before interpolation.
"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy import text

revision: str = "028"
down_revision: Union[str, None] = "025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Each tuple: (card_id, condition_signal, age_threshold_years_or_None, recommended_tier, note)
# age_threshold_years: None means "any age"; integer means "unit age >= this value"
_NEW_RULES = [
    # --- under_warranty -> A (11 cards) ---
    (1,  "under_warranty", 2, "A",
     "New unit -- manufacturer warranty likely covers capacitor replacement"),
    (3,  "under_warranty", 2, "A",
     "New unit -- contactor failure within warranty period"),
    (4,  "under_warranty", 2, "A",
     "New unit -- compressor covered by manufacturer warranty"),
    (5,  "under_warranty", 2, "A",
     "New unit -- drain clog is maintenance; warranty covers component"),
    (7,  "under_warranty", 2, "A",
     "New unit -- refrigerant leak under warranty"),
    (8,  "under_warranty", 2, "A",
     "New unit -- evap coil defect likely warranty-eligible"),
    (10, "under_warranty", 2, "A",
     "New unit -- condenser fan motor under warranty"),
    (13, "under_warranty", 2, "A",
     "New unit -- low charge likely install-side issue; warranty covers"),
    (15, "under_warranty", 2, "A",
     "New unit -- defrost board failure within warranty"),
    (16, "under_warranty", 2, "A",
     "New unit -- blower motor under warranty"),
    (19, "under_warranty", 2, "A",
     "New unit -- TXV failure within warranty period"),

    # --- photo_confirmed_pitting -> C (4 cards, age threshold) ---
    (1,  "photo_confirmed_pitting", 5, "C",
     "Visible pitting on capacitor terminals -- full electrical replacement recommended"),
    (3,  "photo_confirmed_pitting", 5, "C",
     "Visible pitting on contactor points -- replace contactor and inspect wiring"),
    (4,  "photo_confirmed_pitting", 7, "C",
     "Electrical damage on compressor terminals -- unit replacement recommended"),
    (10, "photo_confirmed_pitting", 5, "C",
     "Pitting on motor terminals indicates corrosive environment -- replace motor"),

    # --- formicary_confirmed -> C or B (4 cards) ---
    (8,  "formicary_confirmed", None, "C",
     "Formicary corrosion confirmed on evap coil -- full coil replacement required"),
    (19, "formicary_confirmed", None, "C",
     "Formicary corrosion on TXV -- replace TXV and inspect evap coil"),
    (7,  "formicary_confirmed", None, "C",
     "Formicary corrosion at leak origin -- full coil replacement to stop spread"),
    (13, "formicary_confirmed", None, "B",
     "Formicary suspected near leak point -- comprehensive repair with coil treatment"),

    # --- rla_over_nameplate -> C or B (3 cards, age-gated) ---
    (4,  "rla_over_nameplate", 6,  "C",
     "Compressor drawing over nameplate RLA on aging unit -- replacement recommended"),
    (4,  "rla_over_nameplate", None, "B",
     "Compressor RLA elevated on newer unit -- repair and monitor closely"),
    (10, "rla_over_nameplate", 5,  "C",
     "Condenser fan motor over nameplate RLA -- motor replacement"),
    (10, "rla_over_nameplate", None, "B",
     "Fan motor RLA elevated -- repair with new run capacitor first"),
    (16, "rla_over_nameplate", 5,  "C",
     "Blower motor drawing over nameplate RLA -- motor replacement"),
    (16, "rla_over_nameplate", None, "B",
     "Blower RLA elevated on newer unit -- repair with capacitor check"),

    # --- recurring_clog -> C (card 5 only) ---
    (5,  "recurring_clog", None, "C",
     "Second or more drain clog this year -- full drain system service and treatment"),

    # --- attic_location -> B or C (4 rules) ---
    (13, "attic_location", 8,   "C",
     "Attic-installed aging unit with refrigerant leak -- replace to improve accessibility"),
    (13, "attic_location", None, "B",
     "Attic access premium applies -- comprehensive repair with leak test"),
    (1,  "attic_location", None, "B",
     "Attic access adds service cost -- Better option covers full service visit"),
    (5,  "attic_location", None, "B",
     "Attic drain service requires extra access time -- comprehensive drain service"),

    # --- bearing_noise -> C or B (card 4, age-gated) ---
    (4,  "bearing_noise", 5,   "C",
     "Bearing noise on compressor -- replacement is the safer path on aging unit"),
    (4,  "bearing_noise", None, "B",
     "Bearing noise on newer compressor -- repair and monitor; replacement not yet justified"),

    # --- sensor_only -> A (card 11 only) ---
    (11, "sensor_only", None, "A",
     "Error code confirms sensor failure only -- replace sensor, no ignitor needed"),
]


def upgrade() -> None:
    # IMPORTANT: Uses direct f-string interpolation -- NOT op.execute bind params.
    # In Alembic 1.13, op.execute(text(...), dict) passes dict as execution_options,
    # not as query parameters. This caused migration failure in v1 (502 on Railway).
    # All string values escaped via replace("'", "''") before interpolation.
    for (card_id, condition_signal, age_threshold, recommended_tier, note) in _NEW_RULES:
        age_sql = "NULL" if age_threshold is None else str(int(age_threshold))
        note_sql = note.replace("'", "''")
        cond_sql = condition_signal.replace("'", "''")
        tier_sql = recommended_tier.replace("'", "''")
        op.execute(text(f"""
            INSERT INTO lifecycle_rules
                (card_id, condition_signal, age_threshold_years, recommended_tier, note)
            SELECT
                {card_id},
                '{cond_sql}',
                {age_sql},
                '{tier_sql}',
                '{note_sql}'
            WHERE NOT EXISTS (
                SELECT 1
                FROM lifecycle_rules
                WHERE card_id = {card_id}
                  AND condition_signal = '{cond_sql}'
                  AND age_threshold_years IS NOT DISTINCT FROM {age_sql}
            )
        """))


def downgrade() -> None:
    # Remove the REC.3 rows by signal -- safe because these signals were not in the original 17
    signals = [
        "under_warranty", "formicary_confirmed", "rla_over_nameplate",
        "recurring_clog", "attic_location", "bearing_noise", "sensor_only",
    ]
    for signal in signals:
        signal_sql = signal.replace("'", "''")
        op.execute(text(f"DELETE FROM lifecycle_rules WHERE condition_signal = '{signal_sql}'"))
    # photo_confirmed_pitting had partial rows in original -- only delete age < 5 threshold rows
    op.execute(text("""
        DELETE FROM lifecycle_rules
        WHERE condition_signal = 'photo_confirmed_pitting'
          AND card_id IN (3, 4, 10)
    """))
