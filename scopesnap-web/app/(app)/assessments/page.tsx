"use client";
/**
 * /assessments — Assessment list view (Track DX.2)
 *
 * Replaces the old wizard that lived at this URL.
 * The wizard moved to /assessments/new (which redirects to /assess).
 *
 * Shows all assessments for the contractor's company, newest first.
 * Tap a row -> /assessment/[id] (the estimate builder).
 * Tap "+ New Assessment" -> /assessments/new -> /assess.
 */

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import AssessmentListRow, { type AssessmentItem } from "@/components/AssessmentListRow";

const PAGE_SIZE = 20;

// ── Skeleton row (loading state) ──────────────────────────────────────────────
function SkeletonRow() {
  return (
    <div style={{
      display: "flex", gap: 14, padding: "14px 16px",
      background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10,
    }}>
      <div style={{ width: 80, height: 80, borderRadius: 8, background: "#f1f5f9", flexShrink: 0 }} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8, justifyContent: "center" }}>
        <div style={{ height: 14, width: "55%", background: "#f1f5f9", borderRadius: 4 }} />
        <div style={{ height: 12, width: "40%", background: "#f1f5f9", borderRadius: 4 }} />
        <div style={{ height: 12, width: "30%", background: "#f1f5f9", borderRadius: 4 }} />
      </div>
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────────
function EmptyState() {
  return (
    <div style={{
      textAlign: "center", padding: "64px 24px",
      background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10,
    }}>
      <div style={{ fontSize: 40, marginBottom: 16 }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none"
          stroke="#cbd5e1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
          style={{ display: "block", margin: "0 auto" }}>
          <rect x="2" y="6" width="20" height="12" rx="2"/>
          <path d="M12 10v4M8 12h8"/>
        </svg>
      </div>
      <div style={{ fontWeight: 700, fontSize: 16, color: "#0f172a", marginBottom: 8 }}>
        No assessments yet
      </div>
      <div style={{ fontSize: 14, color: "#64748b", marginBottom: 24 }}>
        Tap <strong>+ New Assessment</strong> to create your first one.
      </div>
      <Link
        href="/assessments/new"
        style={{
          display: "inline-block", padding: "12px 24px",
          background: "#16a34a", color: "#fff",
          borderRadius: 8, fontWeight: 700, fontSize: 14,
          textDecoration: "none",
        }}
      >
        + New Assessment
      </Link>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function AssessmentsPage() {
  const { getToken, isLoaded } = useAuth();
  const [items, setItems] = useState<AssessmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const fetchPage = useCallback(async (pageOffset: number, append: boolean) => {
    if (!isLoaded) return;
    if (append) setLoadingMore(true);
    else setLoading(true);

    try {
      const token = await getToken();
      const data = await apiFetch<{ items: AssessmentItem[]; total: number }>(
        `/api/assessments/?limit=${PAGE_SIZE}&offset=${pageOffset}`,
        { token: token ?? undefined }
      );
      const newItems = data.items ?? [];
      setItems(prev => append ? [...prev, ...newItems] : newItems);
      setHasMore(newItems.length === PAGE_SIZE);
      setOffset(pageOffset + newItems.length);
    } catch {
      setError("Could not load assessments. Check your connection and try again.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [isLoaded, getToken]);

  useEffect(() => {
    fetchPage(0, false);
  }, [fetchPage]);

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "24px 16px", display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 800, color: "#0f172a" }}>
          Assessments
        </h1>
        <Link
          href="/assessments/new"
          style={{
            padding: "10px 20px", background: "#16a34a", color: "#fff",
            borderRadius: 8, fontWeight: 700, fontSize: 14,
            textDecoration: "none", whiteSpace: "nowrap",
          }}
        >
          + New Assessment
        </Link>
      </div>

      {/* Loading state */}
      {loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div style={{
          padding: "16px", background: "rgba(220,38,38,.06)",
          border: "1px solid rgba(220,38,38,.2)", borderRadius: 8,
          fontSize: 14, color: "#dc2626", textAlign: "center",
        }}>
          {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && items.length === 0 && <EmptyState />}

      {/* List */}
      {!loading && !error && items.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {items.map(item => (
            <AssessmentListRow key={item.id} item={item} />
          ))}

          {/* Load more */}
          {hasMore && (
            <button
              onClick={() => fetchPage(offset, true)}
              disabled={loadingMore}
              style={{
                padding: "12px", borderRadius: 8,
                border: "1px solid #e2e8f0", background: "#fff",
                color: "#475569", fontSize: 14, fontWeight: 600,
                cursor: loadingMore ? "not-allowed" : "pointer",
                opacity: loadingMore ? 0.6 : 1,
              }}
            >
              {loadingMore ? "Loading…" : "Load More"}
            </button>
          )}
        </div>
      )}

    </div>
  );
}
