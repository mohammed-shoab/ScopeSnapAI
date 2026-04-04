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

  pageView: (pageName: string) =>
    trackEvent("page_view", { page: pageName }),
};
