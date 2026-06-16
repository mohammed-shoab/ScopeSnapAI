import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { FaultResolutionPage } from "./pages/faultResolution.page";
import { DIAG_CHOOSER_GATE } from "./fixtures/stage3.fixtures";

/**
 * Stage 3C — chooser-gate banner + "Why this recommendation?" / "Show the math"
 * (components/FaultResolutionScreen.tsx). Exercised primarily via the REAL
 * public /d/[share_token] route with a mocked public diagnostic response.
 */
test.describe("Stage 3C — chooser-gate + show-the-math @stage3", () => {
  let fault: FaultResolutionPage;

  test.beforeEach(({ page }) => {
    fault = new FaultResolutionPage(page);
  });

  // Scenario 7 — chooser-gate banner + reveal repair tier
  test("chooser-gate banner appears for unknown-age replacement; 'Show repair-first option' reveals repair tier", async () => {
    await fault.gotoPublicShare("chooser", DIAG_CHOOSER_GATE);

    await expect(fault.chooserBanner).toBeVisible();
    // Banner copy uses "X+ years old".
    await expect(fault.page.getByText(/16\+ years old/)).toBeVisible();

    await expect(fault.showRepairFirstButton).toBeVisible();
    await fault.showRepairFirstButton.click();

    // After reveal, the Repair (A) tier surfaces and the banner is dismissed.
    await expect(fault.showRepairFirstButton).toBeHidden();
    await expect(fault.page.getByText("Repair").first()).toBeVisible();
  });

  // Scenario 8 — Why panel + Show the math render a BAND, never a bare year
  test("'Why this recommendation?' / 'Show the math' renders a remaining-life BAND (range), never a single year", async () => {
    await fault.gotoPublicShare("chooser", DIAG_CHOOSER_GATE);

    await fault.openWhyPanel();

    // Remaining-life is a range like "0-3 years", not an exact single year.
    await expect(fault.whyPanel.getByText(/\d+\s*-\s*\d+\s*years/)).toBeVisible();
    // Guard: the band must not be a bare 4-digit calendar year on its own line.
    await expect(fault.whyPanel.getByText(/^\s*20\d{2}\s*years?\s*$/)).toHaveCount(0);

    // Five weighted factors render.
    await expect(fault.whyPanel.getByText("Replacement-score factors")).toBeVisible();
    await expect(fault.whyPanel.getByText("Total replace score")).toBeVisible();

    // "Show the math" expands the formula without error.
    await fault.showMathButton.click();
    await expect(fault.whyPanel.getByText(/score\s*=\s*0\.40\*age/)).toBeVisible();
  });

  // a11y — disclosure focus + contrast on the chooser banner + Why panel
  test("a11y: chooser-gate + Why panel have no serious axe violations @a11y", async ({ page }) => {
    await fault.gotoPublicShare("chooser", DIAG_CHOOSER_GATE);
    await fault.openWhyPanel();

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical"
    );
    if (serious.length) console.log(JSON.stringify(serious, null, 2));
    expect(serious).toEqual([]);
  });

  // a11y — the "Why this recommendation?" disclosure exposes aria-expanded state
  test("a11y: 'Why this recommendation?' disclosure toggles aria-expanded @a11y", async () => {
    await fault.gotoPublicShare("chooser", DIAG_CHOOSER_GATE);

    await expect(fault.whyButton).toHaveAttribute("aria-expanded", "false");
    await fault.whyButton.click();
    await expect(fault.whyButton).toHaveAttribute("aria-expanded", "true");
    await expect(fault.whyPanel).toBeVisible();
  });
});
