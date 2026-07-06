import { test, expect } from "@playwright/test";

/**
 * Legal-safe landing redirects (next.config.js `redirects()`).
 *
 * The public root `/` and the legacy homeowner landing `/homeowner` both
 * redirect to the contractor landing `/tech`. This is part of the legal-copy
 * architecture: the "diagnosis"-style public surface is funneled to the
 * contractor-facing page so consumer-facing pages don't imply a homeowner can
 * self-diagnose. These tests pin that behaviour at the HTTP layer.
 *
 * Uses Playwright's request context with `maxRedirects: 0` so we inspect the
 * raw redirect response (status + Location) rather than following it through a
 * full browser navigation. Status-agnostic: Next emits 308 for
 * `permanent: true`, but we accept any 3xx (301/302/307/308) so the contract is
 * "it redirects to /tech", not "it uses one specific redirect status".
 */
test.describe("Legal landing redirects @legal", () => {
  const REDIRECT_STATUSES = [301, 302, 307, 308];

  test("GET / redirects to /tech", async ({ request, baseURL }) => {
    const res = await request.get("/", { maxRedirects: 0 });

    expect(REDIRECT_STATUSES).toContain(res.status());

    // Location may be absolute or root-relative; resolve against baseURL and
    // assert the path is exactly /tech.
    const location = res.headers()["location"];
    expect(location, "redirect Location header must be present").toBeTruthy();
    const resolved = new URL(location, baseURL);
    expect(resolved.pathname).toBe("/tech");
  });

  test("GET /homeowner redirects to /tech", async ({ request, baseURL }) => {
    const res = await request.get("/homeowner", { maxRedirects: 0 });

    expect(REDIRECT_STATUSES).toContain(res.status());

    const location = res.headers()["location"];
    expect(location, "redirect Location header must be present").toBeTruthy();
    const resolved = new URL(location, baseURL);
    expect(resolved.pathname).toBe("/tech");
  });

  test("following the / redirect lands on /tech (200)", async ({ request }) => {
    // Sanity check with redirects followed: the final resource resolves.
    const res = await request.get("/");
    expect(res.ok()).toBeTruthy();
    expect(new URL(res.url()).pathname).toBe("/tech");
  });
});
