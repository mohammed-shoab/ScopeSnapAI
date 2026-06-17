/**
 * SnapAI -- /tech landing page (D.1)
 * Contractor-targeted landing page for cold email, LinkedIn DMs, video bio links.
 * Destination: snapai.mainnov.tech/tech
 *
 * PostHog: fires "tech_landing_visited" on mount (captures UTM params)
 * CTA: routes to /dashboard (Clerk auth / sign-up flow)
 */

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import { usePostHog } from "posthog-js/react";

export default function TechLandingPage() {
  const posthog = usePostHog();
  const [copied, setCopied] = useState(false);
  const router = useRouter();
  const { isLoaded, isSignedIn } = useUser();

  // 4.14: redirect signed-in users to dashboard
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.replace("/dashboard");
    }
  }, [isLoaded, isSignedIn, router]);

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
      title: "Snap the nameplate in the truck.",
      description:
        "You're at the job. Open the app, photograph the data plate. Make, model, year, refrigerant pulled in seconds. No supply house phone calls.",
    },
    {
      number: "02",
      title: "Walk the diagnosis on your phone.",
      description:
        "Guided fault tree. Same logic your best senior tech runs in his head — written down. Diagnosis in under 90 seconds, every tech, every call.",
    },
    {
      number: "03",
      title: "Quote and close before you pull out.",
      description:
        "Good / Better / Best estimate with your markup applied. Homeowner approves on your phone. Branded PDF in their inbox before you turn the key.",
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
          Built for Houston contractors first
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary leading-tight mb-5 max-w-3xl mx-auto">
          Diagnose, estimate, and close before you leave the driveway.
        </h1>

        <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto mb-6 leading-relaxed">
          Guided diagnostic, three-tier estimate, homeowner-approved PDF — all on your phone before you leave the driveway.
        </p>

        {/* 4.13 positioning callout */}
        <p className="text-sm text-text-tertiary max-w-xl mx-auto mb-8 italic">
          If your service truck is your office, this is for you. No implementation team. No quarterly review. No IT.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-ss bg-brand-green text-white font-semibold text-base shadow-green hover:bg-brand-green-dark transition-colors"
            onClick={() => posthog?.capture("tech_cta_clicked", { location: "hero" })}
          >
            Start Free Beta Access
          </Link>
          <p className="text-sm text-text-tertiary">Wave 1 — looking for the first 5 Houston techs. Free during beta, no credit card.</p>
        </div>

        {/* 4.15: Hero video embed — TODO: replace placeholder with /hero.mp4 once Shoab provides it */}
        <div className="mt-10 max-w-3xl mx-auto rounded-2xl overflow-hidden bg-surface-card border border-surface-border">
          <video
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            className="w-full h-auto rounded-xl shadow-lg"
          >
            <source src="/hero.mp4" type="video/mp4" />
          </video>
        </div>
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
            most often on Houston residential systems. The diagnostic engine, fault card database,
            and pricing tiers reflect months of that research.
          </p>
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            Wave 1 beta now open — first 5 Houston HVAC techs get founding access.
            Your senior tech reviews the diagnostic tree before we wire it to your team.
            Your input rewrites the tree.
          </p>
          <p className="text-xs font-semibold text-brand-green">
            Free during beta, no credit card. After beta, $39/tech/month with a 14-day free trial. Flat fee, no add-on modules.
          </p>
        </div>
      </section>

            {/* ── Beta CTA (bottom) ──────────────────────────────────────────────── */}
      <section className="bg-brand-green py-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            Free for the first 5 Houston techs.
          </h2>
          <p className="text-green-100 mb-8 leading-relaxed">
            Built with Houston field experience. Diagnostic logic validated against real residential
            split-system calls. R-410A, R-22 surcharges, and Houston labor rates all baked in.
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

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer className="bg-surface-bg border-t border-surface-border py-8">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">

          {/* ── About block (2026-05-29 — resolves geography-honesty fragility per Strategic Narrative v1.1) ─── */}
          <div className="mb-6 pb-6 border-b border-surface-border">
            <p className="text-xs text-text-tertiary leading-relaxed max-w-3xl">
              <span className="font-semibold text-text-secondary">About:</span>{" "}
              SnapAI is built by Shoab, a data scientist based in Pakistan, in close iteration with Houston HVAC techs.
              Wave 1 beta is live now — looking for 5 Houston techs to calibrate the diagnostic tree against real calls.
              Reach out:{" "}
              <a
                href="mailto:sajan@hellosnapai.com"
                className="text-brand-green hover:underline"
              >
                sajan@hellosnapai.com
              </a>
              .
            </p>
          </div>

          {/* ── Existing footer row ──────────────────────────────────── */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-text-tertiary">
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
            <Link href="/dashboard" className="hover:text-text-secondary transition-colors">Sign In</Link>
            <button
              onClick={handleCopyLink}
              className="hover:text-text-secondary transition-colors"
            >
              {copied ? "Link copied!" : "Share this page"}
            </button>
          </div>
        </div>
        </div>
      </footer>

    </main>
  );
}
