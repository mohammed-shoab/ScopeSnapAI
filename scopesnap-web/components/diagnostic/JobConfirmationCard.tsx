"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";
import YesNoButtons from "./YesNoButtons";

export interface FaultCardOption {
  card_id: number;
  name: string;
}

interface JobConfirmationCardProps {
  assessmentId: string;
  diagnosedCardId: number;
  diagnosedCardName: string;
  faultCards: FaultCardOption[];
  authHeaders: Record<string, string>;
  onConfirmed: () => void;
  onSkip: () => void;
}

export default function JobConfirmationCard({
  assessmentId,
  diagnosedCardId,
  diagnosedCardName,
  faultCards,
  authHeaders,
  onConfirmed,
  onSkip,
}: JobConfirmationCardProps) {
  const [actualCardId, setActualCardId] = useState<number>(diagnosedCardId);
  const [complaintResolved, setComplaintResolved] = useState<boolean | null>(null);
  const [finalInvoice, setFinalInvoice] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = complaintResolved !== null && !submitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      const r = await fetch(`${API_URL}/api/job-confirmation`, {
        method: "POST",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({
          assessment_id: assessmentId,
          diagnosed_card_id: diagnosedCardId,
          actual_card_id: actualCardId,
          complaint_resolved: complaintResolved,
          final_invoice_amount: finalInvoice ? parseFloat(finalInvoice.replace(/[^0-9.]/g, "")) : null,
          consent_given: true,
        }),
      });
      if (!r.ok) throw new Error("Submission failed");
      onConfirmed();
    } catch {
      setError("Could not save. Try again.");
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Header */}
      <div className="rounded-2xl p-5" style={{ background: "rgba(52,152,219,0.10)", border: "2px solid #3498db" }}>
        <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: "#3498db" }}>
          30-Second Confirmation
        </p>
        <p className="text-base font-extrabold text-white leading-snug">
          Your honest answer trains the AI. Takes 30 seconds.
        </p>
        <p className="text-sm mt-1" style={{ color: "#7a8299" }}>
          Diagnosed: <span className="text-white font-bold">Card #{diagnosedCardId} — {diagnosedCardName}</span>
        </p>
      </div>

      {/* Q1: What did you actually fix? */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-bold text-text-primary">1. What did you actually fix?</label>
        <select
          value={actualCardId}
          onChange={(e) => setActualCardId(Number(e.target.value))}
          className="w-full px-4 py-3 rounded-xl border-2 font-medium text-sm focus:outline-none"
          style={{ background: "#16213e", borderColor: "#2a2a4a", color: "#f0f0f0" }}
        >
          {faultCards.map(fc => (
            <option key={fc.card_id} value={fc.card_id}>
              Card #{fc.card_id} — {fc.name}
            </option>
          ))}
          <option value={0}>Other / No repair needed</option>
        </select>
      </div>

      {/* Q2: Was the complaint resolved? */}
      <div className="flex flex-col gap-3">
        <label className="text-sm font-bold text-text-primary">2. Was the homeowner&apos;s complaint resolved?</label>
        <YesNoButtons
          onAnswer={(val) => setComplaintResolved(val === "yes")}
          disabled={submitting}
        />
        {complaintResolved !== null && (
          <p className="text-sm font-bold text-center" style={{ color: complaintResolved ? "#2ecc71" : "#e74c3c" }}>
            {complaintResolved ? "Yes — complaint resolved" : "No — issue persists"}
          </p>
        )}
      </div>

      {/* Q3: Final invoice (optional) */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-bold text-text-primary">3. Final invoice amount <span style={{ color: "#7a8299", fontWeight: 400 }}>(optional)</span></label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 font-mono font-bold" style={{ color: "#7a8299" }}>$</span>
          <input
            type="number"
            inputMode="decimal"
            value={finalInvoice}
            onChange={(e) => setFinalInvoice(e.target.value)}
            placeholder="0.00"
            className="w-full pl-8 pr-4 py-3 rounded-xl border-2 font-mono text-right focus:outline-none"
            style={{ background: "#16213e", borderColor: "#2a2a4a", color: "#f0f0f0" }}
          />
        </div>
      </div>

      {error && (
        <p className="text-sm text-center font-medium" style={{ color: "#e74c3c" }}>{error}</p>
      )}

      {/* Actions */}
      <div className="flex flex-col gap-3">
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="w-full py-4 rounded-2xl text-white font-extrabold text-base transition-all active:scale-95 disabled:opacity-40"
          style={{ background: "linear-gradient(135deg, #3498db 0%, #2980b9 100%)" }}
        >
          {submitting ? "Saving..." : "Submit Confirmation"}
        </button>
        <button
          onClick={onSkip}
          className="w-full py-3 rounded-2xl font-semibold text-sm transition-all"
          style={{ color: "#7a8299" }}
        >
          Skip for now
        </button>
      </div>
    </div>
  );
}
