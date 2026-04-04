"use client";
/**
 * SnapAI — Dashboard (Beta)
 * SOW Task 1.7: Simplified beta dashboard — 3 elements only.
 *
 * Elements:
 *  1. Hero CTA — prompt to start first assessment (or "New Assessment" if they have some)
 *  2. Recent Assessments — last 5 assessment cards from real API data
 *  3. Dynamic Stats Line — derived from live data, no hardcoded numbers
 *
 * Removed for beta (feature-flagged for later phases):
 *  - Profit Leaks widget ($70K mock)
 *  - Tech Accuracy Scores (mock data)
 *  - BenchmarkIQ panel (mock data)
 *  - Equipment Aging Alerts (mock data)
 *  - Action Alert card (hardcoded coil replacement warning)
 *  - Four-stat card grid with trend copy
 *  - Date range picker
 */

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";

// ── Types ─────────────────────────────────────────────────────────────────────
interface EstimateItem {
  id: string;
  report_short_id: string;
  status: string;
  total_amount?: number;
  created_at?: string;
  customer_name?: string;
  customer_address?: string;
}

interface CompanyStatus {
  plan: string;
  name: string;
  phone?: string | null;
  license_number?: string | null;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  approved:  { bg: "bg-green-100",  text: "text-green-700" },
  completed: { bg: "bg-green-100",  text: "text-green-700" },
  viewed:    { bg: "bg-blue-100",   text: "text-blue-700" },
  sent:      { bg: "bg-gray-100",   text: "text-gray-600" },
  pending:   { bg: "bg-yellow-100", text: "text-yellow-700" },
  analyzed:  { bg: "bg-blue-100",   text: "text-blue-700" },
  estimated: { bg: "bg-yellow-100", text: "text-yellow-700" },
  draft:     { bg: "bg-gray-100",   text: "text-gray-500" },
};

function fmt(n?: number) {
  if (!n) return "—";
  return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function timeAgo(dateStr?: string) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 2) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const { getToken } = useAuth();
  const [estimates, setEstimates]   = useState<EstimateItem[]>([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState<string | null>(null);
  const [company, setCompany]       = useState<CompanyStatus | null>(null);

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);

  useEffect(() => {
    const load = async () => {
      const headers = await getAuthHeaders();
      // Load company profile (for setup banner)
      fetch(`${API_URL}/api/auth/me`, { headers })
        .then((r) => r.json())
        .then((data) => setCompany(data.company ?? null))
        .catch(() => {});

      // Load recent assessments (limit 5 for dashboard)
      fetch(`${API_URL}/api/estimates/?limit=5`, { headers })
        .then((r) => r.json())
        .then((data) => {
          const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : [];
          setEstimates(list);
          setLoading(false);
        })
        .catch((e) => {
          setError("Could not reach the API");
          setLoading(false);
          console.error(e);
        });
    };
    load();
  }, [getAuthHeaders]);

  // ── Derived stats (only from real data, no hardcoding) ────────────────────
  const safe = Array.isArray(estimates) ? estimates : [];
  const closedCount = safe.filter((e) => ["approved", "completed"].includes(e.status)).length;
  const closeRate   = safe.length > 0 ? Math.round((closedCount / safe.length) * 100) : null;
  const totalValue  = safe.reduce((sum, e) => sum + (e.total_amount ?? 0), 0);
  const avgTicket   = safe.length > 0 ? Math.round(totalValue / safe.length) : null;

  const hasEstimates = safe.length > 0;
  const isFirstTime  = !loading && !error && !hasEstimates;

  return (
    <div className="max-w-2xl mx-auto py-4">

      {/* ── Setup Banner (shown if profile incomplete) ─────────────────────── */}
      {company && (!company.phone || !company.license_number) && (
        <Link
          href="/settings"
          className="flex items-center gap-3 bg-brand-green/5 border border-brand-green/25 rounded-2xl px-4 py-3 mb-6 hover:bg-brand-green/10 transition-colors"
        >
          <span className="text-xl">🚀</span>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-sm">Finish your company profile</p>
            <p className="text-xs text-text-secondary">Add your phone and license number so they appear on reports.</p>
          </div>
          <span className="text-brand-green font-bold text-sm flex-shrink-0">Set up →</span>
        </Link>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          ELEMENT 1 — Hero CTA
      ══════════════════════════════════════════════════════════════════════ */}
      {isFirstTime ? (
        /* First-time state: no assessments yet */
        <div
          className="rounded-2xl px-6 py-10 mb-6 text-center"
          style={{ background: "linear-gradient(135deg, #0f5c38 0%, #0d4a2e 100%)" }}
        >
          <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-4">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
          </div>
          <h2 className="text-white font-bold text-xl mb-2">Take your first assessment</h2>
          <p className="text-white/70 text-sm mb-6 max-w-xs mx-auto">
            Photograph any HVAC unit. AI identifies the equipment and generates Good / Better / Best pricing in seconds.
          </p>
          <Link
            href="/assess"
            className="inline-flex items-center gap-2 bg-white text-brand-green font-bold px-6 py-3 rounded-xl text-sm hover:bg-white/90 transition-colors"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7.25" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.6"/>
              <path d="M8 5v6M5 8h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            New Assessment
          </Link>
        </div>
      ) : (
        /* Returning user: quick action card */
        <div
          className="rounded-2xl px-5 py-5 mb-6 flex items-center justify-between gap-4"
          style={{ background: "linear-gradient(135deg, #0f5c38 0%, #0d4a2e 100%)" }}
        >
          <div className="min-w-0">
            <p className="text-white/70 text-xs font-semibold uppercase tracking-wider mb-1">Ready for your next job?</p>
            <p className="text-white font-bold text-lg leading-snug">Start a new assessment</p>
            <p className="text-white/60 text-xs mt-0.5">90 seconds · AI-powered · Good / Better / Best</p>
          </div>
          <Link
            href="/assess"
            className="flex-shrink-0 inline-flex items-center gap-1.5 bg-white text-brand-green font-bold px-4 py-2.5 rounded-xl text-sm hover:bg-white/90 transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7.25" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.6"/>
              <path d="M8 5v6M5 8h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Assess
          </Link>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          ELEMENT 2 — Recent Assessments (last 5)
      ══════════════════════════════════════════════════════════════════════ */}
      <div className="bg-white border border-surface-border rounded-2xl overflow-hidden mb-4">
        <div className="px-5 py-4 border-b border-surface-border flex items-center justify-between">
          <h2 className="font-bold text-base">Recent Assessments</h2>
          {hasEstimates && (
            <Link href="/estimates" className="text-xs text-brand-green font-semibold hover:underline">
              View all →
            </Link>
          )}
        </div>

        {/* Loading state */}
        {loading && (
          <div className="px-5 py-8 flex items-center justify-center gap-3 text-text-secondary text-sm">
            <div className="w-5 h-5 border-2 border-brand-green border-t-transparent rounded-full animate-spin" />
            Loading assessments…
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="px-5 py-6 text-center">
            <p className="text-sm font-medium text-gray-700 mb-1">API offline</p>
            <p className="text-xs text-text-secondary font-mono">{error}</p>
          </div>
        )}

        {/* Empty state — SOW Task 1.7 / Jobs req: line illustration of phone photographing HVAC unit */}
        {!loading && !error && !hasEstimates && (
          <div className="px-5 py-10 text-center flex flex-col items-center gap-4">
            {/* Monochrome SnapAI blue illustration: phone + viewfinder + HVAC unit */}
            <svg
              width="96" height="116" viewBox="0 0 96 116"
              fill="none" xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              {/* Phone body */}
              <rect x="14" y="4" width="68" height="108" rx="10" stroke="#1565C0" strokeWidth="2.5"/>
              {/* Speaker pill */}
              <rect x="36" y="11" width="24" height="4" rx="2" fill="#1565C0" opacity="0.35"/>
              {/* Home indicator */}
              <rect x="38" y="101" width="20" height="3" rx="1.5" fill="#1565C0" opacity="0.4"/>
              {/* Screen background */}
              <rect x="21" y="22" width="54" height="72" rx="4" fill="#EEF4FC"/>
              {/* Viewfinder corner brackets */}
              <path d="M25 30 L25 23 L32 23" stroke="#1565C0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M71 30 L71 23 L64 23" stroke="#1565C0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M25 86 L25 93 L32 93" stroke="#1565C0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M71 86 L71 93 L64 93" stroke="#1565C0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              {/* HVAC unit body */}
              <rect x="27" y="42" width="42" height="28" rx="3" stroke="#1565C0" strokeWidth="1.8"/>
              {/* Fan circle */}
              <circle cx="48" cy="56" r="9" stroke="#1565C0" strokeWidth="1.5"/>
              {/* Fan blades (4 arcs) */}
              <path d="M48 47 Q52 51 48 56" stroke="#1565C0" strokeWidth="1.2" strokeLinecap="round"/>
              <path d="M57 56 Q53 60 48 56" stroke="#1565C0" strokeWidth="1.2" strokeLinecap="round"/>
              <path d="M48 65 Q44 61 48 56" stroke="#1565C0" strokeWidth="1.2" strokeLinecap="round"/>
              <path d="M39 56 Q43 52 48 56" stroke="#1565C0" strokeWidth="1.2" strokeLinecap="round"/>
              {/* Vent slats below fan */}
              <line x1="29" y1="74" x2="67" y2="74" stroke="#1565C0" strokeWidth="1.2" strokeDasharray="4 3" strokeLinecap="round"/>
              {/* Model plate (right side of unit) */}
              <rect x="60" y="46" width="7" height="10" rx="1" stroke="#1565C0" strokeWidth="1" opacity="0.5"/>
              {/* Camera shutter button on phone edge */}
              <rect x="82" y="40" width="3.5" height="12" rx="1.75" fill="#1565C0" opacity="0.6"/>
            </svg>
            <div>
              <p className="text-text-primary font-semibold text-sm">Your first assessment is 3 taps away</p>
              <p className="text-text-secondary text-xs mt-1">Tap Assess, snap a photo, get an estimate.</p>
            </div>
          </div>
        )}

        {/* Assessment cards */}
        {!loading && !error && hasEstimates && (
          <div className="divide-y divide-surface-border">
            {safe.slice(0, 5).map((est) => {
              const badge = STATUS_COLORS[est.status] ?? STATUS_COLORS.draft;
              return (
                <Link
                  key={est.id}
                  href={`/estimate/${est.id}`}
                  className="flex items-center gap-3 px-5 py-4 hover:bg-surface-bg transition-colors"
                >
                  {/* Icon */}
                  <div className="w-10 h-10 rounded-xl bg-brand-green/8 flex items-center justify-center flex-shrink-0 border border-brand-green/12">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a8754" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                  </div>

                  {/* Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-mono font-bold text-sm">{est.report_short_id}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${badge.bg} ${badge.text}`}>
                        {capitalize(est.status)}
                      </span>
                    </div>
                    <p className="text-xs text-text-secondary truncate">
                      {est.customer_name || "Customer"}{est.customer_address ? ` · ${est.customer_address}` : ""}
                    </p>
                  </div>

                  {/* Amount + time */}
                  <div className="text-right flex-shrink-0">
                    <p className="font-bold text-sm font-mono">{fmt(est.total_amount)}</p>
                    <p className="text-[10px] text-text-secondary mt-0.5">{timeAgo(est.created_at)}</p>
                  </div>

                  <span className="text-text-secondary text-lg ml-1">›</span>
                </Link>
              );
            })}
          </div>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════════════════════
          ELEMENT 3 — Dynamic Stats Line
          Only shown once there is real data to display.
      ══════════════════════════════════════════════════════════════════════ */}
      {hasEstimates && (
        <div className="bg-white border border-surface-border rounded-2xl px-5 py-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-text-secondary mb-3">
            Last {safe.length} Assessment{safe.length !== 1 ? "s" : ""}
          </p>
          <div className="flex items-center gap-0 divide-x divide-surface-border">
            {/* Total sent */}
            <div className="flex-1 text-center pr-4">
              <p className="font-bold text-xl font-mono">{safe.length}</p>
              <p className="text-[10px] text-text-secondary mt-0.5">Sent</p>
            </div>

            {/* Close rate */}
            {closeRate !== null && (
              <div className="flex-1 text-center px-4">
                <p className="font-bold text-xl font-mono text-brand-green">{closeRate}%</p>
                <p className="text-[10px] text-text-secondary mt-0.5">Close Rate</p>
              </div>
            )}

            {/* Avg ticket */}
            {avgTicket !== null && avgTicket > 0 && (
              <div className="flex-1 text-center pl-4">
                <p className="font-bold text-xl font-mono">{fmt(avgTicket)}</p>
                <p className="text-[10px] text-text-secondary mt-0.5">Avg Ticket</p>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
