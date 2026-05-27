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
    AtentionStatus.SCHEDULED: [AtentionStatus.FINISHED, AtentionStatus.CANCELLED],
    AtentionStatus.FINISHED: [],
    AtentionStatus.CANCELLED: [],
}

ERR_NOT_PENDING_REQUEST = "La solicitud no está en estado Pendiente."
ERR_INVALID_TRANSACTION = "Transición de estado no permitida."
ERR_ANTICIPATION = "La programación requiere al menos 24 horas de anticipación."
ERR_SCHEDULE_OVERLAP = "Existe cruce de horario para uno o más consultores."
ERR_MINIMUM_NOTE = "El contenido de la nota debe tener al menos 15 caracteres."
ERR_MINIMUM_FINAL_NOTE = "Las notas finales deben tener al menos 20 caracteres."

TTL_LISTED_CACHE = 30

# Backwards compatibility: Spanish names
EstadoAtencion = AtentionStatus
