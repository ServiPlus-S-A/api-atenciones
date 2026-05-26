import { test as setup } from "@playwright/test";

const roles = ["consultor", "coordinador", "cliente"] as const;

for (const rol of roles) {
  setup(`authenticate as ${rol}`, async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/usuario/i).fill(`user_${rol}`);
    await page.getByLabel(/contraseña/i).fill("testpass123");
    await page.getByRole("button", { name: /ingresar/i }).click();
    await page.context().storageState({ path: `e2e/.auth/${rol}.json` });
  });
}
