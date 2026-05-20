/**
 * userSessionCounter.ts — Track DX (DX.12)
 * localStorage counters for self-graduating UI behaviours.
 *
 * Counter 1: snapai_diagnoses_opened_count
 *   Incremented each time FaultResolutionScreen mounts in authenticated mode.
 *   Used to graduate the Repair Plan section (< 20 => show all 3 tiers).
 *
 * Counter 2: snapai_app_sessions_count
 *   Incremented once per "session" (6-hour cooldown between increments).
 *   Used to graduate the Continue button label (sessions 1-3 => full label).
 *
 * Cross-device sync is v1.5. For v1 these are per-device only.
 */

// ── Diagnoses opened counter ──────────────────────────────────────────────────

const DIAG_KEY = "snapai_diagnoses_opened_count";

export function incrementDiagnosesOpened(): number {
  try {
    const current = parseInt(localStorage.getItem(DIAG_KEY) || "0", 10);
    const next = current + 1;
    localStorage.setItem(DIAG_KEY, String(next));
    return next;
  } catch {
    return 0;
  }
}

export function getDiagnosesOpenedCount(): number {
  try {
    return parseInt(localStorage.getItem(DIAG_KEY) || "0", 10);
  } catch {
    return 0;
  }
}

// ── App sessions counter ──────────────────────────────────────────────────────

const SESSION_COUNT_KEY = "snapai_app_sessions_count";
const SESSION_LAST_KEY  = "snapai_last_session_timestamp";
const SIX_HOURS_MS      = 6 * 60 * 60 * 1000;

export function incrementSessionCount(): number {
  try {
    const now  = Date.now();
    const last = parseInt(localStorage.getItem(SESSION_LAST_KEY) || "0", 10);
    if (now - last > SIX_HOURS_MS) {
      const next = parseInt(localStorage.getItem(SESSION_COUNT_KEY) || "0", 10) + 1;
      localStorage.setItem(SESSION_COUNT_KEY, String(next));
      localStorage.setItem(SESSION_LAST_KEY, String(now));
      return next;
    }
    return parseInt(localStorage.getItem(SESSION_COUNT_KEY) || "0", 10);
  } catch {
    return 0;
  }
}

export function getSessionCount(): number {
  try {
    return parseInt(localStorage.getItem(SESSION_COUNT_KEY) || "0", 10);
  } catch {
    return 0;
  }
}
