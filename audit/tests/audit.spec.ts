import { test, expect } from "@playwright/test";
import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";
import { createClerkClient } from "@clerk/backend";

// Passwordless authenticated audit flow.
// Required env: CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, AUDIT_USER_ID.
// Optional: AUDIT_BASE_URL (default staging).
const SECRET = process.env.CLERK_SECRET_KEY;
const USER_ID = process.env.AUDIT_USER_ID;
const BASE =
  process.env.AUDIT_BASE_URL ||
  process.env.STAGING_URL ||
  "https://staging.snapai.mainnov.tech";

test.describe("SnapAI audit — authenticated (sign-in token)", () => {
  test.skip(
    !SECRET || !USER_ID,
    "Set CLERK_SECRET_KEY and AUDIT_USER_ID to run the authenticated audit flow.",
  );

  test("sign in with a sign-in token and reach the dashboard", async ({ page }) => {
    const backend = createClerkClient({ secretKey: SECRET! });

    // 1) Mint a one-time sign-in token — no password, no email OTP.
    const signInToken = await backend.signInTokens.createSignInToken({
      userId: USER_ID!,
      expiresInSeconds: 600,
    });

    // 2) Bypass Clerk bot detection for this page.
    await setupClerkTestingToken({ page });

    // 3) Set the audit flag at init so Sentry/PostHog drop synthetic events.
    await page.addInitScript(() => {
      try {
        window.sessionStorage.setItem("snapai_audit_mode", "1");
      } catch {
        /* ignore */
      }
    });

    // 4) Load the app so window.Clerk exists, then sign in with the ticket.
    await page.goto(BASE);
    try {
      await clerk.signIn({
        page,
        signInParams: { strategy: "ticket", ticket: signInToken.token },
      });
    } catch {
      // Fallback: let Clerk consume the ticket via the sign-in URL param.
      await page.goto(`${BASE}/sign-in?__clerk_ticket=${signInToken.token}`);
    }

    // 5) Authenticated — verify a gated route loads.
    await page.goto(`${BASE}/dashboard`);
    await expect(page).toHaveURL(/dashboard|app/);
  });
});
