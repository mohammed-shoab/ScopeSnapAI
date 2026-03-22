"use client";
// v2
import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";

interface EstimateItem {
  id: string;
  report_short_id: string;
  status: string;
  total_amount?: number;
  created_at?: string;
  approved_at?: string;
  viewed_at?: string;
  customer_name?: string;
  technician_name?: string;
}

interface CompanyStatus {
  plan: string;
  name: string;
  phone?: string | null;
  license_number?: string | null;
}

const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

const STATUS_BADGE_COLORS: Record<string, { bg: string; text: string }> = {
  approved: { bg: "bg-green-100", text: "text-green-700" },
  completed: { bg: "bg-green-100", text: "text-green-700" },
  pending: { bg: "bg-yellow-100", text: "text-yellow-700" },
  viewed: { bg: "bg-blue-100", text: "text-blue-700" },
  sent: { bg: "bg-gray-100", text: "text-gray-700" },
  draft: { bg: "bg-gray-100", text: "text-gray-700" },
  analyzed: { bg: "bg-blue-100", text: "text-blue-700" },
  estimated: { bg: "bg-yellow-100", text: "text-yellow-700" },
};

function fmt(n?: number) {
  if (!n) return "—";
  return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function timeAgo(dateStr?: string) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// Mock data for sections not yet wired to API
const mockTechAccuracy = [
  { name: "Mike Rodriguez", accuracy: 92, sub: "142 estimates · Top performer" },
  { name: "James Sullivan",  accuracy: 88, sub: "98 estimates · Improving" },
  { name: "Brian Kim",       accuracy: 84, sub: "115 estimates · Under-prices labor" },
  { name: "Javier Vasquez",  accuracy: 78, sub: "91 estimates · Needs coaching" },
];

const mockProfitLeaks = [
  { name: "Coil replacement labor under-estimated", impact: "-$28,200/yr" },
  { name: "R-410A refrigerant cost not updated",    impact: "-$18,900/yr" },
  { name: "Brian's system replacements under-priced", impact: "-$15,300/yr" },
  { name: "Permit costs not included in estimates",  impact: "-$8,160/yr" },
];

const mockEquipmentAging = [
  { name: "Carrier 24ABR",   detail: "18 properties · Avg age 17 yrs · Known compressor failures", status: "Critical" },
  { name: "Trane XR13",      detail: "14 properties · Avg age 16 yrs · Coil failures after yr 14", status: "Aging" },
  { name: "Goodman GSX13",   detail: "11 properties · Avg age 15 yrs · Refrigerant leak after yr 12", status: "Aging" },
];

const mockBenchmarks = [
  { label: "Revenue Per Truck", you: "$380K", avg: "$420K", top: "$520K", youColor: "#c4600a" },
  { label: "Average Ticket",    you: "$4,200", avg: "$3,800", top: "$5,100", youColor: "#1a8754" },
  { label: "Labor Cost %",      you: "38%",    avg: "32%",   top: "28%",   youColor: "#c62828" },
  { label: "Close Rate",        you: "62%",    avg: "51%",   top: "67%",   youColor: "#1a8754" },
];

export default function DashboardPage() {
  const [estimates, setEstimates] = useState<EstimateItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [company, setCompany] = useState<CompanyStatus | null>(null);
  const [dateRange, setDateRange] = useState("This Week");

  useEffect(() => {
    // Load company profile
    fetch(`${API_URL}/api/auth/me`, { headers: DEV_HEADER })
      .then((r) => r.json())
      .then((data) => setCompany(data.company || null))
      .catch(() => {});

    // Load estimates
    fetch(`${API_URL}/api/estimates/?limit=50`, { headers: DEV_HEADER })
      .then((r) => r.json())
      .then((data) => {
        const list = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : [];
        setEstimates(list);
        setLoading(false);
      })
      .catch((e) => {
        setError("Could not load estimates — is the API running?");
        setLoading(false);
        console.error(e);
      });
  }, []);

  // Calculate stats — defensive: ensure estimates is always an array
  const safeEstimates = Array.isArray(estimates) ? estimates : [];
  const estimatesThisWeek = safeEstimates.length;
  const closeRate = safeEstimates.length > 0 ? ((safeEstimates.filter((e) => ["approved", "completed"].includes(e.status)).length / safeEstimates.length) * 100).toFixed(0) : "0";
  const avgTicket = safeEstimates.length > 0 ? Math.round(safeEstimates.reduce((sum, e) => sum + (e.total_amount || 0), 0) / safeEstimates.length) : 0;
  const revenue = safeEstimates
    .filter((e) => ["approved", "completed"].includes(e.status))
    .reduce((sum, e) => sum + (e.total_amount || 0), 0);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-6">

        {/* 1. TOP BAR: Dashboard title + date range picker */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-extrabold tracking-tight" style={{ fontSize: "24px", fontWeight: 800 }}>
            Dashboard
          </h1>
          <button
            onClick={() => setDateRange(dateRange === "This Week" ? "This Month" : "This Week")}
            className="bg-white border border-gray-200 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            {dateRange} ▼
          </button>
        </div>

        {/* Setup Banner */}
        {company && (!company.phone || !company.license_number) && (
          <Link
            href="/onboarding"
            className="block bg-brand-green/5 border border-brand-green/30 rounded-2xl px-4 py-3 mb-8 hover:bg-brand-green/10 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">🚀</span>
              <div className="flex-1">
                <p className="font-semibold text-sm">Complete your company profile</p>
                <p className="text-xs text-text-secondary">Add your phone, license number, and address to appear on estimates.</p>
              </div>
              <span className="text-brand-green font-bold text-sm">Set up →</span>
            </div>
          </Link>
        )}

        {/* 2. HERO METRIC CARD */}
        <div
          className="rounded-2xl mb-8 flex items-center justify-between px-4 py-6 md:px-8 md:py-7 overflow-hidden"
          style={{
            background: "linear-gradient(135deg, #0f5c38 0%, #0d4a2e 100%)",
            borderRadius: "16px",
          }}
        >
          <div className="flex-1 min-w-0">
            <p className="text-white uppercase text-xs tracking-wide" style={{ opacity: 0.7, fontSize: "13px", fontWeight: 600 }}>
              Estimated Annual Profit Leak
            </p>
            <p className="font-bold text-white mt-2" style={{ fontFamily: "IBM Plex Mono", fontSize: "clamp(28px, 8vw, 48px)", fontWeight: 700 }}>
              $70,560
            </p>
            <p className="text-white text-sm mt-1" style={{ opacity: 0.8 }}>
              Your estimates are 14% below actual cost on average · <span style={{ opacity: 0.65 }}>That&apos;s $588 lost per job across 120 jobs/month</span>
            </p>
          </div>
          <Link
            href="/intelligence/leaks"
            className="flex px-4 py-2.5 text-white font-semibold text-sm border items-center gap-1 flex-shrink-0"
            style={{
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              borderColor: "rgba(255, 255, 255, 0.25)",
              borderRadius: "8px",
              fontSize: "13px",
            }}
          >
            View Details →
          </Link>
        </div>

        {/* 3. FOUR STAT CARDS GRID */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Estimates This Week", value: estimatesThisWeek, trend: "↑ 12% vs last week" },
            { label: "Close Rate",          value: `${closeRate}%`,  trend: "↑ 14pts since ScopeSnap" },
            { label: "Average Ticket",      value: fmt(avgTicket),   trend: "↑ $600 since Good/Better/Best" },
            { label: "Revenue",             value: fmt(revenue),     trend: "↑ 23% vs last week" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-white border border-gray-200 rounded-2xl p-5"
              style={{ borderRadius: "14px", padding: "18px 20px" }}
            >
              <p
                className="text-gray-600 uppercase font-semibold tracking-wider"
                style={{ fontSize: "11px", fontWeight: 600, letterSpacing: "0.5px" }}
              >
                {stat.label}
              </p>
              <p
                className="font-bold mt-2 text-gray-900"
                style={{ fontFamily: "IBM Plex Mono", fontSize: "28px", fontWeight: 700 }}
              >
                {stat.value}
              </p>
              <p className="text-xs text-gray-500 mt-1">{stat.trend}</p>
            </div>
          ))}
        </div>

        {/* 4. ACTION ALERT CARD */}
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-5 mb-8">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div className="flex-1">
              <h3 className="font-bold text-gray-900">Coil replacement jobs are under-estimated by 23%</h3>
              <p className="text-sm text-gray-700 mt-1">
                This is your biggest leak — coil jobs consistently take 2+ hours longer than estimated. Fix this and recover ~$28K/year.
              </p>
            </div>
            <button className="px-4 py-2 bg-orange-600 text-white text-sm font-semibold rounded-lg hover:bg-orange-700 transition-colors">
              Review
            </button>
          </div>
        </div>

        {/* 5. TWO-COLUMN LAYOUT */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

          {/* LEFT: Tech Accuracy Scores */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-bold text-gray-900">🎯 Tech Accuracy Scores</h3>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "#e8f0fe", color: "#1565c0" }}>LeakSense AI</span>
            </div>
            <div className="space-y-4">
              {mockTechAccuracy.map((tech) => {
                const barColor = tech.accuracy >= 90 ? "#1a8754" : tech.accuracy >= 85 ? "#1565c0" : tech.accuracy >= 80 ? "#c4600a" : "#c62828";
                return (
                  <div key={tech.name}>
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-sm font-semibold text-gray-900">{tech.name}</span>
                      <span className="text-sm font-bold text-gray-900" style={{ fontFamily: "IBM Plex Mono" }}>{tech.accuracy}%</span>
                    </div>
                    <p className="text-xs text-gray-500 mb-1.5">{tech.sub}</p>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{ width: `${tech.accuracy}%`, background: barColor }} />
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-5 bg-green-50 border border-green-100 rounded-lg p-3">
              <p className="text-xs font-bold text-green-800">💡 AI SUGGESTION</p>
              <p className="text-xs text-green-700 mt-1">Pair Javier with Mike for 5 ride-alongs on coil replacement jobs. Mike&apos;s labor estimates are 23% more accurate on these jobs.</p>
            </div>
          </div>

          {/* RIGHT: BenchmarkIQ Panel */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="font-bold text-gray-900">📈 BenchmarkIQ</h3>
                <p className="text-xs text-gray-500 mt-0.5">Houston Metro</p>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "#f3e8ff", color: "#6a1b9a" }}>vs 287 companies</span>
            </div>
            <div className="space-y-5">
              {mockBenchmarks.map((bm) => (
                <div key={bm.label}>
                  <p className="text-xs font-semibold text-gray-700 mb-1.5">{bm.label}</p>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="text-center">
                      <div className="font-bold font-mono" style={{ color: bm.youColor }}>{bm.you}</div>
                      <div className="text-gray-400 mt-0.5">You</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold font-mono text-gray-500">{bm.avg}</div>
                      <div className="text-gray-400 mt-0.5">Avg</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold font-mono" style={{ color: "#f9a825" }}>{bm.top}</div>
                      <div className="text-gray-400 mt-0.5">Top 25%</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 bg-purple-50 border border-purple-100 rounded-lg p-3">
              <p className="text-xs text-purple-800">Your close rate is top 10% in Houston. The homeowner visual reports are working. Focus on reducing labor cost % to improve revenue per truck.</p>
            </div>
          </div>
        </div>

        {/* 6. PROFIT LEAKS SECTION */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-bold text-gray-900">🔍 Top Profit Leaks Found</h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "#fee2e2", color: "#991b1b" }}>$70.5K/year</span>
          </div>
          <div className="space-y-3">
            {mockProfitLeaks.map((leak) => (
              <div key={leak.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                <p className="text-sm font-medium text-gray-900 flex-1 truncate mr-2 min-w-0">{leak.name}</p>
                <p className="text-sm font-bold text-red-600 font-mono flex-shrink-0">{leak.impact}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 7. EQUIPMENT AGING ALERTS */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">⚠️ Equipment Aging Alerts</h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "#fff7ed", color: "#c2410c" }}>43 properties</span>
          </div>
          {/* Campaign opportunity banner */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-4">
            <p className="text-xs font-bold text-orange-800">🎯 Replacement Campaign Opportunity</p>
            <p className="text-xs text-orange-700 mt-1">43 properties have AC units past 15-year mark. Estimated replacement revenue: $344,000 if 50% convert.</p>
          </div>
          <div className="space-y-3">
            {mockEquipmentAging.map((equipment) => (
              <div key={equipment.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">{equipment.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{equipment.detail}</p>
                </div>
                <span
                  className="px-3 py-1 rounded-full text-xs font-bold flex-shrink-0 ml-3"
                  style={{
                    backgroundColor: equipment.status === "Critical" ? "#fee2e2" : "#fef3c7",
                    color: equipment.status === "Critical" ? "#991b1b" : "#92400e",
                  }}
                >
                  {equipment.status.toUpperCase()}
                </span>
              </div>
            ))}
            <button
              className="w-full mt-2 py-2.5 text-sm font-semibold rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors"
            >
              📧 Generate Replacement Campaign →
            </button>
          </div>
        </div>

        {/* 8. RECENT ESTIMATES TABLE */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
            <h3 className="font-bold text-gray-900">Recent Estimates</h3>
            {!loading && safeEstimates.length > 0 && (
              <span className="text-xs text-gray-500 font-mono">{safeEstimates.length} total</span>
            )}
          </div>

          {loading && (
            <div className="p-8 text-center text-gray-500">
              <div className="spinner w-6 h-6 border-2 border-brand-green border-t-transparent rounded-full mx-auto mb-2" />
              Loading estimates...
            </div>
          )}

          {error && (
            <div className="p-6 text-center">
              <p className="text-brand-red font-medium mb-1">⚠ API Offline</p>
              <p className="text-sm text-gray-500">{error}</p>
              <p className="text-xs text-gray-500 mt-1 font-mono">
                Start: cd scopesnap-api && uvicorn main:app --port 8001
              </p>
            </div>
          )}

          {!loading && !error && safeEstimates.length === 0 && (
            <div className="p-10 text-center text-gray-500">
              <div className="text-4xl mb-3">📋</div>
              <p className="font-medium text-gray-900">No estimates yet</p>
              <p className="text-sm mt-1 mb-4">Tap "New Job" to create your first assessment.</p>
              <Link
                href="/assess"
                className="inline-block bg-brand-green text-white font-bold px-5 py-2.5 rounded-xl text-sm"
              >
                Start Assessment →
              </Link>
            </div>
          )}

          {!loading && !error && safeEstimates.length > 0 && (
            <div className="divide-y divide-gray-200">
              {safeEstimates.slice(0, 10).map((est) => {
                const statusBadge = STATUS_BADGE_COLORS[est.status] || STATUS_BADGE_COLORS.draft;
                return (
                  <Link
                    key={est.id}
                    href={`/estimate/${est.id}`}
                    className="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono font-bold text-sm text-gray-900">{est.report_short_id}</span>
                        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${statusBadge.bg} ${statusBadge.text}`}>
                          {est.status.charAt(0).toUpperCase() + est.status.slice(1)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">{est.customer_name || "Customer"} · {est.technician_name || "Technician"}</p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="font-bold text-sm font-mono text-gray-900">{fmt(est.total_amount)}</p>
                      <p className="text-xs text-gray-500 mt-1">{timeAgo(est.created_at)}</p>
                    </div>
                    <span className="text-gray-400">›</span>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
