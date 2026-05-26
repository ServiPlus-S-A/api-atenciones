import api from "@/lib/axios";
import type { AtencionDTO } from "@/types/atencion.types";

export interface ListadoResponse {
  count: number;
  page: number;
  page_size: number;
  results: AtencionDTO[];
}

export const fetchAtenciones = (params?: Record<string, string | number>) =>
  api.get<ListadoResponse>("/atenciones/", { params }).then((r) => r.data);

export const getAtencion = (id: number) =>
  api.get<AtencionDTO>(`/atenciones/${id}/`).then((r) => r.data);

export const crearAtencion = (body: object) =>
  api.post<AtencionDTO>("/atenciones/", body).then((r) => r.data);

export const programarAtencion = (id: number, body: object) =>
  api.patch<AtencionDTO>(`/atenciones/${id}/programar/`, body).then((r) => r.data);

export const finalizarAtencion = (id: number, body: object) =>
  api.patch<AtencionDTO>(`/atenciones/${id}/finalizar/`, body).then((r) => r.data);

export const anularAtencion = (id: number, body: object) =>
  api.patch<AtencionDTO>(`/atenciones/${id}/anular/`, body).then((r) => r.data);
