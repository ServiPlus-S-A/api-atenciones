import api from "@/lib/axios";
import { EstadoAtencion, type AtencionDTO } from "@/types/atencion.types";

interface ConsultantApi {
  id: string;
  name: string;
  is_leader: boolean;
}

interface AtencionApi {
  id: number;
  status: EstadoAtencion;
  request_id: string;
  scheduled_date: string | null;
  closing_date: string | null;
  consultants?: ConsultantApi[];
  final_note?: string | null;
  cancellation_reason?: string | null;
  customer_name?: string | null;
  cliente_nombre?: string | null;
  created_at?: string | null;
}

export interface ListadoResponse {
  count: number;
  page: number;
  page_size: number;
  results: AtencionDTO[];
}

interface ListadoApiResponse {
  count: number;
  page: number;
  page_size: number;
  results: AtencionApi[];
}

const mapAtencion = (item: AtencionApi): AtencionDTO => ({
  id: item.id,
  estado: item.status,
  solicitud_id: item.request_id,
  fecha_programada: item.scheduled_date,
  fecha_fin: item.closing_date,
  consultores: (item.consultants ?? []).map((consultant) => ({
    id: consultant.id,
    nombre: consultant.name,
    es_lider: consultant.is_leader,
  })),
  notas_finales: item.final_note ?? null,
  fecha_cierre: item.closing_date,
  motivo_anulacion: item.cancellation_reason ?? null,
  cliente_nombre: item.customer_name ?? item.cliente_nombre ?? null,
  fecha_registro: item.created_at ?? null,
});

export const fetchAtenciones = (params?: Record<string, string | number>) =>
  api.get<ListadoApiResponse>("/atenciones/", { params }).then((r) => ({
    ...r.data,
    results: r.data.results.map(mapAtencion),
  }));

export const getAtencion = (id: number) =>
  api.get<AtencionApi>(`/atenciones/${id}/`).then((r) => mapAtencion(r.data));

export const crearAtencion = (body: object) =>
  api.post<AtencionDTO>("/atenciones/", body).then((r) => r.data);

export const programarAtencion = (id: number, body: object) =>
  api.patch<AtencionDTO>(`/atenciones/${id}/programar/`, body).then((r) => r.data);

export const finalizarAtencion = (id: number, body: object) =>
  api.patch<AtencionDTO>(`/atenciones/${id}/finalizar/`, body).then((r) => r.data);

export const anularAtencion = (id: number, body: object) =>
  api.patch<AtencionDTO>(`/atenciones/${id}/anular/`, body).then((r) => r.data);
