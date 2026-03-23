/**
 * Screen — Settings / Company Profile
 * WP-16: Owner can update company info. Also links to Billing.
 *
 * GET   /api/auth/me            — load current profile
 * PATCH /api/auth/me/company    — update company profile
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER: Record<string, string> = {
  "X-Dev-Clerk-User-Id": "test_user_mike",
  "Content-Type": "application/json",
};

interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface CompanyData {
  id: string;
  name: string;
  phone: string | null;
  email: string | null;
  license_number: string | null;
  address_line1: string | null;
  city: string | null;
  state: string | null;
  zip: string | null;
  plan: string;
}

export default function SettingsPage() {
  const { getToken } = useAuth();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [company, setCompany] = useState<CompanyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Form state mirrors company data
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    license_number: "",
    address_line1: "",
    city: "",
    state: "",
    zip: "",
  });

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
  }, [getToken]);

  useEffect(() => {
    const load = async () => {
      const headers = await getAuthHeaders();
      fetch(`${API_URL}/api/auth/me`, { headers })
        .then((r) => r.json())
        .then((data) => {
          setUser(data.user);
          setCompany(data.company);
          if (data.company) {
            setForm({
              name: data.company.name || "",
              phone: data.company.phone || "",
              email: data.company.email || "",
              license_number: data.company.license_number || "",
              address_line1: data.company.address_line1 || "",
              city: data.company.city || "",
              state: data.company.state || "",
              zip: data.company.zip || "",
            });
          }
          setLoading(false);
        })
        .catch(() => {
          setError("Could not load settings — is the API running?");
          setLoading(false);
        });
    };
    load();
  }, [getAuthHeaders]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const headers = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/auth/me/company`, {
        method: "PATCH",
        headers,
        body: JSON.stringify(form),
      });
      if (!r.ok) {
        const err = await r.json();
        if (r.status === 403) {
          setError("Only the company owner can update profile settings.");
          return;
        }
        throw new Error(err.detail || "Failed to save");
      }
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const isOwner = user?.role === "owner";

  const planBadgeColors: Record<string, string> = {
    trial: "bg-gray-100 text-gray-600",
    free: "bg-gray-100 text-gray-600",
    starter: "bg-blue-100 text-blue-700",
    pro: "bg-purple-100 text-purple-700",
  };

  return (
    <div className="space-y-5 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pt-2">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Settings</h1>
          <p className="text-text-secondary text-sm mt-0.5">Manage your company profile</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-brand-red text-sm rounded-xl px-4 py-3">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 text-sm rounded-xl px-4 py-3 flex items-center gap-2">
          <span>✓</span> Profile saved successfully
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          <div className="bg-white border border-surface-border rounded-ss shadow-ss h-24 animate-pulse" />
          <div className="bg-white border border-surface-border rounded-ss shadow-ss h-64 animate-pulse" />
        </div>
      ) : (
        <>
          {/* User Info (read-only) */}
          <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
            <h2 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-4">Your Account</h2>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-brand-green rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-sm">
                  {user?.name?.charAt(0)?.toUpperCase() || "U"}
                </span>
              </div>
              <div>
                <p className="font-semibold text-sm">{user?.name || "—"}</p>
                <p className="text-xs text-text-secondary">{user?.email || "—"}</p>
              </div>
              <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${
                user?.role === "owner"
                  ? "bg-brand-green/10 text-brand-green"
                  : "bg-gray-100 text-gray-600"
              }`}>
                {user?.role || "tech"}
              </span>
            </div>
          </div>

          {/* Company Profile Form */}
          <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary">Company Profile</h2>
              {company?.plan && (
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${planBadgeColors[company.plan] || "bg-gray-100 text-gray-600"}`}>
                  {company.plan === "trial" || company.plan === "free" ? "Free Trial" : company.plan.charAt(0).toUpperCase() + company.plan.slice(1)} Plan
                </span>
              )}
            </div>

            {!isOwner && (
              <div className="bg-amber-50 border border-amber-200 text-amber-700 text-xs rounded-xl px-3 py-2 mb-4">
                Only the company owner can edit the profile. Contact your owner to make changes.
              </div>
            )}

            <div className="space-y-3">
              <div>
                <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  disabled={!isOwner}
                  className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    disabled={!isOwner}
                    placeholder="(555) 123-4567"
                    className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                  />
                </div>
                <div>
                  <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                    License #
                  </label>
                  <input
                    type="text"
                    value={form.license_number}
                    onChange={(e) => setForm({ ...form, license_number: e.target.value })}
                    disabled={!isOwner}
                    placeholder="TX-HVAC-12345"
                    className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                  />
                </div>
              </div>

              <div>
                <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                  Business Email
                </label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  disabled={!isOwner}
                  placeholder="info@yourhvac.com"
                  className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                />
              </div>

              <div>
                <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                  Address
                </label>
                <input
                  type="text"
                  value={form.address_line1}
                  onChange={(e) => setForm({ ...form, address_line1: e.target.value })}
                  disabled={!isOwner}
                  placeholder="123 Main St"
                  className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <div className="col-span-2">
                  <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                    City
                  </label>
                  <input
                    type="text"
                    value={form.city}
                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                    disabled={!isOwner}
                    placeholder="Dallas"
                    className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                  />
                </div>
                <div>
                  <label className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary block mb-2">
                    ZIP
                  </label>
                  <input
                    type="text"
                    value={form.zip}
                    onChange={(e) => setForm({ ...form, zip: e.target.value })}
                    disabled={!isOwner}
                    placeholder="75201"
                    className="w-full border border-surface-border rounded-ss px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green disabled:bg-surface-bg disabled:text-text-secondary"
                  />
                </div>
              </div>
            </div>

            {isOwner && (
              <button
                onClick={handleSave}
                disabled={saving || !form.name.trim()}
                className="mt-5 w-full bg-brand-green text-white font-bold py-3 rounded-xl text-sm shadow-ss hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
            )}
          </div>

          {/* Billing Card */}
          <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-2">Billing & Plan</h2>
                <p className="text-text-secondary text-sm">
                  Manage your subscription, usage, and invoices.
                </p>
              </div>
              <Link
                href="/billing"
                className="bg-brand-green text-white text-sm font-bold px-4 py-2.5 rounded-xl hover:bg-green-700 transition-colors flex-shrink-0"
              >
                Manage →
              </Link>
            </div>
          </div>

          {/* Onboarding Link */}
          <div className="bg-white border border-surface-border rounded-ss shadow-ss p-4 border-dashed">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-1">Onboarding</p>
                <p className="text-xs text-text-secondary">Re-run the setup wizard any time.</p>
              </div>
              <Link
                href="/onboarding"
                className="text-sm text-brand-green font-semibold hover:underline"
              >
                Open →
              </Link>
            </div>
          </div>

          {/* Privacy & Data — SOW Task 1.11 */}
          <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-2">Privacy &amp; Data</h2>
                <p className="text-text-secondary text-sm">
                  Export your data, manage analytics, or delete your account.
                </p>
              </div>
              <Link
                href="/settings/privacy"
                className="text-sm text-brand-green font-semibold hover:underline flex-shrink-0"
              >
                Manage →
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
