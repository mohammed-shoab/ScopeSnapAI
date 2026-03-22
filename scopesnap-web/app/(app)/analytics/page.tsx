/**
 * Screen — Owner Analytics Dashboard (WP-14)
 * Accuracy Tracker: Shows AI accuracy, estimate funnel, conversion metrics, revenue trends, recent estimates.
 * Requires owner or admin role.
 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";

const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

interface MonthlyPoint {
  month: string;
  estimates: number;
  approved: number;
  revenue: number;
}

interface AnalyticsData {
  period_label: string;
  revenue: {
    total_all_time: number;
    this_period: number;
    avg_per_estimate: number;
    pending_deposits: number;
  };
  funnel: {
    total: number;
    sent: number;
    viewed: number;
    approved: number;
    deposit_paid: number;
  };
  conversion_rate: number;
  view_rate: number;
  ai_accuracy: number | null;
  properties: {
    total: number;
    repeat_customers: number;
  };
  monthly_trend: MonthlyPoint[];
  recent_estimates: Array<{
    id: string;
    report_short_id: string;
    status: string;
    total_amount: number | null;
    created_at: string | null;
    approved_at: string | null;
    viewed_at: string | null;
  }>;
}

function fmt(n?: number | null) {
  if (n === null || n === undefined) return "—";
  return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function pct(n?: number | null) {
  if (n === null || n === undefined) return "—";
  return n.toFixed(1) + "%";
}

function timeAgo(dateStr?: string | null) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  estimated: "bg-blue-50 text-blue-700",
  sent: "bg-orange-100 text-orange-600",
  viewed: "bg-blue-100 text-blue-600",
  approved: "bg-green-100 text-green-600",
  deposit_paid: "bg-emerald-100 text-emerald-600",
  completed: "bg-green-100 text-green-600",
};

function FunnelBar({
  label,
  count,
  total,
  color,
}: {
  label: string;
  count: number;
  total: number;
  color: string;
}) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-baseline gap-2">
        <span className="text-sm text-text-secondary">{label}</span>
        <span className="font-mono text-sm font-semibold text-text-primary">{count}</span>
      </div>
      <div className="h-3 bg-surface-secondary rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-right text-xs text-text-secondary font-mono">{percentage}%</div>
    </div>
  );
}

function MiniBarChart({ data }: { data: MonthlyPoint[] }) {
  const maxRevenue = Math.max(...data.map((d) => d.revenue), 1);
  return (
    <div className="flex items-end justify-between gap-2 h-32">
      {data.map((d, i) => (
        <div key={i} className="flex-1 flex flex-col items-center gap-2">
          <div
            className="w-full bg-brand-green rounded-t-sm opacity-85 transition-all duration-500"
            style={{ height: `${(d.revenue / maxRevenue) * 100}px`, minHeight: d.revenue > 0 ? 3 : 0 }}
            title={`${d.month}: ${fmt(d.revenue)}`}
          />
          <span className="text-xs text-text-secondary truncate w-full text-center leading-none font-mono">
            {d.month.slice(0, 3)}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/analytics/dashboard?days=${days}`, { headers: DEV_HEADER })
      .then((r) => {
        if (r.status === 403) throw new Error("Owner or admin access required.");
        if (!r.ok) throw new Error(`API error ${r.status}`);
        return r.json();
      })
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || "Could not load analytics.");
        setLoading(false);
      });
  }, [days]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-center text-text-secondary">
          <div className="w-6 h-6 border-2 border-brand-green border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading analytics...
        </div>
      </div>
    );
  }

  if (error) {
    const isAuthError = error.includes("Owner") || error.includes("admin") || error.includes("403");
    return (
      <div className="card p-8 text-center">
        <p className="text-brand-red font-medium">⚠ {error}</p>
        {isAuthError && (
          <p className="text-sm text-text-secondary mt-1">Only owners and admins can view analytics.</p>
        )}
        <Link href="/dashboard" className="mt-4 inline-block text-brand-green text-sm font-medium">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between pt-2 mb-2">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-text-primary">Accuracy Tracker</h1>
          <p className="text-text-secondary text-sm mt-1">Track how your estimates compare to actual job costs</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="text-sm border border-surface-border rounded-ss px-3 py-2.5 bg-white text-text-primary"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Hero Metric Card - AI Accuracy */}
      <div className="bg-gradient-to-br from-[#0f5c38] to-[#1a8754] rounded-ss shadow-ss overflow-hidden">
        <div className="px-6 py-8">
          <p className="text-[10px] font-bold uppercase tracking-widest font-mono text-white/70 mb-2">Overall AI Accuracy</p>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-4xl sm:text-6xl font-extrabold text-white font-mono">
              {data.ai_accuracy !== null ? data.ai_accuracy : "—"}
            </span>
            <span className="text-white/80 text-lg">%</span>
          </div>
          <p className="text-white/90 text-sm">Predicted vs Actual Cost Match</p>
        </div>
      </div>

      {/* 4-Stat Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Conversion Rate", value: pct(data.conversion_rate) },
          { label: "View Rate", value: pct(data.view_rate) },
          { label: "Total Properties", value: data.properties.total },
          { label: "Repeat Customers", value: data.properties.repeat_customers },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-ss shadow-ss border border-surface-border p-4">
            <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-2">
              {stat.label}
            </p>
            <p className="text-3xl font-extrabold text-text-primary font-mono">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Estimate Funnel Card */}
      <div className="bg-white rounded-ss shadow-ss border border-surface-border p-6">
        <div className="mb-1">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary">Estimate Funnel</p>
          <h2 className="text-lg font-bold text-text-primary mt-1 mb-6">Created → Sent → Viewed → Approved → Deposit Paid</h2>
        </div>
        <div className="space-y-5">
          <FunnelBar label="Created" count={data.funnel.total} total={data.funnel.total} color="bg-gray-400" />
          <FunnelBar label="Sent to Homeowner" count={data.funnel.sent} total={data.funnel.total} color="bg-orange-400" />
          <FunnelBar label="Viewed" count={data.funnel.viewed} total={data.funnel.total} color="bg-blue-400" />
          <FunnelBar label="Approved" count={data.funnel.approved} total={data.funnel.total} color="bg-brand-green" />
          <FunnelBar label="Deposit Paid" count={data.funnel.deposit_paid} total={data.funnel.total} color="bg-emerald-600" />
        </div>
      </div>

      {/* Revenue Overview Card */}
      <div className="bg-white rounded-ss shadow-ss border border-surface-border p-6">
        <div className="mb-6">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary">Revenue Overview</p>
          <h2 className="text-lg font-bold text-text-primary mt-1">Monthly Revenue Trend</h2>
        </div>
        <div className="space-y-6">
          <MiniBarChart data={data.monthly_trend} />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-surface-border">
            {[
              { label: "All-Time Revenue", value: fmt(data.revenue.total_all_time) },
              { label: "This Period", value: fmt(data.revenue.this_period) },
              { label: "Avg per Job", value: fmt(data.revenue.avg_per_estimate) },
              { label: "Pending Deposits", value: fmt(data.revenue.pending_deposits) },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-1">
                  {stat.label}
                </p>
                <p className="text-lg font-extrabold text-text-primary font-mono">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Estimates Table */}
      <div className="bg-white rounded-ss shadow-ss border border-surface-border overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-border">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-1">Recent Activity</p>
          <h2 className="text-lg font-bold text-text-primary">Recent Estimates</h2>
        </div>
        {data.recent_estimates.length === 0 ? (
          <div className="p-8 text-center text-text-secondary">No estimates yet.</div>
        ) : (
          <div className="divide-y divide-surface-border overflow-x-auto">
            <table className="w-full text-sm min-w-[300px]">
              <thead className="bg-surface-bg border-b border-surface-border">
                <tr>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">
                    Estimate ID
                  </th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">
                    Status
                  </th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">
                    Amount
                  </th>
                  <th className="px-3 md:px-6 py-3 text-left text-xs font-bold uppercase tracking-widest font-mono text-text-secondary hidden sm:table-cell">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.recent_estimates.map((est) => (
                  <tr key={est.id} className="hover:bg-surface-bg transition-colors">
                    <td className="px-3 md:px-6 py-4">
                      <Link href={`/estimate/${est.id}`} className="font-mono font-bold text-brand-green hover:underline">
                        {est.report_short_id}
                      </Link>
                    </td>
                    <td className="px-3 md:px-6 py-4">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full inline-block ${STATUS_COLORS[est.status] || "bg-gray-100 text-gray-600"}`}>
                        {est.status.charAt(0).toUpperCase() + est.status.slice(1).replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-3 md:px-6 py-4">
                      <p className="font-bold font-mono text-text-primary">{fmt(est.total_amount)}</p>
                    </td>
                    <td className="px-3 md:px-6 py-4 hidden sm:table-cell">
                      <p className="text-text-secondary font-mono">{timeAgo(est.created_at)}</p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
