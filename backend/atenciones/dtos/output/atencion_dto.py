from dataclasses import dataclass
from datetime import datetime

from atenciones.dtos.output.consultor_ref_dto import ConsultorRefDTO
from atenciones.models import Atencion


@dataclass(frozen=True)
class AtencionDTO:
    id: int
    estado: str
    solicitud_id: int
    fecha_programada: datetime | None
    fecha_fin: datetime | None
    notas_finales: str | None
    fecha_cierre: datetime | None
    consultores: list[ConsultorRefDTO]

    @classmethod
    def from_orm(cls, instancia: Atencion, nombres_consultores: dict[int, str] | None = None) -> "AtencionDTO":
        nombres = nombres_consultores or {}
        consultores = [
            ConsultorRefDTO(
                id=rel.consultor_id,
                nombre=nombres.get(rel.consultor_id, f"Consultor {rel.consultor_id}"),
                es_lider=rel.es_lider,
            )
            for rel in instancia.consultores_rel.all()
        ]
        return cls(
            id=instancia.pk,
            estado=instancia.estado,
            solicitud_id=instancia.solicitud_id,
            fecha_programada=instancia.fecha_programada,
            fecha_fin=instancia.fecha_fin,
            notas_finales=instancia.notas_finales,
            fecha_cierre=instancia.fecha_cierre,
            consultores=consultores,
        )
