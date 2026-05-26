from atenciones.security.permissions import (
    IsCliente,
    IsConsultor,
    IsCoordinador,
    IsOwnerConsultorOrCoordinador,
)

__all__ = ["IsConsultor", "IsCoordinador", "IsCliente", "IsOwnerConsultorOrCoordinador"]
