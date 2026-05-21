"use client";

/**
 * DiagnosisListRow — Track D (D.8)
 * Single row in the /diagnoses history list.
 * Layout: [80x80 nameplate photo] | [fault name bold] [confidence badge]
 *                                   [customer label muted] [relative time muted]
 */

interface DiagnosisListItem {
  session_id: string;
  fault_name: string;
  confidence?: string | null;  // B.3: always "high"/null in production — not shown in list view
  customer_label: string | null;
  customer_address: string | null;  // B.2
  created_at: string;         // ISO 8601
  nameplate_photo_url: string | null;
  share_token: string | null;
}

interface Props {
  item: DiagnosisListItem;
  onClick: (sessionId: string) => void;
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const days = Math.floor(hr / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

export default function DiagnosisListRow({ item, onClick }: Props) {
  return (
    <button
      onClick={() => onClick(item.session_id)}
      style={{
        display: "flex", alignItems: "center", gap: 14,
        width: "100%", background: "#fff",
        border: "1px solid #e2e8f0", borderRadius: 10,
        padding: "12px 14px", cursor: "pointer", textAlign: "left",
      }}
    >
      {/* Nameplate photo — 80x80, gray fallback */}
      <div style={{
        width: 80, height: 80, borderRadius: 8, flexShrink: 0,
        background: "#f1f5f9", overflow: "hidden",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        {item.nameplate_photo_url ? (
          <img
            src={item.nameplate_photo_url}
            alt="Nameplate"
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <path d="m21 15-5-5L5 21"/>
          </svg>
        )}
      </div>

      {/* Text content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", lineHeight: 1.3 }}>
          {item.fault_name}
        </div>
        {item.customer_label && (
          <div style={{ fontSize: 13, color: "#0f172a", marginTop: 3, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {item.customer_label}
          </div>
        )}
        {item.customer_address && (
          <div style={{ fontSize: 12, color: "#64748b", marginTop: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {item.customer_address}
          </div>
        )}
        <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>
          {relativeTime(item.created_at)}
        </div>
      </div>

      {/* Chevron */}
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="2" style={{ flexShrink: 0 }}>
        <path d="m9 18 6-6-6-6"/>
      </svg>
    </button>
  );
}

export type { DiagnosisListItem };
