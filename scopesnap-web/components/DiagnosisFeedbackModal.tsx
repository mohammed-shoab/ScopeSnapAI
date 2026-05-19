"use client";

/**
 * DiagnosisFeedbackModal — Track D (D.10)
 * Shown when tech taps "Different fault found". Collects a free-text description
 * of the actual fault, posts to /api/diagnostic/feedback, then closes.
 */

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface Props {
  sessionId: string;
  /** Called after modal is dismissed.
   *  - submittedText = undefined → user clicked Skip (no POST)
   *  - submittedText = string   → user saved (POST fired, may be empty string)
   */
  onClose: (submittedText?: string) => void;
}

export default function DiagnosisFeedbackModal({ sessionId, onClose }: Props) {
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await apiFetch("/api/diagnostic/feedback", {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          agreement: "different_fault",
          real_fault_text: text.trim() || null,
        }),
      });
      onClose(text);
    } catch {
      setError("Could not save feedback. Please try again.");
      setSaving(false);
    }
  }

  function handleSkip() {
    // Skip fires no POST — onClose called with undefined
    onClose(undefined);
  }

  // ── Backdrop + modal ────────────────────────────────────────────────────────

  return (
    <div
      style={{
        position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
        display: "flex", alignItems: "flex-end", justifyContent: "center",
        zIndex: 1000, padding: "0 0 env(safe-area-inset-bottom, 0)",
      }}
      onClick={(e) => { if (e.target === e.currentTarget) handleSkip(); }}
    >
      <div style={{
        background: "#fff", borderRadius: "16px 16px 0 0", width: "100%",
        maxWidth: 540, padding: "24px 20px 32px",
        boxShadow: "0 -4px 24px rgba(0,0,0,.12)",
      }}>
        <h2 style={{ margin: "0 0 6px", fontSize: 18, fontWeight: 700, color: "#0f172a" }}>
          What was the real fault?
        </h2>
        <p style={{ margin: "0 0 16px", fontSize: 13, color: "#64748b" }}>
          Your answer helps us improve the AI diagnostic.
        </p>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g. Contactor failure, not the capacitor"
          rows={3}
          style={{
            width: "100%", boxSizing: "border-box", resize: "none",
            border: "1.5px solid #e2e8f0", borderRadius: 8, padding: "10px 12px",
            fontSize: 14, color: "#1e293b", fontFamily: "inherit",
            outline: "none",
          }}
          onFocus={(e) => { e.target.style.borderColor = "#2563eb"; }}
          onBlur={(e) => { e.target.style.borderColor = "#e2e8f0"; }}
          autoFocus
        />

        {error && (
          <div style={{ marginTop: 8, fontSize: 12, color: "#dc2626" }}>{error}</div>
        )}

        <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
          <button
            onClick={handleSkip}
            disabled={saving}
            style={{
              flex: 1, padding: "13px 0", borderRadius: 8,
              border: "1.5px solid #e2e8f0", background: "#fff",
              color: "#475569", fontSize: 14, fontWeight: 600, cursor: "pointer",
            }}
          >
            Skip
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            style={{
              flex: 1, padding: "13px 0", borderRadius: 8, border: "none",
              background: saving ? "#94a3b8" : "#1e293b",
              color: "#fff", fontSize: 14, fontWeight: 700, cursor: saving ? "not-allowed" : "pointer",
            }}
          >
            {saving ? "Saving..." : "Save & Close"}
          </button>
        </div>
      </div>
    </div>
  );
}
