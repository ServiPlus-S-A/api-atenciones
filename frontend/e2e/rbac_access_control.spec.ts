import { test, expect } from "@playwright/test";

test.describe("RBAC", () => {
  test("cliente no accede a panel coordinador", async ({ browser }) => {
    const context = await browser.newContext({
      storageState: "e2e/.auth/cliente.json",
    });
    const page = await context.newPage();
    await page.goto("/coordinador");
    await expect(page).not.toHaveURL(/coordinador/);
    await context.close();
  });
});
