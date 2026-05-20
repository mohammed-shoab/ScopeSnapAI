"use client";
/**
 * FiveYearComparison — Track G
 * Unified TCO display for homeowner report + Present Mode.
 * "What might come next" — probability-based, market-localized.
 * Board mandates: column order C->B->A, footer disclaimer always visible,
 * methodology block always rendered.
 */

import { useEffect, useRef } from "react";
import { formatCurrency } from "@/lib/market";
import { track } from "@/lib/tracking";

export type TierTCO = {
  probability_pct: number;
  probability_range: string;
  expected_repair_cost: number;
  energy_savings_5yr: number;
};

type FiveYearComparisonProps = {
  optionA: TierTCO | null;
  optionB: TierTCO | null;
  optionC: TierTCO | null;
  recommendedTier: "A" | "B" | "C";
  market: "US" | "PK";
  mode?: "homeowner_report" | "present_mode";
  sessionId?: string;
};

const OPTION_LABELS: Record<string, string> = {
  A: "Fix Today",
  B: "Fix + Prevent",
  C: "Consider Replace",
};

function riskColor(pct: number): string {
  if (pct >= 50) return "#dc2626";
  if (pct >= 20) return "#d97706";
  return "#16a34a";
}

function RiskBar({ pct, color }: { pct: number; color: string }) {
  return (
    <div style={{ height: 8, background: "#f3f4f6", borderRadius: 4, overflow: "hidden", marginTop: 4 }}>
      <div style={{ width: `${Math.max(pct, 4)}%`, height: "100%", background: color, borderRadius: 4 }} />
    </div>
  );
}

function TierCard({
  tier, tco, isRecommended, market, onInspect,
}: {
  tier: "A" | "B" | "C";
  tco: TierTCO;
  isRecommended: boolean;
  market: "US" | "PK";
  onInspect: () => void;
}) {
  const color = riskColor(tco.probability_pct);
  return (
    <div
      style={{
        flex: "1 1 0", minWidth: 0, position: "relative",
        border: `2px solid ${isRecommended ? "#16a34a" : "#e5e7eb"}`,
        borderRadius: 12,
        background: isRecommended ? "#f0fdf4" : "#ffffff",
        padding: "14px 12px",
      }}
      onMouseEnter={isRecommended ? undefined : onInspect}
      onTouchStart={isRecommended ? undefined : onInspect}
    >
      {isRecommended && (
        <div style={{
          position: "absolute", top: -1, right: 10,
          background: "#16a34a", color: "white",
          fontSize: 9, fontWeight: 700, padding: "2px 8px",
          borderRadius: "0 0 6px 6px", letterSpacing: "0.04em",
        }}>
          ★ RECOMMENDED
        </div>
      )}
      <p style={{ fontSize: 11, fontWeight: 700, color: "#374151", margin: "0 0 1px" }}>Option {tier}</p>
      <p style={{ fontSize: 10, color: "#6b7280", margin: "0 0 10px" }}>{OPTION_LABELS[tier]}</p>

      <p style={{ fontSize: 9, fontWeight: 600, color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 2px" }}>
        Risk of major repair (5 yr)
      </p>
      <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
        <span style={{ fontSize: 20, fontWeight: 800, color, fontFamily: "IBM Plex Mono, monospace" }}>
          {tco.probability_pct}%
        </span>
        <span style={{ fontSize: 9, color: "#9ca3af" }}>({tco.probability_range})</span>
      </div>
      <RiskBar pct={tco.probability_pct} color={color} />

      {tco.expected_repair_cost > 0 && (
        <div style={{ marginTop: 10 }}>
          <p style={{ fontSize: 9, fontWeight: 600, color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 2px" }}>If repair happens</p>
          <p style={{ fontSize: 13, fontWeight: 700, color: "#374151", margin: 0, fontFamily: "IBM Plex Mono, monospace" }}>
            ~{formatCurrency(tco.expected_repair_cost, market)} avg
          </p>
        </div>
      )}

      {tco.energy_savings_5yr > 0 && (
        <div style={{ marginTop: 10 }}>
          <p style={{ fontSize: 9, fontWeight: 600, color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 2px" }}>Energy savings (5 yr)</p>
          <p style={{ fontSize: 13, fontWeight: 700, color: "#16a34a", margin: 0, fontFamily: "IBM Plex Mono, monospace" }}>
            ~{formatCurrency(tco.energy_savings_5yr, market)}
          </p>
        </div>
      )}
    </div>
  );
}

export default function FiveYearComparison({
  optionA, optionB, optionC, recommendedTier, market,
  mode = "homeowner_report", sessionId,
}: FiveYearComparisonProps) {
  const methodologyRef = useRef<HTMLDivElement>(null);
  const firedRef = useRef(false);

  if (!optionA && !optionB && !optionC) return null;

  // tco_section_rendered on mount
  useEffect(() => {
    if (firedRef.current) return;
    firedRef.current = true;
    track.tcoSectionRendered(sessionId ?? "", market, recommendedTier, mode);
  }, []);

  // tco_methodology_viewed via IntersectionObserver
  useEffect(() => {
    const el = methodologyRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        track.tcoMethodologyViewed(sessionId ?? "");
        obs.disconnect();
      }
    }, { threshold: 0.4 });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const isPK = market === "PK";
  const disclaimer = isPK
    ? "Probability data based on Pakistan HVAC field experience and tradesman heuristics. Energy savings calculated from inverter efficiency formulas at ₨60/kWh. Individual unit outcomes vary."
    : "Probability data based on industry HVAC service trends and Houston field experience. Energy savings calculated from DOE SEER efficiency formulas at $0.13/kWh. Individual unit outcomes vary.";

  // Column order: C (left) -> B (centre) -> A (right) — Marcus Reed board directive
  const cols: Array<{ tier: "A" | "B" | "C"; tco: TierTCO | null }> = [
    { tier: "C", tco: optionC },
    { tier: "B", tco: optionB },
    { tier: "A", tco: optionA },
  ];

  return (
    <div>
      {/* Section header */}
      <p style={{ fontSize: 17, fontWeight: 700, color: "#111827", margin: "0 0 2px" }}>
        What might come next
      </p>
      <p style={{ fontSize: 11, color: "#6b7280", margin: "0 0 12px" }}>5-year outlook by option</p>

      {/* Three-column cards — row on sm+, column on mobile */}
      <div className="flex flex-col sm:flex-row gap-2">
        {cols.map(({ tier, tco }) =>
          tco ? (
            <TierCard
              key={tier} tier={tier} tco={tco}
              isRecommended={tier === recommendedTier}
              market={market}
              onInspect={() => track.tcoOptionCompared(sessionId ?? "", tier)}
            />
          ) : null
        )}
      </div>

      {/* Footer disclaimer — always visible, board-mandated */}
      <p style={{ fontSize: 10, color: "#9ca3af", marginTop: 10, lineHeight: 1.5, fontStyle: "italic" }}>
        {disclaimer}
      </p>

      {/* Methodology block — G.9 board-mandated credibility surface */}
      <div ref={methodologyRef} style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid #f3f4f6" }}>
        <p style={{ fontSize: 10, fontWeight: 700, color: "#6b7280", textTransform: "uppercase", letterSpacing: "0.07em", margin: "0 0 5px" }}>
          Methodology — How we calculate the 5-year outlook
        </p>
        <p style={{ fontSize: 10, color: "#9ca3af", lineHeight: 1.6, margin: "0 0 4px" }}>
          {isPK
            ? "Probability of major repair: estimated from Pakistan HVAC field experience and tradesman heuristics. Reflects the likelihood of a follow-up repair greater than ₨5,000 within five years. Individual unit outcomes vary."
            : "Probability of major repair: estimated from industry HVAC service trends and field experience from senior tradesmen. Reflects the likelihood of a follow-up repair greater than $500 within five years. Individual unit outcomes vary."}
        </p>
        <p style={{ fontSize: 10, color: "#9ca3af", lineHeight: 1.6, margin: 0 }}>
          {isPK
            ? "Energy savings: calculated using inverter efficiency formulas, local electricity rate (₨60/kWh K-Electric/LESCO), and typical regional cooling hours per year. Actual savings vary based on unit usage, climate, and utility rate changes."
            : "Energy savings: calculated using DOE SEER efficiency formulas, local electricity rate ($0.13/kWh CenterPoint), and typical regional cooling hours per year (1,800/yr Houston). Actual savings vary based on unit usage, climate, and utility rate changes."}
        </p>
      </div>
    </div>
  );
}
