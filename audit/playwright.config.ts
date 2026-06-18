import { defineConfig, devices } from "@playwright/test";

// Isolated audit harness config. baseURL defaults to staging; override with AUDIT_BASE_URL.
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
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
