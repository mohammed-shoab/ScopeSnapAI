/**
 * Screen — BenchmarkIQ (coming soon stub)
 * Compares this company's pricing to regional market rates.
 */
"use client";

import Link from "next/link";

const BENCHMARKS = [
  { job: "Full AC System Replacement", yours: 6800, market: 6200, position: "above" },
  { job: "Coil Replacement",           yours: 2100, market: 2450, position: "below" },
  { job: "Compressor Replacement",     yours: 1950, market: 1900, position: "at"    },
  { job: "Refrigerant Recharge",       yours: 380,  market: 420,  position: "below" },
  { job: "System Tune-Up",             yours: 145,  market: 135,  position: "above" },
];

function diff(yours: number, market: number) {
  const pct = ((yours - market) / market) * 100;
  return { pct: Math.abs(pct).toFixed(1), dir: pct > 0 ? "above" : pct < 0 ? "below" : "at" };
}

export default function BenchmarkPage() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-8">
      {/* Header */}
      <div className="pt-2">
        <div className="flex items-center gap-2 mb-1">
          <Link href="/dashboard" className="text-sm text-text-secondary hover:text-text-primary">← Back</Link>
          <span className="text-text-secondary">/</span>
          <span className="text-sm text-text-secondary">Intelligence</span>
        </div>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-3xl font-extrabold tracking-tight text-text-primary">📈 BenchmarkIQ</h1>
          <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full">
            Preview Data
          </span>
        </div>
        <p className="text-text-secondary text-sm mt-1">
          How your pricing compares to Phoenix Metro market rates (Q1 2026)
        </p>
      </div>

      {/* Summary Strip */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Above Market", value: "2", icon: "💰", color: "text-brand-green" },
          { label: "Below Market", value: "2", icon: "⚠️", color: "text-yellow-600" },
          { label: "At Market",    value: "1", icon: "✅", color: "text-text-primary" },
        ].map((s) => (
          <div key={s.label} className="bg-white border border-surface-border rounded-xl p-4 text-center">
            <div className="text-2xl mb-1">{s.icon}</div>
            <p className={`text-3xl font-extrabold font-mono ${s.color}`}>{s.value}</p>
            <p className="text-xs text-text-secondary mt-1 font-semibold">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Benchmark Table */}
      <div className="bg-white rounded-xl border border-surface-border overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-surface-border">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-1">Price Comparison</p>
          <h2 className="text-lg font-bold text-text-primary">Your Rates vs. Market</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-surface-bg border-b border-surface-border">
            <tr>
              <th className="px-3 md:px-5 py-3 text-left text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Job Type</th>
              <th className="px-2 md:px-5 py-3 text-right text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Your Rate</th>
              <th className="px-2 md:px-5 py-3 text-right text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Market Avg</th>
              <th className="px-2 md:px-5 py-3 text-right text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Δ</th>
            </tr>
          </thead>
          <tbody>
            {BENCHMARKS.map((b) => {
              const { pct, dir } = diff(b.yours, b.market);
              const color = dir === "above" ? "text-brand-green" : dir === "below" ? "text-yellow-600" : "text-text-secondary";
              const badge = dir === "above" ? "bg-green-50 text-green-700" : dir === "below" ? "bg-yellow-50 text-yellow-700" : "bg-gray-100 text-gray-600";
              return (
                <tr key={b.job} className="border-b border-surface-border hover:bg-surface-bg transition-colors">
                  <td className="px-3 md:px-5 py-3.5 font-medium text-xs md:text-sm">{b.job}</td>
                  <td className="px-2 md:px-5 py-3.5 text-right font-mono font-bold text-xs md:text-sm">${b.yours.toLocaleString()}</td>
                  <td className="px-2 md:px-5 py-3.5 text-right font-mono text-text-secondary text-xs md:text-sm">${b.market.toLocaleString()}</td>
                  <td className="px-2 md:px-5 py-3.5 text-right">
                    <span className={`text-xs font-bold px-1.5 py-0.5 rounded-full ${badge}`}>
                      {dir === "at" ? "=" : dir === "above" ? "+" : "-"}{pct}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Note + Coming Soon */}
      <div className="card p-5 bg-blue-50 border-blue-100">
        <div className="flex items-start gap-3">
          <span className="text-2xl">🚧</span>
          <div>
            <p className="font-bold text-sm">Live Market Data Coming Soon</p>
            <p className="text-xs text-text-secondary mt-1">
              BenchmarkIQ will pull real-time pricing from ScopeSnap network data across 10,000+
              HVAC contractors. The data above uses regional market averages for illustration.
              Full live benchmarking ships in Q2 2026.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Link href="/intelligence/leaks" className="card p-4 flex items-center gap-3 hover:border-brand-green hover:shadow-sm transition-all">
          <span className="text-2xl">💰</span>
          <div>
            <p className="font-bold text-sm">Profit Leaks</p>
            <p className="text-xs text-text-secondary">Find where revenue is escaping</p>
          </div>
        </Link>
        <Link href="/intelligence/history" className="card p-4 flex items-center gap-3 hover:border-brand-green hover:shadow-sm transition-all">
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
