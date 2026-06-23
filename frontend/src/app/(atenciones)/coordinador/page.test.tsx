import { fireEvent, render, screen } from "@testing-library/react";
import CoordinadorPage from "./page";
import { EstadoAtencion } from "@/types/atencion.types";
import { useAtenciones } from "@/features/atenciones/hooks/useAtenciones";

jest.mock("@/features/atenciones/hooks/useAtenciones");

const mockUseAtenciones = jest.mocked(useAtenciones);

describe("CoordinadorPage", () => {
  it("envia filtros de busqueda de HU-12", () => {
    const fetchAtenciones = jest.fn();
    mockUseAtenciones.mockReturnValue({
      atenciones: [],
      loading: false,
      error: null,
      pagination: { page: 1, page_size: 10, count: 0 },
      fetchAtenciones,
      createAtencion: jest.fn(),
      programarAtencion: jest.fn(),
      finalizarAtencion: jest.fn(),
      anularAtencion: jest.fn(),
    });

    render(<CoordinadorPage />);

    fireEvent.change(screen.getByLabelText(/nombre del cliente/i), {
      target: { value: "Cliente Norte" },
    });
    fireEvent.change(screen.getByLabelText(/consultor/i), {
      target: { value: "Maria" },
    });
    fireEvent.change(screen.getByLabelText(/id de solicitud/i), {
      target: { value: "321" },
    });
    fireEvent.change(screen.getByLabelText(/fecha de registro/i), {
      target: { value: "2026-06-23" },
    });
    fireEvent.click(screen.getByRole("button", { name: /buscar/i }));

    expect(fetchAtenciones).toHaveBeenCalledWith({
      nombre_cliente: "Cliente Norte",
      nombre_consultor: "Maria",
      solicitud_id: "321",
      fecha_registro: "2026-06-23",
    });
  });

  it("muestra listado encontrado", () => {
    mockUseAtenciones.mockReturnValue({
      atenciones: [
        {
          id: 9,
          estado: EstadoAtencion.AGENDADA,
          solicitud_id: "555",
          fecha_programada: null,
          fecha_fin: null,
          consultores: [{ id: "1", nombre: "Luis Perez", es_lider: true }],
          notas_finales: null,
          fecha_cierre: null,
          cliente_nombre: "Ana Rojas",
          fecha_registro: "2026-06-23T10:00:00Z",
        },
      ],
      loading: false,
      error: null,
      pagination: { page: 1, page_size: 10, count: 1 },
      fetchAtenciones: jest.fn(),
      createAtencion: jest.fn(),
      programarAtencion: jest.fn(),
      finalizarAtencion: jest.fn(),
      anularAtencion: jest.fn(),
    });

    render(<CoordinadorPage />);

    expect(screen.getByText("Cliente: Ana Rojas")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /ver detalle/i })).toHaveAttribute(
      "href",
      "/coordinador/atenciones/9",
    );
  });
});
