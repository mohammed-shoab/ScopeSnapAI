/**
 * SnapAI — Next.js Proxy (formerly middleware) (WP-11)
 *
 * Authentication strategy:
 * - Development: No-op auth. Routes accessible without auth (API uses X-Dev-Clerk-User-Id).
 * - Production: Clerk protects all /(app)/* routes; unauthenticated -> /sign-in.
 *
 * CSP (audit finding #5/#9): clerkMiddleware runs on EVERY request with
 * contentSecurityPolicy.strict = true, so Clerk emits a per-request nonce +
 * 'strict-dynamic' CSP and exposes it via the x-nonce header. This removes the
 * need for script-src 'unsafe-inline'. Third-party hosts are merged via `directives`.
 * KEEP 'unsafe-eval' (Google Maps) and style-src 'unsafe-inline' (Clerk/Maps).
 *
 * Public routes (no auth required):
 * - /r/*, /d/* — public share pages   - /sign-in, /sign-up — Clerk auth
 * - /payment-success                   - /api/webhooks/* — verified server-side
 * - /clerk, /_next, /favicon, etc.
 */

import { NextRequest, NextResponse } from "next/server";
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const IS_DEV =
  process.env.NEXT_PUBLIC_ENV === "development" ||
  process.env.NODE_ENV === "development";

const API_URL_FOR_CSP =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://scopesnap-api-production.up.railway.app";

// Routes that never require auth
const PUBLIC_PATHS = [
  "/r/",          // Homeowner report pages
  "/d/",          // Public diagnosis share pages (Track D)
  "/sign-in",     // Clerk sign-in
  "/sign-up",     // Clerk sign-up
  "/payment-success",
  "/api/webhooks",
  "/clerk",       // Clerk proxy — must be public so ClerkJS can load unauthenticated
  "/_next",
  "/favicon",
  "/manifest.json",
  "/sw.js",
  "/icon",
  "/offline",
];

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((p) => pathname.startsWith(p));
}

const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/assess(.*)",
  "/assessment(.*)",
  "/assessments(.*)",
  "/settings(.*)",
  "/billing(.*)",
  "/analytics(.*)",
  "/intelligence(.*)",
  "/equipment(.*)",
  "/team(.*)",
  "/onboarding(.*)",
  "/estimates(.*)",
  "/estimate(.*)",
  "/diagnoses(.*)",
]);

export default clerkMiddleware(
  async (auth, request: NextRequest) => {
    const { pathname } = request.nextUrl;

    // Preserve x-pathname injection (used for /onboarding loop guard).
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set("x-pathname", pathname);

    // Preserve x-market injection based on hostname.
    const hostname = request.headers.get("host") || "";
    // BUG-002 fix: match lib/market.ts:48-66 — staging PK uses hyphen not dot.
    const PK_HOSTNAMES = [
      "pk.snapai.mainnov.tech",
      "pk.snapai.app",
      "pk-staging.snapai.mainnov.tech",
    ];
    const market =
      PK_HOSTNAMES.includes(hostname) || hostname.startsWith("pk.")
        ? "PK"
        : "US";
    requestHeaders.set("x-market", market);

    // Enforce auth only in production, only for protected routes, never on
    // public paths. (Clerk injects the CSP header regardless of this branch.)
    if (!IS_DEV && !isPublicPath(pathname) && isProtectedRoute(request)) {
      await auth.protect({
        unauthenticatedUrl: new URL("/sign-in", request.url).toString(),
      });
    }

    return NextResponse.next({ request: { headers: requestHeaders } });
  },
  {
    contentSecurityPolicy: {
      strict: true,
      // Merged with Clerk's defaults — list ONLY the SnapAI third-party hosts.
      directives: {
        "script-src": [
          "'unsafe-eval'",
          "https://us-assets.i.posthog.com",
          "https://maps.googleapis.com",
          "https://maps.gstatic.com",
        ],
        "style-src": ["'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["https://fonts.gstatic.com"],
        "img-src": [
          "data:",
          "blob:",
          "https://*.r2.dev",
          "https://images.clerk.dev",
          "https://www.gstatic.com",
          "https://*.gstatic.com",
          "https://clerk.snapai.mainnov.tech",
          "https://lh3.googleusercontent.com",
        ],
        "connect-src": [
          API_URL_FOR_CSP,
          "https://clerk.snapai.mainnov.tech",
          "https://*.clerk.accounts.dev",
          "https://us.i.posthog.com",
          "https://us-assets.i.posthog.com",
          "https://challenges.cloudflare.com",
          "https://maps.googleapis.com",
          "https://*.ingest.us.sentry.io",
        ],
        "frame-src": [
          "https://clerk.snapai.mainnov.tech",
          "https://*.clerk.accounts.dev",
          "https://challenges.cloudflare.com",
        ],
        "worker-src": ["'self'", "blob:"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "frame-ancestors": ["'none'"],
        "form-action": ["'self'"],
      },
    },
  },
);

export const config = {
  matcher: [
    /*
     * Match all request paths except static files:
     * /_next/static, /_next/image, .ico, .png, .jpg, etc.
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|woff2?)$).*)",
  ],
};
