/**
 * SnapAI -- /tech landing page (D.1)
 * Contractor-targeted landing page for cold email, LinkedIn DMs, video bio links.
 * Destination: snapai.mainnov.tech/tech
 *
 * PostHog: fires "tech_landing_visited" on mount (captures UTM params)
 * CTA: routes to /dashboard (Clerk auth / sign-up flow)
 */

// COPY DRAFT — pending Codie + Alfred sign-off
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePostHog } from "posthog-js/react";

export default function TechLandingPage() {
  const posthog = usePostHog();
  const [copied, setCopied] = useState(false);

  // Waitlist email-capture (moved from former root landing page) — POST /api/waitlist
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/waitlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      if (res.ok) {
        setSubmitted(true);
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data?.detail || "Something went wrong. Please try again.");
      }
    } catch {
      setError("Could not connect. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  // PostHog: fire tech_landing_visited + capture UTM params
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    posthog?.capture("tech_landing_visited", {
      utm_source: params.get("utm_source"),
      utm_medium: params.get("utm_medium"),
      utm_campaign: params.get("utm_campaign"),
      utm_content: params.get("utm_content"),
      referrer: document.referrer || null,
    });
  }, [posthog]);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard unavailable
    }
  };

  const steps = [
    {
      number: "01",
      title: "Photograph the unit",
      description:
        "Open SnapAI, tap New Assessment, and photograph the nameplate and unit. The AI reads make, model, age, and refrigerant automatically.",
    },
    {
      number: "02",
      title: "App walks the tech through the fault",
      description:
        "Answer a series of guided questions about symptoms. The system follows the same fault tree your best senior tech has in his head.",
    },
    {
      number: "03",
      title: "Three context-aware options, one recommendation — in 90 seconds",
      description:
        "SnapAI generates a three-tier estimate with your markup applied. Send the homeowner a branded PDF before you leave the driveway.",
    },
  ];

  return (
    <main className="min-h-screen bg-surface-bg text-text-primary font-sans">

      {/* ── Navigation ─────────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-surface-bg border-b border-surface-border">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div
              className="w-7 h-7 rounded-md flex items-center justify-center text-white text-sm font-bold"
              style={{ backgroundColor: "#1a8754" }}
            >
              S
            </div>
            <span className="font-semibold text-text-primary tracking-tight">SnapAI</span>
            <span className="hidden sm:inline-block text-xs font-medium px-2 py-0.5 rounded-full bg-brand-green-light text-brand-green ml-1">
              FREE BETA
            </span>
          </div>
          <Link
            href="/dashboard"
            className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            Sign In
          </Link>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 pt-16 pb-12 text-center">
        <div className="inline-flex items-center gap-2 text-xs font-semibold tracking-wide uppercase text-brand-green bg-brand-green-light px-3 py-1.5 rounded-full mb-6">
          Built for independent HVAC shops
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary leading-tight mb-5 max-w-3xl mx-auto">
          Your newest tech diagnoses like your most experienced.
        </h1>

        <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto mb-8 leading-relaxed">
          A decision-support app built for independent HVAC shops. It walks your tech through the fault, then lays out three context-aware options and a clear recommendation. Homeowner-approved PDF — before you pull out of the driveway.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-ss bg-brand-green text-white font-semibold text-base shadow-green hover:bg-brand-green-dark transition-colors"
            onClick={() => posthog?.capture("tech_cta_clicked", { location: "hero" })}
          >
            Start free — built for independent HVAC shops
          </Link>
          <p className="text-sm text-text-tertiary">First 10 testers. Free, no commitment.</p>
        </div>

        <p className="text-sm text-text-tertiary max-w-2xl mx-auto mt-6 leading-relaxed">
          SnapAI is a decision-support tool for licensed HVAC professionals. It organizes symptoms and surfaces likely faults to assist the technician&apos;s own judgment; it does not perform diagnosis, and all findings must be verified on site by a qualified tech.
        </p>
      </section>


            {/* ── How It Works ───────────────────────────────────────────────────── */}
      <section className="bg-surface-card border-y border-surface-border py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-12">
            Three steps. One job closed.
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {steps.map((step) => (
              <div key={step.number} className="flex flex-col">
                <div className="text-3xl font-bold text-brand-green mb-3 font-mono">
                  {step.number}
                </div>
                <h3 className="text-base font-semibold text-text-primary mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Builder Positioning (“honest voice” section) ───────── */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        <div className="bg-surface-card border border-surface-border rounded-ss p-8 shadow-ss">
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            We built SnapAI by deeply researching how HVAC diagnostic actually works —
            manufacturer documentation, training references, and the fault patterns that show up
            most often on residential systems. The assessment engine, fault card database,
            and pricing tiers reflect months of that research.
          </p>
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            Beta program now open — first 10 HVAC techs get founding access.
            Your input shapes every release.
          </p>
          <p className="text-xs font-semibold text-brand-green">
            Free during beta. Pricing announced before launch.
          </p>
        </div>
      </section>

            {/* ── Beta CTA (bottom) ──────────────────────────────────────────────── */}
      <section className="bg-brand-green py-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            Free for the first 10 techs.
          </h2>
          <p className="text-green-100 mb-8 leading-relaxed">
            Built with real field experience. Assessment logic validated against real residential
            split-system calls. R-410A, R-22 surcharges, and local labor rates all baked in.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center px-8 py-4 rounded-ss bg-white text-brand-green font-bold text-base hover:bg-green-50 transition-colors shadow-ss-lg"
            onClick={() => posthog?.capture("tech_cta_clicked", { location: "bottom" })}
          >
            Claim Your Free Beta Spot
          </Link>
          <p className="text-green-100 text-xs mt-4">No credit card. No commitment. Cancel anytime.</p>
        </div>
      </section>

      {/* ── Early Access Signup (waitlist — moved from former root landing) ── */}
      <section className="bg-surface-card border-y border-surface-border py-16">
        <div className="max-w-lg mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-2xl font-bold mb-3">Get early access</h2>
          <p className="text-text-secondary mb-8 text-sm leading-relaxed">
            Limited early access — first 30 assessments free.
            No credit card required.
          </p>
          {submitted ? (
            <div className="bg-brand-green/10 border border-brand-green/20 rounded-ss p-6">
              <p className="text-brand-green font-semibold text-lg mb-1">You&apos;re in!</p>
              <p className="text-text-secondary text-sm">
                Check your inbox — we&apos;ll send your access details shortly.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSignup} className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="flex-1 border border-surface-border rounded-ss px-4 py-3 text-sm bg-surface-bg focus:outline-none focus:ring-2 focus:ring-brand-green placeholder:text-text-secondary"
              />
              <button
                type="submit"
                disabled={submitting}
                className="bg-brand-green text-white font-semibold py-3 px-6 rounded-ss hover:bg-brand-green-dark transition-colors text-sm disabled:opacity-60 whitespace-nowrap"
              >
                {submitting ? "Sending…" : "Start Free →"}
              </button>
            </form>
          )}
          {error && (
            <p className="mt-3 text-red-500 text-xs">{error}</p>
          )}
          <p className="mt-4 text-xs text-text-secondary">
            No spam. Unsubscribe any time.
          </p>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer className="bg-surface-bg border-t border-surface-border py-8">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-text-tertiary">
          <div className="flex items-center gap-2">
            <div
              className="w-5 h-5 rounded flex items-center justify-center text-white text-xs font-bold"
              style={{ backgroundColor: "#1a8754" }}
            >
              S
            </div>
            <span>SnapAI by Mainnov</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/privacy" className="hover:text-text-secondary transition-colors">Privacy</Link>
            <Link href="/tos" className="hover:text-text-secondary transition-colors">Terms</Link>
            <Link href="/dashboard" className="hover:text-text-secondary transition-colors">Sign In</Link>
            <button
              onClick={handleCopyLink}
              className="hover:text-text-secondary transition-colors"
            >
              {copied ? "Link copied!" : "Share this page"}
            </button>
          </div>
        </div>
      </footer>

    </main>
  );
}
