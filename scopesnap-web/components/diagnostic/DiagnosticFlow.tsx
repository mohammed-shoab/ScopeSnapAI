"use client";

import { useState, useEffect, useCallback } from "react";
import posthog from "posthog-js";
import { API_URL } from "@/lib/api";
import { detectMarket } from "@/lib/market";
import YesNoButtons from "./YesNoButtons";
import VisualSelect from "./VisualSelect";
import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";
import ReadingInput, { ReadingSpec, ReadingResult } from "./ReadingInput";
import MultiInput, { MultiInputItem, MultiInputData } from "./MultiInput";

// ── Photo skip configuration ───────────────────────────────────────────────

type SkipType = "simple" | "reroute" | "choice" | "code_input" | "water_check";

interface SkipConfig {
  type: SkipType;
  choices?: { label: string; branch_key: string }[];
}

/**
 * Keyed on step_id. Only photo / multi steps that need skip UI are listed.
 * simple    → single "Skip →" link; backend falls to "any" wildcard.
 * reroute   → single button; sends branch_key:"skip" → DB patch routes to Path B.
 * choice    → expands into labeled buttons, each sends a branch_key.
 * code_input→ expands into text field; tech types code, sends branch_key:"skipped".
 * water_check → shown below multi; YES/NO buttons send explicit branch_key.
 */
const PHOTO_SKIP_CONFIG: Record<string, SkipConfig> = {
  // C-YES-ERROR: control board LED photo → any wildcard → resolve_card 7; code stored for record
  "q4-board-photo": { type: "code_input" },
  // D-Grinding: contactor face photo
  "q5-contactor": {
    type: "choice",
    choices: [
      { label: "Pitted / Arced", branch_key: "pitted_or_arced" },
      { label: "Looks Clean", branch_key: "clean" },
    ],
  },
  // E-YES: filter face photo (high_electric_bill)
  "q2-filter-photo": {
    type: "choice",
    choices: [
      { label: "Dirty / Clogged", branch_key: "dirty_or_replace" },
      { label: "Looks Clean", branch_key: "clean" },
    ],
  },
  // F: error code display photo (error_code complaint) — DB patch routes "skipped" → q4-reset
  "q1": { type: "code_input" },
  // H-YES: thermal camera photo — DB patch routes "skip" → q3-visual-photo (Path B)
  "q2-thermal-photo": { type: "reroute" },
  // H-NO: terminal strip visual photo — any wildcard → q4-ir-readings
  "q3-visual-photo": { type: "simple" },
  // S Step 1: filter face photo (service)
  "svc-1-filter": {
    type: "choice",
    choices: [
      { label: "Dirty – Replace", branch_key: "replace" },
      { label: "Dirty – Can Clean", branch_key: "dirty" },
      { label: "Looks Clean", branch_key: "clean" },
    ],
  },
  // S Step 3: condenser coil face photo
  "svc-3-coil": {
    type: "choice",
    choices: [
      { label: "Heavily Blocked", branch_key: "heavily_blocked" },
      { label: "Dirty", branch_key: "dirty" },
      { label: "Clean", branch_key: "clean" },
    ],
  },
  // S Step 8: run photo — any wildcard → service_complete
  "svc-8-run": { type: "simple" },
  // B-Indoor: drain pan multi step (photo-only, no readings)
  "q2-pan-photo": { type: "water_check" },
};

// ── API types ──────────────────────────────────────────────────────────────

interface QuestionOut {
  step_id: string;
  question_text: string;
  hint_text?: string | null;
  input_type: "yesno" | "reading" | "visual_select" | "photo" | "multi";
  options?: { value: string; label: string; icon?: string }[] | null;
  reading_spec?: ReadingSpec | null;
  photo_spec?: PhotoSlotSpec | null;
  is_terminal?: boolean;
}

interface AnswerResponse {
  resolved: boolean;
  card_id?: number | null;
  card_name?: string | null;
  photo_slots?: PhotoSlotSpec[] | null;
  next_step?: QuestionOut | null;
  phase_2_gate?: boolean;
  gate_continuation?: Record<string, unknown> | null;
  escalated?: boolean;
  escalation_reason?: string | null;
  service_step_complete?: boolean;
  finding?: Record<string, unknown> | null;
}

export interface GateContinuation {
  session_id: string;
  card_id: number | null;
  gate_continuation: Record<string, unknown>;
}

export interface AnswerRecord {
  step_id: string;
  question_text: string;
  answer_display: string;
  question_obj: QuestionOut;   // stored so back button can restore
}

// ── Analytics helper — uses posthog-js module singleton (same instance
//    initialised by PostHogProvider.tsx). Gracefully no-ops if not ready.  ──

function trackEvent(name: string, props: Record<string, unknown>) {
  try {
    posthog.capture(name, props);
  } catch { /* never crash on analytics */ }
}

// ── Props ──────────────────────────────────────────────────────────────────

interface DiagnosticFlowProps {
  assessmentId: string;
  complaintType: string;
  getAuthHeaders: () => Promise<Record<string, string>>;
  ocrNameplate?: Record<string, unknown> | null;
  onResolved: (cardId: number, cardName: string, sessionId: string, photoSlots: PhotoSlotSpec[], history: AnswerRecord[]) => void;
  onPhase2Gate: (continuation: GateContinuation) => void;
  onEscalated: (reason: string) => void;
  onCancel: () => void;
}

// ── Component ──────────────────────────────────────────────────────────────

export default function DiagnosticFlow({
  assessmentId,
  complaintType,
  getAuthHeaders,
  ocrNameplate,
  onResolved,
  onPhase2Gate,
  onEscalated,
  onCancel,
}: DiagnosticFlowProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionOut | null>(null);
  const [history, setHistory] = useState<AnswerRecord[]>([]);
  const [totalSteps, setTotalSteps] = useState(0);
  const [sessionStartTime] = useState(Date.now());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [undoing, setUndoing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // live headers — refreshed before every API call so tokens never expire
  const [liveHeaders, setLiveHeaders] = useState<Record<string, string>>({});
  // skip UI state — reset on each new question
  const [skipExpanded, setSkipExpanded] = useState(false);
  const [manualCode, setManualCode] = useState("");

  // ── Start session on mount ─────────────────────────────────────────────

  useEffect(() => {
    const start = async () => {
      setLoading(true);
      setError(null);
      try {
        const h = await getAuthHeaders();
        setLiveHeaders(h);
        const r = await fetch(`${API_URL}/api/diagnostic/session`, {
          method: "POST",
          headers: { ...h, "Content-Type": "application/json" },
          body: JSON.stringify({ assessment_id: assessmentId, complaint_type: complaintType }),
        });
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.detail || "Failed to start diagnostic session");
        }
        const data = await r.json();
        setSessionId(data.session_id);
        setCurrentQuestion(data.current_step);

        // WS-N3: Fetch total step count for progress indicator
        const qr = await fetch(`${API_URL}/api/diagnostic/questions/${complaintType}`, {
          headers: h,
        }).catch(() => null);
        if (qr && qr.ok) {
          const questions = await qr.json();
          setTotalSteps(Array.isArray(questions) ? questions.length : 0);
        }

        trackEvent("diagnostic_session_started", { complaint_type: complaintType });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to start session");
      } finally {
        setLoading(false);
      }
    };
    start();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId, complaintType]);

  // ── Reset skip state on each new question ─────────────────────────────

  useEffect(() => {
    setSkipExpanded(false);
    setManualCode("");
  }, [currentQuestion?.step_id]);

  // ── Submit answer ──────────────────────────────────────────────────────

  const submitAnswer = useCallback(async (answer: unknown, answerDisplay: string) => {
    if (!sessionId || !currentQuestion) return;
    setSubmitting(true);
    setError(null);

    const answerStartTime = Date.now();
    const record: AnswerRecord = {
      step_id: currentQuestion.step_id,
      question_text: currentQuestion.question_text,
      answer_display: answerDisplay,
      question_obj: currentQuestion,
    };
    const updatedHistory = [...history, record];
    setHistory(updatedHistory);

    try {
      const h = await getAuthHeaders();
      setLiveHeaders(h);
      // PK: include refrigerant_type for server-side pressure evaluation
      const isPK = detectMarket() === "PK";
      const isPsiReading =
        isPK &&
        currentQuestion.input_type === "reading" &&
        currentQuestion.reading_spec?.type === "psi";
      // ocrNameplate is the full OcrResult: {outdoor: {...}, indoor: null, ...}
      const outdoorUnit = (ocrNameplate as Record<string, unknown> | null)
        ?.outdoor as Record<string, unknown> | undefined;
      const refrigerantType = isPsiReading
        ? ((outdoorUnit?.refrigerant as string) || "not_sure")
        : undefined;

      const requestBody: Record<string, unknown> = { answer };
      if (refrigerantType) {
        requestBody.refrigerant_type = refrigerantType;
        requestBody.ambient_c = 40; // default mid-summer; future: tech-entered ambient
      }

      const r = await fetch(`${API_URL}/api/diagnostic/session/${sessionId}/answer`, {
        method: "POST",
        headers: { ...h, "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to submit answer");
      }
      const resp: AnswerResponse = await r.json();

      trackEvent("diagnostic_question_answered", {
        complaint_type: complaintType,
        step_id: currentQuestion.step_id,
        answer: answerDisplay,
        time_to_answer_ms: Date.now() - answerStartTime,
      });

      if (resp.phase_2_gate && resp.gate_continuation) {
        trackEvent("diagnostic_phase2_gate", {
          complaint_type: complaintType,
          step_id: currentQuestion.step_id,
        });
        onPhase2Gate({ session_id: sessionId, card_id: resp.card_id ?? null, gate_continuation: resp.gate_continuation });
        return;
      }

      if (resp.escalated) {
        const reason = resp.escalation_reason ?? "tech_judgment";
        trackEvent("diagnostic_escalated", {
          complaint_type: complaintType,
          step_id: currentQuestion.step_id,
          reason,
        });
        onEscalated(reason);
        return;
      }

      if (resp.resolved && resp.card_id) {
        trackEvent("diagnostic_resolved", {
          complaint_type: complaintType,
          card_id: resp.card_id,
          total_questions: updatedHistory.length,
          time_to_resolve_ms: Date.now() - sessionStartTime,
        });
        onResolved(resp.card_id, resp.card_name ?? `Card #${resp.card_id}`, sessionId, resp.photo_slots ?? [], updatedHistory);
        return;
      }

      if (resp.next_step) {
        setCurrentQuestion(resp.next_step);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setHistory(prev => prev.slice(0, -1));
    } finally {
      setSubmitting(false);
    }
  }, [sessionId, currentQuestion, history, getAuthHeaders, complaintType, sessionStartTime, onResolved, onPhase2Gate, onEscalated]);

  // ── WS-N3: Back button (undo last answer) ─────────────────────────────

  const handleUndo = useCallback(async () => {
    if (!sessionId || history.length === 0 || undoing) return;
    setUndoing(true);
    setError(null);
    try {
      const h = await getAuthHeaders();
      setLiveHeaders(h);
      const r = await fetch(`${API_URL}/api/diagnostic/session/${sessionId}/undo`, {
        method: "PATCH",
        headers: { ...h, "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || "Cannot undo");
      }
      const data = await r.json();
      // Restore the question from the undo response
      setCurrentQuestion(data.question);
      // Pop the last history entry (the one we just undid)
      setHistory(prev => prev.slice(0, -1));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Undo failed");
    } finally {
      setUndoing(false);
    }
  }, [sessionId, history, getAuthHeaders, undoing]);

  // ── Answer handlers ────────────────────────────────────────────────────

  const handleYesNo = (value: "yes" | "no") => {
    submitAnswer(value, value.toUpperCase());
  };

  const handleVisualSelect = (value: string) => {
    const opt = currentQuestion?.options?.find(o => o.value === value);
    submitAnswer(value, opt?.label ?? value);
  };

  const handleReading = (result: ReadingResult) => {
    submitAnswer({ value: result.value, unit: result.unit, branch_key: result.branchKey }, `${result.value} ${result.unit} (${result.classification})`);
  };

  const handlePhoto = (photoResult: PhotoResult) => {
    submitAnswer({ photo_url: photoResult.photo_url, slot_name: photoResult.slot_name }, "Photo captured");
  };

  const handleMulti = (data: MultiInputData) => {
    const answer: Record<string, unknown> = {};
    // Explicit branch_key from visual_select or reading takes routing priority
    if (data.branch_key) answer.branch_key = data.branch_key;
    data.photos.forEach(p => { answer[p.slot_name] = { photo_url: p.photo_url, photo_type: p.photo_type }; });
    data.readings.forEach((r, i) => { answer[`reading_${i}`] = { value: r.value, unit: r.unit, branch_key: r.branchKey }; });
    data.selections?.forEach((s, i) => { answer[`selection_${i}`] = { slot_name: s.slot_name, value: s.value }; });
    const display = [
      ...data.photos.map(() => "Photo captured"),
      ...data.readings.map(r => `${r.value} ${r.unit}`),
      ...(data.selections?.map(s => s.value) ?? []),
    ].filter(Boolean).join(" + ") || "Submitted";
    submitAnswer(answer, display);
  };

  // ── Photo skip handlers ────────────────────────────────────────────────

  const handleSkipSimple = (slotName: string) =>
    submitAnswer({ slot_name: slotName, branch_key: "skipped" }, "Photo skipped");

  const handleSkipReroute = (slotName: string) =>
    submitAnswer({ slot_name: slotName, branch_key: "skip" }, "Using manual path (no thermal camera)");

  const handleSkipChoice = (slotName: string, branchKey: string, label: string) =>
    submitAnswer({ slot_name: slotName, branch_key: branchKey }, label);

  const handleSkipCode = (slotName: string) => {
    const code = manualCode.trim();
    if (!code) return;
    submitAnswer({ slot_name: slotName, branch_key: "skipped", manual_error_code: code }, `Code: ${code}`);
  };

  const handleWaterCheck = (branchKey: string, label: string) =>
    submitAnswer({ branch_key: branchKey }, label);

  // ── Render ─────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
        <p className="text-sm" style={{ color: "#7a8299" }}>Starting diagnostic...</p>
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

  const skipConfig = PHOTO_SKIP_CONFIG[currentQuestion.step_id];

  const stepNum = history.length + 1;
  const approxTotal = totalSteps > 0 ? Math.max(totalSteps, stepNum) : null;

  return (
    <div className="flex flex-col gap-5 w-full">

      {/* WS-N3: Progress indicator */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          {history.length > 0 ? (
            <button
              onClick={handleUndo}
              disabled={undoing || submitting}
              className="flex items-center gap-1 text-xs font-semibold transition-opacity disabled:opacity-40"
              style={{ color: "#3498db" }}
            >
              {undoing
                ? <span className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin inline-block" />
                : <span>&#x2190;</span>
              }
              Undo last answer
            </button>
          ) : (
            <span />
          )}
          <span className="text-xs font-semibold" style={{ color: "#7a8299" }}>
            {approxTotal ? `Step ${stepNum} of ~${approxTotal}` : `Step ${stepNum}`}
          </span>
        </div>
        <div className="flex gap-1">
          {Array.from({ length: Math.max(approxTotal ?? stepNum, stepNum) }, (_, i) => (
            <div
              key={i}
              className="h-1.5 rounded-full flex-1 transition-all duration-300"
              style={{ background: i < stepNum ? "#3498db" : "#2a2a4a" }}
            />
          ))}
        </div>
      </div>

      {/* Question */}
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
        {currentQuestion.input_type === "photo" && currentQuestion.photo_spec && (
          <>
            <PhotoSlot spec={currentQuestion.photo_spec} assessmentId={assessmentId}
              authHeaders={liveHeaders} onCapture={handlePhoto} disabled={submitting} />

            {/* ── Photo skip UI ── */}
            {skipConfig && (() => {
              const spec = currentQuestion.photo_spec!;
              return (
                <div className="flex flex-col gap-2">
                  {/* simple: single link */}
                  {skipConfig.type === "simple" && (
                    <button onClick={() => handleSkipSimple(spec.slot_name)} disabled={submitting}
                      className="text-xs font-medium text-center py-1.5" style={{ color: "#4a5568" }}>
                      Skip photo and continue →
                    </button>
                  )}

                  {/* reroute: single descriptive button */}
                  {skipConfig.type === "reroute" && (
                    <button onClick={() => handleSkipReroute(spec.slot_name)} disabled={submitting}
                      className="text-xs font-medium text-center py-1.5" style={{ color: "#4a5568" }}>
                      No thermal camera — switch to 4-step manual method →
                    </button>
                  )}

                  {/* choice: collapse → expand with buttons */}
                  {skipConfig.type === "choice" && (
                    skipExpanded ? (
                      <div className="rounded-xl p-3 flex flex-col gap-2" style={{ background: "#0d1117", border: "1px solid #2a3050" }}>
                        <p className="text-xs font-semibold" style={{ color: "#a0a8c0" }}>Select condition (skip photo):</p>
                        <div className="flex flex-wrap gap-2">
                          {skipConfig.choices!.map(c => (
                            <button key={c.branch_key}
                              onClick={() => handleSkipChoice(spec.slot_name, c.branch_key, c.label)}
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

                  {/* code_input: collapse → text field + proceed */}
                  {skipConfig.type === "code_input" && (
                    skipExpanded ? (
                      <div className="rounded-xl p-3 flex flex-col gap-2" style={{ background: "#0d1117", border: "1px solid #2a3050" }}>
                        <p className="text-xs font-semibold" style={{ color: "#a0a8c0" }}>Enter error code manually:</p>
                        <input type="text" value={manualCode}
                          onChange={e => setManualCode(e.target.value)}
                          placeholder="e.g. E5, 4-flash, U4, CH05"
                          className="w-full px-3 py-2 rounded-xl text-sm"
                          style={{ background: "#16213e", color: "#f0f0f0", border: "1.5px solid #2a3a5a", outline: "none" }} />
                        <button onClick={() => handleSkipCode(spec.slot_name)}
                          disabled={submitting || !manualCode.trim()}
                          className="w-full py-2 rounded-xl font-semibold text-sm"
                          style={{ background: "#3498db", color: "#fff", opacity: (submitting || !manualCode.trim()) ? 0.5 : 1 }}>
                          Proceed with this code →
                        </button>
                      </div>
                    ) : (
                      <button onClick={() => setSkipExpanded(true)} disabled={submitting}
                        className="text-xs font-medium text-center py-1.5" style={{ color: "#4a5568" }}>
                        Enter error code manually instead →
                      </button>
                    )
                  )}
                </div>
              );
            })()}
          </>
        )}

        {currentQuestion.input_type === "multi" && multiItems.length > 0 && (
          <>
            <MultiInput inputs={multiItems} assessmentId={assessmentId}
              authHeaders={liveHeaders} ocrNameplate={ocrNameplate}
              onSubmit={handleMulti} disabled={submitting} />

            {/* ── B-Indoor drain pan: photo-only multi → manual water check ── */}
            {skipConfig?.type === "water_check" && (
              skipExpanded ? (
                <div className="rounded-xl p-3 flex flex-col gap-2" style={{ background: "#0d1117", border: "1px solid #2a3050" }}>
                  <p className="text-xs font-semibold" style={{ color: "#a0a8c0" }}>Tech confirms (skip photos):</p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleWaterCheck("pan_water_present_or_exit_blocked", "Standing water / drain blocked")}
                      disabled={submitting}
                      className="flex-1 py-2.5 rounded-xl font-semibold text-sm"
                      style={{ background: "#e74c3c", color: "#fff" }}>
                      Standing water visible / drain blocked
                    </button>
                    <button
                      onClick={() => handleWaterCheck("pan_dry_and_exit_flowing", "Pan dry, drain flowing")}
                      disabled={submitting}
                      className="flex-1 py-2.5 rounded-xl font-semibold text-sm"
                      style={{ background: "#2ecc71", color: "#0d1117" }}>
                      Pan dry, drain flowing
                    </button>
                  </div>
                </div>
              ) : (
                <button onClick={() => setSkipExpanded(true)} disabled={submitting}
                  className="text-xs font-medium text-center py-1.5" style={{ color: "#4a5568" }}>
                  Can't photograph? Confirm condition manually →
                </button>
              )
            )}
          </>
        )}
      </div>

      {submitting && (
        <div className="flex items-center justify-center gap-2 py-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <span className="text-sm" style={{ color: "#7a8299" }}>Processing...</span>
        </div>
      )}

      {/* WS-N3: Diagnosis chain summary (previous answers) */}
      {history.length > 0 && (
        <div className="rounded-xl p-3 flex flex-col gap-1"
          style={{ background: "#0d1117", border: "1px solid #1a2030" }}>
          <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: "#3a4060" }}>
            Path so far
          </p>
          {history.map((h, i) => (
            <div key={i} className="flex items-start gap-1.5 text-xs" style={{ color: "#4a5568" }}>
              <span style={{ color: "#3a4060" }}>{i + 1}.</span>
              <span className="flex-1 truncate">{h.question_text}</span>
              <span className="font-semibold flex-shrink-0" style={{ color: "#6a8090" }}>
                {h.answer_display}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Cancel */}
      <button
        onClick={() => {
          trackEvent("diagnostic_cancelled", {
            complaint_type: complaintType,
            step_id: currentQuestion?.step_id ?? "unknown",
            steps_completed: history.length,
          });
          onCancel();
        }}
        className="text-xs font-medium text-center py-2 mt-2"
        style={{ color: "#4a5568" }}
      >
        Back to complaint selection
      </button>
    </div>
  );
}
