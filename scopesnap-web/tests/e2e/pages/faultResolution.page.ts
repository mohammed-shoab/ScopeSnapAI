import { Page, Locator, expect } from "@playwright/test";
import { BasePage } from "./base.page";
import { DiagnosticFixture } from "../fixtures/stage3.fixtures";

/**
 * Page Object for Stage 3C — chooser-gate banner + "Why this recommendation?"
 * panel (components/FaultResolutionScreen.tsx). Two entry points:
 *  - gotoPublicShare(): drives the REAL /d/[share_token] route, mocking the
 *    public diagnostic endpoint (client-side fetch → page.route works).
 *  - gotoHarness(): mounts the component via the dev harness with a base64
 *    fixture (deterministic fallback, also used for axe isolation scans).
 */
export class FaultResolutionPage extends BasePage {
  readonly chooserBanner: Locator;
  readonly showRepairFirstButton: Locator;
  readonly whyButton: Locator;
  readonly whyPanel: Locator;
  readonly remainingLifeValue: Locator;
  readonly showMathButton: Locator;
  readonly repairTierLabel: Locator;

  constructor(page: Page) {
    super(page);
    this.chooserBanner = page.getByText(
      /We're recommending replacement because we estimate this unit is/
    );
    this.showRepairFirstButton = page.getByRole("button", { name: "Show repair-first option" });
    this.whyButton = page.getByRole("button", { name: "Why this recommendation?" });
    this.whyPanel = page.locator("#why-rec-panel");
    this.remainingLifeValue = this.whyPanel.getByText(/\d+\s*-\s*\d+\s*years/);
    this.showMathButton = page.getByRole("button", { name: /Show the math|Hide the math/ });
    this.repairTierLabel = page.getByText("Repair", { exact: false });
  }

  async gotoPublicShare(token: string, fixture: DiagnosticFixture): Promise<void> {
    await this.page.route(`**/api/diagnostic/public/${token}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(fixture),
      });
    });
    await this.page.route("**/api/events", (r) => r.fulfill({ status: 200, body: "{}" }));
    await this.navigate(`/d/${token}`);
    await expect(this.whyButton.or(this.chooserBanner)).toBeVisible({ timeout: 15_000 });
  }

  async gotoHarness(fixture?: DiagnosticFixture): Promise<void> {
    await this.page.route("**/api/events", (r) => r.fulfill({ status: 200, body: "{}" }));
    const q = fixture
      ? `?f=${encodeURIComponent(Buffer.from(JSON.stringify(fixture)).toString("base64"))}`
      : "";
    await this.navigate(`/test-harness/fault-resolution${q}`);
    await expect(this.chooserBanner).toBeVisible({ timeout: 15_000 });
  }

  async openWhyPanel(): Promise<void> {
    await this.whyButton.click();
    await expect(this.whyPanel).toBeVisible();
  }
}
