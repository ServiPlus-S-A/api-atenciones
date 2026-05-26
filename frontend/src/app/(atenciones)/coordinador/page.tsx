"use client";

import { AtencionList } from "@/features/atenciones/components/AtencionList";
import { useAtenciones } from "@/features/atenciones/hooks/useAtenciones";
import { Spinner } from "@/components/ui/Spinner";

/** CONCERN-08: coordinador ve TODAS las atenciones incluyendo ANULADAS. */
export default function CoordinadorPage() {
  const { atenciones, loading } = useAtenciones();

  if (loading) return <Spinner />;

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Panel coordinador</h2>
      <AtencionList atenciones={atenciones} showAnuladas />
    </section>
  );
}
