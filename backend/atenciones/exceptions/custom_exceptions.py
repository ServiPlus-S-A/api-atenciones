from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAtencionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "error"
    default_detail = "Error en operación de atención."

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        if code:
            self.default_code = code


class AtencionNoEncontrada(BaseAtencionException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "atencion_no_encontrada"
    default_detail = "Atención no encontrada."


class TransicionInvalidaException(BaseAtencionException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "transicion_invalida"
    default_detail = "Transición de estado no permitida."


class SolicitudNoAutorizada(BaseAtencionException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "solicitud_no_autorizada"
    default_detail = "No autorizado para esta solicitud."


class ConsultorNoDisponible(BaseAtencionException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "consultor_no_disponible"
    default_detail = "Uno o más consultores no están disponibles."


class AnticipacionInsuficiente(BaseAtencionException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "anticipacion_insuficiente"
    default_detail = "Se requiere al menos 24 horas de anticipación."


class CruceHorarioException(BaseAtencionException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "cruce_horario"
    default_detail = "Existe cruce de horario para los consultores."


class ServicioExternoNoDisponible(BaseAtencionException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = "servicio_externo_no_disponible"
    default_detail = "Servicio externo no disponible."
