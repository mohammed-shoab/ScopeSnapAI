"use client";
/**
 * AssessmentListRow — Track DX.2
 * One row in the /assessments list view.
 * Shows: nameplate photo (or HVAC placeholder) / customer / address /
 *        complaint type / status badge / relative time
 */

import Link from "next/link";

export interface AssessmentItem {
  id: string;
  status: string | null;
  nameplate_photo_url: string | null;
  customer_name: string | null;
  customer_address: string | null;
  brand: string | null;
  model: string | null;
  fault_name: string | null;   // B.1: resolved fault card name from diagnostic_sessions
  complaint_type: string | null;
  created_at: string | null;
}

const STATUS_STYLE: Record<string, { bg: string; text: string; label: string }> = {
  draft:    { bg: "#f1f5f9", text: "#64748b", label: "Draft" },
  sent:     { bg: "rgba(37,99,235,.10)", text: "#2563eb", label: "Sent" },
  approved: { bg: "rgba(22,163,74,.10)", text: "#16a34a", label: "Approved" },
  declined: { bg: "rgba(220,38,38,.10)", text: "#dc2626", label: "Declined" },
};

function relativeTime(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return mins <= 1 ? "Just now" : `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "Yesterday";
  if (days < 30) return `${days} days ago`;
  return new Date(iso).toLocaleDateString();
}

function complaintLabel(type: string | null): string {
  const MAP: Record<string, string> = {
    not_cooling: "Not Cooling",
    not_heating: "Not Heating",
    water_dripping: "Water Dripping",
    not_turning_on: "Not Turning On",
    making_noise: "Making Noise",
    high_electric_bill: "High Electric Bill",
    error_code: "Error Code",
    intermittent_shutdown: "Intermittent Shutdown",
    service: "Service / Tune-Up",
  };
  return type ? (MAP[type] ?? type) : "";
}

// ── HVAC placeholder icon (gray, 80x80) ──────────────────────────────────────
function HvacPlaceholder() {
  return (
    <div style={{
      width: 80, height: 80, borderRadius: 8, background: "#f1f5f9",
      display: "flex", alignItems: "center", justifyContent: "center",
      flexShrink: 0,
    }}>
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
        stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="6" width="20" height="12" rx="2"/>
        <path d="M12 10v4M8 12h8"/>
        <circle cx="19" cy="5" r="1" fill="#94a3b8"/>
      </svg>
    </div>
  );
}

export default function AssessmentListRow({ item }: { item: AssessmentItem }) {
  const st = STATUS_STYLE[item.status ?? "draft"] ?? STATUS_STYLE.draft;
  const unitDesc = [item.brand, item.model].filter(Boolean).join(" ") || null;
  const complaint = complaintLabel(item.complaint_type);

  return (
    <Link href={`/assessment/${item.id}`} style={{ textDecoration: "none" }}>
      <div style={{
        display: "flex", gap: 14, alignItems: "flex-start",
        padding: "14px 16px",
        background: "#fff",
        border: "1px solid #e2e8f0",
        borderRadius: 10,
        cursor: "pointer",
        transition: "box-shadow 0.15s",
      }}
        onMouseEnter={e => (e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,.08)")}
        onMouseLeave={e => (e.currentTarget.style.boxShadow = "none")}
      >
        {/* Photo or placeholder */}
        {item.nameplate_photo_url ? (
          <img
            src={item.nameplate_photo_url}
            alt="Nameplate"
            style={{ width: 80, height: 80, borderRadius: 8, objectFit: "cover", flexShrink: 0 }}
          />
        ) : (
          <HvacPlaceholder />
        )}

        {/* Text content */}
        <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 3 }}>
          {/* Customer name (bold) or unit description */}
          <div style={{ fontWeight: 700, fontSize: 14, color: "#0f172a", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {item.customer_name ?? unitDesc ?? "Assessment"}
          </div>

          {/* Address or unit */}
          {item.customer_address && (
            <div style={{ fontSize: 13, color: "#64748b", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {item.customer_address}
            </div>
          )}
          {!item.customer_address && unitDesc && (
            <div style={{ fontSize: 13, color: "#64748b" }}>{unitDesc}</div>
          )}

          {/* Fault name (resolved) or complaint type (symptom) */}
          {(item.fault_name || complaint) && (
            <div style={{ fontSize: 13, color: "#334155" }}>
              {item.fault_name ?? complaint}
            </div>
          )}

          {/* Status badge + time */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 2 }}>
            <span style={{
              padding: "2px 8px", borderRadius: 99, fontSize: 11, fontWeight: 600,
              background: st.bg, color: st.text,
            }}>
              {st.label}
            </span>
            <span style={{ fontSize: 12, color: "#94a3b8" }}>
              {relativeTime(item.created_at)}
            </span>
          </div>
        </div>

        {/* Chevron */}
        <div style={{ color: "#cbd5e1", fontSize: 18, lineHeight: 1, alignSelf: "center", flexShrink: 0 }}>
          {">"}
        </div>
      </div>
    </Link>
  );
}
