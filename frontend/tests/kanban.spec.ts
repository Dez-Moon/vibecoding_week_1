import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page, context }) => {
  await context.clearCookies();
  await page.goto("/login");
  await page.getByTestId("input-username").fill("user");
  await page.getByTestId("input-password").fill("password");
  await page.getByTestId("submit-login").click();
  await page.waitForURL(/\/?$/);
});

test("loads the kanban board", async ({ page }) => {
  await page.goto("/");
  // Wait for board to load
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  // Verify 5 columns are visible
  await expect(page.locator("[data-column-title]")).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  // Debug: check what's in the backlog section
  const backlogSection = page.locator("[data-column-title='Backlog']");
  await backlogSection.waitFor({ state: "visible" });
  const articleCount = await backlogSection.locator("article").count();
  if (articleCount === 0) {
    // Check if articles exist anywhere on the page
    const totalArticles = await page.locator("article").count();
    throw new Error(`No articles in Backlog section. Total articles on page: ${totalArticles}`);
  }
  // Backlog has 2 seed cards
  await expect(backlogSection.locator("article")).toHaveCount(2);
  await backlogSection.getByRole("button", { name: /add a card/i }).click();
  await backlogSection.getByPlaceholder("Card title").fill("Playwright card");
  await backlogSection.getByPlaceholder("Details").fill("Added via e2e.");
  await backlogSection.getByRole("button", { name: /add card/i }).click();
  // After API, Backlog should have 3 cards
  await expect(backlogSection.locator("article")).toHaveCount(3, { timeout: 5000 });
});

test("moves a card between columns", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  const backlogSection = page.locator("[data-column-title='Backlog']");
  const reviewSection = page.locator("[data-column-title='Review']");
  await backlogSection.waitFor({ state: "visible" });
  // Review has 1 seed card
  await expect(reviewSection.locator("article")).toHaveCount(1, { timeout: 5000 });
  // Use mouse-based drag for @dnd-kit compatibility
  const backlogCard = backlogSection.locator("article").first();
  const cardBox = await backlogCard.boundingBox();
  const reviewBox = await reviewSection.boundingBox();
  if (!cardBox || !reviewBox) throw new Error("Unable to get bounding boxes");
  await page.mouse.move(cardBox.x + cardBox.width / 2, cardBox.y + cardBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(reviewBox.x + reviewBox.width / 2, reviewBox.y + reviewBox.height / 2, { steps: 10 });
  await page.mouse.up();
  // Review should now have 2 cards
  await expect(reviewSection.locator("article")).toHaveCount(2, { timeout: 5000 });
});
