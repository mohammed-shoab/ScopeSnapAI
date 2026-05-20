"use client";

/**
 * DiagnosisFeedbackModal — Track DX (DX.6)
 * Replaces the Track D free-text modal with a structured alternative fault picker.
 * Title: "What did you actually find?" (Rory framing — non-confrontational).
 *
 * Layout:
 *  - 5 alternative fault buttons (from fault_cards.alternative_cards JSONB
 *    if populated; otherwise the generic top-5 list shown below)
 *  - "Other (describe)" button — expands a textarea
 *  - Skip button — closes, no POST
 *  - Save & Close button — posts to /api/diagnostic/feedback
 */

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";
import { trackEvent } from "@/lib/tracking";

// Generic top-5 list when fault_cards.alternative_cards is empty
const GENERIC_ALTERNATIVES = [
  { id: null, name: "Compressor Failure" },
  { id: null, name: "Refrigerant Leak" },
  { id: null, name: "Wiring / Communication Fault" },
  { id: null, name: "Sensor / Thermistor Fault" },
  { id: null, name: "Drain Clog / Water Leak" },
];

interface AlternativeOption {
  id: number | null;
  name: string;
}

interface Props {
  sessionId: string;
  /** Alternative fault options from fault_cards.alternative_cards (may be empty) */
  alternatives?: AlternativeOption[];
  /** Called after modal is dismissed.
   *  - result = undefined  → user clicked Skip (no POST)
   *  - result = object     → user saved (POST fired)
   */
  onClose: (result?: { alternativeFaultId: number | null; text: string | null }) => void;
}

export default function DiagnosisFeedbackModal({ sessionId, alternatives, onClose }: Props) {
  const { getToken } = useAuth();
  const [selected, setSelected]   = useState<AlternativeOption | null>(null);
  const [showOther, setShowOther]  = useState(false);
  const [otherText, setOtherText]  = useState("");
  const [saving, setSaving]        = useState(false);
  const [error, setError]          = useState<string | null>(null);

  const options = (alternatives && alternatives.length > 0) ? alternatives : GENERIC_ALTERNATIVES;

  function handleSelectOption(opt: AlternativeOption) {
    setSelected(opt);
    setShowOther(false);
    setOtherText("");
  }

  function handleSelectOther() {
    setSelected(null);
    setShowOther(true);
  }

  async function handleSave() {
    // Must have either a selected option or other text (or can skip)
    if (!selected && !showOther) return;

    setSaving(true);
    setError(null);

    const alternativeFaultId = selected?.id ?? null;
    const realFaultText      = showOther ? (otherText.trim() || null) : null;

    try {
      const token = await getToken();
      await apiFetch("/api/diagnostic/feedback", {
        method: "POST",
        body: JSON.stringify({
          session_id:          sessionId,
          agreement:           "different_fault",
          alternative_fault_id: alternativeFaultId,
          real_fault_text:     realFaultText,
        }),
        token: token ?? undefined,
      });

      trackEvent("fault_screen_agreement", {
        session_id:           sessionId,
        agreement:            "different_fault",
        alternative_fault_id: alternativeFaultId,
        has_text:             !!realFaultText,
      });

      onClose({ alternativeFaultId, text: realFaultText });
    } catch {
      setError("Could not save feedback. Please try again.");
      setSaving(false);
    }
  }

  function handleSkip() {
    trackEvent("fault_screen_agreement_skipped", { session_id: sessionId });
    onClose(undefined);
  }

  const canSave = selected !== null || (showOther && otherText.trim().length > 0);

  // ── Backdrop + bottom-sheet modal ─────────────────────────────────────────

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
        maxHeight: "85vh", overflowY: "auto",
      }}>
        {/* Header */}
        <h2 style={{ margin: "0 0 4px", fontSize: 18, fontWeight: 700, color: "#0f172a" }}>
          What did you actually find?
        </h2>
        <p style={{ margin: "0 0 20px", fontSize: 13, color: "#64748b" }}>
          Tap the fault you found — helps us improve the AI.
        </p>

        {/* Alternative fault buttons */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {options.map((opt, i) => {
            const isSelected = selected?.name === opt.name;
            return (
              <button
                key={i}
                onClick={() => handleSelectOption(opt)}
                style={{
                  width: "100%", padding: "13px 16px", textAlign: "left",
                  borderRadius: 8, border: isSelected ? "2px solid #16a34a" : "1.5px solid #e2e8f0",
                  background: isSelected ? "rgba(22,163,74,.06)" : "#fff",
                  color: isSelected ? "#15803d" : "#1e293b",
                  fontSize: 14, fontWeight: isSelected ? 600 : 400,
                  cursor: "pointer", transition: "border-color 0.1s, background 0.1s",
                }}
              >
                {isSelected && <span style={{ marginRight: 8 }}>✓</span>}
                {opt.name}
              </button>
            );
          })}

          {/* Other (describe) button */}
          <button
            onClick={handleSelectOther}
            style={{
              width: "100%", padding: "13px 16px", textAlign: "left",
              borderRadius: 8, border: showOther ? "2px solid #2563eb" : "1.5px solid #e2e8f0",
              background: showOther ? "rgba(37,99,235,.05)" : "#fff",
              color: showOther ? "#1d4ed8" : "#475569",
              fontSize: 14, fontWeight: showOther ? 600 : 400,
              cursor: "pointer", transition: "border-color 0.1s, background 0.1s",
            }}
          >
            {showOther && <span style={{ marginRight: 8 }}>✓</span>}
            Other (describe)
          </button>

          {/* Text area — expands when Other is selected */}
          {showOther && (
            <textarea
              value={otherText}
              onChange={(e) => setOtherText(e.target.value)}
              placeholder="e.g. Contactor failure, not the capacitor"
              maxLength={500}
              rows={3}
              style={{
                width: "100%", boxSizing: "border-box", resize: "none",
                border: "1.5px solid #e2e8f0", borderRadius: 8, padding: "10px 12px",
                fontSize: 14, color: "#1e293b", fontFamily: "inherit", outline: "none",
              }}
              onFocus={(e) => { e.target.style.borderColor = "#2563eb"; }}
              onBlur={(e)  => { e.target.style.borderColor = "#e2e8f0"; }}
              autoFocus
            />
          )}
        </div>

        {error && (
          <div style={{ marginTop: 10, fontSize: 12, color: "#dc2626" }}>{error}</div>
        )}

        {/* Skip / Save & Close */}
        <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
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
            disabled={saving || !canSave}
            style={{
              flex: 2, padding: "13px 0", borderRadius: 8, border: "none",
              background: (saving || !canSave) ? "#94a3b8" : "#1e293b",
              color: "#fff", fontSize: 14, fontWeight: 700,
              cursor: (saving || !canSave) ? "not-allowed" : "pointer",
            }}
          >
            {saving ? "Saving..." : "Save & Close"}
          </button>
        </div>
      </div>
    </div>
  );
}
