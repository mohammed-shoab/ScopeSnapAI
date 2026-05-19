"use client";

/**
 * FaultResolutionScreen — Track D
 * The diagnosis-screen hero. Renders fault verdict, action steps, parts needed,
 * confidence badge, PK climate note, reasoning chain, feedback buttons.
 *
 * Used in two modes:
 *   "authenticated" — shows customer banner + Mark-as-Solved / Different-fault-found
 *   "public"        — hides PII + hides action buttons; shown at /d/[share_token]
 */

import { useState, useEffect, useRef } from "react";
import { detectMarket } from "@/lib/market";
import { trackEvent } from "@/lib/tracking";
import { apiFetch } from "@/lib/api";
import DiagnosisFeedbackModal from "@/components/DiagnosisFeedbackModal";

// ── Types ─────────────────────────────────────────────────────────────────────

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
}

interface Props {
  data: DiagnosticResult;
  mode?: "authenticated" | "public";
}

// ── Confidence badge ──────────────────────────────────────────────────────────

const CONFIDENCE: Record<string, { bg: string; text: string; label: string }> = {
  high:   { bg: "rgba(22,163,74,.12)",  text: "#16a34a", label: "High Confidence" },
  medium: { bg: "rgba(217,119,6,.12)",  text: "#d97706", label: "Medium Confidence" },
  low:    { bg: "rgba(220,38,38,.12)",  text: "#dc2626", label: "Low Confidence" },
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function FaultResolutionScreen({ data, mode = "authenticated" }: Props) {
  const market = detectMarket();
  const isPublic = mode === "public";
  const conf = CONFIDENCE[data.fault.confidence] ?? CONFIDENCE.high;

  const [feedback, setFeedback] = useState<"solved" | "different_fault" | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [copied, setCopied] = useState(false);
  const [reasoningOpen, setReasoningOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const mountTime = useRef(Date.now());

  // Stack feedback buttons vertically on screens narrower than 480px
  useEffect(() => {
    function checkWidth() { setIsMobile(window.innerWidth < 480); }
    checkWidth();
    window.addEventListener("resize", checkWidth);
    return () => window.removeEventListener("resize", checkWidth);
  }, []);

  // D.13: fault_screen_opened on mount; fault_screen_time_on_screen on unmount
  useEffect(() => {
    trackEvent("fault_screen_opened", {
      session_id: data.session_id,
      mode,
      confidence: data.fault.confidence,
    });
    return () => {
      const seconds = Math.round((Date.now() - mountTime.current) / 1000);
      trackEvent("fault_screen_time_on_screen", { session_id: data.session_id, seconds });
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleMarkSolved() {
    setFeedback("solved");
    trackEvent("fault_screen_agreement", {
      session_id: data.session_id,
      agreement: "solved",
      has_text: false,
    });
    // Fire-and-forget — uses apiFetch so auth headers are injected automatically
    apiFetch("/api/diagnostic/feedback", {
      method: "POST",
      body: JSON.stringify({ session_id: data.session_id, agreement: "solved" }),
    }).catch(() => {});
  }

  function handleDifferentFault() {
    setShowModal(true);
  }

  function handleModalClose(submittedText?: string) {
    setShowModal(false);
    if (submittedText !== undefined) {
      setFeedback("different_fault");
      trackEvent("fault_screen_agreement", {
        session_id: data.session_id,
        agreement: "different_fault",
        has_text: submittedText.length > 0,
      });
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

  function handleReasoningToggle(open: boolean) {
    setReasoningOpen(open);
    if (open) {
      trackEvent("fault_screen_reasoning_expanded", { session_id: data.session_id });
    }
  }

  const hasPhoto = data.photo_evidence.length > 0;
  const hasClimate = market === "PK" && !!data.common_cause_climate;
  const hasAlts = data.alternative_diagnoses.length > 0;
  const showActionButtons = !isPublic && feedback === null;

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div style={{ maxWidth: 672, margin: "0 auto", padding: "16px", display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Customer banner — authenticated mode only */}
      {!isPublic && (data.customer.label || data.customer.address) && (
        <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#475569" }}>
          {data.customer.label && <div style={{ fontWeight: 600, color: "#1e293b" }}>{data.customer.label}</div>}
          {data.customer.address && <div>{data.customer.address}</div>}
        </div>
      )}

      {/* Fault name + confidence badge */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: "#0f172a", lineHeight: 1.2 }}>
          {data.fault.name}
        </h1>
        <span style={{
          padding: "3px 10px",
          borderRadius: 99,
          fontSize: 12,
          fontWeight: 600,
          background: conf.bg,
          color: conf.text,
          whiteSpace: "nowrap",
        }}>
          {conf.label}
        </span>
      </div>

      {/* Time estimate */}
      {data.time_estimate_minutes && (
        <div style={{ fontSize: 13, color: "#64748b" }}>
          Estimated time on job: <strong>{data.time_estimate_minutes} min</strong>
        </div>
      )}

      {/* Action steps */}
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

      {/* Parts needed */}
      {data.parts_needed.length > 0 && (
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "14px 16px" }}>
          <div style={{ fontWeight: 600, marginBottom: 10, fontSize: 14, color: "#0f172a" }}>Parts needed</div>
          <ul style={{ margin: 0, paddingLeft: 18, display: "flex", flexDirection: "column", gap: 6 }}>
            {data.parts_needed.map((part, i) => (
              <li key={i} style={{ fontSize: 14, color: "#334155" }}>{part}</li>
            ))}
          </ul>
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
            <div style={{ padding: "8px 12px", fontSize: 12, color: "#64748b", background: "#f8fafc" }}>
              {data.photo_evidence[0].label}
            </div>
          )}
        </div>
      )}

      {/* Alternative diagnoses — medium/low confidence only */}
      {hasAlts && data.fault.confidence !== "high" && (
        <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "14px 16px" }}>
          <div style={{ fontWeight: 600, marginBottom: 10, fontSize: 14, color: "#0f172a" }}>Other possibilities considered</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
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
        </div>
      )}

      {/* Reasoning chain — collapsed details */}
      <details
        open={reasoningOpen}
        onToggle={(e) => handleReasoningToggle((e.target as HTMLDetailsElement).open)}
        style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 14px" }}
      >
        <summary style={{ cursor: "pointer", fontSize: 13, fontWeight: 600, color: "#475569", userSelect: "none" }}>
          How we got here
        </summary>
        <ol style={{ margin: "10px 0 0 0", paddingLeft: 20, display: "flex", flexDirection: "column", gap: 4 }}>
          {data.reasoning_chain.map((r, i) => (
            <li key={i} style={{ fontSize: 12, color: "#64748b", lineHeight: 1.5 }}>{r}</li>
          ))}
        </ol>
      </details>

      {/* Mark as Solved / Different fault found — authenticated mode, before feedback */}
      {showActionButtons && (
        <div style={{ display: "flex", flexDirection: isMobile ? "column" : "row", gap: 10 }}>
          <button
            onClick={handleMarkSolved}
            style={{
              flex: 1, padding: "14px 0", borderRadius: 8, border: "none",
              background: "#16a34a", color: "#fff", fontSize: 15, fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Mark as Solved
          </button>
          <button
            onClick={handleDifferentFault}
            style={{
              flex: 1, padding: "14px 0", borderRadius: 8,
              border: "1.5px solid #94a3b8", background: "#fff",
              color: "#475569", fontSize: 15, fontWeight: 600, cursor: "pointer",
            }}
          >
            Different fault found
          </button>
        </div>
      )}

      {/* Post-feedback confirmation */}
      {feedback === "solved" && (
        <div style={{ background: "rgba(22,163,74,.08)", border: "1px solid #16a34a", borderRadius: 8, padding: "12px 16px", fontSize: 14, color: "#15803d", fontWeight: 600, textAlign: "center" }}>
          Marked as solved
        </div>
      )}
      {feedback === "different_fault" && (
        <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 16px", fontSize: 14, color: "#475569", textAlign: "center" }}>
          Feedback recorded
        </div>
      )}

      {/* Copy share link */}
      {data.share_url && (
        <button
          onClick={handleShareClick}
          style={{
            width: "100%", padding: "10px 0", background: "none",
            border: "none", color: copied ? "#16a34a" : "#2563eb",
            fontSize: 13, textDecoration: "underline", cursor: "pointer",
          }}
        >
          {copied ? "Link copied!" : "Copy share link"}
        </button>
      )}

      {/* Public mode footer */}
      {isPublic && (
        <div style={{ textAlign: "center", fontSize: 12, color: "#94a3b8", marginTop: 8 }}>
          Built with <strong style={{ color: "#64748b" }}>SnapAI</strong>
        </div>
      )}

      {/* Watermark */}
      <div style={{ textAlign: "center", fontSize: 11, color: "#cbd5e1", marginTop: 4, wordBreak: "break-all" }}>
        SnapAI &middot; {data.share_url || "snapai.mainnov.tech"}
      </div>

      {/* Different fault found — modal */}
      {showModal && (
        <DiagnosisFeedbackModal
          sessionId={data.session_id}
          onClose={handleModalClose}
        />
      )}

    </div>
  );
}
