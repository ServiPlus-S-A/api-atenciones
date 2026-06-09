from dataclasses import dataclass

from atenciones.dtos.output.nota_seguimiento_dto import NotaSeguimientoDTO
from atenciones.models import NotaSeguimiento


@dataclass(frozen=True)
class AddNoteInputDTO:
    atention_id: int
    consultant_id: int
    content: str


class NotaSeguimientoRepository:
    @classmethod
    def guardar_nota(cls, input_dto: AddNoteInputDTO) -> NotaSeguimientoDTO:
        nota = NotaSeguimiento(
            atention_id=input_dto.atention_id,
            consultant_id=input_dto.consultant_id,
            content=input_dto.content,
        )
        nota.save()
        return NotaSeguimientoDTO.from_orm(nota)

    @classmethod
    def listar_por_atencion(
        cls,
        atention_id: int,
        consultant_id: int | None = None,
    ) -> list[NotaSeguimientoDTO]:
        qs = NotaSeguimiento.objects.filter(atention_id=atention_id)
        if consultant_id is not None:
            qs = qs.filter(consultant_id=consultant_id)
        return [NotaSeguimientoDTO.from_orm(n) for n in qs]
