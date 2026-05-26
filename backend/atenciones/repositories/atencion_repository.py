from datetime import datetime

from django.db.models import Prefetch, Q

from atenciones.constants import EstadoAtencion
from atenciones.dtos.input.anular_atencion_input_dto import AnularAtencionInputDTO
from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO
from atenciones.dtos.input.finalizar_atencion_input_dto import FinalizarAtencionInputDTO
from atenciones.dtos.input.programar_atencion_input_dto import ProgramarAtencionInputDTO
from atenciones.dtos.output.atencion_dto import AtencionDTO
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.models import Atencion, AtencionConsultor, NotaSeguimiento


class AtencionRepository:
    """CONCERN-07/08: único punto de acceso ORM; retorna siempre DTOs."""

    @staticmethod
    def _base_qs():
        return Atencion.objects.prefetch_related(
            Prefetch("consultores_rel", queryset=AtencionConsultor.objects.all()),
        )

    @classmethod
    def obtener_por_id(cls, atencion_id: int) -> AtencionDTO:
        try:
            instancia = cls._base_qs().get(pk=atencion_id)
        except Atencion.DoesNotExist:
            raise AtencionNoEncontrada()
        return AtencionDTO.from_orm(instancia)

    @classmethod
    def listar(
        cls,
        filtros: dict,
        estados_excluidos: list[str] | None = None,
    ) -> list[AtencionDTO]:
        qs = cls._base_qs()
        if estados_excluidos:
            qs = qs.exclude(estado__in=estados_excluidos)
        if estado := filtros.get("estado"):
            qs = qs.filter(estado=estado)
        if solicitud_id := filtros.get("solicitud_id"):
            qs = qs.filter(solicitud_id=solicitud_id)
        if fecha_inicio := filtros.get("fecha_inicio"):
            qs = qs.filter(fecha_programada__date__gte=fecha_inicio)
        if fecha_fin := filtros.get("fecha_fin"):
            qs = qs.filter(fecha_programada__date__lte=fecha_fin)
        if consultor_id := filtros.get("consultor_id"):
            qs = qs.filter(consultores_rel__consultor_id=consultor_id)
        return [AtencionDTO.from_orm(a) for a in qs.distinct()]

    @classmethod
    def guardar(cls, input_dto: CrearAtencionInputDTO) -> AtencionDTO:
        atencion = Atencion.objects.create(
            solicitud_id=input_dto.solicitud_id,
            creado_por_id=input_dto.creado_por_id,
            estado=EstadoAtencion.AGENDADA,
        )
        for i, consultor_id in enumerate(input_dto.consultor_ids):
            AtencionConsultor.objects.create(
                atencion=atencion,
                consultor_id=consultor_id,
                es_lider=(i == 0),
            )
        if input_dto.mensaje_preliminar:
            NotaSeguimiento.objects.create(
                atencion=atencion,
                consultor_id=input_dto.creado_por_id,
                contenido=input_dto.mensaje_preliminar,
            )
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atencion.pk))

    @classmethod
    def programar(cls, input_dto: ProgramarAtencionInputDTO) -> AtencionDTO:
        atencion = Atencion.objects.get(pk=input_dto.atencion_id)
        atencion.fecha_programada = input_dto.fecha_programada
        atencion.fecha_fin = input_dto.fecha_fin
        atencion.save(update_fields=["fecha_programada", "fecha_fin", "updated_at"])
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atencion.pk))

    @classmethod
    def finalizar(cls, input_dto: FinalizarAtencionInputDTO) -> AtencionDTO:
        atencion = Atencion.objects.get(pk=input_dto.atencion_id)
        atencion.estado = EstadoAtencion.FINALIZADA
        atencion.notas_finales = input_dto.notas_finales
        atencion.fecha_cierre = datetime.now(tz=atencion.created_at.tzinfo)
        atencion.save(
            update_fields=["estado", "notas_finales", "fecha_cierre", "updated_at"],
        )
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atencion.pk))

    @classmethod
    def anular(cls, input_dto: AnularAtencionInputDTO) -> AtencionDTO:
        atencion = Atencion.objects.get(pk=input_dto.atencion_id)
        atencion.estado = EstadoAtencion.ANULADA
        atencion.motivo_anulacion = input_dto.motivo_anulacion
        atencion.save(update_fields=["estado", "motivo_anulacion", "updated_at"])
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atencion.pk))

    @classmethod
    def buscar_cruces(
        cls,
        consultor_ids: list[int],
        fecha_inicio: datetime,
        fecha_fin: datetime,
        excluir_atencion_id: int | None = None,
    ) -> list[tuple[int, datetime, datetime]]:
        qs = Atencion.objects.filter(
            consultores_rel__consultor_id__in=consultor_ids,
            fecha_programada__isnull=False,
            fecha_fin__isnull=False,
        ).exclude(estado=EstadoAtencion.ANULADA)
        if excluir_atencion_id:
            qs = qs.exclude(pk=excluir_atencion_id)
        qs = qs.filter(
            Q(fecha_programada__lt=fecha_fin) & Q(fecha_fin__gt=fecha_inicio),
        )
        result = []
        for a in qs.prefetch_related("consultores_rel"):
            for rel in a.consultores_rel.all():
                if rel.consultor_id in consultor_ids:
                    result.append((rel.consultor_id, a.fecha_programada, a.fecha_fin))
        return result
