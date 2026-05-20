"use client";

/**
 * DiagnosisListEmptyState — Track D (D.8)
 * Shown when /diagnoses returns 0 results.
 */

interface Props {
  onNewDiagnosis: () => void;
}

export default function DiagnosisListEmptyState({ onNewDiagnosis }: Props) {
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center", padding: "64px 24px", textAlign: "center",
    }}>
      {/* Icon */}
      <div style={{ marginBottom: 20, opacity: 0.35 }}>
        <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="1.2">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
          <path d="M11 8v6M8 11h6"/>
        </svg>
      </div>
      <h3 style={{ margin: "0 0 8px", fontSize: 18, fontWeight: 700, color: "#1e293b" }}>
        No diagnoses yet
      </h3>
      <p style={{ margin: "0 0 24px", fontSize: 14, color: "#64748b", maxWidth: 280 }}>
        Tap New Diagnosis below to get started with your first assessment.
      </p>
      <button
        onClick={onNewDiagnosis}
        style={{
          padding: "12px 28px", borderRadius: 8, border: "none",
          background: "#1e293b", color: "#fff", fontSize: 14,
          fontWeight: 700, cursor: "pointer",
        }}
      >
        New Diagnosis
      </button>
    </div>
  );
}
