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
  id: number | string;
  nombre: string;
  es_lider: boolean;
}

export interface AtencionDTO {
  id: number;
  estado: EstadoAtencion;
  solicitud_id: number | string;
  fecha_programada: string | null;
  fecha_fin: string | null;
  consultores: ConsultorRefDTO[];
  notas_finales: string | null;
  fecha_cierre: string | null;
  motivo_anulacion?: string | null;
  cliente_nombre?: string | null;
  fecha_registro?: string | null;
}

export interface NotaSeguimientoDTO {
  id: number;
  consultor_id: number;
  contenido: string;
  timestamp: string;
}
