from dataclasses import dataclass

from atenciones.dtos.output.nota_seguimiento_dto import NotaSeguimientoDTO
from atenciones.models import NotaSeguimiento


@dataclass(frozen=True)
class AgregarNotaInputDTO:
    atencion_id: int
    consultor_id: int
    contenido: str


class NotaSeguimientoRepository:
    @classmethod
    def guardar_nota(cls, input_dto: AgregarNotaInputDTO) -> NotaSeguimientoDTO:
        nota = NotaSeguimiento(
            atencion_id=input_dto.atencion_id,
            consultor_id=input_dto.consultor_id,
            contenido=input_dto.contenido,
        )
        nota.save()
        return NotaSeguimientoDTO.from_orm(nota)

    @classmethod
    def listar_por_atencion(
        cls,
        atencion_id: int,
        consultor_id: int | None = None,
    ) -> list[NotaSeguimientoDTO]:
        qs = NotaSeguimiento.objects.filter(atencion_id=atencion_id)
        if consultor_id is not None:
            qs = qs.filter(consultor_id=consultor_id)
        return [NotaSeguimientoDTO.from_orm(n) for n in qs]
