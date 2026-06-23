from enum import StrEnum


class AtentionStatus(StrEnum):
    SCHEDULED = "AGENDADA"
    FINISHED = "FINALIZADA"
    CANCELLED = "ANULADA"

    # Spanish aliases (backwards compatibility)
    AGENDADA = SCHEDULED
    FINALIZADA = FINISHED
    ANULADA = CANCELLED


class Rol(StrEnum):
    CONSULTANT = "CONSULTOR"
    CLIENT = "CLIENTE"
    COORDINATOR = "COORDINADOR"

    # Spanish aliases (backwards compatibility)
    CONSULTOR = CONSULTANT
    CLIENTE = CLIENT
    COORDINADOR = COORDINATOR


VALID_TRANSACTIONS: dict[str, list[str]] = {
    AtentionStatus.SCHEDULED: [
        AtentionStatus.SCHEDULED,
        AtentionStatus.FINISHED,
        AtentionStatus.CANCELLED,
    ],
    AtentionStatus.FINISHED: [],
    AtentionStatus.CANCELLED: [],
}

ERR_NOT_PENDING_REQUEST = "La solicitud no está en estado Pendiente."
ERR_INVALID_TRANSACTION = "Transición de estado no permitida."
ERR_ANTICIPATION = "No se permite seleccionar fechas anteriores a la fecha actual."
ERR_SCHEDULE_OVERLAP = "Existe cruce de horario para uno o más consultores."
ERR_MINIMUM_NOTE = "La nota debe tener entre 10 y 1000 caracteres."
ERR_NOTA_SEGUIMIENTO = "La nota debe tener entre 10 y 1000 caracteres."

# HU-02: mensajes de error específicos
ERR_SOLICITUD_NO_AUTORIZADA = (
    "La solicitud ingresada no existe en el sistema o no está autorizada para atención."
)
ERR_MENSAJE_PRELIMINAR = "El diagnostico debe tener entre 15 y 1000 caracteres."
ERR_CONSULTOR_NO_ENCONTRADO = "Consultor {} no encontrado en el sistema."
ERR_CONSULTOR_NO_DISPONIBLE = "Consultor {} no está disponible."
ERR_CONSULTOR_SIN_APTITUD = (
    "Consultor {} no tiene la aptitud requerida para este servicio."
)
ERR_CONSULTOR_DUPLICADO = (
    "La lista de consultor_ids contiene identificadores duplicados."
)

# Actor técnico mientras no hay auth real activa
ACTOR_TECNICO_DEFAULT = "SYSTEM"

TTL_LISTED_CACHE = 30

# Backwards compatibility: Spanish names
EstadoAtencion = AtentionStatus
