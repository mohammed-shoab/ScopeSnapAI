"use client";

/**
 * /diagnoses — Diagnosis history list (Track D, D.8)
 * Fetches paginated list from GET /api/diagnostic/list.
 * Layout: page header + "New Diagnosis" CTA + scrollable list rows + Load More.
 */

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { apiFetch } from "@/lib/api";
import { trackEvent } from "@/lib/tracking";
import DiagnosisListRow, { type DiagnosisListItem } from "@/components/DiagnosisListRow";
import DiagnosisListEmptyState from "@/components/DiagnosisListEmptyState";

interface ListResponse {
  items: DiagnosisListItem[];
  next_cursor: string | null;
  has_more: boolean;
}

export default function DiagnosesPage() {
  const router = useRouter();
  const { getToken, isLoaded } = useAuth();
  const [items, setItems] = useState<DiagnosisListItem[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPage = useCallback(async (cursor?: string) => {
    const params = new URLSearchParams({ limit: "20" });
    if (cursor) params.set("cursor", cursor);
    const token = await getToken();
    const data: ListResponse = await apiFetch(`/api/diagnostic/list?${params}`, { token: token ?? undefined });
    return data;
  }, [getToken]);

  useEffect(() => {
    // BUG-024: wait for Clerk to finish loading before calling getToken()
    // Without this guard, getToken() returns null on first render and the
    // request goes out with no Authorization header → 401 → "Could not load"
    if (!isLoaded) return;
    trackEvent("diagnosis_list_opened", {});
    fetchPage()
      .then((data) => {
        setItems(data.items);
        setNextCursor(data.next_cursor);
        setHasMore(data.has_more);
      })
      .catch(() => setError("Could not load diagnoses."))
      .finally(() => setLoading(false));
  }, [fetchPage, isLoaded]);

  async function handleLoadMore() {
    if (!nextCursor || loadingMore) return;
    setLoadingMore(true);
    try {
      const data = await fetchPage(nextCursor);
      setItems((prev) => [...prev, ...data.items]);
      setNextCursor(data.next_cursor);
      setHasMore(data.has_more);
    } catch {
      setError("Could not load more.");
    } finally {
      setLoadingMore(false);
    }
  }

  function handleRowClick(sessionId: string) {
    router.push(`/diagnoses/${sessionId}`);
  }

  function handleNewDiagnosis() {
    router.push("/assess");
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div style={{ maxWidth: 672, margin: "0 auto", padding: "16px 16px 40px" }}>

      {/* Page header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: "#0f172a" }}>Diagnoses</h1>
        <button
          onClick={handleNewDiagnosis}
          style={{
            padding: "9px 18px", borderRadius: 8, border: "none",
            background: "#1e293b", color: "#fff", fontSize: 13,
            fontWeight: 700, cursor: "pointer",
          }}
        >
          + New Diagnosis
        </button>
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[1, 2, 3].map((n) => (
            <div key={n} style={{
              height: 104, borderRadius: 10, background: "#f1f5f9",
              animation: "pulse 1.5s ease-in-out infinite",
            }} />
          ))}
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div style={{ textAlign: "center", color: "#dc2626", fontSize: 14, padding: "32px 0" }}>{error}</div>
      )}

      {/* Empty state */}
      {!loading && !error && items.length === 0 && (
        <DiagnosisListEmptyState onNewDiagnosis={handleNewDiagnosis} />
      )}

      {/* List */}
      {!loading && items.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {items.map((item) => (
            <DiagnosisListRow key={item.session_id} item={item} onClick={handleRowClick} />
          ))}

          {/* Load More */}
          {hasMore && (
            <button
              onClick={handleLoadMore}
              disabled={loadingMore}
              style={{
                marginTop: 8, padding: "12px 0", width: "100%", borderRadius: 8,
                border: "1.5px solid #e2e8f0", background: "#fff",
                color: "#475569", fontSize: 14, fontWeight: 600,
                cursor: loadingMore ? "not-allowed" : "pointer",
              }}
            >
              {loadingMore ? "Loading..." : "Load more"}
            </button>
          )}
        </div>
      )}

    </div>
  );
}
