-- ============================================================================
-- Patch: svc-4-drain visual_select option values
-- ============================================================================
-- BUG-006 root cause (data side):
--   The svc-4-drain multi step had options: [{value:"yes"},{value:"no"}]
--   but branch_logic_jsonb had keys "flushed" and "skipped".
--   The frontend sends the option value as the branch_key, so "yes"/"no"
--   never matched "flushed"/"skipped" → unhandled_answer escalation.
--
-- Fix: align option values with branch_logic keys.
-- ============================================================================

UPDATE diagnostic_questions
SET options_jsonb = '[
  {
    "kind": "visual_select",
    "spec": {
      "question_text": "Drain flushed?",
      "options": [
        {"value": "flushed", "label": "YES — Flushed"},
        {"value": "skipped", "label": "Skipped"}
      ]
    }
  },
  {
    "kind": "photo",
    "spec": {
      "slot_name": "drain_pan_after",
      "photo_type": "evidence",
      "instruction": "Drain pan after flush - for homeowner PDF.",
      "ai_prompt": null
    }
  }
]'::jsonb
WHERE complaint_type = 'service'
  AND step_id = 'svc-4-drain';

-- Verify
SELECT step_id, options_jsonb
FROM diagnostic_questions
WHERE complaint_type = 'service' AND step_id = 'svc-4-drain';
