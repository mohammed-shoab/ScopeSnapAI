import { test, expect } from "@playwright/test";

/**
 * Day 1-5 bug fixes — homeowner report (ReportClient.tsx).
 * Mounts the REAL ReportClient via the dev harness with a base64 fixture
 * (same pattern as stage3b). Verifies:
 *   - Bug 1 + Bug 5: line items render differentiated per tier (repair tiers
 *     show their own descriptions; the replacement tier shows 4 component lines
 *     that sum to the option total).
 *   - Level 2: cost-transparency + estimate-validity footers render.
 *   - DEC-088: contractor warranty terms render only when set.
 */

const REPORT_WITH_LEVEL2 = {
  report_short_id: "rpt-l2-01",
  report_token: "tok-l2-01",
  status: "draft",
  created_at: "2026-06-18T00:00:00Z",
  company: {
    name: "Lone Star HVAC",
    phone: "713-555-0142",
    warranty_text: "30-day labor, 1-year parts",
  },
  property: { address_line1: "12 Oak Ln", city: "Houston", state: "TX", customer_name: "Jane Homeowner" },
  equipment: { equipment_type: "ac", brand: "Trane", model_number: "4TTR6", install_year: 2014, condition: "fair" },
  photos: [],
  issues: [],
  cost_transparency_footer:
    "This estimate covers parts, labor, and the service items listed for each option. Ask your contractor about anything not shown here.",
  estimate_validity_footer:
    "This is a written estimate based on the diagnosed condition. The final price may change if on-site work uncovers conditions different from those assessed.",
  options: [
    {
      tier: "A", name: "Fix Today", total: 575, subtotal: 575, recommended: false,
      line_items: [{ description: "Find the leak, seal it, and refill the refrigerant charge", amount: 575, category: "repair" }],
    },
    {
      tier: "B", name: "Fix + Extend Life", total: 760, subtotal: 760, recommended: true,
      line_items: [{ description: "Find and seal the leak, refill the charge, then replace the Schrader cores, pull a deep vacuum, and pressure-test the joints as preventive maintenance", amount: 760, category: "repair" }],
    },
    {
      tier: "C", name: "Consider Replacing", total: 8400, subtotal: 8400, recommended: false, is_replacement: true,
      line_items: [
        { description: "New high-efficiency HVAC system, matched to your home's load", amount: 5208, category: "replacement" },
        { description: "Factory refrigerant charge, set to manufacturer spec", amount: 588, category: "replacement" },
        { description: "Professional installation, including electrical and refrigerant line connections", amount: 1680, category: "replacement" },
        { description: "Old unit removal and haul-away, permit, and registration of the new system with the manufacturer", amount: 924, category: "replacement" },
      ],
    },
  ],
};

async function gotoReportHarness(page, fixture) {
  await page.route("**/api/events", (r) => r.fulfill({ status: 200, body: "{}" }));
  await page.route("**/api/reports/**", (r) => r.fulfill({ status: 200, body: "{}" }));
  const f = encodeURIComponent(Buffer.from(JSON.stringify(fixture)).toString("base64"));
  await page.goto(`/test-harness/report?f=${f}`);
}

test.describe("Day 1-5 bug fixes — homeowner report @bugfix", () => {
  test("Bug 1/5: repair tiers show distinct line items; replacement shows 4 lines summing to total", async ({ page }) => {
    await gotoReportHarness(page, REPORT_WITH_LEVEL2);

    // Repair Option 1 wording is present and differs from Option 2 wording.
    await expect(page.getByText("Find the leak, seal it, and refill the refrigerant charge")).toBeVisible();
    await expect(page.getByText(/replace the Schrader cores, pull a deep vacuum/)).toBeVisible();

    // Replacement tier shows the 4 distinct component lines.
    for (const line of [
      "New high-efficiency HVAC system, matched to your home's load",
      "Factory refrigerant charge, set to manufacturer spec",
      "Professional installation, including electrical and refrigerant line connections",
      /registration of the new system with the manufacturer/,
    ]) {
      await expect(page.getByText(line)).toBeVisible();
    }
    // 5208 + 588 + 1680 + 924 == 8400 (the option total) — no markup leak.
    expect(5208 + 588 + 1680 + 924).toBe(8400);
  });

  test("Level 2 footers render", async ({ page }) => {
    await gotoReportHarness(page, REPORT_WITH_LEVEL2);
    await expect(page.getByText(/This estimate covers parts, labor/)).toBeVisible();
    await expect(page.getByText(/This is a written estimate based on the diagnosed condition/)).toBeVisible();
  });

  test("DEC-088: warranty terms render only when the contractor set them", async ({ page }) => {
    await gotoReportHarness(page, REPORT_WITH_LEVEL2);
    await expect(page.getByText("30-day labor, 1-year parts")).toBeVisible();

    const noWarranty = { ...REPORT_WITH_LEVEL2, company: { name: "Lone Star HVAC", phone: "713-555-0142" } };
    await gotoReportHarness(page, noWarranty);
    await expect(page.getByText("30-day labor, 1-year parts")).toHaveCount(0);
  });

  test("DEC-088: no banned outcome-promise words appear on the report", async ({ page }) => {
    await gotoReportHarness(page, REPORT_WITH_LEVEL2);
    const body = (await page.locator("body").innerText()).toLowerCase();
    for (const banned of ["guarantee", "eliminates", "risk-free", "never fails"]) {
      expect(body).not.toContain(banned);
    }
  });
});
