from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAtencionException(APIException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    default_code: str = "error"
    default_detail: str = "Error en operación de atención."

    def __init__(self, detail: str | None = None, code: str | None = None) -> None:
        if code:
            self.default_code = code
        super().__init__(detail=detail, code=code)


class AtencionNoEncontrada(BaseAtencionException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "atencion_no_encontrada"
    default_detail = "Atención no encontrada."


class TransicionInvalidaException(BaseAtencionException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "transicion_invalida"
    default_detail = "Transición de estado no permitida."


class EstadoAtencionNoPermitidoException(BaseAtencionException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "estado_no_permitido"
    default_detail = "Estado de atención no permitido."


class SolicitudNoAutorizada(BaseAtencionException):
    # HU-02: 400 Bad Request (solicitud no existe o no está en estado PENDIENTE)
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "solicitud_no_autorizada"
    default_detail = "La solicitud ingresada no existe en el sistema o no está autorizada para atención."


class ConsultorNoEncontrado(BaseAtencionException):
    # HU-02: 400 cuando el consultor_id no existe en Parametrización
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "consultor_no_encontrado"
    default_detail = "Consultor no encontrado en el sistema."


class ConsultorNoDisponible(BaseAtencionException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "consultor_no_disponible"
    default_detail = "Uno o más consultores no están disponibles."


class AnticipacionInsuficiente(BaseAtencionException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "anticipacion_insuficiente"
    default_detail = "No se permite seleccionar fechas anteriores a la fecha actual."


class CruceHorarioException(BaseAtencionException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "cruce_horario"
    default_detail = (
        "Ya tienes una atención programada en este horario. Por favor selecciona otro."
    )

    def __init__(
        self,
        detail: str | None = None,
        code: str | None = None,
        cruces: list | None = None,
    ) -> None:
        self.cruces = cruces
        super().__init__(detail=detail, code=code)


class ServicioExternoNoDisponible(BaseAtencionException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = "servicio_externo_no_disponible"
    default_detail = "Servicio externo no disponible."


class ParametrosFiltroInvalidos(BaseAtencionException):
    default_code = "parametros_filtro_invalidos"
    default_detail = "Parámetros de filtro inválidos."

    def __init__(self, field_errors: dict) -> None:
        self.field_errors = field_errors
        super().__init__(detail=self.default_detail)


class AtencionDoesNotExist(Exception):
    """Lanzada cuando una atención no existe en la base de datos."""

    pass


class AtencionServiceUnavailableError(Exception):
    """Lanzada cuando hay fallos de base de datos o conexión de red interna."""

    pass
