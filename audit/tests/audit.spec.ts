import { test, expect } from "@playwright/test";
import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";
import { createClerkClient } from "@clerk/backend";

// Authenticated audit flow. Strategy auto-selected:
//   - email contains "clerk_test"  -> email_code first factor with Clerk test OTP 424242
//   - else AUDIT_PASSWORD set       -> password strategy (@clerk/testing helper)
//   - else CLERK_SECRET_KEY+USER_ID -> passwordless sign-in token
// Always needs CLERK_PUBLISHABLE_KEY (+ CLERK_SECRET_KEY for the Testing Token).
const SECRET = process.env.CLERK_SECRET_KEY;
const USER_ID = process.env.AUDIT_USER_ID;
const EMAIL = process.env.AUDIT_EMAIL;
const PASSWORD = process.env.AUDIT_PASSWORD;
const BASE =
  process.env.AUDIT_BASE_URL ||
  process.env.STAGING_URL ||
  "https://staging.snapai.mainnov.tech";

const useEmailCode = !!(EMAIL && EMAIL.includes("clerk_test"));
const usePassword = !!(EMAIL && PASSWORD) && !useEmailCode;
const useToken = !!(SECRET && USER_ID) && !useEmailCode && !usePassword;

test.describe("SnapAI audit — authenticated", () => {
  test.skip(
    !useEmailCode && !usePassword && !useToken,
    "Provide a +clerk_test AUDIT_EMAIL, or AUDIT_EMAIL+AUDIT_PASSWORD, or CLERK_SECRET_KEY+AUDIT_USER_ID.",
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

    if (useEmailCode) {
      // Clerk test users (+clerk_test) accept the magic email code 424242 — no real inbox.
      const result = await page.evaluate(async (email) => {
        const Clerk = (window as any).Clerk;
        const si = await Clerk.client.signIn.create({ identifier: email });
        const f = (si.supportedFirstFactors || []).find(
          (x: any) => x.strategy === "email_code",
        );
        if (!f)
          return {
            ok: false,
            reason: "no email_code factor",
            factors: (si.supportedFirstFactors || []).map((x: any) => x.strategy),
          };
        await si.prepareFirstFactor({
          strategy: "email_code",
          emailAddressId: f.emailAddressId,
        });
        const res = await si.attemptFirstFactor({
          strategy: "email_code",
          code: "424242",
        });
        if (res.status === "complete") {
          await Clerk.setActive({ session: res.createdSessionId });
          return { ok: true };
        }
        return { ok: false, reason: res.status };
      }, EMAIL!);
      expect(result.ok, `email_code sign-in failed: ${JSON.stringify(result)}`).toBeTruthy();
    } else if (usePassword) {
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

    // Proof of authentication: Clerk reports an active user/session client-side.
    await page.waitForFunction(() => !!(window as any).Clerk?.user, null, {
      timeout: 15000,
    });
    const userId = await page.evaluate(() => (window as any).Clerk?.user?.id);
    expect(userId, "Clerk session should be active after sign-in").toBeTruthy();
    console.log("AUTH OK — Clerk user:", userId);

    // Best-effort: a gated route should not bounce us back to /sign-in
    // (new audit users may land on /onboarding instead of /dashboard).
    await page.goto(`${BASE}/dashboard`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(2000);
    console.log("Gated route landed on:", page.url());
  });
});
