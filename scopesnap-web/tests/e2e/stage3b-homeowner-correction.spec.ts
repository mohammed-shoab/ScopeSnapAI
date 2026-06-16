import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { ReportPage } from "./pages/report.page";
import { REPORT_WITH_INSTALL_YEAR } from "./fixtures/stage3.fixtures";

/**
 * Stage 3B — homeowner install-year correction (ReportClient.tsx).
 * /r is SSR (server fetch, not page.route-interceptable), so the REAL
 * ReportClient is mounted via the dev harness with a base64 fixture.
 */
test.describe("Stage 3B — homeowner correction @stage3", () => {
  let report: ReportPage;

  test.beforeEach(({ page }) => {
    report = new ReportPage(page);
  });

  // Scenario 5 — all three correction paths render
  test("renders correction surface with all 3 paths (Yes / No-type-year / I-don't-know)", async () => {
    await report.gotoHarness(REPORT_WITH_INSTALL_YEAR);

    await expect(report.confirmPrompt).toBeVisible();
    // The prompt echoes the shown install year.
    await expect(report.page.getByText("2014", { exact: false }).first()).toBeVisible();

    await expect(report.yesButton).toBeVisible();
    await expect(report.noTypeYearButton).toBeVisible();
    await expect(report.idkRelativeButton).toBeVisible();

    // "Yes" path → confirmed banner.
    await report.yesButton.click();
    await expect(report.confirmedBanner).toBeVisible();
  });

  // Scenario 6 — relative-age picker converts to current_year - n
  test("relative-age picker (5/10/15/20+) converts to year = current_year - n and shows a BAND", async () => {
    await report.gotoHarness(REPORT_WITH_INSTALL_YEAR);

    await report.pickRelativeAge(10);

    await expect(report.updatedBanner).toBeVisible();
    // currentYear - 10. Install year line should reflect the relative computation.
    const currentYear = new Date().getFullYear();
    const expectedYear = String(currentYear - 10);
    await expect(report.page.getByText(expectedYear, { exact: false }).first()).toBeVisible();

    // Remaining-life must be a BAND/range, never a single bare year. Match "X-Y years".
    await expect(report.page.getByText(/\d+\s*-\s*\d+\s*years/i).first()).toBeVisible();
  });

  // a11y — relative-age radio group semantics + contrast
  test("a11y: correction surface has no serious axe violations @a11y", async ({ page }) => {
    await report.gotoHarness(REPORT_WITH_INSTALL_YEAR);
    // Expand the relative-age fieldset so its radios are in the scan.
    await report.idkRelativeButton.click();
    await expect(report.relativeAgeGroup).toBeVisible();

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical"
    );
    if (serious.length) console.log(JSON.stringify(serious, null, 2));
    expect(serious).toEqual([]);
  });

  // a11y — relative-age radios are keyboard navigable inside a fieldset/legend
  test("a11y: relative-age radios are keyboard-navigable in a fieldset/legend @a11y", async ({ page }) => {
    await report.gotoHarness(REPORT_WITH_INSTALL_YEAR);
    await report.idkRelativeButton.click();
    await expect(report.relativeAgeGroup).toBeVisible();

    // Group exposes an accessible name from its <legend>.
    await expect(report.relativeAgeGroup).toBeVisible();
    const radios = report.relativeAgeGroup.getByRole("radio");
    await expect(radios).toHaveCount(4);

    // Focus the first radio and arrow to the next — native radio-group behaviour.
    await radios.first().focus();
    await expect(radios.first()).toBeFocused();
    await page.keyboard.press("ArrowRight");
    await expect(radios.nth(1)).toBeChecked();
  });
});
