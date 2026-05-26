from dataclasses import dataclass
from datetime import datetime

from atenciones.models import NotaSeguimiento


@dataclass(frozen=True)
class NotaSeguimientoDTO:
    id: int
    consultor_id: int
    contenido: str
    timestamp: datetime

    @classmethod
    def from_orm(cls, instancia: NotaSeguimiento) -> "NotaSeguimientoDTO":
        return cls(
            id=instancia.pk,
            consultor_id=instancia.consultor_id,
            contenido=instancia.contenido,
            timestamp=instancia.timestamp,
        )
