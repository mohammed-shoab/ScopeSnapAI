/**
 * SnapAI — DataConfidenceLabel
 * SOW Task 1.9: Trust indicator shown on homeowner reports.
 *
 * Shows AI confidence level for the equipment identification in a compact
 * badge format. Helps homeowners understand the quality of the AI reading.
 *
 * Confidence bands:
 *  ≥90% → High Confidence (green)
 *  75–89% → Good Confidence (amber)
 *  60–74% → Fair Confidence (orange)
 *  <60% → Low Confidence (gray)
 *
 * Usage: <DataConfidenceLabel confidence={92} />
 */

interface DataConfidenceLabelProps {
  confidence?: number | null;
  className?: string;
  style?: React.CSSProperties;
}

interface Band {
  label: string;
  color: string;
  bg: string;
  border: string;
}

function getBand(confidence: number): Band {
  if (confidence >= 90) return { label: "High Confidence", color: "#1a8754", bg: "#e8f5ee", border: "#c8efda" };
  if (confidence >= 75) return { label: "Good Confidence", color: "#1565c0", bg: "#e3f0ff", border: "#b8d4f0" };
  if (confidence >= 60) return { label: "Fair Confidence", color: "#c4600a", bg: "#fef3e8", border: "#f5d9c0" };
  return { label: "Low Confidence", color: "#7a7770", bg: "#f7f6f2", border: "#e5e2da" };
}

export default function DataConfidenceLabel({
  confidence,
  className,
  style,
}: DataConfidenceLabelProps) {
  if (confidence == null || isNaN(confidence)) return null;

  const pct    = Math.round(Math.min(100, Math.max(0, confidence)));
  const band   = getBand(pct);

  return (
    <div
      className={className}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "4px 10px",
        borderRadius: 20,
        background: band.bg,
        border: `1px solid ${band.border}`,
        ...style,
      }}
    >
      {/* Mini confidence bar */}
      <div
        style={{
          width: 32,
          height: 4,
          borderRadius: 2,
          background: "#e5e2da",
          overflow: "hidden",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: band.color,
            borderRadius: 2,
            transition: "width .4s ease",
          }}
        />
      </div>

      {/* Label */}
      <span
        style={{
          fontSize: 10,
          fontWeight: 700,
          color: band.color,
          fontFamily: "IBM Plex Mono, monospace",
          whiteSpace: "nowrap",
        }}
      >
        {pct}% · {band.label}
      </span>
    </div>
  );
}
