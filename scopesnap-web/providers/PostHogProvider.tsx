"use client";

/**
 * PostHog Analytics Provider
 * Page/Brin requirement: instrument everything — know conversion funnels,
 * drop-off points, and user flows before you can improve them.
 *
 * Key events tracked:
 *   assessment_started      — user begins new assessment
 *   assessment_submitted    — assessment form submitted
 *   assessment_ai_complete  — AI analysis returned successfully
 *   estimate_generated      — Good/Better/Best estimate created
 *   estimate_correction     — contractor adjusted AI estimate (training signal)
 *   report_sent             — estimate emailed to homeowner
 *   report_viewed           — homeowner opened their report
 *   report_approved         — homeowner approved a tier
 *   user_signed_up          — new contractor account
 *   $pageview               — automatic page navigation (PostHog built-in)
 */

import posthog from "posthog-js";
import { PostHogProvider as PHProvider } from "posthog-js/react";
import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, Suspense } from "react";

// ── PostHog init ──────────────────────────────────────────────────────────────
const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com";

if (typeof window !== "undefined" && POSTHOG_KEY) {
  posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    capture_pageview: false, // We capture manually below for SPA routing
    capture_pageleave: true,
    autocapture: false,      // Manual instrumentation only (less noise, more signal)
    persistence: "localStorage+cookie",
    // Don't track in dev unless explicitly opted in
    loaded: (ph) => {
      if (process.env.NEXT_PUBLIC_ENV === "development") {
        ph.opt_out_capturing();
      }
    },
  });
}

// ── Page view tracker (SPA-aware) ─────────────────────────────────────────────
function PostHogPageView() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!POSTHOG_KEY) return;
    const url = pathname + (searchParams.toString() ? `?${searchParams}` : "");
    posthog.capture("$pageview", { $current_url: url });
  }, [pathname, searchParams]);

  return null;
}

// ── Provider wrapper ──────────────────────────────────────────────────────────
export function PostHogProvider({ children }: { children: React.ReactNode }) {
  if (!POSTHOG_KEY) {
    // No key configured — render children without analytics (dev/preview)
    return <>{children}</>;
  }

  return (
    <PHProvider client={posthog}>
      <Suspense fallback={null}>
        <PostHogPageView />
      </Suspense>
      {children}
    </PHProvider>
  );
}

// ── Typed event helpers ───────────────────────────────────────────────────────
export const ph = {
  /** Contractor started a new assessment */
  assessmentStarted: (assessmentId?: string) =>
    posthog.capture("assessment_started", { assessment_id: assessmentId }),

  /** Assessment submitted to AI */
  assessmentSubmitted: (photoCount: number) =>
    posthog.capture("assessment_submitted", { photo_count: photoCount }),

  /** AI analysis returned */
  assessmentAIComplete: (assessmentId: string, durationMs?: number) =>
    posthog.capture("assessment_ai_complete", {
      assessment_id: assessmentId,
      duration_ms: durationMs,
    }),

  /** Estimate page opened */
  estimateViewed: (estimateId: string) =>
    posthog.capture("estimate_viewed", { estimate_id: estimateId }),

  /** Estimate emailed to homeowner */
  reportSent: (estimateId: string, tier?: string) =>
    posthog.capture("report_sent", { estimate_id: estimateId, tier }),

  /** Contractor answered "Did you adjust?" — key training signal */
  estimateCorrection: (
    estimateId: string,
    adjusted: boolean,
    aiTotal?: number,
    actualTotal?: number
  ) =>
    posthog.capture("estimate_correction", {
      estimate_id: estimateId,
      adjusted,
      ai_total: aiTotal,
      actual_total: actualTotal,
      delta: aiTotal != null && actualTotal != null ? actualTotal - aiTotal : undefined,
      delta_pct:
        aiTotal != null && actualTotal != null && aiTotal > 0
          ? Math.round(((actualTotal - aiTotal) / aiTotal) * 100)
          : undefined,
    }),

  /** Homeowner opened report */
  reportViewed: (reportShortId: string) =>
    posthog.capture("report_viewed", { report_short_id: reportShortId }),

  /** Homeowner approved a tier */
  reportApproved: (reportShortId: string, tier: string) =>
    posthog.capture("report_approved", { report_short_id: reportShortId, tier }),

  /** Estimate G/B/B generated (after AI completes and card is resolved) */
  estimateGenerated: (estimateId: string, cardName?: string) =>
    posthog.capture("estimate_generated", { estimate_id: estimateId, card_name: cardName }),

  /** Identify contractor for user-level analytics */
  identify: (userId: string, traits?: Record<string, unknown>) =>
    posthog.identify(userId, traits),

  /** Reset on sign-out */
  reset: () => posthog.reset(),
};
