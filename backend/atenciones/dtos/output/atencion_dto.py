from dataclasses import dataclass
from datetime import datetime

from atenciones.dtos.output.consultor_ref_dto import ConsultantRefDTO
from atenciones.models import Atention


@dataclass(frozen=True)
class AtentionDTO:
    id: int
    estado: str
    solicitud_id: str  # UUID string de la solicitud externa
    fecha_programada: datetime | None
    fecha_fin: datetime | None
    notas_finales: str | None
    fecha_cierre: datetime | None
    consultores: list[ConsultantRefDTO]
    motivo_anulacion: str | None = None
    cliente_nombre: str | None = None
    fecha_registro: datetime | None = None

    @classmethod
    def from_orm(
        cls, instancia: Atention, nombres_consultores: dict[str, str] | None = None
    ) -> "AtentionDTO":
        nombres = nombres_consultores or {}
        consultants = [
            ConsultantRefDTO(
                id=str(rel.consultant_id),
                name=nombres.get(
                    str(rel.consultant_id),
                    rel.consultant_name or f"Consultant {rel.consultant_id}",
                ),
                is_leader=rel.is_leader,
            )
            for rel in instancia.consultants_rel.all()
        ]
        return cls(
            id=instancia.pk,
            estado=instancia.status,
            solicitud_id=str(instancia.request_id),
            fecha_programada=instancia.scheduled_date,
            fecha_fin=instancia.closing_date,
            notas_finales=instancia.final_note,
            fecha_cierre=instancia.closing_date,
            consultores=consultants,
            motivo_anulacion=instancia.cancellation_reason,
            cliente_nombre=instancia.customer_name,
            fecha_registro=instancia.created_at,
        )


# Backwards compatibility alias
AtencionDTO = AtentionDTO
