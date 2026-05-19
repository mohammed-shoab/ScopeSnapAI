"""
028 -- lifecycle_rules expansion: 17 -> ~50 rows (US side only)
REC.3 -- Board-approved signals for all 19 fault cards.

New rules added (idempotent -- WHERE NOT EXISTS guard prevents duplicates):
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

FIX NOTE (v3): Added component_name to INSERT -- lifecycle_rules.component_name
is NOT NULL. Lookup via _COMPONENT_BY_CARD dict keyed on card_id.
"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy import text

revision: str = "028"
down_revision: Union[str, None] = "027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# component_name for each fault card (from fault_cards.card_name)
_COMPONENT_BY_CARD = {
    1:  "run_capacitor",    # Capacitor Failure
    3:  "contactor",        # Contactor Failure
    4:  "blower_motor",     # Blower Motor Failure
    5:  "drain_system",     # Drain Clog
    7:  "control_board",    # Control Board / Error Code
    8:  "evaporator_coil",  # Refrigerant Leak (evap coil source)
    10: "compressor",       # Compressor Failure
    11: "flame_sensor",     # sensor_only signal targets flame sensor
    13: "ductwork",         # Ductwork Leak
    15: "fixed_orifice",    # Fixed Orifice / Piston Mismatch
    16: "loose_terminal",   # Loose Terminal
    19: "evaporator_coil",  # Formicary Corrosion (on evap coil)
}

# Each tuple: (card_id, condition_signal, age_threshold_years_or_None, recommended_tier, note)
_NEW_RULES = [
    # --- under_warranty -> A (11 cards) ---
    (1,  "under_warranty", 2, "A",
     "New unit -- manufacturer warranty likely covers capacitor replacement"),
    (3,  "under_warranty", 2, "A",
     "New unit -- contactor failure within warranty period"),
    (4,  "under_warranty", 2, "A",
     "New unit -- blower motor covered by manufacturer warranty"),
    (5,  "under_warranty", 2, "A",
     "New unit -- drain clog is maintenance; warranty covers component"),
    (7,  "under_warranty", 2, "A",
     "New unit -- control board failure under warranty"),
    (8,  "under_warranty", 2, "A",
     "New unit -- refrigerant leak likely install defect; warranty covers"),
    (10, "under_warranty", 2, "A",
     "New unit -- compressor under manufacturer warranty"),
    (13, "under_warranty", 2, "A",
     "New unit -- ductwork leak likely install-side issue; warranty covers"),
    (15, "under_warranty", 2, "A",
     "New unit -- piston/orifice mismatch likely install error; warranty covers"),
    (16, "under_warranty", 2, "A",
     "New unit -- loose terminal within warranty period"),
    (19, "under_warranty", 2, "A",
     "New unit -- formicary corrosion within warranty period"),
    # --- photo_confirmed_pitting -> C (4 cards) ---
    (1,  "photo_confirmed_pitting", 5, "C",
     "Visible pitting on capacitor terminals -- full electrical replacement recommended"),
    (3,  "photo_confirmed_pitting", 5, "C",
     "Visible pitting on contactor points -- replace contactor and inspect wiring"),
    (4,  "photo_confirmed_pitting", 7, "C",
     "Electrical damage on blower motor terminals -- motor replacement recommended"),
    (10, "photo_confirmed_pitting", 5, "C",
     "Pitting on compressor terminals indicates corrosive environment -- replace compressor"),
    # --- formicary_confirmed -> C or B ---
    (8,  "formicary_confirmed", None, "C",
     "Formicary corrosion confirmed on evap coil -- full coil replacement required"),
    (19, "formicary_confirmed", None, "C",
     "Formicary corrosion on evap coil -- replace coil and inspect system"),
    (7,  "formicary_confirmed", None, "C",
     "Formicary corrosion at control board -- full board replacement to stop spread"),
    (13, "formicary_confirmed", None, "B",
     "Formicary suspected near ductwork leak point -- comprehensive repair with coil treatment"),
    # --- rla_over_nameplate -> C or B ---
    (4,  "rla_over_nameplate", 6,  "C",
     "Blower motor drawing over nameplate RLA on aging unit -- replacement recommended"),
    (4,  "rla_over_nameplate", None, "B",
     "Blower motor RLA elevated on newer unit -- repair and monitor closely"),
    (10, "rla_over_nameplate", 5,  "C",
     "Compressor drawing over nameplate RLA -- replacement recommended"),
    (10, "rla_over_nameplate", None, "B",
     "Compressor RLA elevated -- repair with capacitor check first"),
    (16, "rla_over_nameplate", 5,  "C",
     "Loose terminal causing motor over nameplate RLA -- full terminal service"),
    (16, "rla_over_nameplate", None, "B",
     "Terminal issue causing elevated RLA on newer unit -- repair with inspection"),
    # --- recurring_clog ---
    (5,  "recurring_clog", None, "C",
     "Second or more drain clog this year -- full drain system service and treatment"),
    # --- attic_location ---
    (13, "attic_location", 8,   "C",
     "Attic-installed aging unit with ductwork leak -- replace to improve accessibility"),
    (13, "attic_location", None, "B",
     "Attic access premium applies -- comprehensive repair with leak test"),
    (1,  "attic_location", None, "B",
     "Attic access adds service cost -- Better option covers full service visit"),
    (5,  "attic_location", None, "B",
     "Attic drain service requires extra access time -- comprehensive drain service"),
    # --- bearing_noise ---
    (4,  "bearing_noise", 5,   "C",
     "Bearing noise on blower motor -- replacement is the safer path on aging unit"),
    (4,  "bearing_noise", None, "B",
     "Bearing noise on newer blower motor -- repair and monitor; replacement not yet justified"),
    # --- sensor_only ---
    (11, "sensor_only", None, "A",
     "Error code confirms sensor failure only -- replace sensor, no ignitor needed"),
]


def upgrade() -> None:
    for (card_id, condition_signal, age_threshold, recommended_tier, note) in _NEW_RULES:
        age_sql = "NULL" if age_threshold is None else str(int(age_threshold))
        note_sql = note.replace("'", "''")
        cond_sql = condition_signal.replace("'", "''")
        tier_sql = recommended_tier.replace("'", "''")
        comp_sql = _COMPONENT_BY_CARD[card_id].replace("'", "''")
        sql = (
            "INSERT INTO lifecycle_rules"
            " (card_id, component_name, condition_signal, age_threshold_years, recommended_tier, note)"
            " SELECT"
            " " + str(card_id) + ","
            " '" + comp_sql + "',"
            " '" + cond_sql + "',"
            " " + age_sql + ","
            " '" + tier_sql + "',"
            " '" + note_sql + "'"
            " WHERE NOT EXISTS ("
            " SELECT 1 FROM lifecycle_rules"
            " WHERE card_id = " + str(card_id) +
            " AND condition_signal = '" + cond_sql + "'"
            " AND age_threshold_years IS NOT DISTINCT FROM " + age_sql +
            " )"
        )
        op.execute(text(sql))


def downgrade() -> None:
    signals = [
        "under_warranty", "formicary_confirmed", "rla_over_nameplate",
        "recurring_clog", "attic_location", "bearing_noise", "sensor_only",
    ]
    for signal in signals:
        signal_sql = signal.replace("'", "''")
        op.execute(text("DELETE FROM lifecycle_rules WHERE condition_signal = '" + signal_sql + "'"))
    op.execute(text(
        "DELETE FROM lifecycle_rules"
        " WHERE condition_signal = 'photo_confirmed_pitting'"
        " AND card_id IN (3, 4, 10)"
    ))
