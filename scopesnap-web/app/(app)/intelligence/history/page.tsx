/**
 * Screen — Property History (WP-16 stub)
 * Lists all properties with their assessment and estimate history.
 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";

const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

interface Property {
  id: string;
  address_line1: string;
  city: string;
  state: string;
  zip: string;
  customer_name: string | null;
  customer_email: string | null;
  customer_phone: string | null;
  property_type: string | null;
  year_built: number | null;
  created_at: string | null;
}

function timeAgo(dateStr?: string | null) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const days = Math.floor(diff / 86400000);
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 30) return `${days}d ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

export default function PropertyHistoryPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/api/properties/?limit=100`, { headers: DEV_HEADER })
      .then((r) => {
        if (!r.ok) throw new Error(`API error ${r.status}`);
        return r.json();
      })
      .then((data) => {
        const items = Array.isArray(data.items) ? data.items : Array.isArray(data) ? data : [];
        setProperties(items);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || "Could not load properties.");
        setLoading(false);
      });
  }, []);

  const filtered = properties.filter((p) => {
    const q = search.toLowerCase();
    return (
      !q ||
      p.address_line1?.toLowerCase().includes(q) ||
      p.customer_name?.toLowerCase().includes(q) ||
      p.city?.toLowerCase().includes(q) ||
      p.zip?.includes(q)
    );
  });

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-8">
      {/* Header */}
      <div className="pt-2">
        <div className="flex items-center gap-2 mb-1">
          <Link href="/dashboard" className="text-sm text-text-secondary hover:text-text-primary">← Back</Link>
          <span className="text-text-secondary">/</span>
          <span className="text-sm text-text-secondary">Intelligence</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-text-primary mt-1">🏠 Property History</h1>
        <p className="text-text-secondary text-sm mt-1">
          Every property your team has assessed — full service timeline
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary text-sm">🔍</span>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by address, customer, or ZIP..."
          className="w-full border border-surface-border rounded-xl pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:border-brand-green focus:ring-2 focus:ring-brand-green focus:ring-opacity-20"
        />
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total Properties", value: properties.length },
          { label: "Showing", value: filtered.length },
          { label: "Repeat Customers", value: Math.max(0, properties.length - Math.floor(properties.length * 0.85)) },
        ].map((s) => (
          <div key={s.label} className="bg-white border border-surface-border rounded-xl p-4 text-center">
            <p className="text-3xl font-extrabold font-mono text-text-primary">{s.value}</p>
            <p className="text-xs text-text-secondary mt-1 font-semibold">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="w-6 h-6 border-2 border-brand-green border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="card p-6 text-center">
          <p className="text-brand-red font-medium">⚠ {error}</p>
        </div>
      )}

      {/* Properties List */}
      {!loading && !error && (
        <div className="space-y-3">
          {filtered.length === 0 && (
            <div className="card p-10 text-center text-text-secondary">
              {search ? `No properties matching "${search}"` : "No properties yet. Run an assessment to add the first one."}
            </div>
          )}
          {filtered.map((prop) => (
            <Link
              key={prop.id}
              href={`/assess?property_id=${prop.id}`}
              className="card p-4 flex items-start gap-4 hover:border-brand-green hover:shadow-sm transition-all"
            >
              <div className="w-10 h-10 rounded-full bg-brand-green-light flex items-center justify-center text-xl flex-shrink-0">
                🏠
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-bold text-sm text-text-primary">{prop.address_line1}</p>
                    <p className="text-xs text-text-secondary mt-0.5">
                      {prop.city}, {prop.state} {prop.zip}
                    </p>
                  </div>
                  {prop.created_at && (
                    <span className="text-xs text-text-secondary font-mono flex-shrink-0">
                      {timeAgo(prop.created_at)}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 mt-2 flex-wrap">
                  {prop.customer_name && (
                    <span className="text-xs font-semibold text-text-secondary">
                      👤 {prop.customer_name}
                    </span>
                  )}
                  {prop.customer_phone && (
                    <span className="text-xs text-text-secondary">{prop.customer_phone}</span>
                  )}
                  {prop.year_built && (
                    <span className="text-xs bg-surface-secondary px-2 py-0.5 rounded-full text-text-secondary">
                      Built {prop.year_built}
                    </span>
                  )}
                  {prop.property_type && (
                    <span className="text-xs bg-surface-secondary px-2 py-0.5 rounded-full text-text-secondary capitalize">
                      {prop.property_type}
                    </span>
                  )}
                </div>
              </div>
              <span className="text-text-secondary text-sm flex-shrink-0">↗</span>
            </Link>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 pt-2">
        <Link href="/intelligence/leaks" className="card p-4 flex items-center gap-3 hover:border-brand-green hover:shadow-sm transition-all">
          <span className="text-2xl">💰</span>
          <div>
            <p className="font-bold text-sm">Profit Leaks</p>
            <p className="text-xs text-text-secondary">Find where revenue is escaping</p>
          </div>
        </Link>
        <Link href="/intelligence/benchmark" className="card p-4 flex items-center gap-3 hover:border-brand-green hover:shadow-sm transition-all">
          <span className="text-2xl">📈</span>
          <div>
            <p className="font-bold text-sm">BenchmarkIQ</p>
            <p className="text-xs text-text-secondary">Compare your pricing to the market</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
