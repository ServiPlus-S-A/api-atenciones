export interface NotificacionDTO {
  id: number;
  tipo: string;
  mensaje: string;
  leida: boolean;
  created_at: string;
  atencion_id: number | null;
}
