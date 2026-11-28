import { expect, test } from "@playwright/test";

test.describe("Availability Configuration Wizard", () => {
  test("blocked publish shows readiness errors and jumps to step", async ({ page }) => {
    const uniqueName = `E2E Blocked ${Date.now()}`;

    await page.goto("/");
    await expect(page.getByText("Coastal Plains Service Agreement")).toBeVisible();

    // Click "+" on Coastal Plains Service Agreement
    await page
      .getByRole("link", {
        name: "New availability configuration for Coastal Plains Service Agreement",
      })
      .click();

    await expect(page).toHaveURL(/\/configurations\/new/);

    // Fill only the configuration name in Step 1 and save draft
    await page.getByLabel(/AV configuration name/i).fill(uniqueName);
    await page.getByRole("button", { name: "Save draft" }).click();

    // URL should be replaced with the newly created GUID
    await expect(page).toHaveURL(/\/configurations\/[0-9a-f-]{36}/);

    // Review & Publish panel should show blocking errors and keep Publish disabled
    await expect(page.getByText(/Blocking Error\(s\)/i)).toBeVisible();
    await expect(page.getByRole("button", { name: "Publish", exact: true })).toBeDisabled();

    // Clicking a Step 2 blocking error jumps to ?step=2
    await page
      .getByRole("button", { name: /At least one turbine must be selected/i })
      .click();
    await expect(page).toHaveURL(/\?step=2/);
    await expect(page.getByRole("heading", { name: "2. Turbines in scope" })).toBeVisible();

    // Clean up the draft from the Home page
    await page.getByRole("button", { name: "← All contracts" }).click();
    await expect(page).toHaveURL("/");
    await page
      .getByRole("button", { name: `Actions for ${uniqueName}`, exact: true })
      .click();
    await page.getByRole("menuitem", { name: "Delete" }).click();
    await page.getByRole("button", { name: "Delete" }).click();
    await expect(page.getByRole("heading", { name: uniqueName })).not.toBeVisible();
  });

  test("happy path: create 4-step configuration, save draft, and publish", async ({ page }) => {
    const uniqueName = `E2E Publish ${Date.now()}`;

    await page.goto("/");
    await page
      .getByRole("link", {
        name: "New availability configuration for Coastal Plains Service Agreement",
      })
      .click();

    // Step 1: Basic details
    await page.getByLabel(/AV configuration name/i).fill(uniqueName);
    await page.getByRole("combobox", { name: /Warranted calculation type/i }).click();
    await page.getByRole("option", { name: /TBA — Time-Based Availability/i }).click();

    // Pick Start date (day 10) and End date (day 20) via DatePicker popovers
    const monthsAhead = 1 + Math.floor(Math.random() * 24);
    await page.locator("#start-date").click();
    const nextMonthBtn = page.getByRole("button", { name: /next month/i });
    for (let i = 0; i < monthsAhead; i += 1) {
      await nextMonthBtn.click();
    }
    await page.locator('[role="gridcell"] button', { hasText: /^10$/ }).first().click();

    await page.locator("#end-date").click();
    await expect(page.getByRole("dialog")).toHaveCount(1);
    for (let i = 0; i < monthsAhead; i += 1) {
      await nextMonthBtn.click();
    }
    await page.locator('[role="gridcell"] button', { hasText: /^20$/ }).first().click();

    // Step 2: Turbines
    await page.getByRole("button", { name: "Next", exact: true }).click();
    await expect(page.getByRole("heading", { name: "2. Turbines in scope" })).toBeVisible();
    await page.getByLabel(/Select all turbines/i).click();

    // Step 3: Formula & alarms
    await page.getByRole("button", { name: "Next", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "3. Formula & alarm categories" }),
    ).toBeVisible();
    await page.locator("#formula-select").click();
    await page.getByRole("option", { name: /Standard Time-Based Availability/i }).click();

    // Check required GRID and MAINT categories
    await page.getByLabel(/GRID — Grid interruption/i).click();
    await page.getByLabel(/MAINT — Planned maintenance/i).click();

    // Step 4: Details
    await page.getByRole("button", { name: "Next", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "4. Details & wind parameters" }),
    ).toBeVisible();
    await page.locator("#park-availability").fill("97.5");
    await page.locator("#low-wind-variant").click();
    await page.getByRole("option", { name: "Exclude below cut-in" }).click();
    await page.locator("#high-wind-variant").click();
    await page.getByRole("option", { name: "Exclude above cut-out" }).click();

    // Save draft and verify readiness passes
    await page.getByRole("button", { name: "Save draft" }).click();
    await expect(page).toHaveURL(/\/configurations\/[0-9a-f-]{36}/);
    await expect(page.getByText("All deterministic checks passed. Ready to publish.")).toBeVisible();

    // Publish
    const publishBtn = page.getByRole("button", { name: "Publish", exact: true });
    await expect(publishBtn).toBeEnabled();
    await publishBtn.click();

    await expect(page.getByText("This version is published and active.")).toBeVisible();
  });
});
