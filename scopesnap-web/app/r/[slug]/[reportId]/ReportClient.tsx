"use client";

import { useState } from "react";

interface Option {
  tier: string;
  name: string;
  total: number;
  five_year_total?: number;
  line_items?: Array<{ label: string; amount: number }>;
  description?: string;
  savings_note?: string;
  recommended?: boolean;
}

interface Issue {
  component: string;
  issue: string;
  severity: string;
  color: string;
  description_plain?: string;
  description?: string;
}

interface Photo {
  photo_url: string;
  annotated_photo_url: string;
  annotations: Array<{
    label: string;
    x: number;
    y: number;
    severity?: string;
  }>;
}

interface Equipment {
  equipment_type?: string;
  brand?: string;
  model_number?: string;
  install_year?: number;
  condition?: string;
}

interface RemainingLife {
  age_years: number;
  avg_lifespan: number;
  remaining_years: number;
  remaining_pct: number;
}

interface Property {
  address_line1?: string;
  city?: string;
  state?: string;
  zip?: string;
  customer_name?: string;
  customer_phone?: string;
}

interface Company {
  name?: string;
  phone?: string;
  email?: string;
  license_number?: string;
  logo_url?: string;
}

interface Report {
  report_short_id: string;
  report_token: string;
  status: string;
  created_at?: string;
  selected_option?: string;
  approved_at?: string;
  company: Company;
  property?: Property;
  equipment?: Equipment;
  remaining_life?: RemainingLife;
  photos: Photo[];
  issues: Issue[];
  options: Option[];
}

const TIER_LABELS: Record<string, string> = {
  good: "Option A",
  better: "Option B",
  best: "Option C",
};

const CONDITION_COLORS: Record<string, string> = {
  excellent: "#1a8754",
  good: "#1a8754",
  fair: "#e6a817",
  poor: "#c4600a",
  critical: "#c62828",
  failed: "#c62828",
};

const CONDITION_BG: Record<string, string> = {
  excellent: "#e8f5ee",
  good: "#e8f5ee",
  fair: "#fdf6e0",
  poor: "#fef3e8",
  critical: "#fce8e8",
  failed: "#fce8e8",
};

function fmt(n: number): string {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

/** Convert snake_case slugs to Title Case for display ("evaporator_coil" → "Evaporator Coil") */
function formatSlug(s: string): string {
  if (!s) return "";
  return s
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Ensure photo URLs are absolute — prepend API base if they're relative paths */
function resolvePhotoUrl(url: string): string {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  return `${apiBase}${url.startsWith("/") ? "" : "/"}${url}`;
}

function HealthGauge({ condition }: { condition?: string }) {
  const label = (condition || "unknown").toLowerCase();
  const color = CONDITION_COLORS[label] || "#7a7770";
  const getBorderColor = () => {
    if (label === "fair") return "#e6a817";
    return color;
  };

  return (
    <div
      style={{
        width: 64,
        height: 64,
        borderRadius: "50%",
        border: `5px solid #e5e2da`,
        borderTopColor: "#1a8754",
        borderRightColor: "#e6a817",
        borderBottomColor: "#c4600a",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      <span
        style={{
          fontSize: 11,
          fontWeight: 800,
          color: "#e6a817",
          textTransform: "uppercase",
          fontFamily: "IBM Plex Mono, monospace",
          letterSpacing: -0.5,
          textAlign: "center",
          lineHeight: 1.2,
        }}
      >
        {label.toUpperCase()}
      </span>
    </div>
  );
}

function AnnotatedPhotoSvg({ photo }: { photo: Photo }) {
  const annotations = photo.annotations || [];
  const hasUrl = !!(photo.annotated_photo_url || photo.photo_url);

  return (
    <div style={{ borderRadius: 12, overflow: "hidden", background: "#2a2a28", marginBottom: 8 }}>
      {annotations.length > 0 && hasUrl ? (
        <div style={{ position: "relative" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={resolvePhotoUrl(photo.annotated_photo_url || photo.photo_url)}
            alt="Equipment assessment photo"
            style={{ width: "100%", display: "block", maxHeight: 300, objectFit: "cover" }}
            onError={(e) => {
              // If photo fails to load, show the fallback SVG sibling instead
              const parent = e.currentTarget.parentElement?.parentElement;
              if (parent) {
                e.currentTarget.parentElement!.style.display = "none";
                const fallback = parent.querySelector(".photo-fallback") as HTMLElement;
                if (fallback) fallback.style.display = "block";
              }
            }}
          />
        </div>
      ) : null}
      <svg
        className="photo-fallback"
        viewBox="0 0 358 240"
        style={{ width: "100%", display: (annotations.length > 0 && hasUrl) ? "none" : "block" }}
      >
          <rect width="358" height="240" fill="#3a3a35" />
          <rect x="50" y="25" width="258" height="190" rx="6" fill="#5a5a55" stroke="#4a4a45" strokeWidth="2" />
          <circle cx="179" cy="100" r="50" fill="none" stroke="#6a6a65" strokeWidth="1.5" />
          <circle cx="179" cy="100" r="35" fill="none" stroke="#6a6a65" strokeWidth="1" />
          <rect x="90" y="178" width="178" height="26" rx="3" fill="#7a7a75" />
          <text x="179" y="195" textAnchor="middle" fill="#ccc" fontSize="9" fontFamily="IBM Plex Mono">
            HVAC EQUIPMENT
          </text>
          <circle cx="125" cy="85" r="30" fill="none" stroke="#ff4444" strokeWidth="2.5" strokeDasharray="5,3" />
          <line x1="150" y1="65" x2="265" y2="25" stroke="#ff4444" strokeWidth="1.5" />
          <rect x="210" y="8" width="142" height="28" rx="5" fill="#ff4444" />
          <text x="218" y="20" fill="white" fontSize="8" fontWeight="700" fontFamily="Plus Jakarta Sans">
            ⚠ SEE ISSUES BELOW
          </text>
          <text x="218" y="31" fill="rgba(255,255,255,.8)" fontSize="7" fontFamily="Plus Jakarta Sans">
            Annotated by AI
          </text>
      </svg>
      <div style={{ padding: "8px 12px", background: "rgba(0,0,0,.85)", color: "rgba(255,255,255,.7)", fontSize: 10 }}>
        <strong style={{ color: "#22cc66" }}>AI-Enhanced Assessment Photo</strong>
        {" · Red = needs attention · Orange = minor · Green = identified"}
      </div>
    </div>
  );
}

function IssueItem({ issue }: { issue: Issue }) {
  const dotColors: Record<string, string> = { red: "#c62828", orange: "#c4600a", green: "#1a8754" };
  const dotColor = dotColors[issue.color] || "#7a7770";
  const text = issue.description_plain || issue.description || "";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: 8,
        padding: "10px 0",
        borderBottom: "1px solid #e5e2da",
      }}
    >
      <div
        style={{
          width: 10,
          height: 10,
          borderRadius: "50%",
          background: dotColor,
          marginTop: 4,
          flexShrink: 0,
        }}
      />
      <div>
        <h4 style={{ fontSize: 12, fontWeight: 600, margin: 0 }}>
          {formatSlug(issue.component)} — {formatSlug(issue.issue)}
        </h4>
        {text && (
          <p style={{ fontSize: 11, color: "#7a7770", marginTop: 3, lineHeight: 1.6 }}>{text}</p>
        )}
      </div>
    </div>
  );
}

function CostBar({ option, maxVal }: { option: Option; maxVal: number }) {
  const pct = Math.round((option.five_year_total || option.total) / maxVal * 100);
  const isGood = option.tier === "good";
  const isBetter = option.tier === "better";
  const isBest = option.tier === "best";
  const fillColor = isGood ? "#c4600a" : isBetter ? "#1a8754" : "#1565c0";
  const label = TIER_LABELS[option.tier] || option.tier;

  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, fontWeight: 600, marginBottom: 4 }}>
        <span>{label}: {option.name}</span>
        <span style={{ fontFamily: "IBM Plex Mono, monospace", color: fillColor, fontSize: 14 }}>
          {fmt(option.five_year_total || option.total)}
        </span>
      </div>
      <div style={{ height: 24, background: "#f7f6f2", borderRadius: 6, overflow: "hidden", position: "relative" }}>
        <div
          style={{
            width: `${Math.max(pct, 15)}%`,
            height: "100%",
            background: fillColor,
            borderRadius: 6,
            display: "flex",
            alignItems: "center",
            paddingLeft: 8,
          }}
        >
          <span style={{ fontSize: 8, fontWeight: 600, color: "white", whiteSpace: "nowrap" }}>
            {fmt(option.five_year_total || option.total)} over 5 yrs
          </span>
        </div>
      </div>
    </div>
  );
}

export default function ReportClient({ report }: { report: Report }) {
  const alreadyApproved = report.status === "approved";
  const [selectedTier, setSelectedTier] = useState<string>(
    alreadyApproved && report.selected_option
      ? report.selected_option
      : report.options?.find((o) => o.recommended)?.tier || report.options?.[1]?.tier || report.options?.[0]?.tier || ""
  );
  const [approving, setApproving] = useState(false);
  const [approved, setApproved] = useState(alreadyApproved);
  const [approvedTier, setApprovedTier] = useState<string | undefined>(report.selected_option);
  const [error, setError] = useState<string | null>(null);

  const condition = report.equipment?.condition?.toLowerCase() || "unknown";
  const conditionColor = CONDITION_COLORS[condition] || "#7a7770";
  const selectedOption = report.options?.find((o) => o.tier === selectedTier);
  const company = report.company || {};
  const property = report.property;
  const equipment = report.equipment;
  const remainingLife = report.remaining_life;

  const maxFiveYr = Math.max(...(report.options || []).map((o) => o.five_year_total || o.total), 1);

  const handleApprove = async () => {
    if (!selectedTier || approving || approved) return;
    setApproving(true);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/reports/${report.report_token}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected_option: selectedTier }),
      });
      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail || "Approval failed");
      }
      setApproved(true);
      setApprovedTier(selectedTier);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setApproving(false);
    }
  };

  const createdDate = report.created_at
    ? new Date(report.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })
    : "";

  return (
    <div style={{ background: "#f2f1ec", minHeight: "100vh", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Company Header Bar */}
      <div
        style={{
          background: "white",
          borderBottom: "1px solid #e5e2da",
          padding: "14px 16px",
          display: "flex",
          alignItems: "center",
          gap: 10,
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 10,
            background: "#1a8754",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: 800,
            fontSize: 18,
            flexShrink: 0,
          }}
        >
          {company.name ? company.name[0].toUpperCase() : "S"}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0 }}>{company.name || "Your HVAC Company"}</h3>
          <p style={{ fontSize: 10, color: "#7a7770", margin: 0 }}>
            {[company.license_number && `License #${company.license_number}`, company.phone].filter(Boolean).join(" · ")}
          </p>
        </div>
        {company.phone && (
          <a
            href={`tel:${company.phone.replace(/\D/g, "")}`}
            style={{ fontSize: 12, fontWeight: 700, color: "#1a8754", textDecoration: "none", flexShrink: 0 }}
          >
            📞 Call
          </a>
        )}
      </div>

      <div style={{ maxWidth: 480, margin: "0 auto", padding: "0 0 40px", width: "100%" }}>
        {/* Report Header */}
        <div style={{ padding: "20px 16px 8px", textAlign: "center" }}>
          <p
            style={{
              fontFamily: "IBM Plex Mono, monospace",
              fontSize: 10,
              color: "#a8a49c",
              textTransform: "uppercase",
              letterSpacing: 1.5,
              marginBottom: 4,
            }}
          >
            Equipment Health Report
          </p>
          <h1 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 4px", letterSpacing: -0.5 }}>
            {property?.address_line1 || "Your Home"}
          </h1>
          <p style={{ fontSize: 12, color: "#7a7770" }}>
            {[property?.city, property?.state].filter(Boolean).join(", ")}
            {createdDate && ` · ${createdDate}`}
          </p>
          {property?.customer_name && (
            <p style={{ fontSize: 13, fontWeight: 600, marginTop: 4 }}>Prepared for {property.customer_name}</p>
          )}
        </div>

        {/* Health Overview Section */}
        <div
          style={{
            background: "white",
            margin: "10px",
            borderRadius: 16,
            boxShadow: "0 1px 4px rgba(0,0,0,.04), 0 6px 16px rgba(0,0,0,.04)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "14px 16px 0",
              fontSize: 10,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: 1,
              fontFamily: "IBM Plex Mono, monospace",
              color: "#1a8754",
            }}
          >
            System Overview
          </div>
          <div style={{ padding: "12px 16px 16px" }}>
            {/* Health Gauge + Text */}
            <div style={{ display: "flex", alignItems: "center", gap: 14, paddingBottom: 12 }}>
              <HealthGauge condition={condition} />
              <div>
                <h4 style={{ fontSize: 15, fontWeight: 700, margin: 0 }}>
                  Your AC:{" "}
                  <span style={{ color: conditionColor }}>
                    {condition.charAt(0).toUpperCase() + condition.slice(1)} Condition
                  </span>
                </h4>
                <p style={{ fontSize: 11, color: "#7a7770", margin: "3px 0 0" }}>
                  {condition === "fair"
                    ? "Functional but one component needs attention to prevent further issues."
                    : condition === "poor" || condition === "critical"
                    ? "Needs attention soon to prevent system failure."
                    : condition === "good" || condition === "excellent"
                    ? "Your system is in good shape."
                    : "Assessment complete — see details below."}
                </p>
              </div>
            </div>

            {/* Equipment Stats Grid - 2x2 */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700 }}>
                  {equipment?.brand || "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>Brand</div>
              </div>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700 }}>
                  {equipment?.install_year || "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>
                  Installed{equipment?.install_year ? ` (${new Date().getFullYear() - equipment.install_year} yrs ago)` : ""}
                </div>
              </div>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700, color: "#e6a817" }}>
                  {remainingLife ? `${remainingLife.remaining_years} yr${remainingLife.remaining_years !== 1 ? "s" : ""}` : "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>Est. Life Remaining</div>
              </div>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700 }}>
                  {equipment?.model_number ? equipment.model_number.split(" ")[0] : "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>Model / SEER</div>
              </div>
            </div>
          </div>
        </div>

        {/* What We Found Section */}
        <div
          style={{
            background: "white",
            margin: "10px",
            borderRadius: 16,
            boxShadow: "0 1px 4px rgba(0,0,0,.04), 0 6px 16px rgba(0,0,0,.04)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "14px 16px 0",
              fontSize: 10,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: 1,
              fontFamily: "IBM Plex Mono, monospace",
              color: "#c4600a",
            }}
          >
            What We Found
          </div>
          <div style={{ padding: "12px 16px 16px" }}>
            {/* Annotated Photo */}
            {report.photos.length > 0 ? (
              <AnnotatedPhotoSvg photo={report.photos[0]} />
            ) : (
              <AnnotatedPhotoSvg photo={{ photo_url: "", annotated_photo_url: "", annotations: [] }} />
            )}

            {/* Issues List */}
            {report.issues.length === 0 ? (
              <p style={{ fontSize: 13, color: "#7a7770", textAlign: "center", padding: "12px 0" }}>
                No significant issues found. Your system is in good condition.
              </p>
            ) : (
              <div>
                {report.issues.map((issue, i) => (
                  <IssueItem key={i} issue={issue} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Your Options Section */}
        {report.options.length > 0 && (
          <div
            style={{
              background: "white",
              margin: "10px",
              borderRadius: 16,
              boxShadow: "0 1px 4px rgba(0,0,0,.04), 0 6px 16px rgba(0,0,0,.04)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "14px 16px 0",
                fontSize: 10,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 1,
                fontFamily: "IBM Plex Mono, monospace",
                color: "#1a8754",
              }}
            >
              Your Options
            </div>
            <div style={{ padding: "12px 16px 16px" }}>
              {report.options.map((opt, i) => {
                const isSelected = selectedTier === opt.tier;
                const isRec = opt.recommended || opt.tier === "better";

                return (
                  <div
                    key={i}
                    onClick={() => !approved && setSelectedTier(opt.tier)}
                    style={{
                      border: isSelected ? "2px solid #1a8754" : "1px solid #e5e2da",
                      borderRadius: 12,
                      padding: "14px",
                      marginBottom: 8,
                      cursor: approved ? "default" : "pointer",
                      background: isSelected ? "#e8f5ee" : "white",
                      position: "relative",
                      transition: "all .15s",
                    }}
                  >
                    {isRec && (
                      <div
                        style={{
                          position: "absolute",
                          top: -8,
                          right: 12,
                          background: "#1a8754",
                          color: "white",
                          fontSize: 8,
                          fontWeight: 700,
                          padding: "2px 8px",
                          borderRadius: 4,
                          fontFamily: "IBM Plex Mono, monospace",
                        }}
                      >
                        ★ RECOMMENDED
                      </div>
                    )}

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <div
                          style={{
                            fontSize: 9,
                            fontWeight: 700,
                            color: "#a8a49c",
                            textTransform: "uppercase",
                            letterSpacing: 0.5,
                            marginBottom: 2,
                          }}
                        >
                          {TIER_LABELS[opt.tier] || `Option ${i + 1}`}
                        </div>
                        <h4 style={{ fontSize: 13, fontWeight: 700, margin: 0 }}>{opt.name}</h4>
                      </div>
                      <div
                        style={{
                          fontFamily: "IBM Plex Mono, monospace",
                          fontSize: 22,
                          fontWeight: 700,
                          color: "#1a8754",
                          flexShrink: 0,
                          marginLeft: 8,
                        }}
                      >
                        {fmt(opt.total)}
                      </div>
                    </div>

                    {opt.description && (
                      <p style={{ fontSize: 11, color: "#7a7770", marginTop: 6, lineHeight: 1.6 }}>
                        {opt.description}
                      </p>
                    )}

                    {opt.savings_note && (
                      <p style={{ fontSize: 10, color: "#1a8754", fontWeight: 600, marginTop: 4 }}>
                        ✓ {opt.savings_note}
                      </p>
                    )}

                    {/* Line items when selected */}
                    {isSelected && opt.line_items && opt.line_items.length > 0 && (
                      <div style={{ marginTop: 10, borderTop: "1px solid #c8efda", paddingTop: 10 }}>
                        {opt.line_items.map((item, j) => (
                          <div
                            key={j}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              fontSize: 11,
                              padding: "3px 0",
                              color: "#5a5a55",
                            }}
                          >
                            <span>{item.label}</span>
                            <span style={{ fontFamily: "IBM Plex Mono, monospace", fontWeight: 600 }}>
                              {fmt(item.amount)}
                            </span>
                          </div>
                        ))}
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            fontSize: 12,
                            padding: "6px 0 0",
                            borderTop: "1px solid #c8efda",
                            marginTop: 4,
                            fontWeight: 700,
                          }}
                        >
                          <span>Total</span>
                          <span style={{ fontFamily: "IBM Plex Mono, monospace", color: "#1a8754" }}>
                            {fmt(opt.total)}
                          </span>
                        </div>
                      </div>
                    )}

                    {isSelected && !approved && (
                      <div style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 4 }}>
                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#1a8754" }} />
                        <span style={{ fontSize: 11, color: "#1a8754", fontWeight: 600 }}>Selected</span>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Approve Button or Success Message */}
              {approved ? (
                <div
                  style={{
                    background: "#e8f5ee",
                    border: "2px solid #1a8754",
                    borderRadius: 12,
                    padding: "20px 16px",
                    textAlign: "center",
                    marginTop: 8,
                  }}
                >
                  <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
                  <h3 style={{ fontSize: 16, fontWeight: 800, color: "#1a8754", margin: "0 0 4px" }}>Approved!</h3>
                  <p style={{ fontSize: 12, color: "#0f5c38", margin: 0 }}>
                    You selected{" "}
                    <strong>{report.options.find((o) => o.tier === approvedTier)?.name || approvedTier}</strong>.
                    {company.name && ` ${company.name}`} will be in touch shortly to schedule.
                  </p>
                  {company.phone && (
                    <p style={{ fontSize: 11, color: "#7a7770", marginTop: 8 }}>
                      Questions? Call us at{" "}
                      <a
                        href={`tel:${company.phone.replace(/\D/g, "")}`}
                        style={{ color: "#1a8754", fontWeight: 700, textDecoration: "none" }}
                      >
                        {company.phone}
                      </a>
                    </p>
                  )}
                </div>
              ) : (
                <>
                  <button
                    onClick={handleApprove}
                    disabled={approving || !selectedTier}
                    style={{
                      width: "100%",
                      padding: "16px",
                      background: approving ? "#7a7770" : "#1a8754",
                      color: "white",
                      border: "none",
                      borderRadius: 12,
                      fontFamily: "inherit",
                      fontSize: 16,
                      fontWeight: 700,
                      cursor: approving ? "not-allowed" : "pointer",
                      boxShadow: "0 4px 16px rgba(26,135,84,.3)",
                      marginTop: 8,
                      transition: "all .15s",
                    }}
                  >
                    {approving
                      ? "Processing..."
                      : selectedOption
                      ? `✓ Approve ${selectedOption.name} — ${fmt(selectedOption.total)}`
                      : "Select an option above"}
                  </button>
                  <p
                    style={{
                      textAlign: "center",
                      fontSize: 10,
                      color: "#a8a49c",
                      marginTop: 8,
                      lineHeight: 1.5,
                    }}
                  >
                    {selectedOption
                      ? `Deposit ${fmt(Math.round(selectedOption.total * 0.2))} due now · Remaining at completion`
                      : "Tap an option above, then approve"}
                    <br />
                    🔒 Secure payment via Stripe
                  </p>
                  {error && (
                    <p style={{ color: "#c62828", fontSize: 12, textAlign: "center", marginTop: 8, fontWeight: 600 }}>
                      ⚠ {error}
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {/* 5-Year Cost Comparison */}
        {report.options.length > 0 && (
          <div
            style={{
              background: "white",
              margin: "10px",
              borderRadius: 16,
              boxShadow: "0 1px 4px rgba(0,0,0,.04), 0 6px 16px rgba(0,0,0,.04)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "14px 16px 0",
                fontSize: 10,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 1,
                fontFamily: "IBM Plex Mono, monospace",
                color: "#1565c0",
              }}
            >
              5-Year Cost Comparison
            </div>
            <div style={{ padding: "12px 16px 16px" }}>
              {report.options.map((opt, i) => (
                <CostBar key={i} option={opt} maxVal={maxFiveYr} />
              ))}
              <p style={{ fontSize: 10, color: "#a8a49c", marginTop: 4 }}>
                Includes upfront cost + estimated energy savings + future repair probability
              </p>
            </div>
          </div>
        )}

        {/* Contact Section */}
        <div
          style={{
            background: "white",
            margin: "10px",
            borderRadius: 16,
            boxShadow: "0 1px 4px rgba(0,0,0,.04), 0 6px 16px rgba(0,0,0,.04)",
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "20px 16px", textAlign: "center" }}>
            <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 4px" }}>Questions? We're here to help.</p>
            <p style={{ fontSize: 12, color: "#7a7770", margin: 0 }}>{company.name || "Your HVAC Contractor"}</p>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              {company.phone && (
                <a
                  href={`tel:${company.phone.replace(/\D/g, "")}`}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: "#1a8754",
                    color: "white",
                    borderRadius: 8,
                    textDecoration: "none",
                    textAlign: "center",
                    fontWeight: 700,
                    fontSize: 13,
                  }}
                >
                  📞 Call
                </a>
              )}
              {company.phone && (
                <a
                  href={`sms:${company.phone.replace(/\D/g, "")}`}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: "#f7f6f2",
                    color: "#1a1a18",
                    borderRadius: 8,
                    textDecoration: "none",
                    textAlign: "center",
                    fontWeight: 700,
                    fontSize: 13,
                    border: "1px solid #e5e2da",
                  }}
                >
                  💬 Text
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ textAlign: "center", padding: "20px 16px", fontSize: 10, color: "#a8a49c", lineHeight: 1.8 }}>
          {property?.customer_name && `Prepared for ${property.customer_name}`}
          {property?.address_line1 && ` · ${property.address_line1}`}
          {property?.city && `, ${property.city}`}
          {property?.state && ` ${property.state}`}
          <br />
          This report was created using{" "}
          <a href="https://scopesnap.com" style={{ color: "#1a8754", fontWeight: 600, textDecoration: "none" }}>
            ScopeSnap
          </a>{" "}
          HVAC Intelligence
          <br />
          <span style={{ fontFamily: "IBM Plex Mono, monospace" }}>Report ID: {report.report_short_id}</span>
        </div>
      </div>
    </div>
  );
}
