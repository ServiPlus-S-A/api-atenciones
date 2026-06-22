"use client";

import { AtencionList } from "@/features/atenciones/components/AtencionList";
import { useAtenciones } from "@/features/atenciones/hooks/useAtenciones";
import { Spinner } from "@/components/ui/Spinner";
import { useState } from "react";

function FiltrosPanel({ onSearch }: { onSearch: (f: Record<string, string>) => void }) {
  const [clienteNombre, setClienteNombre] = useState("");
  const [consultorNombre, setConsultorNombre] = useState("");
  const [requestId, setRequestId] = useState("");
  const [fechaRegistro, setFechaRegistro] = useState("");

  const buscar = (e?: React.FormEvent) => {
    e?.preventDefault();
    const filtros: Record<string, string> = {};
    if (clienteNombre) filtros.cliente_nombre = clienteNombre;
    if (consultorNombre) filtros.consultor_nombre = consultorNombre;
    if (requestId) filtros.request_id = requestId;
    if (fechaRegistro) filtros.fecha_registro = fechaRegistro;
    onSearch(filtros);
  };

  const limpiar = () => {
    setClienteNombre("");
    setConsultorNombre("");
    setRequestId("");
    setFechaRegistro("");
    onSearch({});
  };

  return (
    <form onSubmit={buscar} className="mb-4 grid grid-cols-1 gap-2 sm:grid-cols-4">
      <input
        placeholder="Cliente (nombre)"
        value={clienteNombre}
        onChange={(e) => setClienteNombre(e.target.value)}
        className="input"
      />
      <input
        placeholder="Consultor (nombre)"
        value={consultorNombre}
        onChange={(e) => setConsultorNombre(e.target.value)}
        className="input"
      />
      <input
        placeholder="ID solicitud"
        value={requestId}
        onChange={(e) => setRequestId(e.target.value)}
        className="input"
      />
      <div className="flex gap-2">
        <input
          type="date"
          value={fechaRegistro}
          onChange={(e) => setFechaRegistro(e.target.value)}
          className="input"
        />
        <button className="btn" type="submit">Buscar</button>
        <button type="button" className="btn-ghost" onClick={limpiar}>Limpiar</button>
      </div>
    </form>
  );
}

/** CONCERN-08: coordinador ve TODAS las atenciones incluyendo ANULADAS. */
export default function CoordinadorPage() {
  const { atenciones, loading, fetchAtenciones } = useAtenciones();

  if (loading) return <Spinner />;

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Panel coordinador</h2>
      <FiltrosPanel onSearch={(f) => fetchAtenciones(f)} />
      <AtencionList atenciones={atenciones} showAnuladas />
    </section>
  );
}
