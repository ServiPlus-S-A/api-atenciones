from atenciones.exceptions.custom_exceptions import (
    AnticipacionInsuficiente,
    AtencionNoEncontrada,
    ConsultorNoDisponible,
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
    "AnticipacionInsuficiente",
    "CruceHorarioException",
    "ServicioExternoNoDisponible",
    "ParametrosFiltroInvalidos",
    "AtencionDoesNotExist",
    "AtencionServiceUnavailableError",
]
