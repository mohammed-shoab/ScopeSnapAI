"use client";

/**
 * /diagnoses/[session_id] — Authenticated diagnosis detail (Track D, D.7)
 * Fetches from GET /api/diagnostic/result/{session_id} and renders FaultResolutionScreen.
 */

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { trackEvent } from "@/lib/tracking";
import FaultResolutionScreen, { type DiagnosticResult } from "@/components/FaultResolutionScreen";

export default function DiagnosisDetailPage() {
  const { session_id } = useParams<{ session_id: string }>();
  const [data, setData] = useState<DiagnosticResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session_id) return;
    apiFetch(`/api/diagnostic/result/${session_id}`)
      .then((res: DiagnosticResult) => {
        setData(res);
        // D.13: revisit tracking — if session is older than 5 minutes it's a revisit
        const age = res.created_at ? Date.now() - new Date(res.created_at).getTime() : 0;
        if (age > 300_000) {
          trackEvent("diagnosis_revisited", { session_id, age_ms: age });
        }
      })
      .catch((err) => {
        const status = err?.status ?? 0;
        if (status === 404) setError("Diagnosis not found.");
        else if (status === 409) setError("This diagnosis is not yet resolved.");
        else setError("Could not load diagnosis.");
      })
      .finally(() => setLoading(false));
  }, [session_id]);

  if (loading) return (
    <div style={{ maxWidth: 672, margin: "40px auto", padding: "0 16px" }}>
      <div style={{ height: 32, width: 180, background: "#f1f5f9", borderRadius: 6, marginBottom: 16 }} />
      <div style={{ height: 200, background: "#f1f5f9", borderRadius: 10 }} />
    </div>
  );

  if (error) return (
    <div style={{ maxWidth: 672, margin: "64px auto", padding: "0 16px", textAlign: "center", color: "#dc2626", fontSize: 15 }}>
      {error}
    </div>
  );

  if (!data) return null;

  return <FaultResolutionScreen data={data} mode="authenticated" />;
}
