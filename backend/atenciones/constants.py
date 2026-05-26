from enum import StrEnum


class EstadoAtencion(StrEnum):
    AGENDADA = "AGENDADA"
    FINALIZADA = "FINALIZADA"
    ANULADA = "ANULADA"


class Rol(StrEnum):
    CONSULTOR = "CONSULTOR"
    CLIENTE = "CLIENTE"
    COORDINADOR = "COORDINADOR"


TRANSICIONES_VALIDAS: dict[str, list[str]] = {
    EstadoAtencion.AGENDADA: [EstadoAtencion.FINALIZADA, EstadoAtencion.ANULADA],
    EstadoAtencion.FINALIZADA: [],
    EstadoAtencion.ANULADA: [],
}

ERR_SOLICITUD_NO_PENDIENTE = "La solicitud no está en estado Pendiente."
ERR_TRANSICION_INVALIDA = "Transición de estado no permitida."
ERR_ANTICIPACION = "La programación requiere al menos 24 horas de anticipación."
ERR_CRUCE_HORARIO = "Existe cruce de horario para uno o más consultores."
ERR_NOTA_MINIMA = "El contenido de la nota debe tener al menos 15 caracteres."
ERR_NOTAS_FINALES_MINIMA = "Las notas finales deben tener al menos 20 caracteres."

TTL_CACHE_LISTADO = 30
