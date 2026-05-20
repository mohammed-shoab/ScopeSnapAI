/**
 * SnapAI — Event Tracking Utility
 * SOW Task 1.10: Send behavioral events to POST /api/events.
 *
 * Design:
 * - Fire-and-forget: never blocks user interaction
 * - Silent fail: network errors are swallowed (never crash the app)
 * - Session ID: generated once per page load, stored in sessionStorage
 * - All events include: event_name, event_data, session_id, page_url
 *
 * Standard event names (lowercase_snake_case):
 *   assessment_started      — user taps "New Assessment"
 *   assessment_photo_added  — photo added to assessment
 *   assessment_submitted    — form submitted to API
 *   assessment_completed    — AI analysis returned successfully
 *   assessment_queued_offline — stored to IndexedDB (offline)
 *   estimate_generated      — Good/Better/Best estimate created
 *   report_viewed           — homeowner opened the report URL
 *   report_approved         — homeowner tapped Approve
 *   email_sent              — estimate email sent to homeowner
 *   email_failed            — email delivery failed after retries
 *   user_signed_up          — new contractor account created
 *   page_view               — any page navigation
 */

import { API_URL } from "./api";

// ── Session ID ────────────────────────────────────────────────────────────────
let _sessionId: string | null = null;

function getSessionId(): string {
  if (_sessionId) return _sessionId;
  try {
    const stored = sessionStorage.getItem("ss_session_id");
    if (stored) {
      _sessionId = stored;
      return stored;
    }
    const id = `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    sessionStorage.setItem("ss_session_id", id);
    _sessionId = id;
    return id;
  } catch {
    // sessionStorage unavailable (SSR or private mode)
    _sessionId = `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    return _sessionId;
  }
}

// ── Event payload type ────────────────────────────────────────────────────────
export interface TrackEventPayload {
  event_name: string;
  event_data?: Record<string, unknown>;
}

// ── trackEvent — fire-and-forget ──────────────────────────────────────────────
export async function trackEvent(
  eventName: string,
  eventData: Record<string, unknown> = {}
): Promise<void> {
  // Don't track in server context
  if (typeof window === "undefined") return;

  const payload = {
    event_name: eventName,
    event_data: eventData,
    session_id: getSessionId(),
    page_url: window.location.href,
    user_agent: navigator.userAgent,
  };

  try {
    // Use navigator.sendBeacon for page_view events (more reliable on unload)
    if (eventName === "page_view" && typeof navigator.sendBeacon === "function") {
      navigator.sendBeacon(
        `${API_URL}/api/events`,
        new Blob([JSON.stringify(payload)], { type: "application/json" })
      );
      return;
    }

    await fetch(`${API_URL}/api/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      // Short timeout — don't block UX
      signal: AbortSignal.timeout?.(3000),
    });
  } catch {
    // Silent fail — tracking must never crash the app
  }
}

// ── Convenience helpers ───────────────────────────────────────────────────────
export const track = {
  assessmentStarted: () => trackEvent("assessment_started"),

  photoAdded: (count: number, fileSizeBytes?: number) =>
    trackEvent("assessment_photo_added", {
      photo_count: count,
      // file_size_bytes: connection quality signal — Bezos req (SOW Task 1.10)
      // Large files on slow connections = blurry photos + timeouts in the field
      ...(fileSizeBytes !== undefined ? { file_size_bytes: fileSizeBytes } : {}),
    }),

  assessmentSubmitted: (photoCount: number) =>
    trackEvent("assessment_submitted", { photo_count: photoCount }),

  assessmentCompleted: (assessmentId: string) =>
    trackEvent("assessment_completed", { assessment_id: assessmentId }),

  assessmentQueuedOffline: () =>
    trackEvent("assessment_queued_offline"),

  estimateGenerated: (estimateId: string, total: number) =>
    trackEvent("estimate_generated", { estimate_id: estimateId, total }),

  reportViewed: (reportShortId: string) =>
    trackEvent("report_viewed", { report_short_id: reportShortId }),

  reportApproved: (reportShortId: string, tier: string) =>
    trackEvent("report_approved", { report_short_id: reportShortId, tier }),


  // -- Recommendation engine events (REC.5) ----------------------------------

  // Fires when the estimate tiers are first shown to the tech.
  // Wire this call in the component that receives the fault-card API response
  // (assess/page.tsx after R.3 is complete, or estimate/[id]/page.tsx after R.7).
  recommendationShown: (
    cardId: number,
    recommendedTier: string,
    reason?: string,
    source?: string,
  ) =>
    trackEvent("recommendation_shown", {
      card_id: cardId,
      recommended_tier: recommendedTier,
      ...(reason !== undefined ? { reason } : {}),
      ...(source !== undefined ? { source } : {}),
    }),

  // Fires when the tech selects a tier different from the recommended one
  // before sending the report.
  // Wire in estimate/[id]/page.tsx after R.7 is complete.
  recommendationOverridden: (
    cardId: number,
    originalTier: string,
    chosenTier: string,
    estimateId?: string,
  ) =>
    trackEvent("recommendation_overridden", {
      card_id: cardId,
      original_recommended_tier: originalTier,
      chosen_tier: chosenTier,
      ...(estimateId !== undefined ? { estimate_id: estimateId } : {}),
    }),

  // Fires when the homeowner approves a tier on the report page.
  // Captures whether the approved tier matches the original recommendation.
  // Wire in ReportClient.tsx after R.1-R.5 are complete.
  recommendationApproved: (
    cardId: number,
    approvedTier: string,
    recommendedTier: string,
    reportId?: string,
  ) =>
    trackEvent("recommendation_approved", {
      card_id: cardId,
      approved_tier: approvedTier,
      recommended_tier: recommendedTier,
      matched_recommendation: approvedTier === recommendedTier,
      ...(reportId !== undefined ? { report_id: reportId } : {}),
    }),

  pageView: (pageName: string) =>
    trackEvent("page_view", { page: pageName }),

  // ── Track D: Diagnosis screen events ────────────────────────────────────────

  // Fires when the /diagnoses list page loads.
  diagnosisListOpened: () =>
    trackEvent("diagnosis_list_opened", {}),

  // Fires when a tech opens a diagnosis detail that is older than 5 minutes (a revisit).
  diagnosisRevisited: (sessionId: string, ageMs: number) =>
    trackEvent("diagnosis_revisited", { session_id: sessionId, age_ms: ageMs }),

  // Fires on mount of FaultResolutionScreen (both authenticated + public modes).
  faultScreenOpened: (sessionId: string, mode: string, confidence: string) =>
    trackEvent("fault_screen_opened", { session_id: sessionId, mode, confidence }),

  // Fires when tech agrees ("solved") or disagrees ("different_fault") with diagnosis.
  faultScreenAgreement: (sessionId: string, agreement: string, hasText: boolean, alternativeFaultId?: number | null) =>
    trackEvent("fault_screen_agreement", {
      session_id: sessionId,
      agreement,
      has_text: hasText,
      ...(alternativeFaultId != null ? { alternative_fault_id: alternativeFaultId } : {}),
    }),

  // Fires when the "Copy share link" button is tapped.
  faultScreenShareClicked: (sessionId: string) =>
    trackEvent("fault_screen_share_clicked", { session_id: sessionId }),

  // Fires when the reasoning chain <details> is expanded.
  faultScreenReasoningExpanded: (sessionId: string) =>
    trackEvent("fault_screen_reasoning_expanded", { session_id: sessionId }),

  // Fires when the public share page (/d/[share_token]) loads successfully.
  diagnosisShareOpenedExternally: (shareToken: string) =>
    trackEvent("diagnosis_share_opened_externally", { share_token: shareToken }),

  // Fires on unmount of FaultResolutionScreen with time spent on screen.
  faultScreenTimeOnScreen: (sessionId: string, seconds: number) =>
    trackEvent("fault_screen_time_on_screen", { session_id: sessionId, seconds }),

  // ── Track DX: Diagnosis screen UX refinement events ──────────────────────

  // Fires when user taps a Repair Plan tier card to expand it (DX.13).
  repairPlanTierExpanded: (sessionId: string, tier: "good" | "better" | "best") =>
    trackEvent("repair_plan_tier_expanded", { session_id: sessionId, tier }),

  // Fires when post-20-diagnoses user taps "See other options" link (DX.13).
  repairPlanSeeOtherOptions: (sessionId: string) =>
    trackEvent("repair_plan_see_other_options_clicked", { session_id: sessionId }),

  // Fires when user taps the Continue button (DX.13).
  faultScreenEstimateGenerated: (sessionId: string, labelVariant: "with_destination" | "short") =>
    trackEvent("fault_screen_estimate_generated", { session_id: sessionId, label_variant: labelVariant }),

  // Fires when user opens Different problem modal then taps Skip (DX.13).
  faultScreenAgreementSkipped: (sessionId: string) =>
    trackEvent("fault_screen_agreement_skipped", { session_id: sessionId }),

  // Fires when user cancels diagnosis from "..." menu (DX.13).
  diagnosisCancelled: (sessionId: string) =>
    trackEvent("diagnosis_cancelled", { session_id: sessionId }),

  // Fires when user restarts diagnostic from "..." menu (DX.13).
  diagnosisRestarted: (sessionId: string) =>
    trackEvent("diagnosis_restarted", { session_id: sessionId }),
  // ── Track G: 5-Year TCO engagement events ────────────────────────────────

  // Fires on mount of FiveYearComparison (once per render, guarded by ref).
  tcoSectionRendered: (sessionId: string, market: string, recommendedTier: string, mode: string) =>
    trackEvent("tco_section_rendered", { session_id: sessionId, market, recommended_tier: recommendedTier, mode }),

  // Fires when user hovers or touches a non-recommended tier card.
  tcoOptionCompared: (sessionId: string, tier: string) =>
    trackEvent("tco_option_compared", { session_id: sessionId, tier }),

  // Fires when the methodology block scrolls into the viewport (IntersectionObserver).
  tcoMethodologyViewed: (sessionId: string) =>
    trackEvent("tco_methodology_viewed", { session_id: sessionId }),

};