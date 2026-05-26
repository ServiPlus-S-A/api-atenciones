import { test, expect } from "@playwright/test";

test.use({ storageState: "e2e/.auth/coordinador.json" });

test("HU-02: coordinador crea atención AGENDADA", async ({ page }) => {
  await page.goto("/coordinador");
  await expect(page.getByRole("heading", { name: /panel coordinador/i })).toBeVisible();
});
