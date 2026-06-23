"use client";

import Link from "next/link";
import { Spinner } from "@/components/ui/Spinner";
import { EstadoBadge } from "@/features/atenciones/components/EstadoBadge";
import { useAtencionDetalle } from "@/features/atenciones/hooks/useAtencionDetalle";

export default function AtencionDetalleCoordinadorPage({
  params,
}: {
  params: { id: string };
}) {
  const { atencion, loading } = useAtencionDetalle(Number(params.id));

  if (loading) return <Spinner />;

  if (!atencion) {
    return <p className="text-serviplus-muted">No fue posible cargar la atención.</p>;
  }

  return (
    <section className="space-y-6">
      <Link href="/coordinador" className="text-sm text-serviplus-primary underline">
        Volver al panel
      </Link>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Atención #{atencion.id}</h2>
          <p className="mt-1 text-sm text-serviplus-muted">
            Solicitud {atencion.solicitud_id}
          </p>
        </div>
        <EstadoBadge estado={atencion.estado} />
      </div>

      <dl className="grid gap-4 rounded-card border p-4 md:grid-cols-2">
        <div>
          <dt className="text-sm text-serviplus-muted">Cliente</dt>
          <dd className="font-medium">{atencion.cliente_nombre || "Sin cliente registrado"}</dd>
        </div>
        <div>
          <dt className="text-sm text-serviplus-muted">Fecha de registro</dt>
          <dd className="font-medium">
            {atencion.fecha_registro
              ? new Date(atencion.fecha_registro).toLocaleString("es-CO")
              : "Sin fecha"}
          </dd>
        </div>
        <div>
          <dt className="text-sm text-serviplus-muted">Consultores</dt>
          <dd className="font-medium">
            {atencion.consultores.map((consultor) => consultor.nombre).join(", ") || "Sin consultores"}
          </dd>
        </div>
        <div>
          <dt className="text-sm text-serviplus-muted">Programación</dt>
          <dd className="font-medium">
            {atencion.fecha_programada
              ? new Date(atencion.fecha_programada).toLocaleString("es-CO")
              : "Sin programar"}
          </dd>
        </div>
        <div className="md:col-span-2">
          <dt className="text-sm text-serviplus-muted">Notas finales</dt>
          <dd className="font-medium">{atencion.notas_finales || "Sin notas finales"}</dd>
        </div>
      </dl>
    </section>
  );
}
