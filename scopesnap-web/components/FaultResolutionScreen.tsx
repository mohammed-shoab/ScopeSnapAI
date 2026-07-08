"use client";

/**
 * FaultResolutionScreen — Track D + Track DX (Group B)
 *
 * Group B changes (DX.3–DX.11):
 *   DX.3  — Repair Plan section (3 tier cards, context-aware labels)
 *   DX.4  — Density trim: customer → subtitle, reasoning → bottom link, parts+time merged
 *   DX.5  — 2-button footer: large Continue + small "Different problem" link
 *   DX.6  — Different problem opens structured picker modal (DiagnosisFeedbackModal)
 *   DX.7  — Animated checkmark on fault name mount
 *   DX.8  — Share icon top-right corner
 *   DX.9  — "..." menu top-right (Cancel diagnosis / Start over)
 *   DX.10 — Self-graduating Repair Plan (< 20 diagnoses: all 3; >= 20: only recommended)
 *   DX.11 — Self-graduating Continue label (sessions 1-3: "Continue to Estimate →"; after: "Continue →")
 *
 * Used in two modes:
 *   "authenticated" — shows customer info + action buttons
 *   "public"        — hides PII + hides action buttons; shown at /d/[share_token]
 */

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { detectMarket } from "@/lib/market";
import { trackEvent } from "@/lib/tracking";
import { apiFetch } from "@/lib/api";
import DiagnosisFeedbackModal from "@/components/DiagnosisFeedbackModal";
import {
  incrementDiagnosesOpened,
  getDiagnosesOpenedCount,
  getSessionCount,
} from "@/lib/userSessionCounter";
import { tierLabelForUnit } from "@/lib/tier-labels";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface RepairPlanTier {
  key: "A" | "B" | "C";
  name: string;
  total: number;
  line_items: Array<{ description: string; amount: number; category: string }>;
  recommended: boolean;
}

/** Stage 3C — one weighted factor in the shadow replace-score breakdown. */
export interface ShadowScoreFactor {
  name: string;
  weight: number;        // 0–1 weight of this factor
  value: number;         // 0–1 normalized factor value
  contribution: number;  // weight * value
  label?: string;        // human-readable explanation
}

/** Stage 3C — shadow replace-score breakdown (backend Stage 4; optional/forward-compatible). */
export interface ShadowReplaceScore {
  total: number;                 // 0–1 weighted replacement score
  formula?: string;              // "Show the math" formula text
  factors: ShadowScoreFactor[];  // the five weighted-score factors
}

/** Stage 3C — recommendation metadata surfaced from the fault-card estimate response. */
export interface RecommendationMeta {
  recommended_tier?: string;
  reasoning?: string;
  age_source?: string | null;
  age_confidence?: string | null;
  reliable_age?: boolean;
  requires_user_chooser?: boolean;
  /** Estimated install year + source label for the "Why this recommendation?" panel. */
  estimated_install_year?: number | null;
  /** Expected remaining-life BAND — render as a range, NEVER year-exact. */
  remaining_life_band?: string | null;
  refrigerant?: string | null;
  /** Whether the refrigerant is 2025+ A2L-compatible (R-454B / R-32). */
  refrigerant_2025_compatible?: boolean | null;
  shadow_replace_score?: ShadowReplaceScore | null;
}

export interface RepairPlan {
  recommended_tier: "A" | "B" | "C";
  tiers: RepairPlanTier[];
  /** Stage 3C — true when we recommend replacement on unconfirmed age. */
  requires_user_chooser?: boolean;
  /** Stage 3C — unit age in years (drives the "X+ years old" banner copy). */
  unit_age_years?: number | null;
  /** Stage 3C — recommendation + show-the-math metadata. */
  recommendation?: RecommendationMeta | null;
}

export interface DiagnosticResult {
  session_id: string;
  assessment_id?: string;
  fault: {
    card_id: number;
    name: string;
    confidence: "high" | "medium" | "low";
  };
  reasoning_chain: string[];
  action_steps: string[];
  parts_needed: string[];
  time_estimate_minutes: number | null;
  common_cause_climate: string | null;
  photo_evidence: { url: string; label?: string }[];
  alternative_diagnoses: { name: string; confidence: string }[];
  customer: { label: string | null; address: string | null };
  share_url: string;
  created_at?: string | null;
  repair_plan?: RepairPlan | null;
}

interface Props {
  data: DiagnosticResult;
  mode?: "authenticated" | "public";
  /** Unit age in years for context-aware tier labels. Optional — diagnostic API may omit it. */
  unitAgeYears?: number | null;
}

// ── Confidence badge ──────────────────────────────────────────────────────────

const CONFIDENCE: Record<string, { bg: string; text: string; label: string }> = {
  high:   { bg: "rgba(22,163,74,.12)",  text: "#16a34a", label: "High Confidence" },
  medium: { bg: "rgba(217,119,6,.12)",  text: "#d97706", label: "Medium Confidence" },
  low:    { bg: "rgba(220,38,38,.12)",  text: "#dc2626", label: "Low Confidence" },
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(n: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);
}

const TIER_LABEL: Record<string, "good" | "better" | "best"> = { A: "good", B: "better", C: "best" };

// ── Component ─────────────────────────────────────────────────────────────────

export default function FaultResolutionScreen({ data, mode = "authenticated", unitAgeYears }: Props) {
  const market   = detectMarket();
  const isPublic = mode === "public";
  const conf     = CONFIDENCE[data.fault.confidence] ?? CONFIDENCE.high;

  const router = useRouter();
  const { getToken } = useAuth();

  // Core state
  const [feedback, setFeedback]           = useState<"different_fault" | null>(null);
  const [showModal, setShowModal]          = useState(false);
  const [copied, setCopied]               = useState(false);
  const [navigating, setNavigating]       = useState(false);
  const mountTime                          = useRef(Date.now());

  // DX.7 — animated checkmark
  const [checkVisible, setCheckVisible]   = useState(false);

  // DX.8/9 — share + menu
  const [menuOpen, setMenuOpen]           = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [showRestartConfirm, setShowRestartConfirm] = useState(false);
  const [cancelling, setCancelling]       = useState(false);
  const menuRef                            = useRef<HTMLDivElement>(null);

  // DX.10 — self-graduating Repair Plan
  const [showOtherTiers, setShowOtherTiers] = useState(false);
  const [expandedTiers, setExpandedTiers]   = useState<Set<string>>(new Set(["B"]));

  // DX.4 — reasoning modal
  const [showReasoning, setShowReasoning]  = useState(false);

  // DX.10/11 — localStorage counters (read once, SSR-safe)
  const diagCount    = typeof window !== "undefined" ? getDiagnosesOpenedCount() : 0;
  const sessionCount = typeof window !== "undefined" ? getSessionCount() : 0;
  const showAllTiers = diagCount < 20;
  const continueLabel = sessionCount <= 3 ? "Continue to Estimate →" : "Continue →";

  const hasPhoto   = data.photo_evidence.length > 0;
  const hasClimate = market === "PK" && !!data.common_cause_climate;
  const hasAlts    = data.alternative_diagnoses.length > 0;

  // Repair Plan data (recommended tier first)
  const repairPlan = data.repair_plan ?? null;
  const recTier    = repairPlan?.recommended_tier ?? "B";
  const allTiers   = repairPlan?.tiers ?? [];
  const orderedTiers: RepairPlanTier[] = [
    ...allTiers.filter(t => t.key === recTier),
    ...allTiers.filter(t => t.key !== recTier),
  ];

  // ── Stage 3C: chooser-gate banner + "Why this recommendation?" panel ────────
  const requiresChooser = !!repairPlan?.requires_user_chooser;
  const recMeta = repairPlan?.recommendation ?? null;
  const unitAge = repairPlan?.unit_age_years ?? unitAgeYears ?? null;
  // When the user overrides the replacement recommendation, reveal the Repair tier
  // as if age <= 8 (show repair-first option).
  const [repairFirstRevealed, setRepairFirstRevealed] = useState(false);
  // Collapsible "Why this recommendation?" panel + "Show the math" sub-toggle.
  const [whyOpen, setWhyOpen] = useState(false);
  const [showMath, setShowMath] = useState(false);
  const whyPanelRef = useRef<HTMLDivElement>(null);

  function handleShowRepairFirst() {
    setRepairFirstRevealed(true);
    trackEvent("replacement_recommendation_overridden_by_user", {
      session_id: data.session_id,
      unit_age_years: unitAge,
      recommended_tier: recTier,
    });
  }

  // ── Effects ──────────────────────────────────────────────────────────────

  // DX.7: animate checkmark after first paint
  useEffect(() => {
    const t = setTimeout(() => setCheckVisible(true), 80);
    return () => clearTimeout(t);
  }, []);

  // Tracking + counter increment on mount
  useEffect(() => {
    trackEvent("fault_screen_opened", {
      session_id: data.session_id,
      mode,
      confidence: data.fault.confidence,
    });
    if (!isPublic) {
      incrementDiagnosesOpened();
    }
    return () => {
      const seconds = Math.round((Date.now() - mountTime.current) / 1000);
      trackEvent("fault_screen_time_on_screen", { session_id: data.session_id, seconds });
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // DX.9: close menu when clicking outside
  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [menuOpen]);

  // ── Handlers ─────────────────────────────────────────────────────────────

  async function handleContinue() {
    if (!data.assessment_id || navigating) return;
    setNavigating(true);
    const variant = sessionCount <= 3 ? "with_destination" : "short";
    trackEvent("fault_screen_estimate_generated", {
      session_id: data.session_id,
      label_variant: variant,
    });
    try {
      const token = await getToken();
      // Stage 3A: forward install-year + age confidence/source captured on the
      // review screen (StepZeroPanel stashes it in sessionStorage on confirm).
      let ageCapture: Record<string, unknown> = {};
      try {
        const raw = typeof window !== "undefined" ? sessionStorage.getItem("snap_age_capture") : null;
        if (raw) {
          const parsed = JSON.parse(raw) as { install_year?: number | null; age_source?: string | null; age_confidence?: string | null };
          if (parsed.install_year != null) ageCapture.install_year = parsed.install_year;
          if (parsed.age_source) ageCapture.age_source = parsed.age_source;
          if (parsed.age_confidence) ageCapture.age_confidence = parsed.age_confidence;
        }
      } catch { /* sessionStorage unavailable — non-fatal */ }
      const est = await apiFetch<{ id: string }>("/api/estimates/fault-card", {
        method: "POST",
        token: token ?? undefined,
        body: JSON.stringify({
          card_id: data.fault.card_id,
          assessment_id: data.assessment_id,
          ...ageCapture,
        }),
      });
      if (!est.id) throw new Error("No estimate ID");
      router.push(`/assessment/${est.id}`);
    } catch (err) {
      console.error("Estimate creation failed:", err);
      setNavigating(false);
    }
  }

  function handleDifferentFault() {
    setShowModal(true);
  }

  function handleModalClose(result?: { alternativeFaultId: number | null; text: string | null }) {
    setShowModal(false);
    if (result !== undefined) {
      setFeedback("different_fault");
    }
  }

  function handleShareClick() {
    trackEvent("fault_screen_share_clicked", { session_id: data.session_id });
    if (data.share_url) {
      navigator.clipboard.writeText(data.share_url).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }).catch(() => {});
    }
  }

  function toggleTier(key: string) {
    setExpandedTiers(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
        const label = TIER_LABEL[key];
        if (label) trackEvent("repair_plan_tier_expanded", { session_id: data.session_id, tier: label });
      }
      return next;
    });
  }

  async function handleCancelDiagnosis() {
    if (cancelling) return;
    setCancelling(true);
    trackEvent("diagnosis_cancelled", { session_id: data.session_id });
    try {
      const token = await getToken();
      await apiFetch(`/api/diagnostic/session/${data.session_id}/cancel`, {
        method: "PATCH",
        token: token ?? undefined,
      });
    } catch {
      // best-effort; navigate regardless
    }
    router.push("/diagnoses");
  }

  function handleStartOver() {
    trackEvent("diagnosis_restarted", { session_id: data.session_id });
    const url = data.assessment_id
      ? `/assess?assessment_id=${data.assessment_id}`
      : "/assess";
    router.push(url);
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div style={{ maxWidth: 672, margin: "0 auto", padding: "16px", display: "flex", flexDirection: "column", gap: 16, position: "relative" }}>

      {/* Keyframe style for animated checkmark (DX.7) */}
      <style>{`
        @keyframes snapcheck {
          0%   { opacity: 0; transform: scale(0.4); }
          60%  { transform: scale(1.18); }
          100% { opacity: 1; transform: scale(1); }
        }
        .snap-check-icon { animation: snapcheck 0.32s ease-out forwards; }
      `}</style>

      {/* ── Top-right corner: Share + ... menu (DX.8, DX.9) ── */}
      {!isPublic && (
        <div style={{ position: "absolute", top: 16, right: 16, display: "flex", gap: 4, zIndex: 10 }}>
          {/* Share icon (DX.8) */}
          <button
            onClick={handleShareClick}
            title="Copy share link"
            style={{
              width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center",
              background: "none", border: "none", cursor: "pointer", borderRadius: 8,
              color: copied ? "#16a34a" : "#475569",
            }}
          >
            {/* Share2 icon SVG */}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
          </button>

          {/* ... menu (DX.9) */}
          <div ref={menuRef} style={{ position: "relative" }}>
            <button
              onClick={() => setMenuOpen(o => !o)}
              title="More options"
              style={{
                width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center",
                background: menuOpen ? "#f1f5f9" : "none", border: "none", cursor: "pointer", borderRadius: 8,
                color: "#475569",
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="5" r="1.5" fill="currentColor"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/><circle cx="12" cy="19" r="1.5" fill="currentColor"/>
              </svg>
            </button>
            {menuOpen && (
              <div style={{
                position: "absolute", top: "100%", right: 0, marginTop: 4,
                background: "#fff", borderRadius: 10, border: "1px solid #e2e8f0",
                boxShadow: "0 4px 16px rgba(0,0,0,.10)", minWidth: 200, overflow: "hidden", zIndex: 100,
              }}>
                <button
                  onClick={() => { setMenuOpen(false); setShowCancelConfirm(true); }}
                  style={{
                    width: "100%", padding: "12px 16px", textAlign: "left", background: "none",
                    border: "none", cursor: "pointer", fontSize: 14, color: "#dc2626", fontWeight: 500,
                  }}
                >
                  Cancel diagnosis
                </button>
                <div style={{ height: 1, background: "#f1f5f9" }} />
                <button
                  onClick={() => { setMenuOpen(false); setShowRestartConfirm(true); }}
                  style={{
                    width: "100%", padding: "12px 16px", textAlign: "left", background: "none",
                    border: "none", cursor: "pointer", fontSize: 14, color: "#334155",
                  }}
                >
                  Start over
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Fault name + confidence + animated checkmark (DX.7) ── */}
      <div style={{ paddingRight: !isPublic ? 96 : 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 4 }}>
          {/* Animated checkmark (DX.7) */}
          {!isPublic && checkVisible && (
            <span
              className="snap-check-icon"
              style={{ color: "#16a34a", fontSize: 22, lineHeight: 1, flexShrink: 0 }}
            >
              ✓
            </span>
          )}
          <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: "#0f172a", lineHeight: 1.25 }}>
            {data.fault.name}
          </h1>
          <span style={{
            padding: "3px 10px", borderRadius: 99, fontSize: 12, fontWeight: 600,
            background: conf.bg, color: conf.text, whiteSpace: "nowrap",
          }}>
            {conf.label}
          </span>
        </div>

        {/* DX.4: customer info → 12px gray subtitle */}
        {!isPublic && (data.customer.label || data.customer.address) && (
          <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 2 }}>
            {[data.customer.label, data.customer.address].filter(Boolean).join(" · ")}
          </div>
        )}
      </div>

      {/* ── Layer-4 in-app decision-support disclaimer (always visible, both modes) ── */}
      <div
        role="note"
        style={{
          background: "#fffbeb",
          border: "1px solid #f59e0b",
          borderRadius: 8,
          padding: "12px 14px",
          fontSize: 13,
          lineHeight: 1.5,
          color: "#78350f",
        }}
      >
        <div style={{ fontWeight: 700, marginBottom: 4, color: "#92400e" }}>
          SnapAI recommendation only — NOT a certified diagnosis.
        </div>
        <div>
          This Output is a probabilistic recommendation. Verify all findings
          independently before acting. Do not present this Output to a Homeowner as
          a certified diagnosis.
        </div>
        {recTier === "C" && (
          <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #fcd34d" }}>
            This is a preliminary finding requiring independent Manual J load
            calculation and licensed inspection before any equipment replacement or
            major service recommendation is presented to the Homeowner.
          </div>
        )}
      </div>

      {/* ── Action steps ── */}
      {data.action_steps.length > 0 && (
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "14px 16px" }}>
          <div style={{ fontWeight: 600, marginBottom: 10, fontSize: 14, color: "#0f172a" }}>What to do</div>
          <ol style={{ margin: 0, paddingLeft: 20, display: "flex", flexDirection: "column", gap: 8 }}>
            {data.action_steps.map((step, i) => (
              <li key={i} style={{ fontSize: 14, color: "#334155", lineHeight: 1.5 }}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {/* DX.4: Parts + Time → merged single line ── */}
      {(data.parts_needed.length > 0 || data.time_estimate_minutes) && (
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "14px 16px" }}>
          <div style={{ fontWeight: 600, marginBottom: 6, fontSize: 14, color: "#0f172a" }}>Parts &amp; Time</div>
          <div style={{ fontSize: 14, color: "#334155" }}>
            {[
              data.parts_needed.join(", "),
              data.time_estimate_minutes ? `${data.time_estimate_minutes} min` : null,
            ].filter(Boolean).join(" · ")}
          </div>
        </div>
      )}

      {/* PK climate note — PK market only */}
      {hasClimate && (
        <div style={{ background: "#fffbeb", border: "1px solid #fbbf24", borderRadius: 8, padding: "12px 14px", fontSize: 13, color: "#92400e" }}>
          <strong>Common in this climate: </strong>{data.common_cause_climate}
        </div>
      )}

      {/* Photo evidence — hero photo */}
      {hasPhoto && (
        <div style={{ borderRadius: 8, overflow: "hidden", border: "1px solid #e2e8f0" }}>
          <img
            src={data.photo_evidence[0].url}
            alt={data.photo_evidence[0].label ?? "Equipment photo"}
            style={{ width: "100%", display: "block", maxHeight: 280, objectFit: "cover" }}
          />
          {data.photo_evidence[0].label && (
            <div style={{ padding: "8px 12px", fontSize: 12, color: "#475569", background: "#f8fafc" }}>
              {data.photo_evidence[0].label}
            </div>
          )}
        </div>
      )}

      {/* DX.4: Alternative diagnoses — collapsed link when medium/low confidence ── */}
      {hasAlts && data.fault.confidence !== "high" && (
        <details style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 14px" }}>
          <summary style={{ cursor: "pointer", fontSize: 13, color: "#475569", userSelect: "none" }}>
            Show alternatives considered
          </summary>
          <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 6 }}>
            {data.alternative_diagnoses.map((alt, i) => {
              const altConf = CONFIDENCE[alt.confidence] ?? CONFIDENCE.low;
              return (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 13 }}>
                  <span style={{ color: "#334155" }}>{alt.name}</span>
                  <span style={{ padding: "2px 8px", borderRadius: 99, background: altConf.bg, color: altConf.text, fontSize: 11, fontWeight: 600 }}>
                    {altConf.label}
                  </span>
                </div>
              );
            })}
          </div>
        </details>
      )}

      {/* ── DX.3: Repair Plan section ── */}
      {repairPlan && orderedTiers.length > 0 && (
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, color: "#0f172a", marginBottom: 10 }}>
            What we&apos;d recommend doing
          </div>

          {/* ── Stage 3C: chooser-gate banner ──
              Shows when the backend recommends replacement on an UNCONFIRMED age.
              WCAG AA: #92400e text on #fffbeb bg (contrast > 4.5:1); not color-alone. */}
          {requiresChooser && !repairFirstRevealed && (
            <div
              data-testid="stage3-chooser-banner"
              style={{
                background: "#fffbeb", border: "1.5px solid #f59e0b", borderRadius: 10,
                padding: "12px 14px", marginBottom: 12, color: "#92400e",
              }}
            >
              <div style={{ fontSize: 13, lineHeight: 1.5, fontWeight: 600 }}>
                We&apos;re recommending replacement because we estimate this unit is{" "}
                {unitAge != null ? `${unitAge}+` : "8+"}{" "}years old. The age wasn&apos;t confirmed.
                See what we&apos;d recommend if the unit is newer.
              </div>
              <button
                onClick={handleShowRepairFirst}
                style={{
                  marginTop: 10, padding: "10px 14px", borderRadius: 8, border: "1.5px solid #92400e",
                  background: "#fff", color: "#92400e", fontSize: 13, fontWeight: 700,
                  cursor: "pointer", minHeight: 44, width: "100%",
                }}
              >
                Show repair-first option
              </button>
            </div>
          )}

          {/* Tiers to show based on self-graduating logic (DX.10).
              Stage 3C: when repairFirstRevealed, also surface the Repair tier (key "A")
              as if age <= 8. */}
          {(() => {
            let visible = showAllTiers ? orderedTiers : orderedTiers.filter(t => t.key === recTier);
            if (repairFirstRevealed) {
              const repairTier = orderedTiers.find(t => t.key === "A");
              if (repairTier && !visible.some(t => t.key === "A")) {
                visible = [repairTier, ...visible];
              }
            }
            return visible;
          })().map(tier => {
            const isExpanded    = expandedTiers.has(tier.key);
            const isRecommended = tier.key === recTier;
            const tierName      = tier.name || tierLabelForUnit(TIER_LABEL[tier.key], unitAgeYears);

            return (
              <div
                key={tier.key}
                style={{
                  border: isRecommended ? "2px solid #16a34a" : "1.5px solid #e2e8f0",
                  borderRadius: 10, marginBottom: 10, overflow: "hidden",
                  background: isRecommended ? "rgba(22,163,74,.03)" : "#fff",
                }}
              >
                {/* Card header — always visible, click to toggle */}
                <button
                  onClick={() => toggleTier(tier.key)}
                  style={{
                    width: "100%", padding: "12px 14px", textAlign: "left",
                    background: "none", border: "none", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontWeight: 700, fontSize: 14, color: "#0f172a" }}>{tierName}</span>
                    {isRecommended && (
                      <span style={{
                        background: "#16a34a", color: "#fff", fontSize: 10, fontWeight: 700,
                        padding: "2px 7px", borderRadius: 99, letterSpacing: "0.04em",
                      }}>
                        RECOMMENDED
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontWeight: 700, fontSize: 14, color: "#0f172a" }}>
                      {fmt(tier.total)}
                    </span>
                    <span style={{ fontSize: 16, color: "#94a3b8", transform: isExpanded ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>
                      &#8964;
                    </span>
                  </div>
                </button>

                {/* Expanded content */}
                {isExpanded && (
                  <div style={{ padding: "0 14px 14px", borderTop: "1px solid #f1f5f9" }}>
                    <ul style={{ margin: "10px 0 0 0", paddingLeft: 18, display: "flex", flexDirection: "column", gap: 4 }}>
                      {tier.line_items.map((item, i) => (
                        <li key={i} style={{ fontSize: 13, color: "#334155" }}>
                          {item.description}
                          {item.category === "parts" && (
                            <span style={{ fontSize: 12, color: "#475569" }}> — {fmt(item.amount)}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}

          {/* DX.10: "See other options" link when post-20-diagnoses */}
          {!showAllTiers && !showOtherTiers && (
            <button
              onClick={() => {
                setShowOtherTiers(true);
                trackEvent("repair_plan_see_other_options_clicked", { session_id: data.session_id });
              }}
              style={{ background: "none", border: "none", cursor: "pointer", fontSize: 13, color: "#2563eb", padding: "4px 0", textDecoration: "underline" }}
            >
              See other options
            </button>
          )}

          {/* Show non-recommended tiers when expanded */}
          {!showAllTiers && showOtherTiers && orderedTiers.filter(t => t.key !== recTier).map(tier => {
            const isExpanded = expandedTiers.has(tier.key);
            const tierName   = tier.name || tierLabelForUnit(TIER_LABEL[tier.key], unitAgeYears);
            return (
              <div
                key={tier.key}
                style={{ border: "1.5px solid #e2e8f0", borderRadius: 10, marginBottom: 10, overflow: "hidden" }}
              >
                <button
                  onClick={() => toggleTier(tier.key)}
                  style={{
                    width: "100%", padding: "12px 14px", textAlign: "left",
                    background: "none", border: "none", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                  }}
                >
                  <span style={{ fontWeight: 700, fontSize: 14, color: "#0f172a" }}>{tierName}</span>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontWeight: 700, fontSize: 14 }}>{fmt(tier.total)}</span>
                    <span style={{ fontSize: 16, color: "#94a3b8", transform: isExpanded ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>&#8964;</span>
                  </div>
                </button>
                {isExpanded && (
                  <div style={{ padding: "0 14px 14px", borderTop: "1px solid #f1f5f9" }}>
                    <ul style={{ margin: "10px 0 0 0", paddingLeft: 18, display: "flex", flexDirection: "column", gap: 4 }}>
                      {tier.line_items.map((item, i) => (
                        <li key={i} style={{ fontSize: 13, color: "#334155" }}>
                          {item.description}
                          {item.category === "parts" && (
                            <span style={{ fontSize: 12, color: "#475569" }}> — {fmt(item.amount)}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}

          {/* ── Stage 3C: "Why this recommendation?" collapsible panel ──
              Lifespans render as BANDS, never year-exact. */}
          {recMeta && (
            <div style={{ marginTop: 12 }}>
              <button
                onClick={() => setWhyOpen(o => !o)}
                aria-expanded={whyOpen}
                aria-controls="why-rec-panel"
                style={{
                  width: "100%", textAlign: "left", background: "#f8fafc",
                  border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 14px",
                  cursor: "pointer", fontSize: 13, fontWeight: 700, color: "#0f172a",
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  minHeight: 44,
                }}
              >
                Why this recommendation?
                <span style={{ fontSize: 16, color: "#475569", transform: whyOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>
                  &#8964;
                </span>
              </button>

              {whyOpen && (
                <div
                  id="why-rec-panel"
                  ref={whyPanelRef}
                  style={{
                    border: "1px solid #e2e8f0", borderTop: "none",
                    borderRadius: "0 0 8px 8px", padding: "12px 14px",
                    display: "flex", flexDirection: "column", gap: 8, fontSize: 13, color: "#334155",
                  }}
                >
                  {/* Estimated install year + source label */}
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                    <span style={{ color: "#475569" }}>Estimated install year</span>
                    <span style={{ fontWeight: 600 }}>
                      {recMeta.estimated_install_year ?? "—"}
                      {recMeta.age_source ? ` (${recMeta.age_source.replace(/_/g, " ")})` : ""}
                    </span>
                  </div>

                  {/* Confidence label */}
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                    <span style={{ color: "#475569" }}>Age confidence</span>
                    <span style={{ fontWeight: 600, textTransform: "capitalize" }}>
                      {recMeta.age_confidence ?? "unknown"}
                    </span>
                  </div>

                  {/* Expected remaining-life BAND — range, never year-exact */}
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                    <span style={{ color: "#475569" }}>Expected remaining life</span>
                    <span style={{ fontWeight: 600 }}>{recMeta.remaining_life_band ?? "—"}</span>
                  </div>

                  {/* Refrigerant + 2025+ compatibility */}
                  {recMeta.refrigerant && (
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                      <span style={{ color: "#475569" }}>Refrigerant</span>
                      <span style={{ fontWeight: 600 }}>
                        {recMeta.refrigerant}
                        {recMeta.refrigerant_2025_compatible === true && " · 2025+ compatible"}
                        {recMeta.refrigerant_2025_compatible === false && " · not 2025+ compatible"}
                      </span>
                    </div>
                  )}

                  {/* Five weighted-score factors + contributions */}
                  {recMeta.shadow_replace_score && recMeta.shadow_replace_score.factors.length > 0 && (
                    <div style={{ marginTop: 4, borderTop: "1px solid #f1f5f9", paddingTop: 8 }}>
                      <div style={{ fontWeight: 700, fontSize: 12, color: "#0f172a", marginBottom: 6 }}>
                        Replacement-score factors
                      </div>
                      {recMeta.shadow_replace_score.factors.map((f, i) => (
                        <div key={i} style={{ display: "flex", justifyContent: "space-between", gap: 8, padding: "2px 0" }}>
                          <span style={{ color: "#475569" }}>{f.label || f.name}</span>
                          <span style={{ fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
                            +{(f.contribution).toFixed(2)} <span style={{ color: "#475569", fontWeight: 400 }}>(w {f.weight.toFixed(2)})</span>
                          </span>
                        </div>
                      ))}
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginTop: 4, fontWeight: 700, color: "#0f172a" }}>
                        <span>Total replace score</span>
                        <span style={{ fontVariantNumeric: "tabular-nums" }}>{recMeta.shadow_replace_score.total.toFixed(2)}</span>
                      </div>

                      {/* "Show the math" sub-toggle — expands the formula text */}
                      {recMeta.shadow_replace_score.formula && (
                        <>
                          <button
                            onClick={() => setShowMath(m => !m)}
                            aria-expanded={showMath}
                            style={{
                              marginTop: 8, background: "none", border: "none", cursor: "pointer",
                              fontSize: 12, color: "#2563eb", padding: "4px 0", textDecoration: "underline",
                            }}
                          >
                            {showMath ? "Hide the math" : "Show the math"}
                          </button>
                          {showMath && (
                            <pre style={{
                              marginTop: 6, whiteSpace: "pre-wrap", wordBreak: "break-word",
                              fontSize: 11, color: "#475569", background: "#f8fafc",
                              border: "1px solid #e2e8f0", borderRadius: 6, padding: "8px 10px",
                              fontFamily: "ui-monospace, monospace",
                            }}>
                              {recMeta.shadow_replace_score.formula}
                            </pre>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── DX.5: 2-button footer — Continue (primary) + Different problem (link) ── */}
      {!isPublic && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 4 }}>
          {/* Primary: Continue button -- hidden for screening-only #24 (Alfred C1: no estimate reachable) */}
          {data.fault.card_id === 24 ? (
            <div style={{
              width: "100%", padding: "13px 14px", borderRadius: 8,
              background: "#f8fafc", border: "1px solid #e2e8f0",
              color: "#475569", fontSize: 14, textAlign: "center", lineHeight: 1.4,
            }}>
              Screening finding - a Manual J load calculation is recommended before any repair or replacement estimate.
            </div>
          ) : (
          <button
            onClick={handleContinue}
            disabled={navigating || !data.assessment_id}
            style={{
              width: "100%", padding: "15px 0", borderRadius: 8, border: "none",
              background: (navigating || !data.assessment_id) ? "#86efac" : "#16a34a",
              color: "#fff", fontSize: 16, fontWeight: 700,
              cursor: (navigating || !data.assessment_id) ? "not-allowed" : "pointer",
              minHeight: 48,
            }}
          >
            {navigating ? "Opening…" : continueLabel}
          </button>
          )}

          {/* Secondary: Different problem link */}
          {feedback === null ? (
            <button
              onClick={handleDifferentFault}
              style={{
                background: "none", border: "none", cursor: "pointer",
                fontSize: 14, color: "#475569", textAlign: "center", padding: "6px 0",
                textDecoration: "underline",
              }}
            >
              Different problem
            </button>
          ) : (
            <div style={{ fontSize: 14, color: "#16a34a", textAlign: "center", fontWeight: 600, padding: "6px 0" }}>
              Feedback recorded ✓
            </div>
          )}
        </div>
      )}

      {/* Public mode footer */}
      {isPublic && (
        <div style={{ textAlign: "center", fontSize: 12, color: "#94a3b8", marginTop: 8 }}>
          Built with <strong style={{ color: "#475569" }}>SnapAI</strong>
        </div>
      )}

      {/* Watermark */}
      <div style={{ textAlign: "center", fontSize: 11, color: "#cbd5e1", wordBreak: "break-all" }}>
        SnapAI &middot; {data.share_url || "snapai.mainnov.tech"}
      </div>

      {/* DX.4: "How we got here →" link at very bottom */}
      {data.reasoning_chain.length > 0 && (
        <button
          onClick={() => setShowReasoning(true)}
          style={{
            background: "none", border: "none", cursor: "pointer",
            fontSize: 11, color: "#94a3b8", textAlign: "center", padding: "2px 0",
            textDecoration: "underline",
          }}
        >
          How we got here &rarr;
        </button>
      )}

      {/* ── Reasoning chain modal (DX.4) ── */}
      {showReasoning && (
        <div
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
            display: "flex", alignItems: "flex-end", justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={() => setShowReasoning(false)}
        >
          <div
            style={{
              background: "#fff", borderRadius: "16px 16px 0 0", width: "100%",
              maxWidth: 540, padding: "24px 20px 32px", maxHeight: "70vh", overflowY: "auto",
              boxShadow: "0 -4px 24px rgba(0,0,0,.12)",
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 14, color: "#0f172a" }}>How we got here</div>
            <ol style={{ margin: 0, paddingLeft: 20, display: "flex", flexDirection: "column", gap: 6 }}>
              {data.reasoning_chain.map((r, i) => (
                <li key={i} style={{ fontSize: 13, color: "#475569", lineHeight: 1.5 }}>{r}</li>
              ))}
            </ol>
            <button
              onClick={() => setShowReasoning(false)}
              style={{
                marginTop: 20, width: "100%", padding: "12px", borderRadius: 8,
                border: "1.5px solid #e2e8f0", background: "#fff",
                fontSize: 14, fontWeight: 600, color: "#475569", cursor: "pointer",
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* ── DX.9: Cancel diagnosis confirm ── */}
      {showCancelConfirm && (
        <div
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 1000, padding: "0 20px",
          }}
        >
          <div style={{
            background: "#fff", borderRadius: 14, padding: "24px 20px",
            maxWidth: 360, width: "100%", boxShadow: "0 8px 32px rgba(0,0,0,.15)",
          }}>
            <div style={{ fontWeight: 700, fontSize: 16, color: "#0f172a", marginBottom: 8 }}>
              Cancel this diagnosis?
            </div>
            <div style={{ fontSize: 13, color: "#475569", marginBottom: 20, lineHeight: 1.5 }}>
              It will be marked as cancelled and won&apos;t appear in your active assessments.
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <button
                onClick={() => setShowCancelConfirm(false)}
                style={{
                  flex: 1, padding: "12px 0", borderRadius: 8,
                  border: "1.5px solid #e2e8f0", background: "#fff",
                  fontSize: 14, fontWeight: 600, color: "#475569", cursor: "pointer",
                }}
              >
                Keep
              </button>
              <button
                onClick={handleCancelDiagnosis}
                disabled={cancelling}
                style={{
                  flex: 1, padding: "12px 0", borderRadius: 8, border: "none",
                  background: cancelling ? "#fca5a5" : "#dc2626",
                  color: "#fff", fontSize: 14, fontWeight: 700, cursor: cancelling ? "not-allowed" : "pointer",
                }}
              >
                {cancelling ? "Cancelling…" : "Cancel diagnosis"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── DX.9: Start over confirm ── */}
      {showRestartConfirm && (
        <div
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)",
            display: "flex", alignItems: "center", justifyContent: "center",
            zIndex: 1000, padding: "0 20px",
          }}
        >
          <div style={{
            background: "#fff", borderRadius: 14, padding: "24px 20px",
            maxWidth: 360, width: "100%", boxShadow: "0 8px 32px rgba(0,0,0,.15)",
          }}>
            <div style={{ fontWeight: 700, fontSize: 16, color: "#0f172a", marginBottom: 8 }}>
              Start over?
            </div>
            <div style={{ fontSize: 13, color: "#475569", marginBottom: 20, lineHeight: 1.5 }}>
              Start the diagnostic over from the beginning?
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <button
                onClick={() => setShowRestartConfirm(false)}
                style={{
                  flex: 1, padding: "12px 0", borderRadius: 8,
                  border: "1.5px solid #e2e8f0", background: "#fff",
                  fontSize: 14, fontWeight: 600, color: "#475569", cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleStartOver}
                style={{
                  flex: 1, padding: "12px 0", borderRadius: 8, border: "none",
                  background: "#0f172a", color: "#fff",
                  fontSize: 14, fontWeight: 700, cursor: "pointer",
                }}
              >
                Start over
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DX.6: Structured feedback modal */}
      {showModal && (
        <DiagnosisFeedbackModal
          sessionId={data.session_id}
          onClose={handleModalClose}
        />
      )}

    </div>
  );
}
