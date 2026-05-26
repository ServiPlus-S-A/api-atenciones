export enum EstadoAtencion {
  AGENDADA = "AGENDADA",
  FINALIZADA = "FINALIZADA",
  ANULADA = "ANULADA",
}

export enum Rol {
  CONSULTOR = "CONSULTOR",
  COORDINADOR = "COORDINADOR",
  CLIENTE = "CLIENTE",
}

export interface ConsultorRefDTO {
  id: number;
  nombre: string;
  es_lider: boolean;
}

export interface AtencionDTO {
  id: number;
  estado: EstadoAtencion;
  solicitud_id: number;
  fecha_programada: string | null;
  fecha_fin: string | null;
  consultores: ConsultorRefDTO[];
  notas_finales: string | null;
  fecha_cierre: string | null;
}

export interface NotaSeguimientoDTO {
  id: number;
  consultor_id: number;
  contenido: string;
  timestamp: string;
}
