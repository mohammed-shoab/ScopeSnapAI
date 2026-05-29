"use client";

import { useState, useEffect } from "react";
import DataConfidenceLabel from "@/components/DataConfidenceLabel";
import { track } from "@/lib/tracking";
import { formatCurrency, detectMarket, getLanguage } from "@/lib/market";
import { URDU_STRINGS } from "@/lib/urdu-strings";
import FiveYearComparison, { type TierTCO } from "@/components/FiveYearComparison";

/**
 * ReportQRCode — SOW Task 1.9 (Zuckerberg requirement)
 * Renders a QR code linking to this report URL with UTM attribution params.
 * Uses api.qrserver.com (free, no key, privacy-safe). R.6 npm approach reverted —
 * react-qr-code v2 TypeScript types conflict; CDN approach is simpler and reliable.
 */
function ReportQRCode({ reportShortId }: { reportShortId: string }) {
  // A.5 fix: lazy initializer computes URL synchronously on first render so
  // QR image is present when the browser print dialog opens (no useEffect delay).
  const [qrUrl] = useState(() => {
    if (typeof window === "undefined") return "";
    const reportUrl = window.location.href.split("?")[0];
    const trackingUrl = `${reportUrl}?utm_source=report&utm_medium=qr&utm_campaign=${reportShortId}`;
    const encoded = encodeURIComponent(trackingUrl);
    return `https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=${encoded}&color=1a8754&bgcolor=ffffff&margin=4`;
  });

  if (!qrUrl) return null;

  return (
    <div style={{ marginTop: 14, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={qrUrl}
        alt="Scan to view this report on any device"
        width={80}
        height={80}
        style={{ borderRadius: 6, border: "1px solid #e2dfd7" }}
      />
      <span style={{ fontSize: 9, color: "#b0aca4", letterSpacing: "0.04em" }}>
        Scan to view on any device
      </span>
    </div>
  );
}

interface Option {
  tier: string;
  name: string;
  total: number;
  five_year_total?: number;
  line_items?: Array<{ label?: string; amount?: number; description?: string; total?: number }>;
  description?: string;
  savings_note?: string;
  five_year_comparison?: TierTCO | null;
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
  custom_branding?: boolean;  // Q.4: always true — PAID_PLANS gate removed. Always show contractor logo.
}

interface Report {
  report_short_id: string;
  report_token: string;
  status: string;
  created_at?: string;
  selected_option?: string;
  approved_at?: string;
  ai_confidence?: number;   // 0–100 — from assessment ai_equipment_id.confidence
  company: Company;
  property?: Property;
  equipment?: Equipment;
  remaining_life?: RemainingLife;
  photos: Photo[];
  issues: Issue[];
  options: Option[];
  site_visit_fee_text?: string;  // R.8
  seasonal_note?: string;         // R.9 (track-f-a.1)
  photo_skipped?: boolean;          // B.6 — on-site photo not captured disclosure
}

const TIER_LABELS: Record<string, string> = {
  good: "Good",
  better: "Better",
  best: "Best",
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
  const bg = CONDITION_BG[label] || "#f5f4f2";

  return (
    <div
      style={{
        width: 64,
        height: 64,
        borderRadius: "50%",
        border: `5px solid ${color}`,
        background: bg,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      <span
        style={{
          fontSize: 10,
          fontWeight: 800,
          color: color,
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

const EQUIP_LABELS: Record<string, string> = {
  ac_unit: "AC Unit",
  heat_pump: "Heat Pump",
  furnace: "Furnace",
  boiler: "Boiler",
  air_handler: "Air Handler",
  mini_split: "Mini-Split",
  package_unit: "Package Unit",
  other: "Equipment",
  unknown: "System",
};

function equipLabel(type: string): string {
  return EQUIP_LABELS[type] || type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function AnnotatedPhotoSvg({ photo, hasIssues }: { photo: Photo; hasIssues?: boolean }) {
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
          {hasIssues && (
            <>
              <circle cx="125" cy="85" r="30" fill="none" stroke="#ff4444" strokeWidth="2.5" strokeDasharray="5,3" />
              <line x1="150" y1="65" x2="265" y2="25" stroke="#ff4444" strokeWidth="1.5" />
              <rect x="210" y="8" width="142" height="28" rx="5" fill="#ff4444" />
              <text x="218" y="20" fill="white" fontSize="8" fontWeight="700" fontFamily="Plus Jakarta Sans">
                ⚠ SEE ISSUES BELOW
              </text>
              <text x="218" y="31" fill="rgba(255,255,255,.8)" fontSize="7" fontFamily="Plus Jakarta Sans">
                Annotated by AI
              </text>
            </>
          )}
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


export default function ReportClient({ report }: { report: Report }) {
  // BUG-037: derive market from stored estimate data, not from hostname.
  // Prevents a PK estimate viewed on the Houston domain from formatting in USD.
  const reportMarket = (((report as any).market as "US" | "PK") || "US");
  // BUG-038: only this arrow fn exists for fmt (module-level was deleted).
  const fmt = (n: number | undefined | null): string =>
    formatCurrency(n as number, reportMarket);

  // Urdu / RTL support for PK homeowner reports
  const [lang, setLang] = useState<"en" | "ur">("en");
  useEffect(() => {
    const stored = getLanguage();
    setLang(stored);
    if (typeof document !== "undefined") {
      document.documentElement.dir = stored === "ur" ? "rtl" : "ltr";
      document.documentElement.lang = stored;
    }
    return () => {
      // Reset to LTR when navigating away from report
      if (typeof document !== "undefined") {
        document.documentElement.dir = "ltr";
        document.documentElement.lang = "en";
      }
    };
  }, []);
  const t = (key: string): string => {
    if (lang !== "ur") return key;
    return URDU_STRINGS[key] ?? key;
  };
  const isRTL = lang === "ur";
  const reportFont = isRTL
    ? "'Noto Nastaliq Urdu', serif"
    : "'Plus Jakarta Sans', sans-serif";

  const alreadyApproved = report.status === "approved";
  // REC.5: The originally recommended tier (derived once, not reactive)
  const initialRecommendedTier =
    report.options?.find((o) => o.recommended)?.tier ||
    report.options?.[1]?.tier ||
    report.options?.[0]?.tier ||
    "better";
  const [selectedTier, setSelectedTier] = useState<string>(
    alreadyApproved && report.selected_option
      ? report.selected_option
      : initialRecommendedTier
  );
  const [approving, setApproving] = useState(false);
  const [approved, setApproved] = useState(alreadyApproved);
  const [approvedTier, setApprovedTier] = useState<string | undefined>(report.selected_option);
  const [error, setError] = useState<string | null>(null);

  // SOW Task 1.10 — track homeowner report view on mount
  useEffect(() => {
    track.reportViewed(report.report_short_id);
  }, [report.report_short_id]);

  const condition = report.equipment?.condition?.toLowerCase() || "unknown";
  const conditionColor = CONDITION_COLORS[condition] || "#7a7770";
  const selectedOption = report.options?.find((o) => o.tier === selectedTier);
  const company = report.company || {};
  const property = report.property;
  const equipment = report.equipment;
  const remainingLife = report.remaining_life;


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
      // REC.5: Track homeowner approval + whether it matched the original recommendation
      track.recommendationApproved(
        (report as unknown as { card_id?: number }).card_id || 0,
        selectedTier,
        initialRecommendedTier,
        report.report_short_id,
      );
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
    <div style={{ background: "#f2f1ec", minHeight: "100vh", fontFamily: reportFont, direction: isRTL ? "rtl" : "ltr" }}>
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
        {/* Phase 1 branding — paid plans only. Free plan shows SnapAI default branding. */}
        {company.custom_branding && company.logo_url ? (
          <img
            src={company.logo_url}
            alt={company.name || "Company logo"}
            style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              objectFit: "contain",
              background: "#f7f6f2",
              border: "1px solid #e5e2da",
              flexShrink: 0,
            }}
          />
        ) : (
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
            {company.custom_branding && company.name ? company.name[0].toUpperCase() : "S"}
          </div>
        )}
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0 }}>
            {company.custom_branding ? (company.name || "Your HVAC Company") : "SnapAI"}
          </h3>
          <p style={{ fontSize: 10, color: "#7a7770", margin: 0 }}>
            {company.custom_branding
              ? [company.license_number && `License #${company.license_number}`, company.phone].filter(Boolean).join(" · ")
              : "Professional HVAC Assessments"}
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          {/* R.1: Print button */}
          <button
            onClick={() => window.print()}
            style={{ fontSize: 11, fontWeight: 600, color: "#7a7770", background: "#f7f6f2", border: "1px solid #e5e2da", borderRadius: 8, padding: "5px 10px", cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
            {t("Print")}
          </button>
          {company.custom_branding && company.phone && (
            <a
              href={`tel:${company.phone.replace(/\D/g, "")}`}
              style={{ fontSize: 12, fontWeight: 700, color: "#1a8754", textDecoration: "none", display: "flex", alignItems: "center", gap: 4 }}
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 11 19.79 19.79 0 0 0 .21 2.36 2 2 0 012.22 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 7.09a16 16 0 006 6l.66-.66a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92z"/></svg>
              {t("Call")}
            </a>
          )}
        </div>
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
            {t("Equipment Health Report")}
          </p>
          <h1 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 4px", letterSpacing: -0.5 }}>
            {property?.customer_name ? `${property.customer_name}'s Home` : property?.address_line1 || ""}
          </h1>
          <p style={{ fontSize: 12, color: "#7a7770" }}>
            {[property?.city, property?.state].filter(Boolean).join(", ")}
            {createdDate && ` · ${createdDate}`}
          </p>
          {property?.customer_name && (
            <p style={{ fontSize: 13, fontWeight: 600, marginTop: 4 }}>{isRTL ? t("Homeowner Name") + ": " : "Prepared for "}{property.customer_name}</p>
          )}
        </div>

        {/* R.4: Health Overview — only shown when at least one nameplate data field has a value */}
        {(equipment?.brand || equipment?.model_number || equipment?.install_year) && (
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
            {t("System Overview")}
          </div>
          <div style={{ padding: "12px 16px 16px" }}>
            {/* Health Gauge + Text */}
            <div style={{ display: "flex", alignItems: "center", gap: 14, paddingBottom: 12 }}>
              <HealthGauge condition={condition} />
              <div>
                <h4 style={{ fontSize: 15, fontWeight: 700, margin: 0 }}>
                  {equipment?.equipment_type
                    ? `Your ${equipLabel(equipment.equipment_type)}:`
                    : "Your System:"}{" "}
                  <span style={{ color: conditionColor }}>
                    {t(condition.charAt(0).toUpperCase() + condition.slice(1))} Condition
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
                <div style={{ fontSize: 9, color: "#a8a49c" }}>{t("Brand")}</div>
              </div>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700 }}>
                  {equipment?.install_year || "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>
                  {t("Installed")}{equipment?.install_year ? ` (${new Date().getFullYear() - equipment.install_year} yrs ago)` : ""}
                </div>
              </div>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700, color: "#e6a817" }}>
                  {remainingLife ? `${remainingLife.remaining_years} yr${remainingLife.remaining_years !== 1 ? "s" : ""}` : "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>{t("Est. Life Remaining")}</div>
              </div>
              <div style={{ background: "#f7f6f2", borderRadius: 8, padding: 8, textAlign: "center" }}>
                <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 16, fontWeight: 700 }}>
                  {equipment?.model_number ? equipment.model_number.split(" ")[0] : "—"}
                </div>
                <div style={{ fontSize: 9, color: "#a8a49c" }}>Model / SEER</div>
              </div>
            </div>

            {/* AI Data Confidence Label — SOW Task 1.9, Decision #2 */}
            {report.ai_confidence != null && (
              <div style={{ marginTop: 10, display: "flex", justifyContent: "center" }}>
                <DataConfidenceLabel confidence={report.ai_confidence} />
              </div>
            )}
          </div>
        </div>
        )}

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
            {/* R.5: Only render photo when photos exist — no placeholder */}
            {report.photos.length > 0 && (
              <AnnotatedPhotoSvg photo={report.photos[0]} hasIssues={report.issues.length > 0} />
            )}

            {/* Issues List */}
            {report.issues.length === 0 ? (
              <p style={{ fontSize: 13, color: "#7a7770", textAlign: "center", padding: "12px 0" }}>
                {isRTL ? "کوئی بڑا مسئلہ نہیں ملا۔ آپ کا سسٹم اچھی حالت میں ہے۔" : "No significant issues found. Your system is in good condition."}
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
                const isRec = !!opt.recommended; // reads backend recommended flag directly (algo-bias fix 2026-05-29)

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
                        {isRTL ? "★ " + t("Recommended").toUpperCase() : "★ RECOMMENDED"}
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
                          {t(TIER_LABELS[opt.tier] || `Option ${i + 1}`)}
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

                    {/* Q.5 — Why recommended expansion (only when badge is shown) */}
                    {isRec && (opt as any).why_recommended && (
                      <details
                        style={{ marginTop: 6 }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <summary
                          style={{
                            fontSize: 10,
                            color: "#1a8754",
                            fontWeight: 600,
                            cursor: "pointer",
                            listStyle: "none",
                            userSelect: "none",
                          }}
                        >
                          {isRTL ? "کیوں تجویز کیا گیا؟ ▾" : "Why recommended? ▾"}
                        </summary>
                        <p style={{ fontSize: 10, color: "#5a5a55", marginTop: 4, lineHeight: 1.5, paddingLeft: 4 }}>
                          {(opt as any).why_recommended}
                        </p>
                      </details>
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
                            <span>{item.description || item.label}</span>
                            <span style={{ fontFamily: "IBM Plex Mono, monospace", fontWeight: 600 }}>
                              {fmt(item.total ?? item.amount)}
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
                          <span>{t("Total")}</span>
                          <span style={{ fontFamily: "IBM Plex Mono, monospace", color: "#1a8754" }}>
                            {fmt(opt.total)}
                          </span>
                        </div>
                      </div>
                    )}

                    {isSelected && !approved && (
                      <div style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 4 }}>
                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#1a8754" }} />
                        <span style={{ fontSize: 11, color: "#1a8754", fontWeight: 600 }}>{t("Selected")}</span>
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
                  <div style={{ fontSize: 36, marginBottom: 10 }}>{"✅"}</div>
                  <h3 style={{ fontSize: 18, fontWeight: 800, color: "#1a8754", margin: "0 0 6px" }}>
                    {report.property?.customer_name ? `Thank you, ${report.property.customer_name}!` : t("Thank you!")}
                  </h3>
                  {company.name && (
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#0f5c38", margin: "0 0 4px" }}>{company.name}</p>
                  )}
                  <p style={{ fontSize: 12, color: "#3a7059", margin: "0 0 8px" }}>
                    {t("You selected ")}
                    <strong>{report.options.find((o) => o.tier === approvedTier)?.name || approvedTier}</strong>{"."}
                  </p>
                  {company.phone && (
                    <a
                      href={`tel:${company.phone.replace(/\D/g, "")}`}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 6,
                        padding: "10px 20px",
                        background: "#1a8754",
                        color: "white",
                        borderRadius: 8,
                        fontWeight: 700,
                        fontSize: 14,
                        textDecoration: "none",
                        margin: "8px 0",
                      }}
                    >
                      {"☎"} {company.phone}
                    </a>
                  )}
                  <p style={{ fontSize: 11, color: "#7a7770", margin: "8px 0 6px", lineHeight: 1.5 }}>
                    {t("We typically respond within 2 hours during business hours.")}
                  </p>
                  <p style={{ fontSize: 10, color: "#a8a49c", margin: 0, fontFamily: "IBM Plex Mono, monospace" }}>
                    {`REF: RPT-${report.report_short_id}`}
                  </p>
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
                      ? "Your contractor will contact you to confirm scheduling and payment details."
                      : "Select an option above, then tap Approve"}
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

        {/* R.8: Site visit fee disclaimer */}
        {report.site_visit_fee_text && (
          <div style={{ margin: "0 10px 4px", padding: "10px 14px", background: "#f7f6f2", borderRadius: 10, border: "1px solid #e5e2da", textAlign: "center" }}>
            <p style={{ fontSize: 10, color: "#7a7770", margin: 0, lineHeight: 1.5 }}>
              {report.site_visit_fee_text}
            </p>
          </div>
        )}
        {/* 5-Year TCO — Track G */}
        {report.options.length > 0 && (
          <div style={{ margin: "10px 0" }}>
            <FiveYearComparison
              optionA={report.options.find((o) => o.tier === "good" || o.tier === "A")?.five_year_comparison ?? null}
              optionB={report.options.find((o) => o.tier === "better" || o.tier === "B")?.five_year_comparison ?? null}
              optionC={report.options.find((o) => o.tier === "best" || o.tier === "C")?.five_year_comparison ?? null}
              recommendedTier={(initialRecommendedTier as "A" | "B" | "C")}
              market={reportMarket}
              mode="homeowner_report"
              sessionId={report.report_short_id}
            />
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
            <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 4px" }}>{t("Questions? We're here to help.")}</p>
            <p style={{ fontSize: 12, color: "#7a7770", margin: 0 }}>
              {company.custom_branding ? (company.name || "Your HVAC Contractor") : "SnapAI"}
            </p>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              {company.custom_branding && company.phone && (
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
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 6,
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 11 19.79 19.79 0 0 0 .21 2.36 2 2 0 012.22 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 7.09a16 16 0 006 6l.66-.66a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92z"/></svg>
                  {t("Call")}
                </a>
              )}
              {company.custom_branding && company.phone && (
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
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 6,
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                  {t("Text")}
                </a>
              )}
            </div>
          </div>
        </div>


        {/* R.9 (track-f-a.1): Peak season surcharge disclosure */}
        {report.seasonal_note && (
          <div style={{ margin: "0 10px 4px", padding: "8px 14px", background: "#f3f4f6", borderRadius: 10, border: "1px solid #e5e7eb", textAlign: "center" }}>
            <p style={{ fontSize: 10, color: "#6b7280", margin: 0, lineHeight: 1.5 }}>
              ℹ️ {t("Peak season service rate applied.")} {report.seasonal_note}
            </p>
          </div>
        )}
        {report.photo_skipped && (
          <div style={{ margin: "0 10px 4px", padding: "8px 14px", background: "#f5f5f5", borderRadius: 10, border: "1px solid #e0e0e0", textAlign: "center" }}>
            <p style={{ fontSize: 10, color: "#6b7280", margin: 0, lineHeight: 1.5 }}>
              On-site photo not captured during this visit.
            </p>
          </div>
        )}

        {/* Footer — SOW Decision #2: two-line SnapAI footer + QR code (Task 1.9 / Zuckerberg) */}
        <div style={{ textAlign: "center", padding: "20px 16px", fontSize: 10, color: "#a8a49c", lineHeight: 1.8 }}>
          <span style={{ fontFamily: "IBM Plex Mono, monospace" }}>
            Report ID: {report.report_short_id}
          </span>
          {property?.address_line1 && (
            <>
              <br />
              {[property.address_line1, property.city, property.state].filter(Boolean).join(", ")}
            </>
          )}
          <br />
          <span style={{ color: "#c8c4bc" }}>
            Verified Assessment by{" "}
            <a
              href="https://snapai.mainnov.tech"
              style={{ color: "#1a8754", fontWeight: 700, textDecoration: "none" }}
            >
              SnapAI
            </a>
          </span>
          <br />
          <span style={{ color: "#b0aca4" }}>
            Professional HVAC assessments for contractors — snapai.mainnov.tech
          </span>
          {/* QR code — Zuckerberg req: homeowner scans to re-open report on any device */}
          {/* UTM params: utm_source=report&utm_medium=qr for attribution tracking */}
          <ReportQRCode reportShortId={report.report_short_id} />
        </div>
      </div>
    </div>
  );
}
