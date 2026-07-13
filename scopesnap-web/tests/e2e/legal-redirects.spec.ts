import { test, expect } from "@playwright/test";

/**
 * Legal-safe landing routing (next.config.js).
 *
 * As of 2026-07-14 (SUPERSEDES the prior "/" -> "/tech" 308 redirect decision,
 * snapai_redirect_308_decision): the public root "/" now RENDERS the contractor
 * /tech landing directly via an internal Next.js rewrite — URL stays "/", HTTP
 * 200, no redirect. The rendered content is still the contractor-facing /tech
 * page (tech-primary + owner "data-audit" door), so the legal intent is
 * preserved: the consumer-visible root serves the contractor page, not a
 * homeowner self-diagnosis surface. The legacy "/homeowner" landing STILL
 * 3xx-redirects to /tech (unchanged).
 *
 * These tests pin that behaviour at the HTTP layer using Playwright's request
 * context with maxRedirects: 0 to inspect the raw response.
 */
test.describe("Legal landing routing @legal", () => {
  const REDIRECT_STATUSES = [301, 302, 307, 308];

  test("GET / renders /tech (200, no redirect)", async ({ request }) => {
    const res = await request.get("/", { maxRedirects: 0 });
    // Root now renders via rewrite -> expect 200, NOT a 3xx redirect.
    expect(res.status()).toBe(200);
    // Body is the /tech landing: assert a stable marker from its <head> <title>
    // (server-rendered, so present in the raw HTML regardless of hydration).
    const body = await res.text();
    expect(body).toContain("turn a tough HVAC call into a clean quote");
  });

  test("GET /homeowner redirects to /tech", async ({ request, baseURL }) => {
    const res = await request.get("/homeowner", { maxRedirects: 0 });

    expect(REDIRECT_STATUSES).toContain(res.status());

    const location = res.headers()["location"];
    expect(location, "redirect Location header must be present").toBeTruthy();
    const resolved = new URL(location, baseURL);
    expect(resolved.pathname).toBe("/tech");
  });

  test("GET / resolves 200 at the root URL (rewrite keeps the URL at /)", async ({ request }) => {
    // With the rewrite, following redirects still lands at "/" (a redirect would
    // have moved the final URL to /tech). The resource must resolve OK.
    const res = await request.get("/");
    expect(res.ok()).toBeTruthy();
    expect(new URL(res.url()).pathname).toBe("/");
  });
});
