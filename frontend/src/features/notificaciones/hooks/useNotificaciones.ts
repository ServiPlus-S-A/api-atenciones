"use client";

import { useEffect, useState } from "react";
import { fetchNotificaciones } from "@/features/notificaciones/services/notificaciones.service";
import type { NotificacionDTO } from "@/types/notificacion.types";

const POLL_INTERVAL_MS = 30_000;

/** CONCERN-02: polling cada 30s; sin SSE (stateless multi-instancia). */
export function useNotificaciones() {
  const [notificaciones, setNotificaciones] = useState<NotificacionDTO[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const data = await fetchNotificaciones();
        if (active) {
          setNotificaciones(data);
          setError(null);
        }
      } catch {
        if (active) setError("Error al cargar notificaciones");
      }
    };

    load();
    const id = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  return { notificaciones, error, noLeidas: notificaciones.filter((n) => !n.leida).length };
}
