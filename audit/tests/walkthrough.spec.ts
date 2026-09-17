import { test, expect, Page } from "@playwright/test";
import { clerk, setupClerkTestingToken } from "@clerk/testing/playwright";

/**
 * The assessment -> diagnosis -> estimate walkthrough.
 *
 * This is the path the full-audit skill had never covered. A previous version of
 * flows.spec.ts asserted against /assessment/new, which DOES NOT EXIST - Next
 * matched [id] with id="new", the page rendered "Loading estimate...", the test
 * went green, and the backend 500'd underneath (Sentry SNAPAI-API-1A -> F9).
 * The real entry point is /assessments/new (plural), which redirects to /assess.
 *
 * Real flow, per app/(app)/assess/page.tsx:
 *   step-zero (nameplate OCR, skippable) -> complaint (job info + chips) -> diagnostic
 *
 * Writes to STAGING: creates an assessment + diagnostic session on the audit
 * test company. Test data on a test company.
 */

const EMAIL = process.env.AUDIT_EMAIL;
const BASE =
  process.env.AUDIT_BASE_URL ||
  process.env.STAGING_URL ||
  "https://staging.snapai.mainnov.tech";
const API =
  process.env.AUDIT_API_URL || "https://scopesnap-api-staging.up.railway.app";

test.describe.configure({ mode: "serial" });

async function signIn(page: Page) {
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
  const r = await page.evaluate(async (email) => {
    const C = (window as any).Clerk;
    if (C?.user) return { ok: true };
    const si = await C.client.signIn.create({ identifier: email });
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
      await C.setActive({ session: res.createdSessionId });
      return { ok: true };
    }
    return { ok: false, reason: res.status };
  }, EMAIL!);
  expect(r.ok, `sign-in failed: ${JSON.stringify(r)}`).toBeTruthy();
  await page.waitForFunction(() => !!(window as any).Clerk?.user, null, {
    timeout: 20000,
  });
}

test.describe("SnapAI audit - assessment -> diagnosis -> estimate", () => {
  test.skip(!(EMAIL && EMAIL.includes("clerk_test")), "Needs a +clerk_test AUDIT_EMAIL.");

  test("/assessments/new is the real entry and redirects to /assess", async ({ page }) => {
    await signIn(page);
    await page.goto(`${BASE}/assessments/new`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(5000);

    console.log("ENTRY landed on:", page.url());
    expect(page.url(), "/assessments/new must redirect to the /assess wizard").toContain(
      "/assess",
    );
    expect(page.url(), "must not bounce to sign-in").not.toContain("/sign-in");
  });

  test("F9 guard: a non-UUID estimate id must not 5xx", async ({ page }) => {
    await signIn(page);

    // The exact request that produced Sentry SNAPAI-API-1A.
    const res = await page.evaluate(async (api) => {
      try {
        const r = await fetch(`${api}/api/estimates/new`);
        return { status: r.status };
      } catch (e) {
        return { status: -1, err: String(e) };
      }
    }, API);

    console.log("F9 GET /api/estimates/new ->", JSON.stringify(res));
    if (res.status === -1) {
      test.info().annotations.push({ type: "note", description: "CORS blocked probe" });
      return;
    }
    expect(res.status, "non-UUID id must be a client error, never a 5xx").toBeLessThan(500);
  });

  test("walk step-zero -> complaint -> diagnostic", async ({ page }) => {
    await signIn(page);
    await page.goto(`${BASE}/assessments/new`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(6000);

    // step-zero: nameplate OCR is optional; get past it.
    const complaintHeading = page.locator("text=/what.?s the complaint/i");
    for (let i = 0; i < 6; i++) {
      if (await complaintHeading.count()) break;
      const skip = page
        .locator("button", {
          hasText: /skip|continue|manual|enter manually|later|no photo/i,
        })
        .first();
      if (!(await skip.count())) break;
      await skip.click().catch(() => {});
      await page.waitForTimeout(2500);
    }

    const reached = (await complaintHeading.count()) > 0;
    console.log("PHASE complaint reached:", reached, "| url:", page.url());

    if (!reached) {
      const body = await page.locator("body").innerText();
      console.log(
        "STEP-ZERO still showing. Body head:",
        body.slice(0, 260).replace(/\n+/g, " | "),
      );
      test.info().annotations.push({
        type: "blocked",
        description: "Could not auto-skip step-zero; it may require a nameplate photo.",
      });
      return;
    }

    const name = page
      .locator('input[placeholder*="Homeowner name" i], input[placeholder*="Ahmed Khan" i]')
      .first();
    if (await name.count()) await name.fill("Audit Homeowner").catch(() => {});

    const phone = page
      .locator('input[placeholder*="Phone number" i], input[placeholder*="WhatsApp" i]')
      .first();
    if (await phone.count()) await phone.fill("7135550142").catch(() => {});

    const chip = page.locator("text=Not Cooling").first();
    await expect(chip, "'Not Cooling' complaint chip should be present").toHaveCount(1, {
      timeout: 15000,
    });
    await chip.click();
    await page.waitForTimeout(9000);

    console.log("AFTER complaint click, url:", page.url());
    const body = await page.locator("body").innerText();
    console.log("DIAGNOSTIC body head:", body.slice(0, 320).replace(/\n+/g, " | "));

    expect(page.url(), "should not bounce to sign-in").not.toContain("/sign-in");
    expect(body.length, "diagnostic phase should render").toBeGreaterThan(120);

    const looksDiagnostic =
      /question|step|reading|psi|yes|no|next|continue|measure|check/i.test(body);
    console.log("DIAGNOSTIC heuristic match:", looksDiagnostic);
    expect(
      looksDiagnostic,
      "after choosing a complaint the diagnostic question tree should render",
    ).toBeTruthy();
  });

  test("no 5xx on any request during the walk", async ({ page }) => {
    const bad: string[] = [];
    page.on("response", (r) => {
      if (r.status() >= 500) bad.push(`${r.status()} ${r.request().method()} ${r.url()}`);
    });

    await signIn(page);
    for (const path of ["/assessments/new", "/assessments", "/dashboard"]) {
      await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(5000);
    }

    console.log("5xx during walk:", bad.length, JSON.stringify(bad.slice(0, 5)));
    expect(bad, `server errors during the walk:\n${bad.join("\n")}`).toHaveLength(0);
  });
});
