-- ============================================================================
-- Phase 3 — Diagnostic Engine — Migration 011
-- ============================================================================

-- 1. diagnostic_questions: the question library (seeded once, edited via SQL)
CREATE TABLE diagnostic_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  complaint_type VARCHAR(50) NOT NULL,
  step_id VARCHAR(40) NOT NULL,
  step_order INTEGER NOT NULL,
  question_text TEXT NOT NULL,
  hint_text TEXT,
  input_type VARCHAR(20) NOT NULL,
  options_jsonb JSONB,
  reading_spec JSONB,
  photo_spec JSONB,
  branch_logic_jsonb JSONB NOT NULL,
  data_collect_jsonb JSONB,
  is_terminal BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(complaint_type, step_id)
);

CREATE INDEX ix_dq_complaint_step  ON diagnostic_questions(complaint_type, step_id);
CREATE INDEX ix_dq_complaint_order ON diagnostic_questions(complaint_type, step_order);

-- 2. diagnostic_sessions: per-assessment live state
CREATE TABLE diagnostic_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES companies(id),
  technician_id UUID REFERENCES users(id),
  complaint_type VARCHAR(50) NOT NULL,
  current_step_id VARCHAR(40) NOT NULL,
  answers_jsonb JSONB DEFAULT '{}'::jsonb,
  resolved_card_id INTEGER REFERENCES fault_cards(card_id),
  resolved_at TIMESTAMPTZ,
  resolution_path JSONB DEFAULT '[]'::jsonb,
  service_findings JSONB DEFAULT '[]'::jsonb,
  status VARCHAR(20) DEFAULT 'active',
  phase_used VARCHAR(10),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_ds_assessment ON diagnostic_sessions(assessment_id);
CREATE INDEX ix_ds_company    ON diagnostic_sessions(company_id);
CREATE INDEX ix_ds_status     ON diagnostic_sessions(status);

ALTER TABLE diagnostic_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY company_isolation_ds ON diagnostic_sessions
  FOR ALL USING (
    company_id = (current_setting('request.jwt.claims', true)::jsonb->>'company_id')::uuid
  );

-- 3. reading_inputs: every numeric reading the tech enters during diagnostic
CREATE TABLE reading_inputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES diagnostic_sessions(id) ON DELETE CASCADE,
  assessment_id UUID NOT NULL REFERENCES assessments(id),
  step_id VARCHAR(40) NOT NULL,
  reading_type VARCHAR(30) NOT NULL,
  reading_subtype VARCHAR(30),
  actual_value NUMERIC(10,3) NOT NULL,
  unit VARCHAR(10) NOT NULL,
  nameplate_spec NUMERIC(10,3),
  spec_source VARCHAR(20),
  tolerance_pct INTEGER DEFAULT 10,
  classification VARCHAR(20),
  passed BOOLEAN,
  flag_message TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_ri_session    ON reading_inputs(session_id);
CREATE INDEX ix_ri_assessment ON reading_inputs(assessment_id);

ALTER TABLE reading_inputs ENABLE ROW LEVEL SECURITY;
CREATE POLICY ri_via_session ON reading_inputs
  FOR ALL USING (
    session_id IN (
      SELECT id FROM diagnostic_sessions
      WHERE company_id = (current_setting('request.jwt.claims', true)::jsonb->>'company_id')::uuid
    )
  );

-- 4. photo_labels: every photo the tech uploads during Phase 3, with its label
CREATE TABLE photo_labels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  session_id UUID REFERENCES diagnostic_sessions(id),
  step_id VARCHAR(40),
  photo_url TEXT NOT NULL,
  photo_type VARCHAR(15) NOT NULL,
  slot_name VARCHAR(50),
  card_id INTEGER REFERENCES fault_cards(card_id),
  ai_prompt_used TEXT,
  ai_grade VARCHAR(20),
  ai_confidence NUMERIC(4,2),
  is_for_pdf BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_pl_assessment ON photo_labels(assessment_id);
CREATE INDEX ix_pl_session    ON photo_labels(session_id);

ALTER TABLE photo_labels ENABLE ROW LEVEL SECURITY;
CREATE POLICY pl_via_assessment ON photo_labels
  FOR ALL USING (
    assessment_id IN (
      SELECT id FROM assessments
      WHERE company_id = (current_setting('request.jwt.claims', true)::jsonb->>'company_id')::uuid
    )
  );

-- 5. job_confirmations: post-job training feedback (1-to-1 with assessment)
CREATE TABLE job_confirmations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL UNIQUE REFERENCES assessments(id) ON DELETE CASCADE,
  session_id UUID REFERENCES diagnostic_sessions(id),
  company_id UUID NOT NULL REFERENCES companies(id),
  technician_id UUID REFERENCES users(id),
  diagnosed_card_id INTEGER REFERENCES fault_cards(card_id),
  actual_card_id INTEGER REFERENCES fault_cards(card_id),
  diagnosis_correct BOOLEAN,
  complaint_resolved BOOLEAN NOT NULL,
  final_invoice_amount NUMERIC(10,2),
  tech_notes TEXT,
  consent_given BOOLEAN DEFAULT TRUE,
  confirmed_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_jc_company ON job_confirmations(company_id);

ALTER TABLE job_confirmations ENABLE ROW LEVEL SECURITY;
CREATE POLICY jc_company_isolation ON job_confirmations
  FOR ALL USING (
    company_id = (current_setting('request.jwt.claims', true)::jsonb->>'company_id')::uuid
  );
