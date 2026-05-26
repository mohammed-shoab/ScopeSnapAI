/**
 * SnapAI -- /homeowner landing page (D.2)
 * Homeowner-targeted landing page for cat ad traffic and homeowner-facing posts.
 * Destination: snapai.mainnov.tech/homeowner
 *
 * PostHog: fires "homeowner_landing_visited" on mount
 * CTA: Share buttons (WhatsApp, email, copy link) -- NO sign-up form
 * Contractors sign up; homeowners share this page with their contractor.
 */

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import { usePostHog } from "posthog-js/react";

export default function HomeownerLandingPage() {
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

  // PostHog: fire homeowner_landing_visited + capture UTM params
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    posthog?.capture("homeowner_landing_visited", {
      utm_source: params.get("utm_source"),
      utm_medium: params.get("utm_medium"),
      utm_campaign: params.get("utm_campaign"),
      utm_content: params.get("utm_content"),
      referrer: document.referrer || null,
    });
  }, [posthog]);

  const pageUrl = typeof window !== "undefined" ? window.location.href : "https://snapai.mainnov.tech/homeowner";
  const shareText = "Ask your HVAC contractor if they use SnapAI — it shows you three repair options with real prices before they leave.";

  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(shareText + " " + pageUrl)}`;
  const emailUrl = `mailto:?subject=${encodeURIComponent("A clearer HVAC estimate — ask your contractor about this")}&body=${encodeURIComponent(shareText + "\n\n" + pageUrl)}`;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(pageUrl);
      setCopied(true);
      posthog?.capture("homeowner_share_clicked", { method: "copy" });
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // clipboard unavailable
    }
  };

  const expectations = [
    {
      number: "01",
      title: "A diagnostic report explaining what is wrong",
      description:
        "Your contractor photographs the unit and follows a guided fault-detection process. The app identifies the problem — no guessing, no vague answers.",
    },
    {
      number: "02",
      title: "Three repair options at different price points",
      description:
        "You see a Good option (quick fix), a Better option (fix plus prevention), and a Best option (most thorough — addresses root cause, includes pressure testing). Real prices. Your call which one to choose.",
    },
    {
      number: "03",
      title: "A 5-year outlook showing future repair risk",
      description:
        "Each option shows the projected repair cost and energy savings over the next five years. You see the full picture before you decide.",
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
          </div>
          <Link
            href="/dashboard"
            className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
          >
            Contractors: Sign In
          </Link>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 pt-16 pb-12 text-center">
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary leading-tight mb-5 max-w-3xl mx-auto">
          Three options. Real prices. No surprises.
        </h1>

        <p className="text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto mb-8 leading-relaxed">
          When your HVAC contractor uses SnapAI, you get a clear written estimate with three
          repair options before they leave. You see what is wrong, what each fix costs, and
          what happens if you wait.
        </p>

        <p className="text-sm text-text-secondary max-w-xl mx-auto mb-4">
          Ask your contractor if they use SnapAI.
          If they do not, share this page with them.
        </p>

        {/* 4.13: market scope line */}
        <p className="text-xs text-text-tertiary max-w-xl mx-auto">
          Currently active in Houston, Texas. Other markets coming.
        </p>
      </section>

      {/* ── What to Expect ─────────────────────────────────────────────────── */}
      <section className="bg-surface-card border-y border-surface-border py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-4">
            What you get when your contractor uses SnapAI
          </h2>
          <p className="text-center text-text-secondary mb-12 max-w-xl mx-auto text-sm">
            No more "I will call you with a price." No more waiting two days for a quote.
            No more wondering if you are being overcharged.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {expectations.map((item) => (
              <div key={item.number} className="flex flex-col">
                <div className="text-3xl font-bold text-brand-green mb-3 font-mono">
                  {item.number}
                </div>
                <h3 className="text-base font-semibold text-text-primary mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
          <p className="text-sm text-text-secondary mt-8 text-center max-w-lg mx-auto leading-relaxed">
            Your contractor’s SnapAI estimate marks one tier as ★️ Recommended based on your unit’s age and condition — sometimes Good, sometimes Better, sometimes Best.
          </p>
        </div>
      </section>

      {/* ── Sample Report Preview ──────────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 py-16">
        <h2 className="text-2xl font-bold text-center mb-10">
          What the estimate looks like
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto">
          {[
            {
              tier: "Good",
              label: "Quick fix",
              color: "text-text-primary",
              bg: "bg-surface-card",
              border: "border-surface-border",
              description: "Replace the failed component. Gets you running today.",
            },
            {
              tier: "Better",
              label: "Fix + prevent",
              color: "text-brand-green",
              bg: "bg-brand-green-light",
              border: "border-brand-green",
              description: "Fix the fault and address the root cause. Recommended.",
              recommended: true,
            },
            {
              tier: "Best",
              label: "Most Thorough",
              color: "text-text-primary",
              bg: "bg-surface-card",
              border: "border-surface-border",
              description: "New system install. Best long-term value if unit is aging.",
            },
          ].map((option) => (
            <div
              key={option.tier}
              className={`${option.bg} border ${option.border} rounded-ss p-5 shadow-ss relative`}
            >
              {option.recommended && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-xs font-bold text-white bg-brand-green px-3 py-1 rounded-full shadow-green">
                  RECOMMENDED
                </div>
              )}
              <div className={`text-lg font-bold ${option.color} mb-0.5`}>{option.tier}</div>
              <div className="text-xs text-text-tertiary font-medium mb-3 uppercase tracking-wide">
                {option.label}
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">{option.description}</p>
            </div>
          ))}
        </div>
        <p className="text-center text-xs text-text-tertiary mt-6">
          Every estimate includes parts, labor, and a branded PDF delivered to your inbox.
        </p>
      </section>

      {/* ── Share Section ──────────────────────────────────────────────────── */}
      <section className="bg-brand-green py-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            Share with your contractor
          </h2>
          <p className="text-green-100 mb-10 leading-relaxed">
            Your contractor controls whether you get a SnapAI estimate.
            Forward this page and ask them to sign up. It is free for them during beta.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-ss bg-white text-brand-green font-semibold text-sm hover:bg-green-50 transition-colors shadow-ss-lg"
              onClick={() => posthog?.capture("homeowner_share_clicked", { method: "whatsapp" })}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 shrink-0">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
              </svg>
              Share via WhatsApp
            </a>

            <a
              href={emailUrl}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-ss bg-white text-brand-green font-semibold text-sm hover:bg-green-50 transition-colors shadow-ss-lg"
              onClick={() => posthog?.capture("homeowner_share_clicked", { method: "email" })}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 shrink-0">
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
              </svg>
              Share via Email
            </a>

            <button
              onClick={handleCopyLink}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-ss border-2 border-white text-white font-semibold text-sm hover:bg-white hover:text-brand-green transition-colors"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 shrink-0">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              {copied ? "Copied!" : "Copy Link"}
            </button>
          </div>

          <div className="mt-10 pt-8 border-t border-green-600">
            <p className="text-green-100 text-sm mb-4">
              Are you an HVAC contractor? Sign up free during beta.
            </p>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center px-6 py-3 rounded-ss border border-white text-white font-medium text-sm hover:bg-green-700 transition-colors"
              onClick={() => posthog?.capture("homeowner_contractor_cta_clicked")}
            >
              Contractor Sign Up -- Free Beta
            </Link>
          </div>
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
            <Link href="/dashboard" className="hover:text-text-secondary transition-colors">Contractor Sign In</Link>
          </div>
        </div>
      </footer>

    </main>
  );
}
