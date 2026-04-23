/**
 * Assessments List Page
 * Shows all estimates for the authenticated company with status badges,
 * amounts, and links to individual estimate builders.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";

const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

interface Estimate {
  id: string;
  report_short_id: string;
  status: string;
  equipment_type?: string;
  overall_condition?: string;
  total_amount?: number;
  markup_percent?: number;
  homeowner_report_url?: string;
  contractor_pdf_url?: string;
  created_at?: string;
  property?: {
    address_line1?: string;
    customer_name?: string;
  };
}

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  draft:    { bg: "bg-yellow-100", text: "text-yellow-700", label: "Draft" },
  sent:     { bg: "bg-blue-100",   text: "text-blue-700",   label: "Sent" },
  approved: { bg: "bg-green-100",  text: "text-green-700",  label: "Approved" },
  declined: { bg: "bg-red-100",    text: "text-red-700",    label: "Declined" },
};

function fmt(n?: number) {
  return n != null ? "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—";
}

function timeAgo(dateStr?: string) {
  if (!dateStr) return "—";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  const hrs  = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  if (hrs < 24) return `${hrs}h ago`;
  return `${days}d ago`;
}

const EQUIP_LABELS: Record<string, string> = {
  ac_unit: "AC Unit", heat_pump: "Heat Pump", furnace: "Furnace",
  boiler: "Boiler", air_handler: "Air Handler", mini_split: "Mini-Split",
  package_unit: "Package Unit", other: "Other",
};

export default function EstimatesPage() {
  const { getToken } = useAuth();
  const [assessments, setAssessments] = useState<Estimate[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);

  useEffect(() => {
    const load = async () => {
      const headers = await getAuthHeaders();
      fetch(`${API_URL}/api/estimates/?limit=50`, { headers })
        .then((r) => r.json())
        .then((data) => {
          const items = Array.isArray(data.items) ? data.items : Array.isArray(data) ? data : [];
          setAssessments(items);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    };
    load();
  }, [getAuthHeaders]);

  const filtered = estimates.filter((e) => {
    const matchesFilter = filter === "all" || e.status === filter;
    const q = search.toLowerCase();
    const matchesSearch =
      !q ||
      e.report_short_id?.toLowerCase().includes(q) ||
      e.property?.address_line1?.toLowerCase().includes(q) ||
      e.property?.customer_name?.toLowerCase().includes(q) ||
      e.equipment_type?.toLowerCase().includes(q);
    return matchesFilter && matchesSearch;
  });

  const counts = estimates.reduce<Record<string, number>>((acc, e) => {
    acc[e.status] = (acc[e.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-text-primary">Assessments</h1>
          <p className="text-sm text-text-secondary mt-0.5">
            {estimates.length} total · {counts.sent || 0} sent · {counts.approved || 0} approved
          </p>
        </div>
        <Link
          href="/assess"
          className="flex items-center gap-2 bg-brand-green text-white font-bold px-4 py-3 rounded-xl text-sm hover:shadow-lg transition-shadow"
        >
          + New Assessment
        </Link>
      </div>

      {/* Filter Tabs + Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-1 bg-surface-secondary rounded-xl p-1 flex-shrink-0">
          {["all", "draft", "sent", "approved", "declined"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg capitalize transition-colors ${
                filter === f
                  ? "bg-white shadow-sm text-text-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {f === "all" ? `All (${estimates.length})` : `${STATUS_STYLES[f]?.label} (${counts[f] || 0})`}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Search by address, name, or report ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green focus:ring-2 focus:ring-brand-green focus:ring-opacity-20"
        />
      </div>

      {/* Assessments Table */}
      {loading ? (
        <div className="text-center py-16 text-text-secondary">
          <div className="w-8 h-8 border-2 border-brand-green border-t-transparent rounded-full mx-auto mb-3 animate-spin" />
          Loading estimates...
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-text-secondary text-lg">
            {search || filter !== "all" ? "No estimates match your filters." : "No estimates yet."}
          </p>
          <Link
            href="/assess"
            className="inline-block mt-4 bg-brand-green text-white font-bold px-6 py-3 rounded-xl hover:shadow-lg transition-shadow"
          >
            Start First Assessment →
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-surface-border overflow-hidden shadow-sm">
          {/* Table Header — 3 cols mobile, 5 cols desktop */}
          <div className="grid grid-cols-[1fr_auto_auto] md:grid-cols-[1fr_auto_auto_auto_auto] gap-2 md:gap-4 px-4 py-2.5 bg-surface-bg border-b border-surface-border text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">
            <span>Report / Address</span>
            <span className="hidden md:block text-center w-24">Equipment</span>
            <span className="text-right w-16 md:w-24">Amount</span>
            <span className="text-center w-16 md:w-20">Status</span>
            <span className="hidden md:block text-right w-20">Date</span>
          </div>

          {/* Rows */}
          <div className="divide-y divide-surface-border">
            {filtered.map((est) => {
              const statusStyle = STATUS_STYLES[est.status] || STATUS_STYLES.draft;
              return (
                <Link
                  key={est.id}
                  href={`/assessment/${est.id}`}
                  className="grid grid-cols-[1fr_auto_auto] md:grid-cols-[1fr_auto_auto_auto_auto] gap-2 md:gap-4 px-4 py-3.5 items-center hover:bg-surface-bg transition-colors group"
                >
                  {/* Report ID + Address */}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-sm text-brand-green group-hover:underline">
                        {est.report_short_id}
                      </span>
                    </div>
                    <div className="text-xs text-text-secondary mt-0.5 truncate">
                      {est.property?.customer_name
                        ? `${est.property.customer_name} · ${est.property.address_line1 || "—"}`
                        : est.property?.address_line1 || "No address"}
                    </div>
                  </div>

                  {/* Equipment — desktop only */}
                  <div className="hidden md:block w-24 text-center">
                    <span className="text-xs text-text-secondary">
                      {EQUIP_LABELS[est.equipment_type || ""] || est.equipment_type || "—"}
                    </span>
                  </div>

                  {/* Amount */}
                  <div className="w-16 md:w-24 text-right font-mono font-bold text-sm">
                    {fmt(est.total_amount)}
                  </div>

                  {/* Status Badge */}
                  <div className="w-16 md:w-20 flex justify-center">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-semibold ${statusStyle.bg} ${statusStyle.text}`}
                    >
                      {statusStyle.label}
                    </span>
                  </div>

                  {/* Date — desktop only */}
                  <div className="hidden md:block w-20 text-right text-xs text-text-secondary">
                    {timeAgo(est.created_at)}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
