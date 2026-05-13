/**
 * Screen — Profit Leaks (WP-15)
 * Shows the contractor where revenue is being lost:
 *  - Sent estimates that were never approved (revenue left on table)
 *  - Homeowners who chose "good" when "better" was recommended (upsell gap)
 *  - Drafts that were never sent (stalled pipeline)
 *  - Low-markup jobs (margin leaks)
 *  - Slow send time (quote-to-deliver lag)
 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import { formatCurrency } from "@/lib/market";

const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

interface Estimate {
  id: string;
  report_short_id: string;
  status: string;
  total_amount: number | null;
  markup_percent: number;
  selected_option: string | null;
  options: Array<{
    tier: string;
    total: number;
    name: string;
    energy_savings?: { annual_savings: number } | number;
  }>;
  created_at: string | null;
  sent_at: string | null;
  viewed_at: string | null;
  approved_at: string | null;
}

interface LeakBucket {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
  amount: number;
  count: number;
  severity: "high" | "medium" | "low";
  items: LeakItem[];
  cta?: string;
  ctaHref?: string;
}

interface LeakItem {
  id: string;
  label: string;
  sublabel: string;
  amount: number;
  badge?: string;
}

function fmt(n: number) {
  return formatCurrency(n);
}

function daysSince(dateStr: string | null): number {
  if (!dateStr) return 0;
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86400000);
}

function computeLeaks(estimates: Estimate[]): {
  buckets: LeakBucket[];
  totalLeak: number;
  totalOpportunity: number;
} {
  const now = Date.now();

  // ── Bucket 1: Sent but not approved (revenue on the table) ────────────────
  const sentNotApproved = estimates.filter(
    (e) => e.status === "sent" || e.status === "viewed"
  );
  const sentLeakAmount = sentNotApproved.reduce(
    (sum, e) => sum + (e.total_amount || 0),
    0
  );

  // ── Bucket 2: Drafts/estimated — never sent ────────────────────────────────
  const stalledDrafts = estimates.filter(
    (e) =>
      (e.status === "draft" || e.status === "estimated") &&
      daysSince(e.created_at) > 2
  );
  const stalledAmount = stalledDrafts.reduce(
    (sum, e) => sum + (e.total_amount || 0),
    0
  );

  // ── Bucket 3: Upsell gap (chose Good when Better was recommended) ─────────
  const upsellGap = estimates
    .filter((e) => {
      const chosen = e.selected_option || "good";
      const betterOpt = e.options.find((o) => o.tier === "better");
      const chosenOpt = e.options.find((o) => o.tier === chosen);
      return chosen === "good" && betterOpt && chosenOpt;
    })
    .map((e) => {
      const goodOpt = e.options.find((o) => o.tier === "good");
      const betterOpt = e.options.find((o) => o.tier === "better");
      return {
        estimate: e,
        gap: (betterOpt?.total || 0) - (goodOpt?.total || 0),
      };
    });
  const upsellAmount = upsellGap.reduce((sum, x) => sum + x.gap, 0);

  // ── Bucket 4: Low-markup jobs (< 25%) ────────────────────────────────────
  const lowMarkup = estimates.filter(
    (e) =>
      e.markup_percent < 25 &&
      e.status !== "draft" &&
      (e.total_amount || 0) > 0
  );
  const lowMarkupLeak = lowMarkup.reduce((sum, e) => {
    // Estimate extra revenue if markup was 35%
    const currentMarkup = e.markup_percent / 100;
    const subtotal = (e.total_amount || 0) / (1 + currentMarkup);
    const targetRevenue = subtotal * 1.35;
    return sum + (targetRevenue - (e.total_amount || 0));
  }, 0);

  // ── Bucket 5: Slow quote delivery (created > 24h before sent) ─────────────
  const slowQuotes = estimates.filter((e) => {
    if (!e.sent_at || !e.created_at) return false;
    const lag = new Date(e.sent_at).getTime() - new Date(e.created_at).getTime();
    return lag > 48 * 3600 * 1000; // > 48 hours
  });
  // Slow quotes don't lose exact dollar amount, but research shows 1-day lag
  // cuts close rate by ~30%. Estimate impact: 30% of revenue at risk.
  const slowQuoteLeak = slowQuotes.reduce(
    (sum, e) => sum + (e.total_amount || 0) * 0.3,
    0
  );

  const totalLeak = sentLeakAmount + stalledAmount + upsellAmount + lowMarkupLeak + slowQuoteLeak;
  const totalOpportunity = sentLeakAmount + stalledAmount + upsellAmount;

  const buckets: LeakBucket[] = [];

  if (sentNotApproved.length > 0) {
    buckets.push({
      id: "sent-pending",
      icon: "📤",
      title: "Assessments Awaiting Approval",
      subtitle: "Revenue sitting in homeowner inboxes — follow up now",
      amount: sentLeakAmount,
      count: sentNotApproved.length,
      severity: sentLeakAmount > 10000 ? "high" : sentLeakAmount > 3000 ? "medium" : "low",
      cta: "View Estimates",
      ctaHref: "/dashboard",
      items: sentNotApproved.slice(0, 5).map((e) => ({
        id: e.id,
        label: e.report_short_id,
        sublabel: `${e.status === "viewed" ? "Viewed" : "Sent"} ${daysSince(e.sent_at || e.created_at)}d ago`,
        amount: e.total_amount || 0,
        badge: e.status === "viewed" ? "👁 Viewed" : "📬 Sent",
      })),
    });
  }

  if (stalledDrafts.length > 0) {
    buckets.push({
      id: "stalled",
      icon: "⏸",
      title: "Stalled in Draft",
      subtitle: "Assessments created but never sent to homeowner",
      amount: stalledAmount,
      count: stalledDrafts.length,
      severity: stalledDrafts.length > 3 ? "high" : "medium",
      cta: "Send Now",
      ctaHref: "/dashboard",
      items: stalledDrafts.slice(0, 5).map((e) => ({
        id: e.id,
        label: e.report_short_id,
        sublabel: `Sitting for ${daysSince(e.created_at)} days`,
        amount: e.total_amount || 0,
        badge: `⏸ ${e.status}`,
      })),
    });
  }

  if (upsellGap.length > 0) {
    buckets.push({
      id: "upsell",
      icon: "📊",
      title: "Upsell Gap",
      subtitle: "Jobs where homeowner chose base option — upgrade revenue missed",
      amount: upsellAmount,
      count: upsellGap.length,
      severity: upsellAmount > 5000 ? "high" : "medium",
      items: upsellGap.slice(0, 5).map((x) => ({
        id: x.estimate.id,
        label: x.estimate.report_short_id,
        sublabel: "Chose Good → could have been Better",
        amount: x.gap,
        badge: "+$" + Math.round(x.gap).toLocaleString() + " if upgraded",
      })),
    });
  }

  if (lowMarkup.length > 0) {
    buckets.push({
      id: "low-margin",
      icon: "🔻",
      title: "Below-Target Margin",
      subtitle: `${lowMarkup.length} jobs priced under 25% markup — leaving money behind`,
      amount: lowMarkupLeak,
      count: lowMarkup.length,
      severity: "medium",
      items: lowMarkup.slice(0, 5).map((e) => ({
        id: e.id,
        label: e.report_short_id,
        sublabel: `${e.markup_percent}% markup — target is 35%`,
        amount: lowMarkupLeak / lowMarkup.length,
        badge: `${e.markup_percent}% margin`,
      })),
    });
  }

  if (slowQuotes.length > 0) {
    buckets.push({
      id: "slow-send",
      icon: "🐢",
      title: "Slow Quote Delivery",
      subtitle: "Delivered 48h+ after assessment — close rate drops ~30%",
      amount: slowQuoteLeak,
      count: slowQuotes.length,
      severity: "low",
      items: slowQuotes.slice(0, 5).map((e) => {
        const lagH = Math.round(
          (new Date(e.sent_at!).getTime() - new Date(e.created_at!).getTime()) / 3600000
        );
        return {
          id: e.id,
          label: e.report_short_id,
          sublabel: `Sent ${lagH}h after assessment`,
          amount: (e.total_amount || 0) * 0.3,
          badge: `${lagH}h lag`,
        };
      }),
    });
  }

  // If no leaks found, show empty state
  return { buckets, totalLeak, totalOpportunity };
}

const SEVERITY_COLORS = {
  high: "border-l-brand-red bg-red-50",
  medium: "border-l-yellow-400 bg-yellow-50",
  low: "border-l-blue-400 bg-blue-50",
};

const SEVERITY_BADGE = {
  high: "bg-brand-red text-white",
  medium: "bg-yellow-400 text-yellow-900",
  low: "bg-blue-100 text-blue-700",
};

const SEVERITY_LABEL = {
  high: "High Impact",
  medium: "Medium Impact",
  low: "Low Impact",
};

export default function ProfitLeaksPage() {
  const [estimates, setEstimates] = useState<Estimate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedBucket, setExpandedBucket] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/estimates/?limit=100`, { headers: DEV_HEADER })
      .then((r) => {
        if (!r.ok) throw new Error(`API error ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setEstimates(Array.isArray(data.items) ? data.items : []);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || "Could not load estimates.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-center text-text-secondary">
          <div className="w-6 h-6 border-2 border-brand-green border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Analyzing profit leaks...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-8 text-center">
        <p className="text-brand-red font-medium">⚠ {error}</p>
        <Link href="/dashboard" className="mt-4 inline-block text-brand-green text-sm font-medium">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  const { buckets, totalLeak, totalOpportunity } = computeLeaks(estimates);
  const approvedRevenue = estimates
    .filter((e) => e.status === "approved" || e.status === "deposit_paid" || e.status === "completed")
    .reduce((sum, e) => sum + (e.total_amount || 0), 0);

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-8">
      {/* Header */}
      <div className="pt-2">
        <div className="flex items-center gap-2 mb-1">
          <Link href="/dashboard" className="text-sm text-text-secondary hover:text-text-primary">
            ← Back
          </Link>
          <span className="text-text-secondary">/</span>
          <span className="text-sm text-text-secondary">Intelligence</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-text-primary mt-1">
          💰 Profit Leaks
        </h1>
        <p className="text-text-secondary text-sm mt-1">
          Where your revenue is slipping — and what to do about it
        </p>
      </div>

      {/* Hero Metric Strip */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-brand-red to-red-700 rounded-xl p-4 text-white">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-white/70 mb-1">
            Identified Leaks
          </p>
          <p className="text-3xl font-extrabold font-mono">{fmt(totalLeak)}</p>
          <p className="text-xs text-white/70 mt-1">{buckets.length} categories</p>
        </div>
        <div className="bg-white border border-surface-border rounded-xl p-4">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-1">
            Recoverable Now
          </p>
          <p className="text-3xl font-extrabold font-mono text-brand-green">
            {fmt(totalOpportunity)}
          </p>
          <p className="text-xs text-text-secondary mt-1">Pending approvals + drafts</p>
        </div>
        <div className="bg-white border border-surface-border rounded-xl p-4">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-1">
            Approved Revenue
          </p>
          <p className="text-3xl font-extrabold font-mono text-text-primary">
            {fmt(approvedRevenue)}
          </p>
          <p className="text-xs text-text-secondary mt-1">All-time won jobs</p>
        </div>
      </div>

      {/* No leaks — great state */}
      {buckets.length === 0 && (
        <div className="card p-12 text-center space-y-3">
          <div className="text-5xl">🎯</div>
          <h2 className="text-xl font-extrabold text-brand-green">No Leaks Detected</h2>
          <p className="text-text-secondary text-sm max-w-sm mx-auto">
            All estimates are moving through the pipeline efficiently. Keep it up!
          </p>
          <p className="text-xs text-text-secondary">
            Run more assessments to keep this report populated.
          </p>
        </div>
      )}

      {/* Leak Buckets */}
      {buckets.map((bucket) => {
        const isExpanded = expandedBucket === bucket.id;
        return (
          <div
            key={bucket.id}
            className={`rounded-xl border-l-4 overflow-hidden ${SEVERITY_COLORS[bucket.severity]}`}
          >
            {/* Bucket Header */}
            <button
              onClick={() => setExpandedBucket(isExpanded ? null : bucket.id)}
              className="w-full text-left p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <span className="text-2xl leading-none mt-0.5">{bucket.icon}</span>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-base text-text-primary">{bucket.title}</h3>
                      <span
                        className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${SEVERITY_BADGE[bucket.severity]}`}
                      >
                        {SEVERITY_LABEL[bucket.severity]}
                      </span>
                    </div>
                    <p className="text-sm text-text-secondary mt-0.5">{bucket.subtitle}</p>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-2xl font-extrabold font-mono text-brand-red">
                    {fmt(bucket.amount)}
                  </p>
                  <p className="text-xs text-text-secondary mt-0.5">
                    {bucket.count} job{bucket.count !== 1 ? "s" : ""}
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-between mt-3">
                {bucket.cta && (
                  <Link
                    href={bucket.ctaHref || "#"}
                    onClick={(e) => e.stopPropagation()}
                    className="text-xs font-bold text-brand-green hover:underline"
                  >
                    {bucket.cta} →
                  </Link>
                )}
                <span className="text-xs text-text-secondary ml-auto">
                  {isExpanded ? "Hide details ▲" : `Show ${bucket.items.length} jobs ▼`}
                </span>
              </div>
            </button>

            {/* Expanded Items */}
            {isExpanded && bucket.items.length > 0 && (
              <div className="border-t border-white/60 bg-white/70">
                {bucket.items.map((item) => (
                  <Link
                    key={item.id}
                    href={`/assessment/${item.id}`}
                    className="flex items-center justify-between px-5 py-3 hover:bg-white/80 transition-colors border-b border-white/40 last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm font-bold text-brand-green">
                        {item.label}
                      </span>
                      <span className="text-xs text-text-secondary">{item.sublabel}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      {item.badge && (
                        <span className="text-xs font-semibold px-2 py-0.5 bg-white rounded-full border border-surface-border text-text-secondary">
                          {item.badge}
                        </span>
                      )}
                      <span className="font-mono font-bold text-sm text-text-primary">
                        {fmt(item.amount)}
                      </span>
                      <span className="text-text-secondary text-xs">↗</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Playbook Card */}
      {buckets.length > 0 && (
        <div className="card p-5">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-3">
            Recovery Playbook
          </p>
          <div className="space-y-3">
            {buckets.some((b) => b.id === "sent-pending") && (
              <div className="flex items-start gap-3">
                <span className="text-lg">1️⃣</span>
                <div>
                  <p className="font-semibold text-sm">Follow up on pending estimates today</p>
                  <p className="text-xs text-text-secondary">
                    A same-day call after viewing increases close rate by 40%. The "viewed" ones are
                    hot — call them first.
                  </p>
                </div>
              </div>
            )}
            {buckets.some((b) => b.id === "stalled") && (
              <div className="flex items-start gap-3">
                <span className="text-lg">2️⃣</span>
                <div>
                  <p className="font-semibold text-sm">Send stalled drafts immediately</p>
                  <p className="text-xs text-text-secondary">
                    Every day of delay reduces approval probability. Use the Output tab to generate
                    documents and send now.
                  </p>
                </div>
              </div>
            )}
            {buckets.some((b) => b.id === "slow-send") && (
              <div className="flex items-start gap-3">
                <span className="text-lg">3️⃣</span>
                <div>
                  <p className="font-semibold text-sm">Deliver quotes within 24 hours</p>
                  <p className="text-xs text-text-secondary">
                    Set a team rule: all assessments → estimates → sent same day or next morning.
                    SnapAI makes this easy.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Link to other intelligence pages */}
      <div className="grid grid-cols-2 gap-4">
        <Link
          href="/intelligence/benchmark"
          className="card p-4 flex items-center gap-3 hover:border-brand-green hover:shadow-sm transition-all"
        >
          <span className="text-2xl">📈</span>
          <div>
            <p className="font-bold text-sm">BenchmarkIQ</p>
            <p className="text-xs text-text-secondary">Compare your pricing to the market</p>
          </div>
        </Link>
        <Link
          href="/intelligence/history"
          className="card p-4 flex items-center gap-3 hover:border-brand-green hover:shadow-sm transition-all"
        >
          <span className="text-2xl">🏠</span>
          <div>
            <p className="font-bold text-sm">Property History</p>
            <p className="text-xs text-text-secondary">Full timeline per property</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
