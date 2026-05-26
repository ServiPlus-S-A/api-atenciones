"use client";

import { useEffect, useState } from "react";
import { getRol } from "@/lib/auth";
import { getAtencion } from "@/features/atenciones/services/atenciones.service";
import { EstadoAtencion, Rol, type AtencionDTO } from "@/types/atencion.types";

export function useAtencionDetalle(id: number) {
  const [atencion, setAtencion] = useState<AtencionDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const rol = getRol();

  useEffect(() => {
    getAtencion(id)
      .then(setAtencion)
      .finally(() => setLoading(false));
  }, [id]);

  const puedeProgramar =
    atencion?.estado === EstadoAtencion.AGENDADA && rol === Rol.COORDINADOR;
  const puedeFinalizarConsultor =
    atencion?.estado === EstadoAtencion.AGENDADA && rol === Rol.CONSULTOR;
  const puedeAnularCoordinador =
    atencion?.estado === EstadoAtencion.AGENDADA && rol === Rol.COORDINADOR;

  return { atencion, loading, puedeProgramar, puedeFinalizarConsultor, puedeAnularCoordinador };
}
