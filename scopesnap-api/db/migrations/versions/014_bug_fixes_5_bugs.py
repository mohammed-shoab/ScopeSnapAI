"""014 — Bug fixes: BUG #9 / #11 / #12 / #13 + 3 untested branches

Revision ID: 014
Revises: 013
Create Date: 2026-05-11

Fixes applied
-------------

BUG #9  (error_code/q4-reset — dead-end "no" branch):
  wsg3 patch replaced the original jump_to_complaint with
  ``escalate: true`` — no repair path.  Fix: "no" → resolve_card 7
  (control board / nuisance-trip card), same as "yes".

BUG #11 (not_cooling/q3-contactor — voltage always escalates):
  reading_spec had no low_threshold, so the frontend classifyReading()
  fell to the generic branchKey:"ok" path for every voltage value.
  Fix: add low_threshold:100 to reading_spec so the new frontend
  voltage handler produces "no_power" (<100 V) or "power_passes_normal"
  (>=100 V).

BUG #12 (water_dripping/outdoor — immediate 404→422):
  q1 outdoor_refrigerant branch used phase_2_gate → frontend POSTed
  to /estimates/fault-card with card_id=null → Pydantic error.
  Fix: replace phase_2_gate with next_step_id + insert suction PSI step.

BUG #13 (not_heating/q4-flame-sensor — flame-sensor uA always escalates):
  (a) reading_spec type was "micro_amps" (underscore) — frontend
      classifyReading() checks type==="microamps" (no underscore) so
      always fell to generic branchKey:"ok".
  Fix: change type to "microamps".
  (b) branch_logic lacked keys for the numeric output ("low"/"ok") that
      the fixed frontend will now produce.
  Fix: add "low" → resolve_card 11, "ok" → escalate (sensor good).

Untested #1 (not_turning_on/q2-no-power — same voltage threshold bug):
  Same root cause as BUG #11.  Add low_threshold:100 to reading_spec.

Untested #2 (making_noise/q4-compressor — over-rla always escalates):
  "over_rla" had both resolve_card:10 AND escalate:true.  In
  _process_branch, the escalate check runs first → always escalates.
  Fix: remove escalate:true from "over_rla".

Untested #3 (making_noise/q1 hissing — same phase_2_gate bug as BUG #12):
  Fix: replace phase_2_gate with next_step_id + insert suction PSI step.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


# ── Shared reading / branch specs ─────────────────────────────────────────────

_WD_SUCTION_READING_SPEC = (
    '{"type": "psi", "unit": "PSI", "subtype": "suction",'
    ' "compare_to": null,'
    ' "low_threshold": 60, "high_threshold": 110,'
    ' "placeholder": "e.g. 70 PSI"}'
)

_WD_SUCTION_BRANCH_LOGIC = (
    '{'
    '"low":  {"resolve_card": 8,  "photo_slots": [{"slot": "uv_dye_glow",'
    '  "photo_type": "evidence",'
    '  "instruction": "UV dye glow under blacklight — for homeowner PDF.",'
    '  "ai_prompt": null}]},'
    '"ok":   {"escalate": true, "reason": "Outdoor drip — pressures normal; check line-set insulation / condensation"},'
    '"high": {"resolve_card": 14, "photo_slots": [{"slot": "condenser_coil_face",'
    '  "photo_type": "diagnostic",'
    '  "instruction": "Face-on shot of condenser coil — capture full face.",'
    '  "ai_prompt": "Grade dirt density on condenser coil face: clean / dirty / heavily_blocked."}]}'
    '}'
)

_HISS_SUCTION_READING_SPEC = (
    '{"type": "psi", "unit": "PSI", "subtype": "suction",'
    ' "compare_to": null,'
    ' "low_threshold": 60, "high_threshold": 110,'
    ' "placeholder": "e.g. 70 PSI"}'
)

_HISS_SUCTION_BRANCH_LOGIC = (
    '{'
    '"low":  {"resolve_card": 8,  "photo_slots": [{"slot": "uv_dye_glow",'
    '  "photo_type": "evidence",'
    '  "instruction": "UV dye glow under blacklight — for homeowner PDF.",'
    '  "ai_prompt": null}]},'
    '"ok":   {"escalate": true, "reason": "Hissing — pressures normal; check TXV chatter / expansion noise"},'
    '"high": {"resolve_card": 14, "photo_slots": [{"slot": "condenser_coil_face",'
    '  "photo_type": "diagnostic",'
    '  "instruction": "Face-on shot of condenser coil — capture full face.",'
    '  "ai_prompt": "Grade dirt density on condenser coil face: clean / dirty / heavily_blocked."}]}'
    '}'
)


def upgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    # ── BUG #9: error_code/q4-reset — restore repair path on "no" ────────────
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = '{
              "yes": {"resolve_card": 7, "note": "Nuisance trip resolved by reset"},
              "no":  {"resolve_card": 7, "note": "Control board lockout — replace control board (Card #7)"}
            }'::jsonb
            WHERE complaint_type = 'error_code' AND step_id = 'q4-reset'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json('{"yes":{"resolve_card":7,"note":"Nuisance trip resolved by reset"},"no":{"resolve_card":7,"note":"Control board lockout — replace control board (Card #7)"}}')
            WHERE complaint_type = 'error_code' AND step_id = 'q4-reset'
        """))

    # ── BUG #11: not_cooling/q3-contactor — add low_threshold to reading_spec ─
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = jsonb_set(
                COALESCE(reading_spec, '{}'::jsonb),
                '{low_threshold}',
                '100'::jsonb
            )
            WHERE complaint_type = 'not_cooling' AND step_id = 'q3-contactor'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = json_patch(
                COALESCE(reading_spec, '{}'),
                '{"low_threshold": 100}'
            )
            WHERE complaint_type = 'not_cooling' AND step_id = 'q3-contactor'
        """))

    # ── BUG #12: water_dripping/q1 — replace phase_2_gate with step pointer ──
    # Insert q2-wd-suction step (step_order 2, pushes existing q2-pan-photo to 3+)
    # NOTE: existing water_dripping steps are q1=1, q2-pan-photo=2, q3-freeze-check=3.
    # We insert q2-wd-suction at step_order 10 (outdoor branch only — indoor stays on
    # q2-pan-photo) so no renumbering conflicts. The engine follows next_step_id, not
    # step_order integer sequence, for branching.
    if pg:
        bind.execute(text(f"""
            INSERT INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('water_dripping', 'q2-wd-suction', 10,
               'Read suction line pressure (low-side manifold gauge).',
               'Connect to suction service port. Outdoor drip often signals refrigerant charge issue.',
               'reading',
               NULL,
               '{_WD_SUCTION_READING_SPEC}'::jsonb,
               NULL,
               '{_WD_SUCTION_BRANCH_LOGIC}'::jsonb,
               NULL,
               FALSE)
            ON CONFLICT (complaint_type, step_id) DO NOTHING
        """))

        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{outdoor_refrigerant}',
                '{"next_step_id": "q2-wd-suction"}'::jsonb
            )
            WHERE complaint_type = 'water_dripping' AND step_id = 'q1'
        """))
    else:
        bind.execute(text(f"""
            INSERT OR IGNORE INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('water_dripping', 'q2-wd-suction', 10,
               'Read suction line pressure (low-side manifold gauge).',
               'Connect to suction service port. Outdoor drip often signals refrigerant charge issue.',
               'reading',
               NULL,
               '{_WD_SUCTION_READING_SPEC}',
               NULL,
               '{_WD_SUCTION_BRANCH_LOGIC}',
               NULL,
               0)
        """))

        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{"outdoor_refrigerant": {"next_step_id": "q2-wd-suction"}}'
            )
            WHERE complaint_type = 'water_dripping' AND step_id = 'q1'
        """))

    # ── BUG #13: not_heating/q4-flame-sensor — fix type underscore + add keys ─
    # (a) Fix reading_spec type: "micro_amps" → "microamps"
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = jsonb_set(
                reading_spec,
                '{type}',
                '"microamps"'::jsonb
            )
            WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = json_patch(reading_spec, '{"type": "microamps"}')
            WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'
        """))

    # (b) Add "low" and "ok" branch keys produced by frontend after the type fix.
    #     We merge into the existing branch_logic_jsonb (wsg3 already added the
    #     photo_branch_map + "replace"/"marginal" keys — we extend, not replace).
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = branch_logic_jsonb
              || '{"low": {"resolve_card": 11, "note": "uA below 1 — replace flame sensor"},
                   "ok":  {"escalate": true, "reason": "Flame sensor reads ok — investigate gas pressure / valve"}
                  }'::jsonb
            WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{"low": {"resolve_card": 11, "note": "uA below 1 — replace flame sensor"},
                  "ok":  {"escalate": true, "reason": "Flame sensor reads ok — investigate gas pressure / valve"}}'
            )
            WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'
        """))

    # ── Untested #1: not_turning_on/q2-no-power — add low_threshold ───────────
    # The branch_logic (wsd3) already has correct keys.  reading_spec needs
    # low_threshold:100 so the frontend voltage handler fires correctly.
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = (
                SELECT jsonb_agg(
                    CASE WHEN elem->>'kind' = 'reading'
                         THEN jsonb_set(elem, '{spec,low_threshold}', '100'::jsonb)
                         ELSE elem
                    END
                )
                FROM jsonb_array_elements(
                    CASE jsonb_typeof(reading_spec)
                         WHEN 'array' THEN reading_spec
                         ELSE jsonb_build_array(reading_spec)
                    END
                ) AS elem
            )
            WHERE complaint_type = 'not_turning_on' AND step_id = 'q2-no-power'
              AND reading_spec IS NOT NULL
        """))
        # q2-no-power uses input_type='multi' with options_jsonb array containing
        # a reading spec — update that array element instead
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = (
                SELECT jsonb_agg(
                    CASE WHEN (elem->>'kind') = 'reading'
                              AND (elem->'spec'->>'type') = 'voltage'
                         THEN jsonb_set(elem, '{spec,low_threshold}', '100'::jsonb)
                         ELSE elem
                    END
                )
                FROM jsonb_array_elements(options_jsonb) AS elem
            )
            WHERE complaint_type = 'not_turning_on' AND step_id = 'q2-no-power'
        """))
    else:
        # SQLite: full replacement of options_jsonb with updated reading spec
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = '[{"kind":"photo","spec":{"slot_name":"contactor_face","photo_type":"diagnostic","instruction":"Contactor contact face close-up.","ai_prompt":"Classify contact face: clean / pitted / arced / welded."}},{"kind":"reading","spec":{"type":"voltage","unit":"V","subtype":"L1_L2","placeholder":"V at L1+L2","low_threshold":100}}]'
            WHERE complaint_type = 'not_turning_on' AND step_id = 'q2-no-power'
        """))

    # Same fix for not_cooling/q3-contactor options_jsonb (the reading spec lives there)
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET options_jsonb = (
                SELECT jsonb_agg(
                    CASE WHEN (elem->>'kind') = 'reading'
                              AND (elem->'spec'->>'type') = 'voltage'
                         THEN jsonb_set(elem, '{spec,low_threshold}', '100'::jsonb)
                         ELSE elem
                    END
                )
                FROM jsonb_array_elements(options_jsonb) AS elem
            )
            WHERE complaint_type = 'not_cooling' AND step_id = 'q3-contactor'
              AND jsonb_typeof(options_jsonb) = 'array'
        """))

    # ── Untested #2: making_noise/q4-compressor — remove escalate from over_rla
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{over_rla}',
                '{"resolve_card": 10, "photo_slots": [{"slot": "compressor_exterior", "photo_type": "evidence", "instruction": "Compressor exterior — for homeowner PDF.", "ai_prompt": null}]}'::jsonb
            )
            WHERE complaint_type = 'making_noise' AND step_id = 'q4-compressor'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{"over_rla": {"resolve_card": 10, "photo_slots": [{"slot": "compressor_exterior", "photo_type": "evidence", "instruction": "Compressor exterior — for homeowner PDF.", "ai_prompt": null}]}}'
            )
            WHERE complaint_type = 'making_noise' AND step_id = 'q4-compressor'
        """))

    # ── Untested #3: making_noise/q1 hissing — replace phase_2_gate ───────────
    # Insert q2-hiss-suction step
    if pg:
        bind.execute(text(f"""
            INSERT INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('making_noise', 'q2-hiss-suction', 10,
               'Read suction line pressure (low-side manifold gauge).',
               'Hissing often indicates refrigerant leak or TXV chatter. R-410A normal suction: 60-110 PSI.',
               'reading',
               NULL,
               '{_HISS_SUCTION_READING_SPEC}'::jsonb,
               NULL,
               '{_HISS_SUCTION_BRANCH_LOGIC}'::jsonb,
               NULL,
               FALSE)
            ON CONFLICT (complaint_type, step_id) DO NOTHING
        """))

        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{hissing}',
                '{"next_step_id": "q2-hiss-suction"}'::jsonb
            )
            WHERE complaint_type = 'making_noise' AND step_id = 'q1'
        """))
    else:
        bind.execute(text(f"""
            INSERT OR IGNORE INTO diagnostic_questions
              (complaint_type, step_id, step_order, question_text, hint_text,
               input_type, options_jsonb, reading_spec, photo_spec,
               branch_logic_jsonb, data_collect_jsonb, is_terminal)
            VALUES
              ('making_noise', 'q2-hiss-suction', 10,
               'Read suction line pressure (low-side manifold gauge).',
               'Hissing often indicates refrigerant leak or TXV chatter. R-410A normal suction: 60-110 PSI.',
               'reading',
               NULL,
               '{_HISS_SUCTION_READING_SPEC}',
               NULL,
               '{_HISS_SUCTION_BRANCH_LOGIC}',
               NULL,
               0)
        """))

        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json_patch(
                branch_logic_jsonb,
                '{"hissing": {"next_step_id": "q2-hiss-suction"}}'
            )
            WHERE complaint_type = 'making_noise' AND step_id = 'q1'
        """))


def downgrade() -> None:
    bind = op.get_bind()
    pg = _is_postgres()

    # Reverse BUG #9 — restore escalation dead-end (wsg3 state)
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = '{
              "yes": {"resolve_card": 7, "note": "Nuisance trip resolved by reset"},
              "no":  {"escalate": true, "reason": "Lockout returns after reset — possible intermittent_shutdown; re-diagnose under Tab H"}
            }'::jsonb
            WHERE complaint_type = 'error_code' AND step_id = 'q4-reset'
        """))
    else:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = json('{"yes":{"resolve_card":7},"no":{"escalate":true,"reason":"Lockout returns after reset"}}')
            WHERE complaint_type = 'error_code' AND step_id = 'q4-reset'
        """))

    # Reverse BUG #11 — remove low_threshold from reading_spec
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = reading_spec - 'low_threshold'
            WHERE complaint_type = 'not_cooling' AND step_id = 'q3-contactor'
        """))

    # Reverse BUG #12 — restore phase_2_gate, delete suction step
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{outdoor_refrigerant}',
                '{"phase_2_gate": true, "after": {"low_suction_high_superheat": {"resolve_card": 8, "photo_slots": [{"slot": "uv_dye_glow", "photo_type": "evidence", "instruction": "UV dye glow under blacklight.", "ai_prompt": null}]}}}'::jsonb
            )
            WHERE complaint_type = 'water_dripping' AND step_id = 'q1'
        """))
        bind.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'water_dripping' AND step_id = 'q2-wd-suction'
        """))
    else:
        bind.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'water_dripping' AND step_id = 'q2-wd-suction'
        """))

    # Reverse BUG #13 — restore "micro_amps" type, remove added keys
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET reading_spec = jsonb_set(reading_spec, '{type}', '"micro_amps"'::jsonb)
            WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'
        """))
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = branch_logic_jsonb - 'low' - 'ok'
            WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor'
        """))

    # Reverse Untested #2 — restore escalate:true in over_rla
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{over_rla}',
                '{"resolve_card": 10, "escalate": true, "reason": "Compressor over-amping - tech judgment"}'::jsonb
            )
            WHERE complaint_type = 'making_noise' AND step_id = 'q4-compressor'
        """))

    # Reverse Untested #3 — restore phase_2_gate, delete suction step
    if pg:
        bind.execute(text("""
            UPDATE diagnostic_questions
            SET branch_logic_jsonb = jsonb_set(
                branch_logic_jsonb,
                '{hissing}',
                '{"phase_2_gate": true, "after": {"low_suction_high_superheat": {"resolve_card": 8}}}'::jsonb
            )
            WHERE complaint_type = 'making_noise' AND step_id = 'q1'
        """))
        bind.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'making_noise' AND step_id = 'q2-hiss-suction'
        """))
    else:
        bind.execute(text("""
            DELETE FROM diagnostic_questions
            WHERE complaint_type = 'making_noise' AND step_id = 'q2-hiss-suction'
        """))
