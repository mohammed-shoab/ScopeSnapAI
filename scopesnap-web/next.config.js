/** @type {import('next').NextConfig} */
// build: 2026-05-24c -- fix ambient selector in manual/DB-lookup tab (cache-bust: WA-49)

const API_URL_FOR_CSP = process.env.NEXT_PUBLIC_API_URL || 'https://scopesnap-api-production.up.railway.app';

const { withSentryConfig } = require("@sentry/nextjs");

const nextConfig = {
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
    ];
  },
  serverExternalPackages: ['crypto-js'],
  output: process.env.NEXT_STANDALONE === "true" ? "standalone" : undefined,
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        ...config.watchOptions,
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
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
          {
            // CSP — maps.googleapis.com + maps.gstatic.com added for Google Maps JS API (Stage 3 / DEC-076)
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://clerk.snapai.mainnov.tech https://*.clerk.accounts.dev https://us-assets.i.posthog.com https://challenges.cloudflare.com https://maps.googleapis.com https://maps.gstatic.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob: https://*.r2.dev https://img.clerk.com https://images.clerk.dev https://www.gstatic.com https://*.gstatic.com https://clerk.snapai.mainnov.tech https://lh3.googleusercontent.com",
              `connect-src 'self' ${API_URL_FOR_CSP} https://clerk.snapai.mainnov.tech https://*.clerk.accounts.dev https://us.i.posthog.com https://us-assets.i.posthog.com https://challenges.cloudflare.com https://maps.googleapis.com https://*.ingest.us.sentry.io`,
              "frame-src 'self' https://clerk.snapai.mainnov.tech https://*.clerk.accounts.dev https://challenges.cloudflare.com",
              "worker-src 'self' blob:",
              // Hardening (ZAP "no fallback"): these directives do NOT inherit default-src.
              "object-src 'none'",
              "base-uri 'self'",
              "frame-ancestors 'none'",
              "form-action 'self'",
            ].join("; "),
          },
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
  disableLogger: true,
});
