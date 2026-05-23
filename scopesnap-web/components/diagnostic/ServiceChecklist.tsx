"use client";

import { useState, useEffect, useCallback } from "react";
import { API_URL } from "@/lib/api";
import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";
import ReadingInput, { ReadingSpec, ReadingResult } from "./ReadingInput";
import VisualSelect from "./VisualSelect";
import MultiInput, { MultiInputItem } from "./MultiInput";
import YesNoButtons from "./YesNoButtons";

// ── Service photo skip configuration ──────────────────────────────────────────

type SvcSkipType = "simple" | "choice";

interface SvcSkipConfig {
  type: SvcSkipType;
  choices?: { label: string; branch_key: string }[];
}

const SVC_PHOTO_SKIP_CONFIG: Record<string, SvcSkipConfig> = {
  // S Step 1: filter face photo
  "svc-1-filter": {
    type: "choice",
    choices: [
      { label: "Dirty – Replace",   branch_key: "replace" },
      { label: "Dirty – Can Clean", branch_key: "dirty" },
      { label: "Looks Clean",           branch_key: "clean" },
    ],
  },
  // S Step 3: condenser coil face photo
  "svc-3-coil": {
    type: "choice",
    choices: [
      { label: "Heavily Blocked", branch_key: "heavily_blocked" },
      { label: "Dirty",           branch_key: "dirty" },
      { label: "Clean",           branch_key: "clean" },
    ],
  },
  // S Step 4: drain flush photo — tech already flushed; just needs to confirm
  "svc-4-drain": {
    type: "choice",
    choices: [
      { label: "Drain Flushed",    branch_key: "flushed" },
      { label: "Could Not Flush",  branch_key: "skipped" },
    ],
  },
  // S Step 8: run photo — any wildcard → service_complete
  "svc-8-run": { type: "simple" },
};

// ── Types ──────────────────────────────────────────────────────────────────

interface QuestionOut {
  step_id: string;
  question_text: string;
  hint_text?: string | null;
  input_type: string;
  options?: { value: string; label: string; icon?: string }[] | null;
  reading_spec?: ReadingSpec | null;
  photo_spec?: PhotoSlotSpec | null;
  is_terminal?: boolean;
}

interface ServiceFinding {
  step_id: string;
  description: string;
  amount_min?: number;
  amount_max?: number;
  code?: string;
  is_flag?: boolean;
}

export interface ServiceEstimateResult {
  session_id: string;
  base_items: { code: string; description: string; amount_min: number; amount_max: number; amount_typical: number }[];
  add_ons: { code: string; description: string; amount_min: number; amount_max: number; amount_typical: number }[];
  flags: { code: string; description: string; is_flag: boolean }[];
  total_min: number;
  total_max: number;
  total_typical: number;
  markup_pct: number;
  findings_count: number;
}

interface ServiceChecklistProps {
  assessmentId: string;
  getAuthHeaders: () => Promise<Record<string, string>>;
  ocrNameplate?: Record<string, unknown> | null;
  onComplete: (result: ServiceEstimateResult, sessionId: string) => void;
  onCancel: () => void;
}

const TOTAL_STEPS = 8;

const STEP_LABELS: Record<string, string> = {
  "svc-1-filter":    "Filter inspection",
  "svc-2-cap":       "Capacitor check",
  "svc-3-coil":      "Coil inspection",
  "svc-4-drain":     "Drain flush",
  "svc-5-terminals": "Electrical check",
  "svc-6-amps":      "Amp draw check",
  "svc-7-deltaT":    "Delta-T check",
  "svc-8-run":       "System run test",
};

// ── Component ──────────────────────────────────────────────────────────────

export default function ServiceChecklist({
  assessmentId,
  getAuthHeaders,
  ocrNameplate,
  onComplete,
  onCancel,
}: ServiceChecklistProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionOut | null>(null);
  const [stepNumber, setStepNumber] = useState(1);
  const [findings, setFindings] = useState<ServiceFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [generatingEstimate, setGeneratingEstimate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // skip UI state — reset on each new step
  const [skipExpanded, setSkipExpanded] = useState(false);
  const [manualCode, setManualCode] = useState("");
  const [liveHeaders, setLiveHeaders] = useState<Record<string, string>>({});

  // ── Start session ──────────────────────────────────────────────────────

  useEffect(() => {
    const start = async () => {
      setLoading(true);
      setError(null);
      try {
        const headers = await getAuthHeaders();
        setLiveHeaders(headers);
        const r = await fetch(`${API_URL}/api/diagnostic/session`, {
          method: "POST",
          headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify({ assessment_id: assessmentId, complaint_type: "service" }),
        });
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.detail || "Failed to start service session");
        }
        const data = await r.json();
        setSessionId(data.session_id);
        setCurrentQuestion(data.current_step);
        setStepNumber(1);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to start session");
      } finally {
        setLoading(false);
      }
    };
    start();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId]);

  // Reset skip state on each new step
  useEffect(() => {
    setSkipExpanded(false);
    setManualCode("");
  }, [currentQuestion?.step_id]);

  // ── Submit step answer ─────────────────────────────────────────────────

  const submitStep = useCallback(async (answer: unknown) => {
    if (!sessionId || !currentQuestion) return;
    setSubmitting(true);
    setError(null);
    try {
      const headers = await getAuthHeaders();
      setLiveHeaders(headers);
      const r = await fetch(`${API_URL}/api/diagnostic/session/${sessionId}/answer`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to submit step");
      }
      const resp = await r.json();

      // Accumulate finding if present
      if (resp.finding) {
        const li = resp.finding.line_item || {};
        const code = resp.finding.line_item_code || li.code || "";
        const isFlagCode = code.startsWith("flag_");
        setFindings(prev => [...prev, {
          step_id: currentQuestion.step_id,
          description: isFlagCode
            ? resp.finding.note || code
            : li.description || describeLineItem(code, li),
          amount_min: isFlagCode ? 0 : (li.amount_min || 0),
          amount_max: isFlagCode ? 0 : (li.amount_max || 0),
          code,
          is_flag: isFlagCode,
        }]);
      }

      if (resp.service_step_complete) {
        // Terminal step — backend auto-generates estimate; navigate directly.
        // BUG-036 fix: POST /api/estimates/service does not exist; handleServiceComplete
        // ignores the result and redirects to /assessment/{id}, so call onComplete directly.
        setGeneratingEstimate(true);
        onComplete(
          {
            session_id: sessionId,
            base_items: findings.filter(f => !f.is_flag).map(f => ({
              code: f.code || "",
              description: f.description,
              amount_min: f.amount_min || 0,
              amount_max: f.amount_max || 0,
              amount_typical: Math.round(((f.amount_min || 0) + (f.amount_max || 0)) / 2),
            })),
            add_ons: [],
            flags: findings.filter(f => f.is_flag).map(f => ({
              code: f.code || "",
              description: f.description,
              is_flag: true,
            })),
            total_min: findings.filter(f => !f.is_flag).reduce((s, f) => s + (f.amount_min || 0), 0),
            total_max: findings.filter(f => !f.is_flag).reduce((s, f) => s + (f.amount_max || 0), 0),
            total_typical: Math.round(
              findings.filter(f => !f.is_flag).reduce((s, f) => s + ((f.amount_min || 0) + (f.amount_max || 0)) / 2, 0)
            ),
            markup_pct: 35,
            findings_count: findings.length,
          },
          sessionId
        );
        return;
      }

      if (resp.next_step) {
        setCurrentQuestion(resp.next_step);
        setStepNumber(n => n + 1);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, currentQuestion, getAuthHeaders]);

  // ── Answer handlers ────────────────────────────────────────────────────

  const handleYesNo = (v: "yes" | "no") => submitStep(v);
  const handleVisualSelect = (v: string) => submitStep(v);
  const handleReading = (result: ReadingResult) =>
    submitStep({ value: result.value, unit: result.unit, branch_key: result.branchKey });
  const handlePhoto = (r: PhotoResult) =>
    submitStep({ photo_url: r.photo_url, slot_name: r.slot_name });
  const handleMulti = (data: { photos: PhotoResult[]; readings: ReadingResult[] }) => {
    const answer: Record<string, unknown> = {};
    data.photos.forEach(p => { answer[p.slot_name] = { photo_url: p.photo_url, photo_type: p.photo_type }; });
    data.readings.forEach((r, i) => { answer[`reading_${i}`] = { value: r.value, unit: r.unit, branch_key: r.branchKey }; });
    submitStep(answer);
  };

  // ── Render ─────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
        <p className="text-sm" style={{ color: "#7a8299" }}>Starting service checklist...</p>
      </div>
    );
  }

  if (generatingEstimate) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <div className="text-4xl">&#x2705;</div>
        <h2 className="text-xl font-extrabold text-white">Service Complete</h2>
        <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin mt-2" />
        <p className="text-sm" style={{ color: "#7a8299" }}>Building your service estimate...</p>
        {findings.filter(f => !f.is_flag).length > 0 && (
          <p className="text-xs font-medium mt-1" style={{ color: "#1abc9c" }}>
            {findings.filter(f => !f.is_flag).length} finding{findings.filter(f => !f.is_flag).length !== 1 ? "s" : ""} found
          </p>
        )}
      </div>
    );
  }

  if (error && !currentQuestion) {
    return (
      <div className="flex flex-col gap-4 py-8">
        <div className="rounded-xl p-4" style={{ background: "rgba(231,76,60,0.12)", border: "1px solid #e74c3c" }}>
          <p className="text-sm font-bold text-center" style={{ color: "#e74c3c" }}>{error}</p>
        </div>
        <button onClick={onCancel} className="w-full py-3 rounded-2xl font-semibold text-sm"
          style={{ background: "#16213e", color: "#f0f0f0" }}>
          Back to Complaint Selection
        </button>
      </div>
    );
  }

  if (!currentQuestion) return null;

  const multiItems: MultiInputItem[] = currentQuestion.input_type === "multi" && currentQuestion.options
    ? (currentQuestion.options as unknown as MultiInputItem[])
    : [];

  const dollarFindings = findings.filter(f => !f.is_flag && (f.amount_max || 0) > 0);
  const flagFindings = findings.filter(f => f.is_flag);

  return (
    <div className="flex flex-col gap-5 w-full">

      {/* Header: Step progress */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-widest" style={{ color: "#1abc9c" }}>
            Regular Service
          </span>
          <span className="text-xs font-semibold" style={{ color: "#7a8299" }}>
            Step {stepNumber} of {TOTAL_STEPS}
          </span>
        </div>
        <div className="flex gap-1">
          {Array.from({ length: TOTAL_STEPS }, (_, i) => (
            <div
              key={i}
              className="h-1.5 rounded-full flex-1 transition-all duration-300"
              style={{ background: i < stepNumber ? "#1abc9c" : "#1a2a20" }}
            />
          ))}
        </div>
        <p className="text-xs" style={{ color: "#4a8a6a" }}>
          {STEP_LABELS[currentQuestion.step_id] || currentQuestion.step_id}
        </p>
      </div>

      {/* Running findings */}
      {findings.length > 0 && (
        <div className="rounded-xl p-3 flex flex-col gap-1.5"
          style={{ background: "#071a14", border: "1px solid #1a3a30" }}>
          <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: "#2a6a5a" }}>
            Findings so far
          </p>
          {dollarFindings.map((f, i) => (
            <div key={i} className="flex items-center justify-between gap-2">
              <span className="text-xs" style={{ color: "#a8f5e8" }}>{f.description}</span>
              <span className="text-xs font-semibold font-mono" style={{ color: "#1abc9c" }}>
                ${f.amount_min}–${f.amount_max}
              </span>
            </div>
          ))}
          {flagFindings.map((f, i) => (
            <div key={i} className="flex items-center gap-1.5">
              <span className="text-xs" style={{ color: "#e67e22" }}>&#x26A0;</span>
              <span className="text-xs" style={{ color: "#e67e22" }}>{f.description}</span>
            </div>
          ))}
        </div>
      )}

      {/* Current step question */}
      <div className="flex flex-col gap-1.5">
        <h2 className="text-xl font-extrabold text-white leading-snug">{currentQuestion.question_text}</h2>
        {currentQuestion.hint_text && (
          <p className="text-sm" style={{ color: "#7a8299" }}>{currentQuestion.hint_text}</p>
        )}
      </div>

      {error && (
        <div className="rounded-xl px-4 py-2.5" style={{ background: "rgba(231,76,60,0.12)" }}>
          <p className="text-xs font-medium" style={{ color: "#e74c3c" }}>{error}</p>
        </div>
      )}

      {/* Input widget */}
      <div className="flex flex-col gap-4">
        {currentQuestion.input_type === "yesno" && (
          <YesNoButtons onAnswer={handleYesNo} disabled={submitting} />
        )}
        {currentQuestion.input_type === "visual_select" && currentQuestion.options && (
          <VisualSelect options={currentQuestion.options} onAnswer={handleVisualSelect} disabled={submitting} />
        )}
        {currentQuestion.input_type === "reading" && currentQuestion.reading_spec && (
          <ReadingInput spec={currentQuestion.reading_spec} ocrNameplate={ocrNameplate}
            onSubmit={handleReading} disabled={submitting} />
        )}
        {currentQuestion.input_type === "photo" && currentQuestion.photo_spec && (() => {
          const spec = currentQuestion.photo_spec!;
          const skipConfig = SVC_PHOTO_SKIP_CONFIG[currentQuestion.step_id];
          return (
            <>
              <PhotoSlot spec={spec} assessmentId={assessmentId}
                authHeaders={liveHeaders} onCapture={handlePhoto} disabled={submitting} />

              { /* ── Photo skip UI ── */}
              {skipConfig && (
                <div className="flex flex-col gap-2">

                  {/* simple: single skip link */}
                  {skipConfig.type === "simple" && (
                    <button
                      onClick={() => submitStep({ slot_name: spec.slot_name, branch_key: "skipped" })}
                      disabled={submitting}
                      className="text-xs font-medium text-center py-1.5"
                      style={{ color: "#4a5568" }}>
                      Can&apos;t access right now?
                    </button>
                  )}

                  {/* choice: collapse → expand with labeled buttons */}
                  {skipConfig.type === "choice" && (
                    skipExpanded ? (
                      <div className="rounded-xl p-3 flex flex-col gap-2" style={{ background: "#0d1117", border: "1px solid #2a3050" }}>
                        <p className="text-xs font-semibold" style={{ color: "#a0a8c0" }}>Select condition (skip photo):</p>
                        <div className="flex flex-wrap gap-2">
                          {skipConfig.choices!.map(c => (
                            <button key={c.branch_key}
                              onClick={() => submitStep({ slot_name: spec.slot_name, branch_key: c.branch_key })}
                              disabled={submitting}
                              className="px-4 py-2 rounded-xl font-semibold text-sm"
                              style={{ background: "#16213e", color: "#f0f0f0", border: "1.5px solid #2a3a5a" }}>
                              {c.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <button onClick={() => setSkipExpanded(true)} disabled={submitting}
                        className="text-xs font-medium text-center py-1.5" style={{ color: "#4a5568" }}>
                        Skip photo — select condition manually →
                      </button>
                    )
                  )}

                </div>
              )}
            </>
          );
        })()}
        {currentQuestion.input_type === "multi" && multiItems.length > 0 && (
          <MultiInput inputs={multiItems} assessmentId={assessmentId}
            authHeaders={liveHeaders} ocrNameplate={ocrNameplate}
            onSubmit={handleMulti} disabled={submitting} />
        )}
      </div>

      {submitting && (
        <div className="flex items-center justify-center gap-2 py-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <span className="text-sm" style={{ color: "#7a8299" }}>Saving step...</span>
        </div>
      )}

      <button onClick={onCancel} className="text-xs font-medium text-center py-2 mt-2"
        style={{ color: "#4a5568" }}>
        Back to complaint selection
      </button>
    </div>
  );
}

// ── Helpers ────────────────────────────────────────────────────────────────

function describeLineItem(code: string, li: Record<string, unknown>): string {
  const map: Record<string, string> = {
    filter_replacement: "Filter replacement",
    coil_cleaning:      "Condenser coil cleaning",
    flush_tablet:       "Drain flush tablet",
    card_1_addon:       "Capacitor — preventive replacement",
    card_16_addon:      "Loose terminal — repair",
  };
  return (li.description as string) || map[code] || code;
}
