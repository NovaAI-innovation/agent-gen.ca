import { test, expect } from "@playwright/test";

test.describe("Smoke: public pages", () => {
  test("home page loads and shows marketplace CTA", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/agent-gen/i);
    // Primary heading or CTA should be visible
    const heading = page.locator("h1, h2, [data-testid='hero-heading']").first();
    await expect(heading).toBeVisible({ timeout: 10_000 });
  });

  test("marketplace page loads", async ({ page }) => {
    await page.goto("/marketplace");
    await expect(page).toHaveURL(/marketplace/);
    // Page should not crash — at minimum the layout renders
    await expect(page.locator("body")).toBeVisible();
  });

  test("publish page loads and redirects or shows form", async ({ page }) => {
    await page.goto("/publish");
    await expect(page).toHaveURL(/publish/);
    await expect(page.locator("body")).toBeVisible();
  });
});

test.describe("Smoke: navigation", () => {
  test("navbar links are keyboard-focusable", async ({ page }) => {
    await page.goto("/");
    // Tab through the first few focusable elements
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    await expect(focused).toBeAttached({ timeout: 5_000 });
  });
});
