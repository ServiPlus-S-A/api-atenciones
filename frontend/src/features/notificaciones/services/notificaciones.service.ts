import api from "@/lib/axios";
import type { NotificacionDTO } from "@/types/notificacion.types";

export const fetchNotificaciones = () =>
  api.get<NotificacionDTO[]>("/notificaciones/").then((r) => r.data);

export const marcarLeida = (id: number) =>
  api.patch(`/notificaciones/${id}/`, { leida: true });
