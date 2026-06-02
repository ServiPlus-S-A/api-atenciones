from dataclasses import dataclass
from datetime import datetime

from atenciones.models import NotaSeguimiento


@dataclass(frozen=True)
class MonitoringNoteDTO:
    id: int
    consultant_id: int
    content: str
    created_at: datetime

    @classmethod
    def from_orm(cls, instancia: NotaSeguimiento) -> "MonitoringNoteDTO":
        return cls(
            id=instancia.pk,
            consultant_id=instancia.consultant_id,
            content=instancia.content,
            created_at=instancia.created_at,
        )


# Backwards compatibility alias
NotaSeguimientoDTO = MonitoringNoteDTO
