/**
 * SnapAI — Sentry Frontend Error Tracking
 * Catches unhandled errors in the browser and reports them to Sentry.
 * DSN set via NEXT_PUBLIC_SENTRY_DSN environment variable.
 */
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,            // 10% of transactions traced
  replaysOnErrorSampleRate: 1.0,    // 100% of error sessions recorded
  replaysSessionSampleRate: 0.01,   // 1% of normal sessions recorded
  environment: process.env.NEXT_PUBLIC_ENV || "production",
  release: "snapai-web@1.0.0",
  integrations: [
    Sentry.replayIntegration(),
  ],
  // Don't send errors in development
  enabled: process.env.NEXT_PUBLIC_ENV !== "development",
});
