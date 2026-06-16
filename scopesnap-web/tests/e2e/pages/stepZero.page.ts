import { Page, Locator, expect } from "@playwright/test";
import { BasePage } from "./base.page";
import { OcrResultFixture } from "../fixtures/stage3.fixtures";

/**
 * Page Object for Stage 3A — install-year review on the assess "step-zero"
 * screen (components/StepZeroPanel.tsx). Drives the REAL component: mocks the
 * /api/ocr/nameplate endpoint, uploads a fake nameplate photo, and the real
 * prefill useEffect runs against the mocked decode.
 */
export class StepZeroPage extends BasePage {
  readonly installYearSelect: Locator;
  readonly askHomeownerHint: Locator;
  readonly legacyBadge: Locator;
  readonly confidenceGroup: Locator;
  readonly outdoorFileInput: Locator;

  constructor(page: Page) {
    super(page);
    this.installYearSelect = page.getByLabel("Year installed");
    this.askHomeownerHint = page.getByText(
      "We couldn't read the age — ask the homeowner if they know."
    );
    this.legacyBadge = page.getByText("estimated from brand discontinue");
    // The age-confidence radios live in a <fieldset> with this <legend>.
    this.confidenceGroup = page.getByRole("group", { name: "How sure are we?" });
    // The hidden outdoor nameplate file input.
    this.outdoorFileInput = page.locator('input[type="file"]').first();
  }

  /** Mock the OCR endpoint to return a crafted decode, then go to /assess. */
  async gotoWithDecode(ocr: OcrResultFixture): Promise<void> {
    await this.page.route("**/api/ocr/nameplate", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(ocr),
      });
    });
    // Keep telemetry/network deterministic. Mock brand lookups so the panel
    // renders without auth-gated data.
    await this.page.route("**/api/events", (r) => r.fulfill({ status: 200, body: "{}" }));
    await this.page.route("**/api/models/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: "[]" }));
    // Stage 3A is exercised via the dev harness (the real /assess route is
    // Clerk-auth-gated). The decoded outdoor unit is seeded via ?f= → the real
    // prefill logic runs deterministically without the OCR/upload pipeline.
    const seed = Buffer.from(JSON.stringify(ocr.outdoor)).toString("base64");
    await this.navigate(`/test-harness/step-zero?f=${encodeURIComponent(seed)}`);
  }

  /** The harness seeds the decode via ?f=, so just wait for the review block. */
  async uploadNameplate(): Promise<void> {
    await expect(this.installYearSelect).toBeVisible({ timeout: 15_000 });
  }

  async expectYearPrefilled(year: number): Promise<void> {
    await expect(this.installYearSelect).toHaveValue(String(year));
  }

  async expectYearBlank(): Promise<void> {
    await expect(this.installYearSelect).toHaveValue("");
  }
}
