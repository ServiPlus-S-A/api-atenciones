from dataclasses import dataclass
from datetime import datetime

from atenciones.dtos.output.consultor_ref_dto import ConsultantRefDTO
from atenciones.models import Atention


@dataclass(frozen=True)
class AtentionDTO:
    id: int
    estado: str
    solicitud_id: int
    fecha_programada: datetime | None
    fecha_fin: datetime | None
    notas_finales: str | None
    fecha_cierre: datetime | None
    consultores: list[ConsultantRefDTO]

    @classmethod
    def from_orm(cls, instancia: Atention, nombres_consultores: dict[int, str] | None = None) -> "AtentionDTO":
        nombres = nombres_consultores or {}
        consultants = [
            ConsultantRefDTO(
                id=rel.consultant_id,
                name=nombres.get(rel.consultant_id, f"Consultant {rel.consultant_id}"),
                is_leader=rel.is_leader,
            )
            for rel in instancia.consultants_rel.all()
        ]
        return cls(
            id=instancia.pk,
            estado=instancia.status,
            solicitud_id=instancia.request_id,
            fecha_programada=instancia.scheduled_date,
            fecha_fin=instancia.closing_date,
            notas_finales=instancia.final_note,
            fecha_cierre=instancia.closing_date,
            consultores=consultants,
        )


# Backwards compatibility alias
AtencionDTO = AtentionDTO
