import { render, screen } from "@testing-library/react";
import { EstadoBadge } from "@/features/atenciones/components/EstadoBadge";
import { EstadoAtencion } from "@/types/atencion.types";

describe("EstadoBadge", () => {
  it("renderiza texto correcto para AGENDADA", () => {
    render(<EstadoBadge estado={EstadoAtencion.AGENDADA} />);
    expect(screen.getByLabelText(/estado: agendada/i)).toHaveTextContent("Agendada");
  });
});
