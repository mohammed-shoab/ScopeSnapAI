import { test, expect } from "@playwright/test";
import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";
import { createClerkClient } from "@clerk/backend";

// Authenticated audit flow. Two supported strategies:
//   A) password  — set AUDIT_EMAIL + AUDIT_PASSWORD (canonical @clerk/testing method)
//   B) sign-in token — set CLERK_SECRET_KEY + AUDIT_USER_ID (passwordless)
// Always needs CLERK_PUBLISHABLE_KEY (+ CLERK_SECRET_KEY for the Testing Token / token strategy).
const SECRET = process.env.CLERK_SECRET_KEY;
const USER_ID = process.env.AUDIT_USER_ID;
const EMAIL = process.env.AUDIT_EMAIL;
const PASSWORD = process.env.AUDIT_PASSWORD;
const BASE =
  process.env.AUDIT_BASE_URL ||
  process.env.STAGING_URL ||
  "https://staging.snapai.mainnov.tech";

const canPassword = !!(EMAIL && PASSWORD);
const canToken = !!(SECRET && USER_ID);

test.describe("SnapAI audit — authenticated", () => {
  test.skip(
    !canPassword && !canToken,
    "Set AUDIT_EMAIL+AUDIT_PASSWORD (password) or CLERK_SECRET_KEY+AUDIT_USER_ID (token).",
  );

  test("sign in and reach a gated route", async ({ page }) => {
    await setupClerkTestingToken({ page });
    await page.addInitScript(() => {
      try {
        window.sessionStorage.setItem("snapai_audit_mode", "1");
      } catch {
        /* ignore */
      }
    });
    await page.goto(`${BASE}/sign-in`);
    await clerk.loaded({ page });

    if (canPassword) {
      await clerk.signIn({
        page,
        signInParams: { strategy: "password", identifier: EMAIL!, password: PASSWORD! },
      });
    } else {
      const backend = createClerkClient({ secretKey: SECRET! });
      const signInToken = await backend.signInTokens.createSignInToken({
        userId: USER_ID!,
        expiresInSeconds: 600,
      });
      try {
        await clerk.signIn({
          page,
          signInParams: { strategy: "ticket", ticket: signInToken.token },
        });
      } catch {
        await page.goto(`${BASE}/sign-in?__clerk_ticket=${signInToken.token}`);
      }
    }

    await page.goto(`${BASE}/dashboard`);
    await expect(page).toHaveURL(/dashboard|app/);
  });
});
