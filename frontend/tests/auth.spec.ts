import { test, expect } from "@playwright/test";

test.beforeEach(async ({ context }) => {
  await context.clearCookies();
});

test("visiting the board while signed out redirects to login", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login\/?$/);
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
});

test("logging in lands on the board", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("input-username").fill("user");
  await page.getByTestId("input-password").fill("password");
  await page.getByTestId("submit-login").click();

  await expect(page).toHaveURL(/\/?$/);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
});

test("signing out returns to the login page", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("input-username").fill("user");
  await page.getByTestId("input-password").fill("password");
  await page.getByTestId("submit-login").click();
  await expect(page).toHaveURL(/\/?$/);

  await page.getByTestId("logout-button").click();
  await expect(page).toHaveURL(/\/login\/?$/);
});
