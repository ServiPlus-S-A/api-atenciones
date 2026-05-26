import { EstadoAtencion } from "@/types/atencion.types";

const config: Record<EstadoAtencion, { color: string; label: string }> = {
  [EstadoAtencion.AGENDADA]: { color: "bg-blue-100 text-blue-800", label: "Agendada" },
  [EstadoAtencion.FINALIZADA]: { color: "bg-green-100 text-green-800", label: "Finalizada" },
  [EstadoAtencion.ANULADA]: { color: "bg-red-100 text-red-800", label: "Anulada" },
};

export function EstadoBadge({ estado }: { estado: EstadoAtencion }) {
  const { color, label } = config[estado];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-sm font-medium ${color}`}
      aria-label={`Estado: ${label}`}
    >
      {label}
    </span>
  );
}
