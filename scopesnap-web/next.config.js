/** @type {import('next').NextConfig} */
// build: 2026-05-24c -- fix ambient selector in manual/DB-lookup tab (cache-bust: WA-49)

const API_URL_FOR_CSP = process.env.NEXT_PUBLIC_API_URL || 'https://scopesnap-api-production.up.railway.app';

const { withSentryConfig } = require("@sentry/nextjs");

const nextConfig = {
  // Next 16 blocks cross-origin access to /_next/* dev resources (HMR, chunks)
  // from hosts not listed here. The Playwright e2e suite reaches the dev server
  // via 127.0.0.1/localhost, which were getting blocked -> page scripts failed
  // -> navigations died (this is what reddened playwright-e2e.yml). Dev-only.
  allowedDevOrigins: ["localhost", "127.0.0.1"],
  async redirects() {
    return [
      {
        source: "/:path*",
        has: [{ type: "host", value: "scope-snap-ai.vercel.app" }],
        destination: "https://snapai.mainnov.tech/:path*",
        permanent: true,
      },
      {
        source: "/estimates",
        destination: "/assessments",
        permanent: true,
      },
      {
        source: "/estimate/:id",
        destination: "/assessment/:id",
        permanent: true,
      },
      {
        source: "/homeowner",
        destination: "/tech",
        permanent: true,
      },
    ];
  },
  async rewrites() {
    // 2026-06-18: the site root "/" now RENDERS the /tech landing (tech-primary +
    // owner door) directly via internal rewrite — URL stays "/", content = /tech,
    // HTTP 200 (no 308). Supersedes the prior "/" -> "/tech" permanent redirect
    // (snapai_redirect_308_decision). "/homeowner" still 308-redirects to /tech.
    return [
      {
        source: "/",
        destination: "/tech",
      },
    ];
  },
  serverExternalPackages: ['crypto-js'],
  output: process.env.NEXT_STANDALONE === "true" ? "standalone" : undefined,
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/files/**",
      },
      {
        protocol: "https",
        hostname: "*.r2.dev",
        pathname: "/**",
      },
    ],
  },
  // Hardening (ZAP): stop leaking the framework in X-Powered-By.
  poweredByHeader: false,
  // NOTE: experimental.sri (SRI) was tried and REVERTED — it blocked the Next.js
  // bundle scripts at runtime on Vercel (Clerk failed to load, sign-in broke),
  // even though the build succeeded. Needs a different approach; see findings doc.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "Permissions-Policy",
            value: "camera=(self), microphone=(), geolocation=()",
          },
          // CSP is now emitted by Clerk's middleware (proxy.ts) with a per-request
          // nonce + 'strict-dynamic' (audit finding #5/#9) — single source of truth.
          // The static CSP (script-src 'unsafe-inline') was removed here.
        ],
      },
    ];
  },
};

module.exports = withSentryConfig(nextConfig, {
  // Build-time metadata for the snapai-web Sentry project. Sourcemap upload is
  // DISABLED (no SENTRY_AUTH_TOKEN needed) so the build never fails on auth.
  org: "mainnov",
  project: "snapai-web",
  silent: true,
  sourcemaps: { disable: true },
});
