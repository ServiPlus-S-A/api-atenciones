"use client";

import { FormEvent, useMemo, useState } from "react";
import { AtencionList } from "@/features/atenciones/components/AtencionList";
import { useAtenciones } from "@/features/atenciones/hooks/useAtenciones";
import { Spinner } from "@/components/ui/Spinner";

/** CONCERN-08: coordinador ve TODAS las atenciones incluyendo ANULADAS. */
export default function CoordinadorPage() {
  const { atenciones, loading, error, fetchAtenciones } = useAtenciones();
  const [filtros, setFiltros] = useState({
    nombre_cliente: "",
    nombre_consultor: "",
    solicitud_id: "",
    fecha_registro: "",
  });
  const [busquedaAplicada, setBusquedaAplicada] = useState(false);

  const hasFiltros = useMemo(
    () => Object.values(filtros).some((value) => value.trim() !== ""),
    [filtros],
  );

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const params = Object.fromEntries(
      Object.entries(filtros).filter(([, value]) => value.trim() !== ""),
    );
    setBusquedaAplicada(Object.keys(params).length > 0);
    fetchAtenciones(params);
  };

  const onReset = () => {
    const empty = {
      nombre_cliente: "",
      nombre_consultor: "",
      solicitud_id: "",
      fecha_registro: "",
    };
    setFiltros(empty);
    setBusquedaAplicada(false);
    fetchAtenciones({});
  };

  if (loading) return <Spinner />;

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Panel de atenciones</h2>
        <p className="mt-1 text-sm text-serviplus-muted">
          Consulta atenciones por cliente, consultor, solicitud o fecha de registro.
        </p>
      </div>

      <form onSubmit={onSubmit} className="grid gap-4 rounded-card border p-4 md:grid-cols-4">
        <label className="text-sm">
          Nombre del cliente
          <input
            className="mt-1 w-full rounded-card border px-3 py-2"
            value={filtros.nombre_cliente}
            onChange={(event) =>
              setFiltros((prev) => ({ ...prev, nombre_cliente: event.target.value }))
            }
            placeholder="Ej. Ana Rojas"
          />
        </label>
        <label className="text-sm">
          Consultor
          <input
            className="mt-1 w-full rounded-card border px-3 py-2"
            value={filtros.nombre_consultor}
            onChange={(event) =>
              setFiltros((prev) => ({ ...prev, nombre_consultor: event.target.value }))
            }
            placeholder="Nombre o ID"
          />
        </label>
        <label className="text-sm">
          ID de solicitud
          <input
            className="mt-1 w-full rounded-card border px-3 py-2"
            value={filtros.solicitud_id}
            onChange={(event) =>
              setFiltros((prev) => ({ ...prev, solicitud_id: event.target.value }))
            }
            placeholder="Ej. 123"
          />
        </label>
        <label className="text-sm">
          Fecha de registro
          <input
            className="mt-1 w-full rounded-card border px-3 py-2"
            type="date"
            value={filtros.fecha_registro}
            onChange={(event) =>
              setFiltros((prev) => ({ ...prev, fecha_registro: event.target.value }))
            }
          />
        </label>
        <div className="flex gap-3 md:col-span-4">
          <button
            type="submit"
            className="rounded-card bg-serviplus-primary px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            disabled={!hasFiltros}
          >
            Buscar
          </button>
          <button
            type="button"
            onClick={onReset}
            className="rounded-card border px-4 py-2 text-sm font-medium"
          >
            Limpiar
          </button>
        </div>
      </form>

      {error && <p className="rounded-card border border-red-200 p-3 text-sm text-red-700">{error}</p>}

      <AtencionList
        atenciones={atenciones}
        showAnuladas
        emptyMessage={
          busquedaAplicada
            ? "Ninguna atención responde a sus especificaciones."
            : "No hay atenciones para mostrar."
        }
      />
    </section>
  );
}
