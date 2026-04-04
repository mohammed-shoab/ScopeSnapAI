"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER: Record<string, string> = {
  "X-Dev-Clerk-User-Id": "test_user_mike",
  "Content-Type": "application/json",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface CompanyProfile {
  name: string;
  phone: string;
  license_number: string;
  logo_url?: string;
}

type Trade = "hvac" | "plumbing" | "electrical" | "roofing";

const TRADES: Record<Trade, { icon: string; label: string; description: string }> = {
  hvac: {
    icon: "❄️",
    label: "HVAC",
    description: "AC, Furnace, Heat Pump",
  },
  plumbing: {
    icon: "🔧",
    label: "Plumbing",
    description: "Water Heater, Pipes, Drains",
  },
  electrical: {
    icon: "⚡",
    label: "Electrical",
    description: "Panels, Wiring, Outlets",
  },
  roofing: {
    icon: "🏠",
    label: "Roofing",
    description: "Shingles, Flashing, Gutters",
  },
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  const [profile, setProfile] = useState<CompanyProfile>({
    name: "",
    phone: "",
    license_number: "",
  });

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token
      ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
      : { "Content-Type": "application/json" };
  }, [getToken]);

  // Load current company info
  useEffect(() => {
    const load = async () => {
      const headers = await getAuthHeaders();
      fetch(`${API_URL}/api/auth/me`, { headers })
        .then((r) => r.json())
        .then((data) => {
          if (data.company) {
            setProfile((prev) => ({
              ...prev,
              name: data.company.name || "",
              phone: data.company.phone || "",
              license_number: data.company.license_number || "",
              logo_url: data.company.logo_url || undefined,
            }));
            if (data.company.logo_url) {
              setLogoPreview(data.company.logo_url);
            }
          }
        })
        .catch(() => {});
    };
    load();
  }, [getAuthHeaders]);

  // ── Handlers ────────────────────────────────────────────────────────────────

  const handleTradeSelect = (trade: Trade) => {
    setSelectedTrade(trade);
  };

  const handleTradeContinue = () => {
    if (!selectedTrade) return;
    setStep(2);
  };

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Read file as data URL for preview
    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target?.result as string;
      setLogoPreview(dataUrl);
      setProfile({ ...profile, logo_url: dataUrl });
    };
    reader.readAsDataURL(file);
  };

  const handleCompanyInfoSave = async () => {
    if (!profile.name.trim()) {
      setError("Company name is required");
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const headers = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/auth/me/company`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({
          name: profile.name,
          phone: profile.phone,
          license_number: profile.license_number,
          trade: selectedTrade,
        }),
      });
      if (!r.ok) {
        const err = await r.json();
        throw new Error(err.detail || "Failed to save company info");
      }
      // Redirect to dashboard
      router.push("/dashboard");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleSkip = async () => {
    setSaving(true);
    try {
      const headers = await getAuthHeaders();
      await fetch(`${API_URL}/api/auth/me/company`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({
          trade: selectedTrade,
        }),
      });
      router.push("/dashboard");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Skip failed");
    } finally {
      setSaving(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  // 2 actual form steps (welcome is pre-step, not counted):
  //   step 1 = Welcome  (no dot active — about to begin)
  //   step 2 = Trade    (dot 1 active — "Step 1 of 2")
  //   step 3 = Company  (dot 2 active — "Step 2 of 2")
  const totalSteps = 2;

  // Render dot indicators
  const DotIndicators = () => (
    <div className="flex justify-center gap-2 mt-8">
      {Array.from({ length: totalSteps }).map((_, i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full transition-colors ${
            i + 1 === step - 1 ? "bg-brand-green" : "bg-surface-border"
          }`}
        />
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-surface-bg flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        {/* ── Step 1: Welcome ───────────────────────────────────────────────── */}
        {step === 1 && (
          <>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-brand-green rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-green">
                <span className="text-white font-bold text-2xl">S</span>
              </div>
              <h1 className="text-4xl font-extrabold tracking-tight mb-2">
                <span className="text-text-primary">Scope</span>
                <span className="text-brand-green">Snap</span>
              </h1>
              <p className="text-text-secondary text-sm leading-relaxed max-w-sm mx-auto">
                AI-powered equipment intelligence. Photo → Estimate → Customer Report. In under 5 minutes.
              </p>
            </div>

            <div className="card p-8">
              {/* Feature icons grid */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                {[
                  { icon: "📸", label: "Photo to Estimate" },
                  { icon: "🔍", label: "Equipment Intelligence" },
                  { icon: "📊", label: "Visual Reports" },
                  { icon: "🎯", label: "Accuracy Tracking" },
                ].map((item) => (
                  <div key={item.label} className="flex flex-col items-center gap-2 p-3">
                    <div className="text-3xl">{item.icon}</div>
                    <div className="text-xs font-semibold text-text-secondary text-center">
                      {item.label}
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={() => setStep(2)}
                className="w-full bg-brand-green text-white font-bold py-3 rounded-xl text-sm shadow-green hover:bg-brand-green-dark transition-colors mb-3"
              >
                Get Started →
              </button>

              <p className="text-center text-xs text-text-secondary">
                Takes 30 seconds to set up
              </p>
            </div>

            <DotIndicators />
          </>
        )}

        {/* ── Step 2: Trade Selection ───────────────────────────────────────── */}
        {step === 2 && (
          <>
            <div className="text-center mb-8">
              <p className="text-xs font-mono font-semibold text-text-secondary tracking-wide uppercase mb-3">
                Step 1 of 2
              </p>
              <h1 className="text-3xl font-extrabold tracking-tight mb-2">
                What's your trade?
              </h1>
              <p className="text-text-secondary text-sm leading-relaxed max-w-sm mx-auto">
                This configures your equipment database, pricing templates, and AI prompts. You can change this later.
              </p>
            </div>

            <div className="card p-8">
              <div className="grid grid-cols-2 gap-4 mb-8">
                {(Object.entries(TRADES) as Array<[Trade, typeof TRADES[Trade]]>).map(
                  ([trade, { icon, label, description }]) => (
                    <button
                      key={trade}
                      onClick={() => handleTradeSelect(trade)}
                      className={`flex flex-col items-center gap-3 p-5 rounded-lg border-2 transition-all ${
                        selectedTrade === trade
                          ? "border-brand-green bg-brand-green-light"
                          : "border-surface-border hover:border-brand-green/40"
                      }`}
                    >
                      <div className="text-3xl">{icon}</div>
                      <div className="text-center">
                        <div className="text-sm font-bold text-text-primary">{label}</div>
                        <div className="text-xs text-text-secondary mt-0.5">
                          {description}
                        </div>
                      </div>
                    </button>
                  )
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 border border-surface-border text-text-secondary font-semibold py-3 rounded-lg text-sm hover:bg-surface-bg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleTradeContinue}
                  disabled={!selectedTrade}
                  className="flex-1 bg-brand-green text-white font-bold py-3 rounded-lg text-sm shadow-green hover:bg-brand-green-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue →
                </button>
              </div>
            </div>

            <DotIndicators />
          </>
        )}

        {/* ── Step 3: Company Info ──────────────────────────────────────────── */}
        {step === 3 && (
          <>
            <div className="text-center mb-8">
              <p className="text-xs font-mono font-semibold text-text-secondary tracking-wide uppercase mb-3">
                Step 2 of 2
              </p>
              <h1 className="text-3xl font-extrabold tracking-tight mb-2">
                Your Company
              </h1>
              <p className="text-text-secondary text-sm leading-relaxed max-w-sm mx-auto">
                This appears on estimates and reports your customers receive.
              </p>
            </div>

            <div className="card p-8">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 mb-6">
                  {error}
                </div>
              )}

              <div className="space-y-5 mb-6">
                {/* Company Name */}
                <div>
                  <label className="text-xs font-semibold text-text-secondary uppercase tracking-wide block mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    placeholder="Your Company LLC"
                    className="w-full border border-surface-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green"
                  />
                </div>

                {/* Phone and License */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-text-secondary uppercase tracking-wide block mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={profile.phone}
                      onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                      placeholder="(555) 123-4567"
                      className="w-full border border-surface-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-text-secondary uppercase tracking-wide block mb-2">
                      License #
                    </label>
                    <input
                      type="text"
                      value={profile.license_number}
                      onChange={(e) =>
                        setProfile({ ...profile, license_number: e.target.value })
                      }
                      placeholder="TX-12345"
                      className="w-full border border-surface-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/30 focus:border-brand-green"
                    />
                  </div>
                </div>

                {/* Logo Upload */}
                <div>
                  <label className="text-xs font-semibold text-text-secondary uppercase tracking-wide block mb-2">
                    Company Logo
                  </label>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full border-2 border-dashed border-surface-border rounded-lg p-8 flex flex-col items-center justify-center gap-3 hover:border-brand-green/40 transition-colors"
                  >
                    {logoPreview ? (
                      <>
                        <img
                          src={logoPreview}
                          alt="Company logo"
                          className="h-16 w-auto object-contain"
                        />
                        <span className="text-xs text-text-secondary">Click to change</span>
                      </>
                    ) : (
                      <>
                        <div className="text-2xl">📷</div>
                        <span className="text-xs text-text-secondary">
                          Click to upload (optional)
                        </span>
                      </>
                    )}
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="hidden"
                  />
                </div>
              </div>

              <div className="flex gap-3 mb-3">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 border border-surface-border text-text-secondary font-semibold py-3 rounded-lg text-sm hover:bg-surface-bg transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleCompanyInfoSave}
                  disabled={saving || !profile.name.trim()}
                  className="flex-1 bg-brand-green text-white font-bold py-3 rounded-lg text-sm shadow-green hover:bg-brand-green-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? "Launching..." : "Launch SnapAI 🚀"}
                </button>
              </div>

              <button
                onClick={handleSkip}
                disabled={saving}
                className="w-full text-center text-xs text-text-secondary hover:text-text-primary py-2 transition-colors"
              >
                I'll finish this later
              </button>
            </div>

            <DotIndicators />
          </>
        )}
      </div>
    </div>
  );
}
