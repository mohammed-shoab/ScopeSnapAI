"use client";
/**
 * PresentMode — RW-03
 * Full-screen 4-slide slideshow overlay for showing the homeowner.
 * Opens as an overlay (fixed inset-0 z-50) — no navigation away.
 * Slides: 1) Annotated Photo  2) Health Card  3) Options  4) 5-Year Value
 * Matches SnapAI_Prototype_Demo.html Present Mode screens.
 */

import { useState, useEffect, useCallback } from "react";
import { formatCurrency, detectMarket } from "@/lib/market";
import FiveYearComparison, { type TierTCO } from "@/components/FiveYearComparison";

// ─── Types ─────────────────────────────────────────────────────────────────
interface LineItem {
  category?: string;
  item_type?: string;
  description?: string;
  label?: string;
  labor_hours?: number;
  labor_rate?: number;
  parts_cost?: number;
  permit_cost?: number;
  disposal_cost?: number;
  total?: number;
  amount?: number;
}

interface EnergySavings {
  annual_savings: number;
  five_year_savings?: number;
}

interface Option {
  tier: string;
  name: string;
  description?: string;
  total: number;
  subtotal?: number;
  five_year_total?: number;
  five_year_comparison?: TierTCO | null;
  line_items?: LineItem[];
  energy_savings?: EnergySavings | number;
  job_type?: string;
}

interface EstimateData {
  id: string;
  report_short_id: string;
  options: Option[];
  markup_percent: number;
  assessment_id?: string;
}

interface PresentModeProps {
  estimate: EstimateData;
  selectedTier: string;
  onClose: () => void;
  onSelectTier: (tier: string) => void;
  /** Bug 3: real assessment photo for Slide 1 (falls back to SVG when absent). */
  photoUrl?: string;
  /** Bug 3: overall condition rating — drives the Slide 1 health badge. */
  conditionRating?: string;
}

// Level 2 "Why this matters" footers (Codie-authored, DEC-088 compliant).
// Canonical source — these are frontend-only and intentionally NOT duplicated
// in a backend JSON (avoids the two-sources-of-truth drift Rob flagged).
const PRESENT_FOOTERS = {
  repair: "Repairs address the diagnosed fault and return the system to working order. Your contractor can walk you through what each option includes.",
  replacement: "A new system runs at current efficiency standards. Your contractor installs it, registers it with the manufacturer, and configures it for your home.",
  default: "Each option below is priced for the work it includes. Compare them with your contractor and choose what fits your home and budget.",
};

// Map a condition string -> badge label + color (Bug 3).
function conditionBadge(rating?: string): { label: string; color: string } | null {
  if (!rating) return null;
  const r = rating.toLowerCase();
  if (r.includes("critical")) return { label: "CRITICAL", color: "#c62828" };
  if (r.includes("poor")) return { label: "POOR", color: "#c4600a" };
  if (r.includes("fair")) return { label: "FAIR", color: "#e6a817" };
  if (r.includes("good") || r.includes("excellent")) return { label: "GOOD", color: "#1a8754" };
  return null;
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function fmt(n?: number) {
  return formatCurrency(n);
}

function getAnnualSavings(opt: Option): number {
  if (!opt.energy_savings) return 0;
  if (typeof opt.energy_savings === "number") return opt.energy_savings;
  return (opt.energy_savings as EnergySavings).annual_savings || 0;
}

// Derive a health score 0-100 from the option condition / tier
function healthScore(options: Option[]): { score: number; label: string; color: string; years: string } {
  // Use selected option tier as proxy for condition severity
  const hasCritical = options.some(o => o.name?.toLowerCase().includes("critical") || o.description?.toLowerCase().includes("critical"));
  const hasPoor = options.some(o => o.name?.toLowerCase().includes("poor") || o.description?.toLowerCase().includes("poor"));
  if (hasCritical) return { score: 22, label: "CRITICAL", color: "#c62828", years: "1–2 years" };
  if (hasPoor) return { score: 42, label: "POOR", color: "#c4600a", years: "2–4 years" };
  // Default: fair
  return { score: 64, label: "FAIR", color: "#e6a817", years: "6–11 years" };
}

// Derive a short list of issues from the options' line items
function deriveIssues(options: Option[]): Array<{label: string; severity: "red"|"orange"|"yellow"}> {
  const issues: Array<{label: string; severity: "red"|"orange"|"yellow"}> = [];
  const seen = new Set<string>();
  for (const opt of options) {
    for (const item of (opt.line_items || [])) {
      const label = item.description || item.label || item.category || "";
      if (label && !seen.has(label)) {
        seen.add(label);
        const s = item.item_type === "labor" ? "orange" : item.category?.toLowerCase().includes("critical") ? "red" : "orange";
        issues.push({ label, severity: s });
      }
    }
    if (issues.length >= 4) break;
  }
  // Fallback if no line items
  if (issues.length === 0) {
    issues.push({ label: "Equipment needs attention", severity: "orange" });
  }
  return issues.slice(0, 4);
}

// ─── Health Gauge (SVG arc) ────────────────────────────────────────────────
function HealthGauge({ score, color, label }: { score: number; color: string; label: string }) {
  const r = 60;
  const cx = 80;
  const cy = 80;
  const strokeWidth = 12;
  const circumference = 2 * Math.PI * r;
  // We only use the top 270° of the circle (from -135° to +135°)
  const arcFraction = 0.75;
  const dashTotal = circumference * arcFraction;
  const dashFill = (score / 100) * dashTotal;

  return (
    <svg width="160" height="130" viewBox="0 0 160 130" className="mx-auto">
      {/* Background arc */}
      <circle
        cx={cx} cy={cy} r={r}
        fill="none"
        stroke="rgba(255,255,255,0.15)"
        strokeWidth={strokeWidth}
        strokeDasharray={`${dashTotal} ${circumference}`}
        strokeDashoffset={circumference * 0.125}
        strokeLinecap="round"
        transform={`rotate(-225 ${cx} ${cy})`}
      />
      {/* Filled arc */}
      <circle
        cx={cx} cy={cy} r={r}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={`${dashFill} ${circumference}`}
        strokeDashoffset={circumference * 0.125}
        strokeLinecap="round"
        transform={`rotate(-225 ${cx} ${cy})`}
        style={{ transition: "stroke-dasharray 0.8s ease" }}
      />
      {/* Label */}
      <text x={cx} y={cy - 4} textAnchor="middle" fill="white" fontSize="22" fontWeight="800" fontFamily="'IBM Plex Mono',monospace">
        {label}
      </text>
      <text x={cx} y={cy + 16} textAnchor="middle" fill="rgba(255,255,255,0.6)" fontSize="11" fontFamily="'Plus Jakarta Sans',sans-serif">
        Equipment Health
      </text>
    </svg>
  );
}

// ─── Slide 1 — Annotated Photo ─────────────────────────────────────────────
function Slide1Photo({ issues, photoUrl, badge, footer }: {
  issues: Array<{label: string; severity: "red"|"orange"|"yellow"}>;
  photoUrl?: string;
  badge?: { label: string; color: string } | null;
  footer?: string;
}) {
  const CALLOUT_POSITIONS = [
    { top: "18%", left: "15%" },
    { top: "22%", right: "12%" },
    { bottom: "30%", left: "18%" },
    { bottom: "32%", right: "14%" },
  ];
  const sevColor: Record<string, string> = { red: "#c62828", orange: "#c4600a", yellow: "#e6a817" };

  return (
    <div className="flex flex-col h-full">
      {/* Equipment visual area */}
      <div className="flex-1 relative flex items-center justify-center overflow-hidden"
        style={{ background: "linear-gradient(180deg,#0d0d0b 0%,#1a1a18 100%)" }}>

        {/* Health badge (Bug 3) */}
        {badge && (
          <div
            className="absolute top-3 right-3 z-10 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-full"
            style={{ background: badge.color, letterSpacing: "0.05em" }}
          >
            {badge.label}
          </div>
        )}

        {/* Bug 3: real assessment photo when available, else SVG placeholder */}
        {photoUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={photoUrl}
            alt="Assessed equipment"
            className="absolute inset-0 w-full h-full object-cover"
            style={{ opacity: 0.92 }}
          />
        ) : (
        <svg width="200" height="160" viewBox="0 0 200 160" fill="none" opacity="0.7">
          {/* AC unit outline */}
          <rect x="20" y="30" width="160" height="110" rx="8" stroke="#4a4a48" strokeWidth="2" fill="#2a2a28"/>
          <rect x="30" y="45" width="60" height="80" rx="4" stroke="#3a3a38" strokeWidth="1.5" fill="#222220"/>
          <rect x="105" y="45" width="60" height="80" rx="4" stroke="#3a3a38" strokeWidth="1.5" fill="#222220"/>
          {/* Fins */}
          {[50,60,70,80,90,100,110].map(y => (
            <line key={y} x1="30" y1={y} x2="90" y2={y} stroke="#3a3a38" strokeWidth="1"/>
          ))}
          {[50,60,70,80,90,100,110].map(y => (
            <line key={y} x1="105" y1={y} x2="165" y2={y} stroke="#3a3a38" strokeWidth="1"/>
          ))}
          {/* Fan circle */}
          <circle cx="100" cy="85" r="28" stroke="#4a4a48" strokeWidth="2" fill="#222220"/>
          <circle cx="100" cy="85" r="18" stroke="#3a3a38" strokeWidth="1" fill="none"/>
          <line x1="100" y1="67" x2="100" y2="103" stroke="#3a3a38" strokeWidth="1"/>
          <line x1="82" y1="85" x2="118" y2="85" stroke="#3a3a38" strokeWidth="1"/>
        </svg>
        )}

        {/* Animated callout dots */}
        {issues.slice(0, 4).map((issue, i) => {
          const pos = CALLOUT_POSITIONS[i] || CALLOUT_POSITIONS[0];
          return (
            <div
              key={i}
              className="absolute flex items-center gap-1.5"
              style={{ ...pos, animation: `fadeIn 0.4s ease ${i * 0.3 + 0.5}s both` }}
            >
              <div
                className="w-3.5 h-3.5 rounded-full border-2 border-white flex-shrink-0 animate-pulse"
                style={{ background: sevColor[issue.severity] }}
              />
              <span
                className="text-white text-[10px] font-bold px-2 py-0.5 rounded-full"
                style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(4px)", maxWidth: 100, lineHeight: 1.3 }}
              >
                {issue.label.length > 28 ? issue.label.slice(0, 27) + "…" : issue.label}
              </span>
            </div>
          );
        })}
        <style>{`@keyframes fadeIn { from{opacity:0;transform:scale(0.85)} to{opacity:1;transform:scale(1)} }`}</style>
      </div>

      {/* Bottom info */}
      <div className="px-6 py-5 space-y-1" style={{ background: "#0f0f0d" }}>
        <p className="text-white text-xs font-mono uppercase tracking-widest opacity-60">Equipment Diagnosis</p>
        <p className="text-white font-extrabold text-lg">
          {issues.length} issue{issues.length !== 1 ? "s" : ""} identified
        </p>
        <p className="text-white/50 text-xs">Swipe to see full breakdown →</p>
        {footer && (
          <p className="text-white/70 text-[11px] leading-snug pt-2 border-t border-white/10 mt-2">
            <span className="font-bold uppercase tracking-wide text-white/50">Why this matters: </span>
            {footer}
          </p>
        )}
      </div>
    </div>
  );
}

// ─── Slide 2 — Health Card ─────────────────────────────────────────────────
function Slide2Health({ estimate }: { estimate: EstimateData }) {
  const options = estimate.options || [];
  const hs = healthScore(options);
  const issues = deriveIssues(options);

  return (
    <div className="flex flex-col h-full px-6 py-8 space-y-6"
      style={{ background: "linear-gradient(160deg,#0f5c38 0%,#0a3d28 100%)" }}>

      {/* Equipment ID */}
      <div className="text-center">
        <p className="text-white/60 text-xs font-mono uppercase tracking-widest mb-1">Equipment</p>
        <p className="text-white font-extrabold text-xl tracking-tight">
          HVAC System
        </p>
        <p className="text-white/70 text-sm mt-1">Report {estimate.report_short_id}</p>
      </div>

      {/* Health gauge */}
      <div className="text-center">
        <HealthGauge score={hs.score} color={hs.color} label={hs.label} />
        <p className="text-white/60 text-sm mt-1">Est. {hs.years} remaining</p>
      </div>

      {/* Issue pills */}
      <div className="flex flex-wrap gap-2 justify-center">
        {issues.map((iss, i) => {
          const c: Record<string, string> = { red: "#c62828", orange: "#c4600a", yellow: "#e6a817" };
          return (
            <span
              key={i}
              className="text-xs font-semibold px-3 py-1 rounded-full text-white"
              style={{ background: `${c[iss.severity]}cc` }}
            >
              {iss.label.length > 22 ? iss.label.slice(0, 20) + "…" : iss.label}
            </span>
          );
        })}
      </div>
    </div>
  );
}

// ─── Slide 3 — Options Comparison ─────────────────────────────────────────
function Slide3Options({ estimate, selectedTier, onSelectTier }: {
  estimate: EstimateData;
  selectedTier: string;
  onSelectTier: (tier: string) => void;
}) {
  const options = estimate.options || [];
  const colors: Record<string, { border: string; badge: string; price: string }> = {
    good:   { border: "#6b7280", badge: "#6b7280", price: "#1a1a18" },
    better: { border: "#1a8754", badge: "#1a8754", price: "#1a8754" },
    best:   { border: "#1565c0", badge: "#1565c0", price: "#1565c0" },
  };
  const letters: Record<string, string> = { good: "A", better: "B", best: "C" };

  return (
    <div className="flex flex-col h-full px-5 py-6 space-y-4"
      style={{ background: "#1a1a18" }}>
      <div className="text-center">
        <p className="text-white/50 text-xs font-mono uppercase tracking-widest mb-1">Your Options</p>
        <p className="text-white font-extrabold text-xl">Choose Your Solution</p>
      </div>

      <div className="space-y-3 flex-1">
        {options.map((opt) => {
          const isSelected = selectedTier === opt.tier;
          const c = colors[opt.tier] || colors.good;
          return (
            <button
              key={opt.tier}
              onClick={() => onSelectTier(opt.tier)}
              className="w-full text-left p-4 rounded-2xl transition-all"
              style={{
                background: isSelected ? "white" : "rgba(255,255,255,0.06)",
                border: `2px solid ${isSelected ? c.border : "rgba(255,255,255,0.12)"}`,
                transform: isSelected ? "scale(1.02)" : "scale(1)",
              }}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="text-xs font-bold px-2 py-0.5 rounded-full text-white"
                      style={{ background: c.badge }}
                    >
                      Option {letters[opt.tier] || opt.tier.toUpperCase()}
                      {opt.tier === "better" && " ★"}
                    </span>
                    {opt.job_type && (
                      <span className="text-xs text-white/50" style={{ color: isSelected ? "#7a7770" : undefined }}>
                        {opt.job_type === "repair" ? "🔧 Repair" : "🔄 Replace"}
                      </span>
                    )}
                  </div>
                  <p className={`font-bold text-sm leading-tight ${isSelected ? "text-text-primary" : "text-white/90"}`}>
                    {opt.name}
                  </p>
                  {opt.description && (
                    <p className={`text-xs mt-0.5 leading-snug ${isSelected ? "text-text-secondary" : "text-white/50"}`}>
                      {opt.description}
                    </p>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xl font-extrabold font-mono" style={{ color: isSelected ? c.price : "white" }}>
                    {fmt(opt.total)}
                  </p>
                  {isSelected && <span className="text-brand-green text-xs font-bold">Selected ✓</span>}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <p className="text-center text-white/40 text-xs">Tap an option to select it</p>
    </div>
  );
}

// ─── Slide 4 — 5-Year Value (Track G) ──────────────────────────────────────
function Slide4Value({ estimate, selectedTier }: { estimate: EstimateData; selectedTier: string }) {
  const options = estimate.options || [];
  const market = detectMarket();
  const recommendedTier = (selectedTier as "A" | "B" | "C");

  return (
    <div className="flex flex-col h-full bg-white overflow-y-auto">
      <FiveYearComparison
        optionA={options.find((o) => o.tier === "A")?.five_year_comparison ?? null}
        optionB={options.find((o) => o.tier === "B")?.five_year_comparison ?? null}
        optionC={options.find((o) => o.tier === "C")?.five_year_comparison ?? null}
        recommendedTier={recommendedTier}
        market={market}
        mode="present_mode"
        sessionId={estimate.report_short_id}
      />
    </div>
  );
}

// ─── Main PresentMode Component ────────────────────────────────────────────
export default function PresentMode({ estimate, selectedTier, onClose, onSelectTier, photoUrl, conditionRating }: PresentModeProps) {
  const [slide, setSlide] = useState(0);
  const totalSlides = 4;

  // Swipe support
  const [touchStart, setTouchStart] = useState<number | null>(null);

  const next = useCallback(() => setSlide(s => Math.min(s + 1, totalSlides - 1)), []);
  const prev = useCallback(() => setSlide(s => Math.max(s - 1, 0)), []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") next();
      if (e.key === "ArrowLeft") prev();
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [next, prev, onClose]);

  const issues = deriveIssues(estimate.options || []);

  // Bug 3: health badge from condition; "Why this matters" footer by tier.
  const badge = conditionBadge(conditionRating)
    || { label: healthScore(estimate.options || []).label, color: healthScore(estimate.options || []).color };
  const selectedOpt = (estimate.options || []).find((o) => o.tier === selectedTier);
  const slide1Footer = selectedOpt
    ? (selectedOpt.tier === "C" ? PRESENT_FOOTERS.replacement : PRESENT_FOOTERS.repair)
    : PRESENT_FOOTERS.default;

  const SLIDES = [
    { title: "Diagnosis", component: <Slide1Photo issues={issues} photoUrl={photoUrl} badge={badge} footer={slide1Footer} /> },
    { title: "Health", component: <Slide2Health estimate={estimate} /> },
    { title: "Options", component: <Slide3Options estimate={estimate} selectedTier={selectedTier} onSelectTier={onSelectTier} /> },
    { title: "Value", component: <Slide4Value estimate={estimate} selectedTier={selectedTier} /> },
  ];

  return (
    <div
      className="fixed inset-0 z-[200] flex flex-col"
      style={{ background: "#0a0a08" }}
      onTouchStart={(e) => setTouchStart(e.touches[0].clientX)}
      onTouchEnd={(e) => {
        if (touchStart === null) return;
        const diff = touchStart - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) { diff > 0 ? next() : prev(); }
        setTouchStart(null);
      }}
    >
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 pt-safe pt-4 pb-3" style={{ background: "rgba(0,0,0,0.4)" }}>
        <button
          onClick={onClose}
          className="text-white/70 hover:text-white text-sm font-semibold flex items-center gap-1.5 transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
          Exit
        </button>

        <div className="flex gap-1.5">
          {SLIDES.map((_, i) => (
            <button key={i} onClick={() => setSlide(i)}>
              <div
                className="rounded-full transition-all duration-200"
                style={{
                  width: i === slide ? 20 : 6,
                  height: 6,
                  background: i === slide ? "#1a8754" : "rgba(255,255,255,0.3)",
                }}
              />
            </button>
          ))}
        </div>

        <span className="text-white/50 text-xs font-mono">{slide + 1} / {totalSlides}</span>
      </div>

      {/* Slide content */}
      <div className="flex-1 overflow-hidden relative">
        <div
          className="flex h-full transition-transform duration-350 ease-in-out"
          style={{ transform: `translateX(-${slide * 100}%)`, width: `${totalSlides * 100}%` }}
        >
          {SLIDES.map((s, i) => (
            <div key={i} className="flex-shrink-0 overflow-hidden" style={{ width: `${100 / totalSlides}%` }}>
              {s.component}
            </div>
          ))}
        </div>
      </div>

      {/* Bottom nav arrows */}
      <div className="flex items-center justify-between px-5 py-4 pb-safe" style={{ background: "rgba(0,0,0,0.4)" }}>
        <button
          onClick={prev}
          disabled={slide === 0}
          className="flex items-center gap-2 text-sm font-semibold transition-opacity"
          style={{ color: slide === 0 ? "rgba(255,255,255,0.2)" : "white" }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          {slide > 0 ? SLIDES[slide - 1].title : ""}
        </button>

        <span className="text-white/60 text-xs font-semibold uppercase tracking-wider">
          {SLIDES[slide].title}
        </span>

        <button
          onClick={next}
          disabled={slide === totalSlides - 1}
          className="flex items-center gap-2 text-sm font-semibold transition-opacity"
          style={{ color: slide === totalSlides - 1 ? "rgba(255,255,255,0.2)" : "white" }}
        >
          {slide < totalSlides - 1 ? SLIDES[slide + 1].title : ""}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>
      </div>
    </div>
  );
}
