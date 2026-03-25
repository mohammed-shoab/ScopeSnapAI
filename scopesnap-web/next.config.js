/** @type {import('next').NextConfig} */
const nextConfig = {
  // Prevent crypto-js (Clerk dependency) from being split into a server-side vendor chunk.
  // Without this, Vercel's build cache can contain a stale webpack-runtime.js that references
  // vendor-chunks/crypto-js.js which no longer exists in subsequent cached builds —
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
};

module.exports = nextConfig;
