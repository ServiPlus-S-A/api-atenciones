from dataclasses import dataclass
from datetime import datetime
from atenciones.dtos.output.nota_seguimiento_dto import MonitoringNoteDTO


@dataclass(frozen=True)
class AtencionDetalleCoordinadorDTO:
    id: int
    request_id: str
    solicitud_nombre: str | None
    cliente_nombre: str | None
    scheduled_date: datetime | None
    closing_date: datetime | None
    status: str
    diagnostico_inicial: str | None
    notas: list[MonitoringNoteDTO]
    mensaje_bitacora: str | None
    acciones_disponibles: dict[str, bool]
