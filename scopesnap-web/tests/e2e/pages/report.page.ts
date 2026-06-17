import { Page, Locator, expect } from "@playwright/test";
import { BasePage } from "./base.page";
import { ReportFixture } from "../fixtures/stage3.fixtures";

/**
 * Page Object for Stage 3B — homeowner install-year correction surface
 * (app/r/[slug]/[reportId]/ReportClient.tsx). The production /r route is SSR
 * (server fetch, not interceptable by page.route), so the specs mount the REAL
 * ReportClient via the dev harness with a base64 fixture report.
 */
export class ReportPage extends BasePage {
  readonly confirmPrompt: Locator;
  readonly yesButton: Locator;
  readonly noTypeYearButton: Locator;
  readonly idkRelativeButton: Locator;
  readonly correctedYearInput: Locator;
  readonly correctedYearSaveButton: Locator;
  readonly relativeAgeGroup: Locator;
  readonly relativeSaveButton: Locator;
  readonly updatedBanner: Locator;
  readonly confirmedBanner: Locator;

  constructor(page: Page) {
    super(page);
    this.confirmPrompt = page.getByText("Is this correct?");
    this.yesButton = page.getByRole("button", { name: "Yes, that's right" });
    this.noTypeYearButton = page.getByRole("button", { name: /No — actual year is/ });
    this.idkRelativeButton = page.getByRole("button", { name: /I don't know/ });
    this.correctedYearInput = page.getByLabel("Actual install year");
    this.correctedYearSaveButton = page.locator("#corrected-year-input ~ button");
    this.relativeAgeGroup = page.getByRole("group", { name: "About how many years ago?" });
    this.relativeSaveButton = this.relativeAgeGroup.getByRole("button", { name: "Save" });
    this.updatedBanner = page.getByText("Updated based on your correction");
    this.confirmedBanner = page.getByText("Thanks — age confirmed.");
  }

  async gotoHarness(fixture: ReportFixture): Promise<void> {
    await this.page.route("**/api/events", (r) => r.fulfill({ status: 200, body: "{}" }));
    await this.page.route("**/api/reports/**", (r) => r.fulfill({ status: 200, body: "{}" }));
    const f = encodeURIComponent(Buffer.from(JSON.stringify(fixture)).toString("base64"));
    await this.navigate(`/test-harness/report?f=${f}`);
    await expect(this.confirmPrompt).toBeVisible({ timeout: 15_000 });
  }

  async pickRelativeAge(years: 5 | 10 | 15 | 20): Promise<void> {
    await this.idkRelativeButton.click();
    await expect(this.relativeAgeGroup).toBeVisible();
    const label = years === 20 ? "20+" : String(years);
    await this.relativeAgeGroup.getByText(label, { exact: true }).click();
    await this.relativeSaveButton.click();
  }
}
