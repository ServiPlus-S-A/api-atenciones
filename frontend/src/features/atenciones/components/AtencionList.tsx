"use client";

import { useMemo } from "react";
import { EstadoBadge } from "@/features/atenciones/components/EstadoBadge";
import type { AtencionDTO } from "@/types/atencion.types";
import { EstadoAtencion } from "@/types/atencion.types";

interface Props {
  atenciones: AtencionDTO[];
  showAnuladas?: boolean;
}

export function AtencionList({ atenciones, showAnuladas = false }: Props) {
  const technicians = useMemo(() => {
    const map: Record<number, { id: number; nombre: string }> = {};
    atenciones.forEach((a) =>
      a.consultores.forEach((c) => {
        map[c.id] = { id: c.id, nombre: c.nombre };
      }),
    );
    return map;
  }, [atenciones]);

  const visible = showAnuladas
    ? atenciones
    : atenciones.filter((a) => a.estado !== EstadoAtencion.ANULADA);

  if (visible.length === 0) {
    return <p className="text-serviplus-muted">No hay atenciones para mostrar.</p>;
  }

  return (
    <ul className="divide-y rounded-card border">
      {visible.map((a) => (
        <li key={a.id} className="flex items-center justify-between p-4">
          <div>
            <span className="font-medium">#{a.id}</span>
            <span className="ml-2 text-sm text-serviplus-muted">Solicitud {a.solicitud_id}</span>
            <div className="mt-1 text-sm">
              {a.consultores.map((c) => technicians[c.id]?.nombre ?? c.nombre).join(", ")}
            </div>
          </div>
          <EstadoBadge estado={a.estado} />
        </li>
      ))}
    </ul>
  );
}
