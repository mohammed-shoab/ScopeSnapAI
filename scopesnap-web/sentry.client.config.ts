/**
 * SnapAI — Sentry Frontend Error Tracking
 * Catches unhandled errors in the browser and reports them to Sentry.
 * DSN set via NEXT_PUBLIC_SENTRY_DSN environment variable.
 */
import * as Sentry from "@sentry/nextjs";

const __isAuditSynthetic =
  typeof window !== "undefined" &&
  (window.location.search.includes("audit_synthetic=1") ||
    window.sessionStorage.getItem("snapai_audit_mode") === "1");

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,            // 10% of transactions traced
  replaysOnErrorSampleRate: __isAuditSynthetic ? 0 : 1.0,    // 100% of error sessions recorded
  replaysSessionSampleRate: __isAuditSynthetic ? 0 : 0.01,   // 1% of normal sessions recorded
  environment: process.env.NEXT_PUBLIC_ENV || "production",
  release: "snapai-web@1.0.0",
  integrations: [
    Sentry.replayIntegration(),
  ],
  // Don't send errors in development
  enabled: process.env.NEXT_PUBLIC_ENV !== "development",
  beforeSend(event) {
    // Drop synthetic events generated during audit runs.
    if (typeof window !== "undefined") {
      const isAuditSynthetic =
        window.location.search.includes("audit_synthetic=1") ||
        window.sessionStorage.getItem("snapai_audit_mode") === "1";
      if (isAuditSynthetic) return null;
    }
    return event;
  },
});
