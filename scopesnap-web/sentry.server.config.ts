/**
 * SnapAI — Sentry Server-Side Error Tracking
 * Catches errors in Next.js API routes and server components.
 */
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NEXT_PUBLIC_ENV || "production",
  release: "snapai-web@1.0.0",
  enabled: process.env.NEXT_PUBLIC_ENV !== "development",
});
