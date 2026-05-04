"use client";

import { useState, useEffect, useCallback } from "react";
import { API_URL } from "@/lib/api";
import YesNoButtons from "./YesNoButtons";
import VisualSelect from "./VisualSelect";
import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";
import ReadingInput, { ReadingSpec, ReadingResult } from "./ReadingInput";
import MultiInput, { MultiInputItem } from "./MultiInput";

// ── API types (mirror backend Pydantic models) ─────────────────────────────

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
  gate_continuation: Record<string, unknown>;
}

export interface AnswerRecord {
  step_id: string;
  question_text: string;
  answer_display: string;
}

// ── Props ──────────────────────────────────────────────────────────────────

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

// ── Component ──────────────────────────────────────────────────────────────

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
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stepCount, setStepCount] = useState(0);

  // Start session on mount
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
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to start session");
      } finally {
        setLoading(false);
      }
    };
    start();
  }, [assessmentId, complaintType]);

  const submitAnswer = useCallback(async (answer: unknown, answerDisplay: string) => {
    if (!sessionId || !currentQuestion) return;
    setSubmitting(true);
    setError(null);

    // Append to history
    const record: AnswerRecord = {
      step_id: currentQuestion.step_id,
      question_text: currentQuestion.question_text,
      answer_display: answerDisplay,
    };
    const updatedHistory = [...history, record];
    setHistory(updatedHistory);
    setStepCount(n => n + 1);

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

      if (resp.phase_2_gate && resp.gate_continuation) {
        onPhase2Gate({ session_id: sessionId, gate_continuation: resp.gate_continuation });
        return;
      }

      if (resp.escalated) {
        onEscalated(resp.escalation_reason ?? "Diagnostic could not reach a specific card. Manual inspection required.");
        return;
      }

      if (resp.resolved && resp.card_id) {
        onResolved(resp.card_id, resp.card_name ?? `Card #${resp.card_id}`, sessionId, resp.photo_slots ?? [], updatedHistory);
        return;
      }

      if (resp.next_step) {
        setCurrentQuestion(resp.next_step);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      // Pop last history entry on error
      setHistory(prev => prev.slice(0, -1));
      setStepCount(n => Math.max(0, n - 1));
    } finally {
      setSubmitting(false);
    }
  }, [sessionId, currentQuestion, history, authHeaders, onResolved, onPhase2Gate, onEscalated]);

  // ── Answer handlers per input_type ──────────────────────────────────────

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

  // ── Render ───────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16">
        <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-text-secondary">Starting diagnostic...</p>
      </div>
    );
  }

  if (error && !currentQuestion) {
    return (
      <div className="flex flex-col gap-4 py-8">
        <div className="rounded-xl p-4" style={{ background: "rgba(231,76,60,0.12)", border: "1px solid #e74c3c" }}>
          <p className="text-sm font-bold text-center" style={{ color: "#e74c3c" }}>{error}</p>
        </div>
        <button
          onClick={onCancel}
          className="w-full py-3 rounded-2xl font-semibold text-sm"
          style={{ background: "#16213e", color: "#f0f0f0" }}
        >
          Back to Complaint Selection
        </button>
      </div>
    );
  }

  if (!currentQuestion) return null;

  const multiItems: MultiInputItem[] = currentQuestion.input_type === "multi" && currentQuestion.options
    ? (currentQuestion.options as unknown as MultiInputItem[])
    : [];

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Progress */}
      {stepCount > 0 && (
        <div className="flex items-center gap-2">
          {[...Array(Math.min(stepCount + 1, 6))].map((_, i) => (
            <div
              key={i}
              className="h-1.5 rounded-full flex-1 transition-all"
              style={{ background: i < stepCount ? "#3498db" : "#2a2a4a" }}
            />
          ))}
        </div>
      )}

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
          <ReadingInput spec={currentQuestion.reading_spec} ocrNameplate={ocrNameplate} onSubmit={handleReading} disabled={submitting} />
        )}

        {currentQuestion.input_type === "photo" && currentQuestion.photo_spec && (
          <PhotoSlot
            spec={currentQuestion.photo_spec}
            assessmentId={assessmentId}
            authHeaders={authHeaders}
            onCapture={handlePhoto}
            disabled={submitting}
          />
        )}

        {currentQuestion.input_type === "multi" && multiItems.length > 0 && (
          <MultiInput
            inputs={multiItems}
            assessmentId={assessmentId}
            authHeaders={authHeaders}
            ocrNameplate={ocrNameplate}
            onSubmit={handleMulti}
            disabled={submitting}
          />
        )}
      </div>

      {submitting && (
        <div className="flex items-center justify-center gap-2 py-2">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-text-secondary">Processing...</span>
        </div>
      )}

      {/* Cancel */}
      <button
        onClick={onCancel}
        className="text-xs font-medium text-center py-2 mt-2"
        style={{ color: "#4a5568" }}
      >
        Back to complaint selection
      </button>
    </div>
  );
}
