"use client";

import { useState, useEffect, useCallback } from "react";
import { API_URL } from "@/lib/api";
import YesNoButtons from "./YesNoButtons";
import VisualSelect from "./VisualSelect";
import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";
import ReadingInput, { ReadingSpec, ReadingResult } from "./ReadingInput";
import MultiInput, { MultiInputItem } from "./MultiInput";
import posthog from 'posthog-js';

// ââ API types ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

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

// ââ Analytics helper â graceful if PostHog not loaded âââââââââââââââââââââ

function trackEvent(name: string, props: Record<string, unknown>) {
  try {
    // PostHog loaded by providers/PostHogProvider.tsx
    if (typeof window !== "undefined" && (window as unknown as Record<string, unknown>).posthog) {
      ((window as unknown as Record<string, unknown>).posthog as { capture: (n: string, p: Record<string, unknown>) => void }).capture(name, props);
    }
  } catch { /* never crash on analytics */ }
}

// ââ Props ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

interface DiagnosticFlowProps {
  assessmentId: string;
  complaintType: string;
  authHeaders: Record<string, string>;
  ocrNameplate?: Record<string, unknown> | null;
  onResolved: (cardId: number, cardName: string, sessionId: string, photoSlots: PhotoSlotSpec[], history: AnswerRecord[]) => void;
  onPhase2Gate: (continuation: GateContinuation) => void;
  onEscalated: (reason: string) => void;
  onCancel: () => void;
}

// ââ Component ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

export default function DiagnosticFlow({
  assessmentId,
  complaintType,
  authHeaders,
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

  // ââ Start session on mount âââââââââââââââââââââââââââââââââââââââââââââ

  useEffect(() => {
    const start = async () => {
      setLoading(true);
      setError(null);
      try {
        const r = await fetch(`${API_URL}/api/diagnostic/session`, {
          method: "POST",
          headers: { ...authHeaders, "Content-Type": "application/json" },
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
          headers: authHeaders,
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

  // ââ Submit answer ââââââââââââââââââââââââââââââââââââââââââââââââââââââ

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
      const r = await fetch(`${API_URL}/api/diagnostic/session/${sessionId}/answer`, {
        method: "POST",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
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
      });      posthog.capture('diagnostic_question_answered', { question: currentQuestion?.hint_text ?? '', answer: answerDisplay ?? String(answer), complaint_type: complaintType ?? '' });


      if (resp.phase_2_gate && resp.gate_continuation) {
      posthog.capture('diagnostic_phase2_gate', { complaint_type: complaintType ?? '' });
        trackEvent("diagnostic_session_phase2_gate", {
          complaint_type: complaintType,
          step_id: currentQuestion.step_id,
        });
        onPhase2Gate({ session_id: sessionId, card_id: resp.card_id ?? null, gate_continuation: resp.gate_continuation });
        return;
      }

      if (resp.escalated) {
        const reason = resp.escalation_reason ?? "tech_judgment";
        trackEvent("diagnostic_session_escalated", {
          complaint_type: complaintType,
          step_id: currentQuestion.step_id,
          reason,
        });
        onEscalated(reason);
        return;
      }

      if (resp.resolved && resp.card_id) {
        trackEvent("diagnostic_session_resolved", {
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
  }, [sessionId, currentQuestion, history, authHeaders, complaintType, sessionStartTime, onResolved, onPhase2Gate, onEscalated]);

  // ââ WS-N3: Back button (undo last answer) âââââââââââââââââââââââââââââ

  const handleUndo = useCallback(async () => {
    if (!sessionId || history.length === 0 || undoing) return;
    setUndoing(true);
    setError(null);
    try {
      const r = await fetch(`${API_URL}/api/diagnostic/session/${sessionId}/undo`, {
        method: "PATCH",
        headers: { ...authHeaders, "Content-Type": "application/json" },
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
  }, [sessionId, history, authHeaders, undoing]);

  // ââ Answer handlers ââââââââââââââââââââââââââââââââââââââââââââââââââââ

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

  const handleMulti = (data: { photos: PhotoResult[]; readings: ReadingResult[] }) => {
    const answer: Record<string, unknown> = {};
    data.photos.forEach(p => { answer[p.slot_name] = { photo_url: p.photo_url, photo_type: p.photo_type }; });
    data.readings.forEach((r, i) => { answer[`reading_${i}`] = { value: r.value, unit: r.unit, branch_key: r.branchKey }; });
    const display = [
      ...data.photos.map(() => "Photo captured"),
      ...data.readings.map(r => `${r.value} ${r.unit}`),
    ].join(" + ");
    submitAnswer(answer, display);
  };

  // ââ Render âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

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
          <PhotoSlot spec={currentQuestion.photo_spec} assessmentId={assessmentId}
            authHeaders={authHeaders} onCapture={handlePhoto} disabled={submitting} />
        )}
        {currentQuestion.input_type === "multi" && multiItems.length > 0 && (
          <MultiInput inputs={multiItems} assessmentId={assessmentId}
            authHeaders={authHeaders} ocrNameplate={ocrNameplate}
            onSubmit={handleMulti} disabled={submitting} />
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
          trackEvent("diagnostic_session_cancelled", {
            complaint_type: complaintType,
            step_id: currentQuestion?.step_id ?? "unknown",
            steps_completed: history.length,
          });
          posthog.capture('diagnostic_cancelled', { complaint_type: complaintType ?? '' });
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
