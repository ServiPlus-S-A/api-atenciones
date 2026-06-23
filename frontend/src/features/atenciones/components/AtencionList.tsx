"use client";

import { useMemo } from "react";
import Link from "next/link";
import { EstadoBadge } from "@/features/atenciones/components/EstadoBadge";
import type { AtencionDTO } from "@/types/atencion.types";
import { EstadoAtencion } from "@/types/atencion.types";

interface Props {
  atenciones: AtencionDTO[];
  showAnuladas?: boolean;
  emptyMessage?: string;
}

export function AtencionList({
  atenciones,
  showAnuladas = false,
  emptyMessage = "No hay atenciones para mostrar.",
}: Props) {
  const technicians = useMemo(() => {
    const map: Record<string, { id: number | string; nombre: string }> = {};
    atenciones.forEach((a) =>
      a.consultores.forEach((c) => {
        map[String(c.id)] = { id: c.id, nombre: c.nombre };
      }),
    );
    return map;
  }, [atenciones]);

  const visible = showAnuladas
    ? atenciones
    : atenciones.filter((a) => a.estado !== EstadoAtencion.ANULADA);

  if (visible.length === 0) {
    return <p className="rounded-card border border-dashed p-4 text-serviplus-muted">{emptyMessage}</p>;
  }

  return (
    <ul className="divide-y rounded-card border">
      {visible.map((a) => (
        <li key={a.id} className="flex items-center justify-between p-4">
          <div>
            <span className="font-medium">#{a.id}</span>
            <span className="ml-2 text-sm text-serviplus-muted">Solicitud {a.solicitud_id}</span>
            <div className="mt-1 text-sm text-serviplus-muted">
              Cliente: {a.cliente_nombre || "Sin cliente registrado"}
            </div>
            <div className="mt-1 text-sm">
              {a.consultores.map((c) => technicians[String(c.id)]?.nombre ?? c.nombre).join(", ")}
            </div>
            <div className="mt-1 text-xs text-serviplus-muted">
              Registro: {a.fecha_registro ? new Date(a.fecha_registro).toLocaleDateString("es-CO") : "Sin fecha"}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <EstadoBadge estado={a.estado} />
            <Link
              href={`/coordinador/atenciones/${a.id}`}
              className="rounded-card border px-3 py-2 text-sm font-medium text-serviplus-primary hover:bg-serviplus-primary/10"
            >
              Ver detalle
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}
