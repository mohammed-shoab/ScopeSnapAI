-- Migration 012: Add skip branches to photo steps that need rerouting
-- Applied: 2026-05-09

-- H-YES thermal camera: "skip" → route to Path B (q3-visual-photo)
UPDATE diagnostic_questions
SET branch_logic_jsonb = branch_logic_jsonb || '{"skip": {"next_step_id": "q3-visual-photo"}}'::jsonb
WHERE complaint_type = 'intermittent_shutdown'
  AND step_id = 'q2-thermal-photo';

-- Error code q1: "skipped" → route to reset step (nuisance fallback)
UPDATE diagnostic_questions
SET branch_logic_jsonb = branch_logic_jsonb || '{"skipped": {"next_step_id": "q4-reset"}}'::jsonb
WHERE complaint_type = 'error_code'
  AND step_id = 'q1';

-- Verify
SELECT complaint_type, step_id, branch_logic_jsonb->'skip' AS skip_branch, branch_logic_jsonb->'skipped' AS skipped_branch
FROM diagnostic_questions
WHERE (complaint_type = 'intermittent_shutdown' AND step_id = 'q2-thermal-photo')
   OR (complaint_type = 'error_code' AND step_id = 'q1');
