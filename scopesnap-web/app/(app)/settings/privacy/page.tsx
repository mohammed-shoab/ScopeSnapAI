"use client";
/**
 * ScopeSnap — Privacy Settings Page
 * SOW Task 1.11: Data privacy controls for beta users.
 *
 * Controls:
 * - Export all assessment data as CSV
 * - View what data ScopeSnap stores
 * - Delete account (links to support for now — full delete in Phase 2)
 * - Analytics opt-out (stored in localStorage — disables trackEvent calls)
 */

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

const DATA_WE_STORE = [
  {
    category: "Company Profile",
    items: ["Company name, phone, email, address, license number"],
    retention: "Until account deletion",
  },
  {
    category: "Assessment Photos",
    items: ["HVAC equipment photos you upload for AI analysis"],
    retention: "Until assessment deleted or account deleted",
  },
  {
    category: "AI Analysis Results",
    items: ["Equipment identification, condition scores, detected issues"],
    retention: "Until assessment deleted",
  },
  {
    category: "Estimates",
    items: ["Good/Better/Best pricing, line items, homeowner approval status"],
    retention: "Until assessment deleted",
  },
  {
    category: "Homeowner Data",
    items: ["Name, address, phone — only what you enter"],
    retention: "Until assessment deleted",
  },
  {
    category: "Usage Analytics",
    items: ["Pages visited, features used, session duration (anonymized)"],
    retention: "90 days rolling",
  },
];

export default function PrivacySettingsPage() {
  const { getToken } = useAuth();
  const [exporting, setExporting] = useState(false);
  const [exportDone, setExportDone] = useState(false);
  const [exportError, setExportError] = useState("");

  // Analytics opt-out state (localStorage)
  const [analyticsOptedOut, setAnalyticsOptedOut] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem("ss_analytics_optout") === "true";
  });

  function toggleAnalytics() {
    const newValue = !analyticsOptedOut;
    setAnalyticsOptedOut(newValue);
    if (typeof window !== "undefined") {
      if (newValue) {
        localStorage.setItem("ss_analytics_optout", "true");
      } else {
        localStorage.removeItem("ss_analytics_optout");
      }
    }
  }

  async function handleExport() {
    setExporting(true);
    setExportError("");
    try {
      let headers: Record<string, string>;
      if (IS_DEV) {
        headers = DEV_HEADER;
      } else {
        const token = await getToken();
        headers = token ? { Authorization: `Bearer ${token}` } : {};
      }
      const res = await fetch(`${API_URL}/api/estimates/export/csv`, {
        headers,
      });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `scopesnap_data_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setExportDone(true);
    } catch {
      setExportError("Could not export data. Please try again.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-6">

      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-sm text-text-secondary mb-2">
          <Link href="/settings" className="hover:text-text-primary transition-colors">Settings</Link>
          <span>›</span>
          <span>Privacy</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Privacy & Data</h1>
        <p className="text-text-secondary text-sm mt-1">
          Control your data, download a copy, or understand what ScopeSnap stores.
        </p>
      </div>

      {/* Export Data */}
      <div className="bg-white border border-surface-border rounded-2xl p-5">
        <h2 className="font-bold text-base mb-1">Export your data</h2>
        <p className="text-text-secondary text-sm mb-4">
          Download a CSV of all your assessments, estimates, and job history.
          Includes customer names, addresses, equipment details, and pricing.
        </p>
        <div className="flex items-center gap-3">
          <button
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-2 bg-brand-green text-white font-semibold px-4 py-2.5 rounded-xl text-sm hover:bg-green-700 transition-colors disabled:opacity-60"
          >
            {exporting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Preparing…
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Download CSV
              </>
            )}
          </button>
          {exportDone && <span className="text-brand-green text-sm font-medium">✓ Downloaded!</span>}
          {exportError && <span className="text-red-500 text-sm">{exportError}</span>}
        </div>
      </div>

      {/* Analytics Opt-out */}
      <div className="bg-white border border-surface-border rounded-2xl p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="font-bold text-base mb-1">Usage analytics</h2>
            <p className="text-text-secondary text-sm">
              ScopeSnap collects anonymized usage data (pages visited, features used) to
              improve the product during beta. No personal data or assessment content is included.
            </p>
          </div>
          <button
            onClick={toggleAnalytics}
            className={`flex-shrink-0 w-11 h-6 rounded-full transition-colors relative ${
              analyticsOptedOut ? "bg-gray-300" : "bg-brand-green"
            }`}
            aria-label={analyticsOptedOut ? "Enable analytics" : "Disable analytics"}
          >
            <div
              className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                analyticsOptedOut ? "translate-x-0.5" : "translate-x-5"
              }`}
            />
          </button>
        </div>
        <p className="text-xs text-text-secondary mt-3">
          Currently: <strong>{analyticsOptedOut ? "Opted out" : "Opted in (default)"}</strong>
        </p>
      </div>

      {/* What we store */}
      <div className="bg-white border border-surface-border rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-surface-border">
          <h2 className="font-bold text-base">What ScopeSnap stores</h2>
          <p className="text-text-secondary text-sm mt-0.5">
            We only store data you enter or generate within the app.
          </p>
        </div>
        <div className="divide-y divide-surface-border">
          {DATA_WE_STORE.map((item) => (
            <div key={item.category} className="px-5 py-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm">{item.category}</p>
                  <p className="text-text-secondary text-xs mt-0.5">{item.items[0]}</p>
                </div>
                <span className="text-[10px] font-medium text-text-secondary bg-surface-bg border border-surface-border px-2 py-1 rounded-full flex-shrink-0 whitespace-nowrap">
                  {item.retention}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Delete Account */}
      <div className="bg-white border border-red-100 rounded-2xl p-5">
        <h2 className="font-bold text-base mb-1 text-red-600">Delete account</h2>
        <p className="text-text-secondary text-sm mb-4">
          Permanently delete your account and all associated data. This cannot be undone.
          During beta, account deletion is handled by our team.
        </p>
        <a
          href="mailto:support@scopesnap.ai?subject=Delete My ScopeSnap Account"
          className="inline-flex items-center gap-2 border border-red-200 text-red-600 font-semibold px-4 py-2.5 rounded-xl text-sm hover:bg-red-50 transition-colors"
        >
          Request account deletion
        </a>
        <p className="text-xs text-text-secondary mt-3">
          We'll process your request within 5 business days and confirm by email.
        </p>
      </div>

    </div>
  );
}
