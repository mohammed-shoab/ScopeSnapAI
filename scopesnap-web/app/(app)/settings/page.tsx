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

      {/* ── Profile Completion Banner ─────────────────────────────────────── */}
      {!loading && company && isOwner && (!form.phone.trim() || !form.email.trim()) && (
        <div className="bg-amber-50 border border-amber-300 rounded-ss p-4 flex items-start gap-3">
          <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-amber-800">Your company profile is incomplete</p>
            <p className="text-xs text-amber-700 mt-0.5">
              {[
                !form.phone.trim() && "phone number",
                !form.email.trim() && "business email",
              ]
                .filter(Boolean)
                .join(" and ")}{" "}
              {(!form.phone.trim() && !form.email.trim()) ? "are" : "is"} missing — needed to send estimates to customers.
            </p>
          </div>
          <button
            onClick={() => {
              const el = document.getElementById(!form.phone.trim() ? "company-phone-field" : "company-email-field");
              el?.scrollIntoView({ behavior: "smooth", block: "center" });
              setTimeout(() => el?.focus(), 300);
            }}
            className="text-xs font-bold text-amber-700 border border-amber-300 bg-white px-3 py-1.5 rounded-lg hover:bg-amber-100 transition-colors flex-shrink-0 whitespace-nowrap"
          >
            Complete →
          </button>
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
                    id="company-phone-field"
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
                  id="company-email-field"
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

          {/* ── Estimate Markup % ─────────────────────────────────────────── */}
          <MarkupSetting apiUrl={API_URL} getAuthHeaders={getAuthHeaders} />

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

// ── Markup Setting Component ───────────────────────────────────────────────────

function MarkupSetting({
  apiUrl,
  getAuthHeaders,
}: {
  apiUrl: string;
  getAuthHeaders: () => Promise<Record<string, string>>;
}) {
  const [markup, setMarkup] = useState<number | null>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Array<{from_pct: number; to_pct: number; changed_at: string; note?: string}>>([]);

  useEffect(() => {
    (async () => {
      const headers = await getAuthHeaders();
      const r = await fetch(`${apiUrl}/api/pricing-rules/markup`, { headers });
      if (r.ok) {
        const d = await r.json();
        setMarkup(d.markup_pct);
        setHistory(d.history || []);
      }
    })();
  }, [apiUrl, getAuthHeaders]);

  const handleSave = async () => {
    const pct = parseFloat(draft);
    if (isNaN(pct) || pct < 0 || pct > 200) {
      setError("Markup must be between 0% and 200%.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const headers = await getAuthHeaders();
      const r = await fetch(`${apiUrl}/api/pricing-rules/markup`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({ markup_pct: pct, change_note: note.trim() || null }),
      });
      if (!r.ok) throw new Error(await r.text());
      const d = await r.json();
      setMarkup(d.new_markup_pct);
      setHistory(prev => [{
        from_pct: d.previous_markup_pct,
        to_pct: d.new_markup_pct,
        changed_at: new Date().toISOString(),
        note: note.trim() || undefined,
      }, ...prev]);
      setEditing(false);
      setNote("");
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
      setError("Failed to update markup. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
      <h2 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-4">
        Estimate Markup %
      </h2>

      {markup === null ? (
        <p className="text-sm text-text-secondary">Loading…</p>
      ) : editing ? (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="relative">
              <input
                type="number"
                value={draft}
                onChange={e => setDraft(e.target.value)}
                min="0"
                max="200"
                step="0.5"
                className="w-28 border border-surface-border rounded-lg px-3 py-2 text-sm text-center font-bold focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green"
                placeholder={String(markup)}
                autoFocus
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-text-secondary">%</span>
            </div>
            <span className="text-xs text-text-secondary">of base cost applied to all new estimates</span>
          </div>
          <input
            type="text"
            value={note}
            onChange={e => setNote(e.target.value)}
            placeholder="Reason for change (optional)"
            className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green"
          />
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={saving || !draft}
              className="px-4 py-2 bg-brand-green text-white text-sm font-bold rounded-lg disabled:opacity-50 hover:bg-green-700 transition-colors"
            >
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              onClick={() => { setEditing(false); setError(null); setNote(""); }}
              className="px-4 py-2 border border-surface-border text-sm font-semibold rounded-lg hover:bg-surface-bg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl font-extrabold text-text-primary">{markup}%</span>
            <div>
              <p className="text-xs text-text-secondary">applied to all new estimates</p>
              {success && <p className="text-xs text-brand-green font-semibold">✓ Saved</p>}
            </div>
          </div>
          <button
            onClick={() => { setDraft(String(markup)); setEditing(true); }}
            className="text-sm text-brand-green font-semibold hover:underline"
          >
            Edit →
          </button>
        </div>
      )}

      {/* Change history */}
      {history.length > 0 && !editing && (
        <div className="mt-4 border-t border-surface-border pt-3">
          <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-2">
            Recent Changes
          </p>
          <div className="space-y-1.5">
            {history.slice(0, 3).map((h, i) => (
              <div key={i} className="flex items-center justify-between text-xs text-text-secondary">
                <span>
                  <span className="font-semibold text-text-primary">{h.from_pct}%</span>
                  {" → "}
                  <span className="font-semibold text-brand-green">{h.to_pct}%</span>
                  {h.note && <span className="text-gray-400"> — {h.note}</span>}
                </span>
                <span className="text-[10px] font-mono">
                  {new Date(h.changed_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
