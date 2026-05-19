"use client";

/**
 * /d/[share_token] — Public share route (Track D, D.9)
 * Unauthenticated. Fetches from GET /api/diagnostic/public/{share_token}.
 * Renders FaultResolutionScreen in public mode (no PII, no action buttons).
 */

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { trackEvent } from "@/lib/tracking";
import FaultResolutionScreen, { type DiagnosticResult } from "@/components/FaultResolutionScreen";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function PublicSharePage() {
  const { share_token } = useParams<{ share_token: string }>();
  const [data, setData] = useState<DiagnosticResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!share_token) return;
    // No auth header — this is a public endpoint
    fetch(`${API_URL}/api/diagnostic/public/${share_token}`)
      .then(async (res) => {
        if (!res.ok) {
          if (res.status === 404) throw new Error("not_found");
          throw new Error("server_error");
        }
        return res.json();
      })
      .then((res: DiagnosticResult) => {
        setData(res);
        trackEvent("diagnosis_share_opened_externally", { share_token });
      })
      .catch((err) => {
        if (err.message === "not_found") setError("This diagnosis link is not valid or has expired.");
        else setError("Could not load the shared diagnosis.");
      })
      .finally(() => setLoading(false));
  }, [share_token]);

  if (loading) return (
    <div style={{ maxWidth: 672, margin: "40px auto", padding: "0 16px" }}>
      <div style={{ height: 32, width: 200, background: "#f1f5f9", borderRadius: 6, marginBottom: 16 }} />
      <div style={{ height: 200, background: "#f1f5f9", borderRadius: 10 }} />
    </div>
  );

  if (error) return (
    <div style={{ maxWidth: 480, margin: "80px auto", padding: "0 24px", textAlign: "center" }}>
      <div style={{ fontSize: 40, marginBottom: 16 }}>&#x26A0;&#xFE0F;</div>
      <h2 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", marginBottom: 8 }}>Link not found</h2>
      <p style={{ fontSize: 14, color: "#64748b" }}>{error}</p>
    </div>
  );

  if (!data) return null;

  return (
    <div>
      {/* Minimal public header */}
      <div style={{ borderBottom: "1px solid #e2e8f0", padding: "12px 20px", display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ fontWeight: 700, fontSize: 15, color: "#0f172a" }}>SnapAI</span>
        <span style={{ fontSize: 12, color: "#94a3b8" }}>Diagnostic Report</span>
      </div>
      <FaultResolutionScreen data={data} mode="public" />
    </div>
  );
}
