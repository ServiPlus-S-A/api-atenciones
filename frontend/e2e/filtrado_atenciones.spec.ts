import { test, expect } from "@playwright/test";

test.use({ storageState: "e2e/.auth/coordinador.json" });

const oneAtencionResponse = {
  count: 1,
  total_pages: 1,
  page: 1,
  page_size: 10,
  results: [
    {
      id: 123,
      estado: "AGENDADA",
      solicitud_id: "R2",
      consultants: [
        { id: "20", name: "Juan Perez", is_leader: true, role: "CONSULTOR" }
      ]
    }
  ]
};

const emptyResponse = {
  count: 0,
  total_pages: 0,
  page: 1,
  page_size: 10,
  results: []
};

test("Filtrar por cliente_nombre muestra resultados", async ({ page }) => {
  await page.route("**/api/atenciones/**", (route, request) => {
    const url = new URL(request.url());
    if (url.searchParams.get("cliente_nombre") === "Juan") {
      route.fulfill({ status: 200, body: JSON.stringify(oneAtencionResponse), contentType: 'application/json' });
      return;
    }
    route.continue();
  });

  await page.goto("/coordinador");
  await expect(page.getByRole("heading", { name: /panel coordinador/i })).toBeVisible();

  await page.getByPlaceholder("Cliente (nombre)").fill("Juan");
  await page.getByRole("button", { name: /buscar/i }).click();

  await expect(page.getByText("#123")).toBeVisible();
  await expect(page.getByText(/Juan Perez/)).toBeVisible();
});

test("Filtrar por cliente_nombre sin resultados muestra mensaje", async ({ page }) => {
  await page.route("**/api/atenciones/**", (route, request) => {
    const url = new URL(request.url());
    if (url.searchParams.get("cliente_nombre") === "NoExiste") {
      route.fulfill({ status: 200, body: JSON.stringify(emptyResponse), contentType: 'application/json' });
      return;
    }
    route.continue();
  });

  await page.goto("/coordinador");
  await page.getByPlaceholder("Cliente (nombre)").fill("NoExiste");
  await page.getByRole("button", { name: /buscar/i }).click();

  await expect(page.getByText(/No hay atenciones para mostrar/i)).toBeVisible();
});
