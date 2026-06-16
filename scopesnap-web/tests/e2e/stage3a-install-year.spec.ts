import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { StepZeroPage } from "./pages/stepZero.page";
import {
  OCR_HIGH_CONFIDENCE,
  OCR_LOW_CONFIDENCE,
  OCR_LEGACY_BRAND,
} from "./fixtures/stage3.fixtures";

/**
 * Stage 3A — install-date review (components/StepZeroPanel.tsx).
 * Drives the REAL component via /assess in dev mode, mocking /api/ocr/nameplate.
 */
test.describe("Stage 3A — install-year review @stage3", () => {
  let stepZero: StepZeroPage;

  test.beforeEach(({ page }) => {
    stepZero = new StepZeroPage(page);
  });

  // Scenario 1
  test("high-confidence decode pre-fills year and shows no 'Ask homeowner' placeholder", async () => {
    await stepZero.gotoWithDecode(OCR_HIGH_CONFIDENCE);
    await stepZero.uploadNameplate();

    await stepZero.expectYearPrefilled(2018);
    await expect(stepZero.askHomeownerHint).toBeHidden();
    // Confidence selector should read "Sure".
    await expect(stepZero.confidenceGroup.getByRole("radio", { name: "Sure" })).toBeChecked();
  });

  // Scenario 2
  test("low/failed decode leaves year BLANK with italic 'Ask homeowner' hint, no yellow highlight", async () => {
    await stepZero.gotoWithDecode(OCR_LOW_CONFIDENCE);
    await stepZero.uploadNameplate();

    await stepZero.expectYearBlank();
    await expect(stepZero.askHomeownerHint).toBeVisible();
    // The blank-state placeholder option reads "Ask homeowner".
    await expect(stepZero.installYearSelect.locator("option", { hasText: "Ask homeowner" })).toHaveCount(1);
    // No alarm/yellow highlight — border stays neutral grey (#9ca3af), never amber.
    const border = await stepZero.installYearSelect.evaluate(
      (el) => getComputedStyle(el).borderTopColor
    );
    expect(border).not.toBe("rgb(245, 158, 11)"); // not amber-500
    expect(border).not.toBe("rgb(234, 179, 8)");  // not yellow-500
    // Italic placeholder styling.
    const fontStyle = await stepZero.installYearSelect.evaluate(
      (el) => getComputedStyle(el).fontStyle
    );
    expect(fontStyle).toBe("italic");
  });

  // Scenario 3
  test("legacy brand pre-fills midpoint year and shows 'estimated from brand discontinue' badge", async () => {
    await stepZero.gotoWithDecode(OCR_LEGACY_BRAND);
    await stepZero.uploadNameplate();

    await stepZero.expectYearPrefilled(1998);
    await expect(stepZero.legacyBadge).toBeVisible();
    await expect(stepZero.confidenceGroup.getByRole("radio", { name: "Approximate" })).toBeChecked();
  });

  // Scenario 4
  test("setting year blank keeps age_confidence 'unknown' and pops NO modal", async ({ page }) => {
    await stepZero.gotoWithDecode(OCR_HIGH_CONFIDENCE);
    await stepZero.uploadNameplate();
    await stepZero.expectYearPrefilled(2018);

    // Clear the year back to the "Ask homeowner" blank option.
    await stepZero.installYearSelect.selectOption("");
    await stepZero.expectYearBlank();

    // Confidence falls back to Unknown; no dialog/modal appears.
    await expect(stepZero.confidenceGroup.getByRole("radio", { name: "Unknown" })).toBeChecked();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(page.getByRole("alertdialog")).toHaveCount(0);
  });

  // a11y — the install-year review markup
  test("a11y: install-year review has no serious axe violations @a11y", async ({ page }) => {
    await stepZero.gotoWithDecode(OCR_LOW_CONFIDENCE);
    await stepZero.uploadNameplate();

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical"
    );
    if (serious.length) console.log(JSON.stringify(serious, null, 2));
    expect(serious).toEqual([]);
  });
});
