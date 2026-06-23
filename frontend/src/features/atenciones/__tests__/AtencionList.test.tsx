import { render, screen } from "@testing-library/react";
import { AtencionList } from "@/features/atenciones/components/AtencionList";
import { EstadoAtencion, type AtencionDTO } from "@/types/atencion.types";

const atencion: AtencionDTO = {
  id: 7,
  estado: EstadoAtencion.AGENDADA,
  solicitud_id: "123",
  fecha_programada: null,
  fecha_fin: null,
  consultores: [{ id: "c-1", nombre: "Maria Gomez", es_lider: true }],
  notas_finales: null,
  fecha_cierre: null,
  cliente_nombre: "Cliente Norte",
  fecha_registro: "2026-06-23T10:00:00Z",
};

describe("AtencionList", () => {
  it("muestra mensaje especifico cuando no hay resultados", () => {
    render(
      <AtencionList
        atenciones={[]}
        emptyMessage="Ninguna atención responde a sus especificaciones."
      />,
    );

    expect(
      screen.getByText("Ninguna atención responde a sus especificaciones."),
    ).toBeInTheDocument();
  });

  it("muestra datos de la atencion y permite ir al detalle", () => {
    render(<AtencionList atenciones={[atencion]} showAnuladas />);

    expect(screen.getByText("Cliente: Cliente Norte")).toBeInTheDocument();
    expect(screen.getByText("Maria Gomez")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /ver detalle/i })).toHaveAttribute(
      "href",
      "/coordinador/atenciones/7",
    );
  });
});
