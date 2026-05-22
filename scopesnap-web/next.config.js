/** @type {import('next').NextConfig} */
// build: 2026-05-23

// Dynamic API URL â set via NEXT_PUBLIC_API_URL env var (staging vs production).
// Used both as the JS bundle constant AND in the CSP connect-src header so that
// the browser Security Policy allows fetches to whichever backend is active.
const API_URL_FOR_CSP = process.env.NEXT_PUBLIC_API_URL || 'https://scopesnap-api-production.up.railway.app';

const nextConfig = {
  // Redirect the raw Vercel deployment URL to the canonical production domain.
  // Clerk production keys are domain-locked to snapai.mainnov.tech â anyone
  // landing on scope-snap-ai.vercel.app would see a broken sign-in page without this.
  async redirects() {
    return [
      {
        source: "/:path*",
        has: [{ type: "host", value: "scope-snap-ai.vercel.app" }],
        destination: "https://snapai.mainnov.tech/:path*",
        permanent: true,   // 308 â browsers cache this redirect
      },
      // BUG-03 fix: rename /estimates â /assessments and /estimate â /assessment
      // 301 redirects preserve bookmarks and old links
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
  // Prevent crypto-js (Clerk dependency) from being split into a server-side vendor chunk.
  // Without this, Vercel's build cache can contain a stale webpack-runtime.js that references
  // vendor-chunks/crypto-js.js which no longer exists in subsequent cached builds â
  // causing "Cannot find module './vendor-chunks/crypto-js.js'" on the homeowner report page.
  serverExternalPackages: ['crypto-js'],
  // Standalone output for Docker production image (smaller image, faster cold starts)
  output: process.env.NEXT_STANDALONE === "true" ? "standalone" : undefined,
  // Enable polling-based webpack file watcher for Docker on Windows.
  // inotify events don't cross the WSL2/Docker volume boundary, so without polling
  // the dev server never detects changes and compiled chunks go stale.
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        ...config.watchOptions,
        poll: 1000, // check for changes every 1 second
        aggregateTimeout: 300,
      };
    }
    return config;
  },
  // Images from localhost (dev) and R2 (prod)
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
  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
  },
  // Security headers â Content Security Policy + standard hardening
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
            // CSP â allows Clerk, Google Fonts, PostHog, Resend-tracked images
            // 'unsafe-inline' required for Clerk's embedded components + Tailwind
            // challenges.cloudflare.com required for Clerk's Turnstile CAPTCHA
            // www.gstatic.com required for Google OAuth icon (some Clerk versions)
            // API_URL_FOR_CSP is dynamic â resolves to staging or production backend
            // depending on NEXT_PUBLIC_API_URL env var set in Vercel project settings.
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://clerk.snapai.mainnov.tech https://*.clerk.accounts.dev https://us-assets.i.posthog.com https://challenges.cloudflare.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: blob: https://*.r2.dev https://img.clerk.com https://images.clerk.dev https://www.gstatic.com https://*.gstatic.com https://clerk.snapai.mainnov.tech https://lh3.googleusercontent.com",
              `connect-src 'self' ${API_URL_FOR_CSP} https://clerk.snapai.mainnov.tech https://*.clerk.accounts.dev https://us.i.posthog.com https://us-assets.i.posthog.com https://challenges.cloudflare.com`,
              "frame-src 'self' https://clerk.snapai.mainnov.tech https://*.clerk.accounts.dev https://challenges.cloudflare.com",
              "worker-src 'self' blob:",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
