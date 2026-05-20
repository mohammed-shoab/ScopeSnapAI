-- ============================================================================
-- WS-G3/H3/I3/J3/K3 Seed Patch — fix branch key mismatches for 5 new tabs
-- Run in Supabase SQL editor — safe to re-run (idempotent UPDATEs)
-- 2026-05-05
-- ============================================================================

-- ── Fix 1 (WS-H3): making_noise/q5-contactor ─────────────────────────────────
-- Bug: AI returns "pitted"/"arced"/"welded" but branch_logic keys are
--      "pitted_or_arced" (compound). Add photo_branch_map to collapse grades.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "photo_branch_map": {
    "pitted":   "pitted_or_arced",
    "arced":    "pitted_or_arced",
    "welded":   "pitted_or_arced",
    "clean":    "clean",
    "_default": "clean"
  },
  "pitted_or_arced": {
    "resolve_card": 3
  },
  "clean": {
    "escalate": true,
    "reason": "Contactor visually clean — investigate noise source"
  }
}'::jsonb
WHERE complaint_type = 'making_noise' AND step_id = 'q5-contactor';

-- ── Fix 2 (WS-I3): not_heating/q3-ignitor ────────────────────────────────────
-- Bug: engine returns "open"/"out_of_spec" for ohms; AI returns
--      "intact"/"hairline_crack"/"broken". Branch keys "cracked_or_open_ohms"
--      and "intact_and_normal" are never directly produced.
-- Fix: add reading keys + photo_branch_map.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "photo_branch_map": {
    "hairline_crack": "cracked_or_open_ohms",
    "broken":         "cracked_or_open_ohms",
    "intact":         "intact_and_normal",
    "_default":       "intact_and_normal"
  },
  "open":          { "resolve_card": 11 },
  "out_of_spec":   { "resolve_card": 11 },
  "no_voltage":    { "escalate": true, "reason": "No voltage at ignitor — check control board / transformer" },
  "cracked_or_open_ohms": { "resolve_card": 11 },
  "intact_and_normal":    { "escalate": true, "reason": "Ignitor good — investigate gas valve / control board" }
}'::jsonb
WHERE complaint_type = 'not_heating' AND step_id = 'q3-ignitor';

-- ── Fix 3 (WS-I3): not_heating/q4-flame-sensor ───────────────────────────────
-- Bug: engine returns "replace"/"marginal" for micro_amps; AI returns
--      "clean"/"light_oxide"/"heavy_oxide". Compound keys never produced.
-- Fix: add micro_amps reading keys + photo_branch_map.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "photo_branch_map": {
    "heavy_oxide":  "heavy_oxide_or_low_uA",
    "light_oxide":  "light_oxide_marginal_uA",
    "clean":        "clean_and_high_uA",
    "_default":     "light_oxide_marginal_uA"
  },
  "replace":  { "resolve_card": 11, "note": "uA below 1 — replace flame sensor" },
  "marginal":  { "escalate": true, "reason": "Clean flame sensor rod and retest" },
  "heavy_oxide_or_low_uA":  { "resolve_card": 11 },
  "light_oxide_marginal_uA": { "escalate": true, "reason": "Clean flame sensor rod and retest" },
  "clean_and_high_uA": { "escalate": true, "reason": "Flame sensor good — investigate gas pressure / valve" }
}'::jsonb
WHERE complaint_type = 'not_heating' AND step_id = 'q4-flame-sensor';

-- ── Fix 4 (WS-K3): intermittent_shutdown/q2-thermal-photo ────────────────────
-- Bug: ai_prompt asks for structured JSON output (hotspot_count, max_delta_F)
--      but _grade_single_photo() returns first word of JSON — not a valid grade.
-- Fix: simplify ai_prompt to return one of two known class labels directly.
UPDATE diagnostic_questions
SET photo_spec = '{
  "slot_name": "thermal_terminals",
  "photo_type": "diagnostic",
  "instruction": "Capture thermal image with FLIR or smartphone thermal attachment, then upload here.",
  "ai_prompt": "Analyse this thermal image. Output exactly one word from this list: hotspot_present (if any area is >20°F above ambient background) or no_hotspot (if all temperatures are within 20°F of ambient). Output the single word only — no punctuation, no explanation."
}'::jsonb
WHERE complaint_type = 'intermittent_shutdown' AND step_id = 'q2-thermal-photo';

-- ── Fix 5 (WS-K3): intermittent_shutdown/q4-ir-readings ──────────────────────
-- Bug: reading_spec type "temp_F" with subtype "terminal_n" always returns "ok"
--      from the engine — branch_logic keys max_delta_over_10F/all_within_10F
--      are never produced.
-- Fix: change type to "temp_delta" so the new engine handler evaluates the
--      delta the tech enters (max terminal temp minus ambient).
UPDATE diagnostic_questions
SET reading_spec = '{
  "type": "temp_delta",
  "unit": "F",
  "placeholder": "Enter max terminal temperature delta vs ambient (°F). e.g. if terminal reads 135°F and ambient is 90°F enter 45"
}'::jsonb
WHERE complaint_type = 'intermittent_shutdown' AND step_id = 'q4-ir-readings';

-- ── Fix 6 (WS-K3): intermittent_shutdown/q5-voltage-drop ─────────────────────
-- Bug: engine returns "ok"/"elevated"/"elevated_high"/"fault" but branch_logic
--      only has "fault" and "elevated_or_ok" (a compound key never produced).
-- Fix: expand branch_logic to handle all four engine outputs.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "fault":          { "resolve_card": 16, "note": "Path B confirmed — fault-level voltage drop" },
  "elevated_high":  { "resolve_card": 16, "note": "High voltage drop — loose terminal confirmed" },
  "elevated":       { "escalate": true, "reason": "Marginal voltage drop — Path B caps at 85-90%. Consider FLIR camera ($400 ROI = 5-10x payback on 1 avoided misdiag)." },
  "ok":             { "escalate": true, "reason": "Path B caps at 85-90% catch rate. FLIR One recommended." }
}'::jsonb
WHERE complaint_type = 'intermittent_shutdown' AND step_id = 'q5-voltage-drop';

-- ── Fix 7 (WS-J3): error_code/q4-reset ──────────────────────────────────────
-- Bug: "no" branch uses "jump_to_complaint" which the API does not support
--      (causes unhandled routing → server error).
-- Fix: replace with explicit escalation + note for the tech.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "yes": { "resolve_card": 7, "note": "Nuisance trip resolved by reset" },
  "no":  { "escalate": true, "reason": "Lockout returns after reset — possible intermittent_shutdown; re-diagnose under Tab H" }
}'::jsonb
WHERE complaint_type = 'error_code' AND step_id = 'q4-reset';

-- ── Fix 8 (WS-G3): high_electric_bill/q2-filter-photo ────────────────────────
-- Bug: AI returns "clean"/"dirty"/"replace" but branch_logic key "dirty_or_replace"
--      is a compound never produced directly.
-- Fix: add photo_branch_map to collapse grades.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "photo_branch_map": {
    "dirty":   "dirty_or_replace",
    "replace": "dirty_or_replace",
    "clean":   "clean",
    "_default": "clean"
  },
  "dirty_or_replace": {
    "resolve_card": 2
  },
  "clean": {
    "resolve_card": 18,
    "escalate": true,
    "reason": "Filter clean but running constantly — load calculation / undersizing investigation"
  }
}'::jsonb
WHERE complaint_type = 'high_electric_bill' AND step_id = 'q2-filter-photo';

-- ── Verify all 8 patches applied ─────────────────────────────────────────────
SELECT complaint_type, step_id,
       CASE WHEN branch_logic_jsonb ? 'photo_branch_map' THEN 'has_map' ELSE 'no_map' END AS photo_map,
       CASE WHEN reading_spec->>'type' = 'temp_delta' THEN 'temp_delta' ELSE reading_spec->>'type' END AS reading_type,
       LEFT(branch_logic_jsonb::text, 60) AS branch_preview
FROM diagnostic_questions
WHERE (complaint_type = 'making_noise'           AND step_id = 'q5-contactor')
   OR (complaint_type = 'not_heating'             AND step_id IN ('q3-ignitor','q4-flame-sensor'))
   OR (complaint_type = 'intermittent_shutdown'   AND step_id IN ('q2-thermal-photo','q4-ir-readings','q5-voltage-drop'))
   OR (complaint_type = 'error_code'              AND step_id = 'q4-reset')
   OR (complaint_type = 'high_electric_bill'      AND step_id = 'q2-filter-photo')
ORDER BY complaint_type, step_id;
