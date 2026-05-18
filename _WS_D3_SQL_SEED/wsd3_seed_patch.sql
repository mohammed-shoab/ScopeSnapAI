-- ============================================================================
-- WS-D3/E3/F3 Seed Patch — fix branch key mismatches discovered during E2E testing
-- Run in Supabase SQL editor (Monaco) — safe to re-run (idempotent UPDATEs)
-- 2026-05-04
-- ============================================================================

-- ── Fix 1: not_cooling / q3-contactor ────────────────────────────────────────
-- Bug: engine returns "power_passes_normal" for ~230V at L1+L2.
--      Seed used "power_doesnt_pass" (never produced by engine → always escalated).
-- Fix: "power_passes_normal" = power reaches contactor but unit won't run = Card #3.
--      Add "no_power" + "phase_loss" as explicit escalation paths.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "power_passes_normal": {
    "resolve_card": 3,
    "photo_slots": []
  },
  "no_power": {
    "escalate": true,
    "reason": "No power at L1+L2 — check breaker / disconnect"
  },
  "phase_loss": {
    "escalate": true,
    "reason": "Phase loss at L1+L2 — check incoming power supply"
  }
}'::jsonb
WHERE complaint_type = 'not_cooling' AND step_id = 'q3-contactor';

-- ── Fix 2: not_turning_on / q2-no-power ──────────────────────────────────────
-- Bug: "power_reaches_doesnt_pass" and "no_power_at_all" never produced by engine.
-- Fix: align with engine keys.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "power_passes_normal": {
    "resolve_card": 3,
    "photo_slots": []
  },
  "no_power": {
    "escalate": true,
    "reason": "No power at L1+L2 — check breaker / disconnect"
  },
  "phase_loss": {
    "escalate": true,
    "reason": "Phase loss detected — check incoming power"
  }
}'::jsonb
WHERE complaint_type = 'not_turning_on' AND step_id = 'q2-no-power';

-- ── Fix 3: water_dripping / q3-freeze-check ───────────────────────────────────
-- Bug: seed uses "delta_T_low" (camelCase T) but engine returns "delta_t_low".
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "delta_t_low": {
    "resolve_card": 9,
    "photo_slots": []
  },
  "delta_t_ok": {
    "escalate": true,
    "reason": "Pan dry, exit flowing, delta-T ok — water source not identified, manual diagnosis"
  },
  "delta_t_high": {
    "escalate": true,
    "reason": "High delta-T — over-cooling, possible low airflow, investigate"
  }
}'::jsonb
WHERE complaint_type = 'water_dripping' AND step_id = 'q3-freeze-check';

-- ── Fix 4: water_dripping / q2-pan-photo — add photo_branch_map ──────────────
-- For photo-only multi steps, backend uses photo_branch_map to derive compound
-- branch key from individual AI grades.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "photo_branch_map": {
    "standing_water": "pan_water_present_or_exit_blocked",
    "overflowing":    "pan_water_present_or_exit_blocked",
    "blocked":        "pan_water_present_or_exit_blocked",
    "_default":       "pan_dry_and_exit_flowing"
  },
  "pan_water_present_or_exit_blocked": {
    "resolve_card": 5,
    "photo_slots": []
  },
  "pan_dry_and_exit_flowing": {
    "next_step_id": "q3-freeze-check"
  }
}'::jsonb
WHERE complaint_type = 'water_dripping' AND step_id = 'q2-pan-photo';

-- ── Fix 5: high_electric_bill / q3-coil-photo — add photo_branch_map ─────────
-- Multi with coil photo + discharge PSI + delta_T readings.
-- If coil is dirty/heavily_blocked OR discharge PSI high → Card #14.
-- Engine may return "ok" for discharge PSI at normal conditions — photo grade
-- is the tiebreaker. Add photo_branch_map so backend grades the coil photo.
UPDATE diagnostic_questions
SET branch_logic_jsonb = '{
  "photo_branch_map": {
    "dirty":            "coil_dirty_or_high_discharge",
    "heavily_blocked":  "coil_dirty_or_high_discharge",
    "_default":         "all_clean"
  },
  "coil_dirty_or_high_discharge": {
    "resolve_card": 14
  },
  "all_clean": {
    "escalate": true,
    "reason": "Coil clean, normal pressure — Tech Judgment (possible undersizing / duct issue)"
  }
}'::jsonb
WHERE complaint_type = 'high_electric_bill' AND step_id = 'q3-coil-photo';

-- ── Verify ────────────────────────────────────────────────────────────────────
SELECT complaint_type, step_id,
       branch_logic_jsonb->>'photo_branch_map' IS NOT NULL AS has_photo_map,
       branch_logic_jsonb
FROM diagnostic_questions
WHERE step_id IN ('q3-contactor','q2-no-power','q3-freeze-check','q2-pan-photo','q3-coil-photo')
ORDER BY complaint_type, step_id;
