import * as Sentry from "@sentry/nextjs";

// Next 16/Turbopack server+edge Sentry init. Turbopack does not auto-load the
// legacy sentry.server/edge.config files at build time, so they are loaded here
// from the register() hook based on the runtime.
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }
  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }
}

export const onRequestError = Sentry.captureRequestError;
