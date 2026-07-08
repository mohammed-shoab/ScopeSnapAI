/**
 * ReadingReceipt -- GATE-5 inline reading-vs-target block on terminal fault cards.
 * Fed by the backend `reading_receipt` payload. Shows the reading, the target, the
 * result, why-this-card, and confidence; on high-exposure cards it appends the
 * enhanced Layer-4 note. The standard Layer-4 disclaimer is rendered separately by
 * FaultResolutionScreen (this block sits directly beneath it).
 */

export interface ReadingReceiptData {
  reading_value: number | string;
  unit?: string | null;
  target_low?: number | string | null;
  target_high?: number | string | null;
  target_source?: string | null;
  result: string; // "low" | "within range" | "high"
  why_line?: string | null;
  ruled_out?: { fault: string; because_reading: string }[] | null;
  confidence?: string | null; // "High" | "Medium" | "Low"
  high_exposure?: boolean;
}

const RESULT_COLOR: Record<string, string> = {
  "within range": "#16a34a",
  low: "#b45309",
  high: "#b45309",
};

const ENHANCED_L4 =
  "This is a preliminary finding requiring independent Manual J load calculation and " +
  "licensed inspection before any equipment replacement or major service recommendation " +
  "is presented to the homeowner.";

export default function ReadingReceipt({ data }: { data: ReadingReceiptData }) {
  const hasTarget = data.target_low != null && data.target_high != null;
  const resultColor = RESULT_COLOR[(data.result || "").toLowerCase()] || "#475569";
  return (
    <div
      data-testid="reading-receipt"
      style={{
        border: "1px solid #e2e8f0", borderRadius: 8, background: "#f8fafc",
        padding: 14, fontSize: 14, color: "#334155",
        display: "flex", flexDirection: "column", gap: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <span style={{ color: "#64748b" }}>You entered</span>
        <span style={{ fontWeight: 700, fontFamily: "monospace" }}>
          {data.reading_value} {data.unit ?? ""}
        </span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
        <span style={{ color: "#64748b" }}>Compared against</span>
        <span style={{ fontWeight: 600, textAlign: "right" }}>
          {hasTarget ? `${data.target_low}-${data.target_high} ${data.unit ?? ""}` : "reference targets"}
          {data.target_source ? (
            <span style={{ fontWeight: 400, color: "#94a3b8" }}> ({data.target_source})</span>
          ) : null}
        </span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ color: "#64748b" }}>Result</span>
        <span style={{ fontWeight: 700, textTransform: "uppercase", fontSize: 12, color: resultColor }}>
          {data.result}
        </span>
      </div>
      {data.why_line ? (
        <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: 8 }}>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: "#94a3b8" }}>
            Why this card
          </div>
          <div style={{ color: "#334155" }}>{data.why_line}</div>
        </div>
      ) : null}
      {data.confidence ? (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #e2e8f0", paddingTop: 8 }}>
          <span style={{ color: "#64748b" }}>Confidence</span>
          <span style={{ fontWeight: 700, fontSize: 12, textTransform: "uppercase" }}>{data.confidence}</span>
        </div>
      ) : null}
      {data.high_exposure ? (
        <div
          data-testid="reading-receipt-enhanced-l4"
          style={{ borderTop: "1px solid #e2e8f0", paddingTop: 8, fontSize: 12, color: "#64748b", fontWeight: 600 }}
        >
          {ENHANCED_L4}
        </div>
      ) : null}
    </div>
  );
}
