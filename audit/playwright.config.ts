import { defineConfig, devices } from "@playwright/test";

// Isolated audit harness config. baseURL defaults to staging; override with AUDIT_BASE_URL.
// Staging is behind Vercel Deployment Protection (401). To let automation through, set a
// "Protection Bypass for Automation" secret in the Vercel project and pass it as
// VERCEL_AUTOMATION_BYPASS_SECRET — it's sent as the documented bypass header + cookie.
const bypass = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
const extraHTTPHeaders = bypass
  ? {
      "x-vercel-protection-bypass": bypass,
      "x-vercel-set-bypass-cookie": "true",
    }
  : undefined;

export default defineConfig({
  testDir: "./tests",
  globalSetup: "./global.setup.ts",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL:
      process.env.AUDIT_BASE_URL ||
      process.env.STAGING_URL ||
      "https://staging.snapai.mainnov.tech",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    extraHTTPHeaders,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
