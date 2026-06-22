from atenciones.exceptions.custom_exceptions import (
    AnticipacionInsuficiente,
    AtencionNoEncontrada,
    ConsultorNoDisponible,
    ConsultorNoAsignado,
    CruceHorarioException,
    ParametrosFiltroInvalidos,
    ServicioExternoNoDisponible,
    SolicitudNoAutorizada,
    TransicionInvalidaException,
    AtencionDoesNotExist,
    AtencionServiceUnavailableError,
)

__all__ = [
    "AtencionNoEncontrada",
    "TransicionInvalidaException",
    "SolicitudNoAutorizada",
    "ConsultorNoDisponible",
    "ConsultorNoAsignado",
    "AnticipacionInsuficiente",
    "CruceHorarioException",
    "ServicioExternoNoDisponible",
    "ParametrosFiltroInvalidos",
    "AtencionDoesNotExist",
    "AtencionServiceUnavailableError",
]
