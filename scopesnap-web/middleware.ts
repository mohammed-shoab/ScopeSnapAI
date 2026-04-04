/**
 * SnapAI — Next.js Middleware (WP-11)
 *
 * Authentication strategy:
 * - Development: No-op. Routes are accessible without auth.
 *   The API uses X-Dev-Clerk-User-Id header bypass.
 * - Production: Clerk middleware protects all /(app)/* routes.
 *   Unauthenticated users are redirected to /sign-in.
 *
 * Public routes (no auth required):
 * - /r/* — homeowner report pages (magic link)
 * - /sign-in, /sign-up — Clerk auth pages
 * - /payment-success — post-Stripe redirect
 * - /api/webhooks/* — Clerk + Stripe webhooks (verified server-side)
 * - /health, / — public API
 */

import { NextRequest, NextResponse } from "next/server";

const IS_DEV =
  process.env.NEXT_PUBLIC_ENV === "development" ||
  process.env.NODE_ENV === "development";

// Routes that never require auth
const PUBLIC_PATHS = [
  "/r/",          // Homeowner report pages
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

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Always allow public paths
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // Dev mode: skip auth entirely
  if (IS_DEV) {
    return NextResponse.next();
  }

  // Production: use Clerk to protect routes
  try {
    const { clerkMiddleware, createRouteMatcher } = await import(
      "@clerk/nextjs/server"
    );

    const isProtectedRoute = createRouteMatcher([
      "/dashboard(.*)",
      "/assess(.*)",
      "/estimate(.*)",
    ]);

    return clerkMiddleware(async (auth, req) => {
      if (isProtectedRoute(req)) {
        // Clerk v5: auth() returns AuthObject — must await protect() to allow
        // the redirect to complete before continuing to NextResponse.next()
        await auth().protect({
          unauthenticatedUrl: new URL("/sign-in", req.url).toString(),
        });
      }
      return NextResponse.next();
    })(request, {} as never);
  } catch {
    // Clerk not installed or misconfigured — fail open in dev, fail closed in prod
    if (IS_DEV) {
      return NextResponse.next();
    }
    // In prod with broken Clerk, redirect to sign-in
    return NextResponse.redirect(new URL("/sign-in", request.url));
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except static files:
     * /_next/static, /_next/image, .ico, .png, .jpg, etc.
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|woff2?)$).*)",
  ],
};
