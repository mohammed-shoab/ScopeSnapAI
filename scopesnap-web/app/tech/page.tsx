/**
 * SnapAI -- /tech landing page (D.1)
 * Contractor-targeted landing page for cold email, LinkedIn DMs, video bio links.
 * Destination: snapai.mainnov.tech/tech  (also served at the site root "/" via rewrite)
 *
 * PostHog: fires "tech_landing_visited" on mount (captures UTM params)
 * Primary CTA: routes to /dashboard (Clerk auth / sign-up flow)
 * Secondary (owner) CTA: book-a-call for the free data audit (owner door)
 */

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePostHog } from "posthog-js/react";

// TODO(Shoab): replace with the real book-a-call scheduling link (Cal.com / Calendly).
// PLACEHOLDER for now — the owner "Request your free audit" secondary CTA points here.
const OWNER_AUDIT_BOOKING_URL = "https://cal.com/REPLACE-ME/snapai-audit";

export default function TechLandingPage() {
  const posthog = usePostHog();
  const [copied, setCopied] = useState(false);

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
        "Answer a set of guided questions about what the unit's doing. SnapAI walks your tech through the fault, step by step.",
    },
    {
      number: "03",
      title: "Three clear options and a recommendation — in minutes",
      description:
        "SnapAI builds a three-tier estimate with your markup applied. Hand the homeowner a branded PDF before you leave.",
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
          Turn a tough HVAC call into a clean, three-option quote.
        </h1>

        <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto mb-8 leading-relaxed">
          SnapAI is the app that helps any HVAC tech assess a tough call and turn it into a clear, three-option quote for the homeowner in minutes — no CRM to get trapped in, and your tech makes every call.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-ss bg-brand-green text-white font-semibold text-base shadow-green hover:bg-brand-green-dark transition-colors"
            onClick={() => posthog?.capture("tech_cta_clicked", { location: "hero" })}
          >
            Start free →
          </Link>
          <p className="text-sm text-text-tertiary">Free for the first 10 techs. No credit card, no commitment.</p>
        </div>

        <p className="text-sm text-text-tertiary max-w-2xl mx-auto mt-6 leading-relaxed">
          SnapAI is a decision-support tool for licensed HVAC professionals. It organizes symptoms and surfaces likely faults to assist the technician&apos;s own judgment; it does not perform diagnosis, and all findings must be verified on site by a qualified tech.
        </p>
      </section>


            {/* ── How It Works ───────────────────────────────────────────────────── */}
      <section className="bg-surface-card border-y border-surface-border py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-12">
            Three steps, one clean quote.
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

      {/* ── Builder Positioning (research-backed section) ───────── */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        <div className="bg-surface-card border border-surface-border rounded-ss p-8 shadow-ss">
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            We built SnapAI by deeply researching how HVAC diagnostics actually work —
            manufacturer documentation, training references, and the fault patterns that show up
            most often on residential systems. The assessment engine, fault card database,
            and pricing tiers reflect months of that research.
          </p>
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            Now open to the first 10 HVAC techs. Free — and your input shapes what we build next.
          </p>
          <p className="text-xs font-semibold text-brand-green">
            Free while we build it with you. Pricing comes later.
          </p>
        </div>
      </section>

            {/* ── Primary CTA (bottom) ───────────────────────────────────────────── */}
      <section className="bg-brand-green py-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            Free for the first 10 techs.
          </h2>
          <p className="text-green-100 mb-8 leading-relaxed">
            Built from deep research — manufacturer specs, training references, and the residential
            fault patterns that show up most. R-410A and R-22 surcharges and your local labor rates
            are baked in.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center px-8 py-4 rounded-ss bg-white text-brand-green font-bold text-base hover:bg-green-50 transition-colors shadow-ss-lg"
            onClick={() => posthog?.capture("tech_cta_clicked", { location: "bottom" })}
          >
            Start free →
          </Link>
          <p className="text-green-100 text-xs mt-4">Free for the first 10 techs. No credit card.</p>
        </div>
      </section>

      {/* ── Owner Door (secondary — free data-audit offer) ─────────────────── */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        <div className="border border-surface-border rounded-ss p-8 bg-surface-bg">
          <h2 className="text-xl font-bold text-text-primary mb-3">Own a shop?</h2>
          <p className="text-sm text-text-secondary leading-relaxed mb-6">
            I&apos;m the data scientist who built SnapAI. Send me your last year of tickets and I&apos;ll
            show you — free — your real callback, repeat-visit, and lost-quote numbers on the tough
            calls, based on what your tickets show. I only take a few shops a month because I run
            every analysis myself.
          </p>
          <a
            href={OWNER_AUDIT_BOOKING_URL}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => posthog?.capture("owner_audit_cta_clicked", { location: "owner_door" })}
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-ss border border-brand-green text-brand-green font-semibold text-sm hover:bg-brand-green-light transition-colors"
          >
            Request your free audit →
          </a>
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
