"use client";

import { useCallback, useEffect, useState } from "react";
import * as service from "@/features/atenciones/services/atenciones.service";
import type { AtencionDTO } from "@/types/atencion.types";

const DEFAULT_FILTROS: Record<string, string | number> = {};

export function useAtenciones(initialFiltros: Record<string, string | number> = DEFAULT_FILTROS) {
  const [atenciones, setAtenciones] = useState<AtencionDTO[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({ page: 1, page_size: 10, count: 0 });

  const fetchAtenciones = useCallback(async (filtros = initialFiltros) => {
    setLoading(true);
    setError(null);
    try {
      const data = await service.fetchAtenciones(filtros);
      setAtenciones(data.results);
      setPagination({ page: data.page, page_size: data.page_size, count: data.count });
    } catch {
      setError("No se pudieron cargar las atenciones.");
    } finally {
      setLoading(false);
    }
  }, [initialFiltros]);

  useEffect(() => {
    fetchAtenciones();
  }, [fetchAtenciones]);

  const invalidate = () => fetchAtenciones();

  return {
    atenciones,
    loading,
    error,
    pagination,
    fetchAtenciones,
    createAtencion: async (body: object) => {
      const created = await service.crearAtencion(body);
      await invalidate();
      return created;
    },
    programarAtencion: async (id: number, body: object) => {
      const updated = await service.programarAtencion(id, body);
      await invalidate();
      return updated;
    },
    finalizarAtencion: async (id: number, body: object) => {
      const updated = await service.finalizarAtencion(id, body);
      await invalidate();
      return updated;
    },
    anularAtencion: async (id: number, body: object) => {
      const updated = await service.anularAtencion(id, body);
      await invalidate();
      return updated;
    },
  };
}
