import { defineConfig, devices } from "@playwright/test";

/**
 * Stage 3 Playwright config — Brand Decoder single-screen UX e2e.
 *
 * baseURL is taken from env BASE_URL (default http://localhost:3000) so the same
 * specs run against a local dev server or a staging deploy with SSO disabled.
 *
 * The specs are backend-independent: every API call is mocked with page.route()
 * and the real Stage 3 components are mounted via dev-only harness routes under
 * /test-harness/* (see app/test-harness/). This keeps the run deterministic and
 * free of Clerk/SSO and a live FastAPI backend.
 *
 * Boot the server with NEXT_PUBLIC_ENV=development so middleware.ts becomes a
 * no-op (no Clerk gate). The webServer block below does that automatically when
 * BASE_URL is not set.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html", { open: "never" }],
    ["list"],
  ],
  use: {
    // Use 127.0.0.1 (not "localhost"): newer Playwright/Chromium can fail to
    // resolve "localhost" in CI (ERR_NAME_NOT_RESOLVED) even though Node's
    // webServer health-check resolves it fine — which is exactly what reddened
    // this suite. 127.0.0.1 is unambiguous and reaches the `next dev` server.
    baseURL: process.env.BASE_URL || "http://127.0.0.1:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile-chrome",
      use: { ...devices["Pixel 5"] },
    },
  ],
  webServer: process.env.BASE_URL
    ? undefined
    : {
        command: "npm run dev -- -H 127.0.0.1",
        url: "http://127.0.0.1:3000",
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
        env: {
          NEXT_PUBLIC_ENV: "development",
          NODE_ENV: "development",
          NEXT_PUBLIC_API_URL: "http://localhost:8000",
          NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:
            process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "pk_test_Y2xlcmsuZXhhbXBsZS5jb20k",
          CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY || "sk_test_dummy0000000000000000000000000000",
        },
      },
});
