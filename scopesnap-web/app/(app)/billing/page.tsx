/**
 * Screen — Billing & Subscription
 * WP-16: Shows current plan, usage, upgrade options, and Stripe portal access.
 *
 * GET  /api/billing/plans        — list plans
 * GET  /api/billing/subscription — current plan status
 * POST /api/billing/subscribe    — create Stripe Checkout
 * POST /api/billing/portal       — create Stripe Customer Portal session
 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/api";

const DEV_HEADER: Record<string, string> = {
  "X-Dev-Clerk-User-Id": "test_user_mike",
  "Content-Type": "application/json",
};

interface Plan {
  id: string;
  name: string;
  price_monthly: number;
  estimate_limit: number | null;
  features: string[];
}

interface Subscription {
  company_id: string;
  plan: string;
  plan_name: string;
  price_monthly: number;
  estimate_limit: number | null;
  monthly_estimate_count: number;
  remaining_estimates: number | null;
  features: string[];
  stripe_subscription_id: string | null;
  is_active: boolean;
  can_create_estimate: boolean;
}

export default function BillingPage() {
  const [sub, setSub] = useState<Subscription | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/billing/subscription`, { headers: DEV_HEADER }).then((r) => r.ok ? r.json() : null),
      fetch(`${API_URL}/api/billing/plans`).then((r) => r.ok ? r.json() : null),
    ])
      .then(([subData, plansData]) => {
        setSub(subData && !subData.detail ? subData : null);
        setPlans(plansData?.plans || []);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load billing info — is the API running?");
        setLoading(false);
      });
  }, []);

  const handleSubscribe = async (planId: string) => {
    setActionLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API_URL}/api/billing/subscribe`, {
        method: "POST",
        headers: DEV_HEADER,
        body: JSON.stringify({ plan_id: planId }),
      });
      const data = await r.json();
      if (!r.ok) {
        if (r.status === 403) {
          setError("Only the account owner can manage subscriptions.");
          return;
        }
        throw new Error(data.detail || "Checkout failed");
      }
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setActionLoading(false);
    }
  };

  const handlePortal = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API_URL}/api/billing/portal`, {
        method: "POST",
        headers: DEV_HEADER,
      });
      const data = await r.json();
      if (!r.ok) {
        if (r.status === 403) {
          setError("Only the account owner can manage subscriptions.");
          return;
        }
        throw new Error(data.detail || "Portal failed");
      }
      if (data.portal_url) {
        window.location.href = data.portal_url;
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "An error occurred");
    } finally {
      setActionLoading(false);
    }
  };

  const usagePercent =
    sub && sub.estimate_limit
      ? Math.min(100, Math.round((sub.monthly_estimate_count / sub.estimate_limit) * 100))
      : null;

  const planColors: Record<string, string> = {
    trial: "bg-gray-100 text-gray-700",
    starter: "bg-blue-100 text-blue-700",
    pro: "bg-purple-100 text-purple-700",
    free: "bg-gray-100 text-gray-600",
  };

  return (
    <div className="space-y-5 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pt-2">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">Billing</h1>
          <p className="text-text-secondary text-sm mt-0.5">Manage your subscription and usage</p>
        </div>
        <Link
          href="/settings"
          className="text-sm text-text-secondary hover:text-text-primary transition-colors"
        >
          ← Settings
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-brand-red text-sm rounded-xl px-4 py-3">
          {error}
        </div>
      )}
      {successMsg && (
        <div className="bg-green-50 border border-green-200 text-green-700 text-sm rounded-xl px-4 py-3">
          {successMsg}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          <div className="bg-white border border-surface-border rounded-ss shadow-ss h-32 animate-pulse" />
          <div className="bg-white border border-surface-border rounded-ss shadow-ss h-48 animate-pulse" />
        </div>
      ) : sub ? (
        <>
          {/* Current Plan Card */}
          <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <p className="text-[9px] font-mono font-bold uppercase tracking-widest text-text-secondary mb-2">
                  Current Plan
                </p>
                <div className="flex items-center gap-2 mb-2">
                  <h2 className="text-xl font-extrabold font-mono">{sub.plan_name}</h2>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${planColors[sub.plan] || "bg-gray-100 text-gray-600"}`}>
                    {sub.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <p className="text-text-secondary text-sm font-mono">
                  {sub.price_monthly === 0 ? "Free" : `$${sub.price_monthly}/month`}
                </p>
              </div>
              {sub.stripe_subscription_id && (
                <button
                  onClick={handlePortal}
                  disabled={actionLoading}
                  className="text-sm text-brand-green font-semibold hover:underline disabled:opacity-50"
                >
                  Manage Subscription →
                </button>
              )}
            </div>

            {/* Usage */}
            <div className="bg-surface-bg rounded-ss p-4 border border-surface-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold">Assessments This Month</span>
                <span className="text-sm font-mono font-bold">
                  {sub.monthly_estimate_count}
                  {sub.estimate_limit !== null ? ` / ${sub.estimate_limit}` : " / ∞"}
                </span>
              </div>
              {usagePercent !== null ? (
                <div className="h-2 bg-surface-border rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      usagePercent >= 90 ? "bg-brand-red" : usagePercent >= 70 ? "bg-brand-orange" : "bg-brand-green"
                    }`}
                    style={{ width: `${usagePercent}%` }}
                  />
                </div>
              ) : (
                <div className="h-2 bg-surface-border rounded-full overflow-hidden">
                  <div className="h-full w-1/4 bg-brand-green rounded-full" />
                </div>
              )}
              {sub.remaining_estimates !== null && (
                <p className="text-xs text-text-secondary mt-1.5">
                  {sub.remaining_estimates === 0 ? (
                    <span className="text-brand-red font-semibold">Limit reached — upgrade to continue</span>
                  ) : (
                    `${sub.remaining_estimates} estimates remaining`
                  )}
                </p>
              )}
            </div>

            {/* Features */}
            <div className="mt-4 flex flex-wrap gap-1.5">
              {(sub.features ?? []).map((f) => (
                <span
                  key={f}
                  className="text-xs bg-surface-bg border border-surface-border text-text-secondary px-2 py-0.5 rounded-full"
                >
                  ✓ {f}
                </span>
              ))}
            </div>
          </div>

          {/* Upgrade / Change Plan */}
          {sub.plan !== "pro" && (
            <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
              <h3 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-2">
                {sub.plan === "trial" || sub.plan === "free" ? "Upgrade Your Plan" : "Change Plan"}
              </h3>
              <p className="text-text-secondary text-sm mb-4">
                Unlock unlimited estimates, SMS notifications, follow-up automation, and more.
              </p>
              <div className="space-y-3">
                {plans
                  .filter((p) => p.id !== "trial" && p.id !== (sub.plan === "free" ? "" : sub.plan))
                  .map((plan) => (
                    <div
                      key={plan.id}
                      className="border border-surface-border rounded-ss p-4 flex items-center gap-4 bg-white hover:bg-surface-bg transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="font-extrabold text-sm font-mono">{plan.name}</span>
                          {plan.id === "pro" && (
                            <span className="text-xs font-bold bg-brand-green text-white px-1.5 py-0.5 rounded-full">
                              RECOMMENDED
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-text-secondary font-mono">
                          {plan.estimate_limit === null ? "Unlimited estimates" : `${plan.estimate_limit} estimates/month`}
                        </p>
                        <ul className="mt-1 space-y-0.5">
                          {plan.features.slice(0, 2).map((f) => (
                            <li key={f} className="text-xs text-text-secondary flex items-center gap-1">
                              <span className="text-brand-green text-[10px]">✓</span> {f}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="font-extrabold text-lg font-mono">${plan.price_monthly}</p>
                        <p className="text-xs text-text-secondary font-mono">/month</p>
                        <button
                          onClick={() => handleSubscribe(plan.id)}
                          disabled={actionLoading}
                          className="mt-2 bg-brand-green text-white text-xs font-bold px-3 py-1.5 rounded-xl hover:bg-green-700 transition-colors disabled:opacity-50 shadow-ss"
                        >
                          {actionLoading ? "..." : "Upgrade →"}
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Pro plan — portal link */}
          {sub.plan === "pro" && (
            <div className="bg-white border border-surface-border rounded-ss shadow-ss p-5">
              <h3 className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-2">Manage Subscription</h3>
              <p className="text-text-secondary text-sm mb-4">
                Update payment method, view invoices, or cancel your subscription via the Stripe portal.
              </p>
              <button
                onClick={handlePortal}
                disabled={actionLoading}
                className="bg-brand-green text-white font-bold px-4 py-2.5 rounded-xl text-sm shadow-ss hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {actionLoading ? "Loading..." : "Open Billing Portal →"}
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white border border-surface-border rounded-ss shadow-ss p-8 text-center text-text-secondary">
          <p>Billing info unavailable. Please try again.</p>
        </div>
      )}
    </div>
  );
}
