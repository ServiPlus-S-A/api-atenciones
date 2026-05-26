"use client";

import { AtencionList } from "@/features/atenciones/components/AtencionList";
import { useAtenciones } from "@/features/atenciones/hooks/useAtenciones";
import { Spinner } from "@/components/ui/Spinner";

export default function MisAtencionesPage() {
  const { atenciones, loading, error } = useAtenciones();

  if (loading) return <Spinner />;
  if (error) return <p className="text-serviplus-danger">{error}</p>;

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Mis atenciones</h2>
      <AtencionList atenciones={atenciones} />
    </section>
  );
}
