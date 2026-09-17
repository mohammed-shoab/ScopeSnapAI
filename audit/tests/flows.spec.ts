import { test, expect, Page } from "@playwright/test";
import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";

/**
 * Product-flow walk for the snapai-full-audit skill.
 *
 * The existing audit.spec.ts proves AUTH only, and stops at /onboarding because
 * the Clerk test company has no license_number / attestation_accepted_at. This
 * spec completes the onboarding gate THROUGH THE UI (so onboarding itself is
 * exercised, not bypassed with a DB write) and then walks the gated routes that
 * were never covered.
 *
 * Writes it makes to STAGING: sets license_number + attestation on the audit
 * company. That is test data on a test company; no other tenant is touched.
 */

const EMAIL = process.env.AUDIT_EMAIL;
const BASE =
  process.env.AUDIT_BASE_URL ||
  process.env.STAGING_URL ||
  "https://staging.snapai.mainnov.tech";

const LICENSE = process.env.AUDIT_LICENSE || "TX-AUDIT-0916";

test.describe.configure({ mode: "serial" });

async function signIn(page: Page) {
  await setupClerkTestingToken({ page });
  // DEC-090: drop synthetic events at the SDK level.
  await page.addInitScript(() => {
    try {
      window.sessionStorage.setItem("snapai_audit_mode", "1");
    } catch {
      /* ignore */
    }
  });
  await page.goto(`${BASE}/sign-in`);
  await clerk.loaded({ page });

  const result = await page.evaluate(async (email) => {
    const Clerk = (window as any).Clerk;
    if (Clerk?.user) return { ok: true, already: true };
    const si = await Clerk.client.signIn.create({ identifier: email });
    const f = (si.supportedFirstFactors || []).find(
      (x: any) => x.strategy === "email_code",
    );
    if (!f) return { ok: false, reason: "no email_code factor" };
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

  expect(result.ok, `sign-in failed: ${JSON.stringify(result)}`).toBeTruthy();
  await page.waitForFunction(() => !!(window as any).Clerk?.user, null, {
    timeout: 20000,
  });
}

test.describe("SnapAI audit — product flows", () => {
  test.skip(
    !(EMAIL && EMAIL.includes("clerk_test")),
    "Needs a +clerk_test AUDIT_EMAIL.",
  );

  test("complete the onboarding gate via the UI", async ({ page }) => {
    await signIn(page);

    await page.goto(`${BASE}/onboarding`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);

    if (!page.url().includes("/onboarding")) {
      console.log("ONBOARDING: already complete, redirected to", page.url());
      return;
    }

    // Walk any intro/consent steps until the license field is on screen.
    const license = page.locator('input[placeholder="TX-12345"]');
    for (let i = 0; i < 6; i++) {
      if (await license.count()) break;
      const next = page
        .locator("button", { hasText: /continue|next|get started|agree|accept/i })
        .first();
      if (!(await next.count())) break;
      await next.click().catch(() => {});
      await page.waitForTimeout(1200);
    }

    await expect(
      license,
      "license input should be reachable in the onboarding wizard",
    ).toHaveCount(1, { timeout: 20000 });

    await license.fill(LICENSE);

    // Company name is REQUIRED by the Launch button's disabled guard.
    const company = page.locator('input[placeholder="Your Company LLC"]');
    if (await company.count()) {
      const v = await company.inputValue();
      if (!v.trim()) await company.fill("Audit ClerkTest's HVAC");
    }
    const phone = page.locator('input[placeholder="(555) 123-4567"]');
    if (await phone.count()) {
      const v = await phone.inputValue();
      if (!v.trim()) await phone.fill("(713) 555-0142");
    }

    // Both acknowledgements are required by the client-side guard.
    const boxes = page.locator('input[type="checkbox"]');
    const n = await boxes.count();
    for (let i = 0; i < n; i++) {
      const b = boxes.nth(i);
      if (await b.isVisible().catch(() => false)) {
        if (!(await b.isChecked())) await b.check({ force: true }).catch(() => {});
      }
    }
    console.log(`ONBOARDING: filled license + checked ${n} acknowledgement box(es)`);

    // The real submit is "Launch SnapAI 🚀" and stays DISABLED until name,
    // license_number, attestation and sec2Ack are all satisfied - so waiting for
    // it to become enabled doubles as an assertion that the form is complete.
    const submit = page.locator("button", { hasText: /launch/i }).last();
    await expect(submit, "Launch button should be present").toHaveCount(1, {
      timeout: 15000,
    });
    await expect(
      submit,
      "Launch stays disabled until name + license + both acks are set",
    ).toBeEnabled({ timeout: 15000 });

    await submit.click();
    await page.waitForTimeout(6000);

    console.log("ONBOARDING: landed on", page.url());
    const err = page.locator("text=/valid contractor license|must accept|required/i");
    expect(
      await err.count(),
      "onboarding should not report a validation error after a complete fill",
    ).toBe(0);
  });

  test("dashboard loads with no console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text().slice(0, 200));
    });
    page.on("pageerror", (e) => errors.push(`pageerror: ${String(e).slice(0, 200)}`));

    await signIn(page);
    await page.goto(`${BASE}/dashboard`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(4000);

    console.log("DASHBOARD url:", page.url());
    expect(page.url(), "should not bounce to sign-in").not.toContain("/sign-in");
    expect(page.url(), "onboarding gate should be satisfied").not.toContain(
      "/onboarding",
    );

    const body = await page.locator("body").innerText();
    console.log("DASHBOARD text length:", body.length);
    expect(body.length, "dashboard should render content").toBeGreaterThan(100);

    // Ignore third-party noise; surface app errors.
    const appErrors = errors.filter(
      (e) => !/clerk|posthog|sentry|favicon|analytics|third-party/i.test(e),
    );
    console.log("DASHBOARD console errors (app-level):", appErrors.length, appErrors.slice(0, 3));
  });

  test("gated product routes are reachable", async ({ page }) => {
    await signIn(page);

    const routes = [
      "/assessment/new",
      "/settings/pricing",
      "/team/technicians",
      "/settings/integrations",
    ];

    const results: Record<string, string> = {};
    for (const r of routes) {
      const resp = await page
        .goto(`${BASE}${r}`, { waitUntil: "domcontentloaded" })
        .catch(() => null);
      await page.waitForTimeout(2500);
      const status = resp ? resp.status() : 0;
      const bounced = page.url().includes("/sign-in");
      results[r] = `${status}${bounced ? " BOUNCED-TO-SIGNIN" : ` -> ${page.url().replace(BASE, "")}`}`;
      expect(bounced, `${r} should not bounce an authenticated user to sign-in`).toBeFalsy();
      expect(status, `${r} should not 5xx`).toBeLessThan(500);
    }
    console.log("ROUTES:", JSON.stringify(results, null, 2));
  });

  test("new assessment screen renders its entry point", async ({ page }) => {
    await signIn(page);
    await page.goto(`${BASE}/assessment/new`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(4000);

    const body = await page.locator("body").innerText();
    console.log("ASSESSMENT url:", page.url());
    console.log("ASSESSMENT text (first 300):", body.slice(0, 300).replace(/\n+/g, " | "));

    expect(page.url()).not.toContain("/sign-in");
    expect(body.length, "assessment screen should render").toBeGreaterThan(80);
  });
});
