from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProgramarAtencionInputDTO:
    atencion_id: int
    fecha_programada: datetime
    fecha_fin: datetime
    programado_por_id: int
