from datetime import datetime

from django.db.models import Prefetch, Q

from atenciones.constants import EstadoAtencion
from atenciones.dtos.input.anular_atencion_input_dto import AnularAtencionInputDTO
from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO
from atenciones.dtos.input.finalizar_atencion_input_dto import FinalizarAtencionInputDTO
from atenciones.dtos.input.programar_atencion_input_dto import ProgramarAtencionInputDTO
from atenciones.dtos.output.atencion_dto import AtencionDTO
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.models import Atention, AtentionConsultant, MonitoringNote


class AtencionRepository:
    """CONCERN-07/08: único punto de acceso ORM; retorna siempre DTOs."""

    @staticmethod
    def _base_qs():
        return Atention.objects.prefetch_related(
            Prefetch("consultants_rel", queryset=AtentionConsultant.objects.all()),
        )

    @classmethod
    def obtener_por_id(cls, atencion_id: int) -> AtencionDTO:
        try:
            instancia = cls._base_qs().get(pk=atencion_id)
        except Atention.DoesNotExist:
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
            qs = qs.exclude(status__in=estados_excluidos)
        if estado := filtros.get("estado"):
            qs = qs.filter(status=estado)
        if request_id := filtros.get("request_id"):
            qs = qs.filter(request_id=request_id)
        if fecha_inicio := filtros.get("fecha_inicio"):
            qs = qs.filter(scheduled_date__date__gte=fecha_inicio)
        if fecha_fin := filtros.get("fecha_fin"):
            qs = qs.filter(scheduled_date__date__lte=fecha_fin)
        if consultant_id := filtros.get("consultor_id"):
            qs = qs.filter(consultants_rel__consultant_id=consultant_id)
        return [AtencionDTO.from_orm(a) for a in qs.distinct()]

    @classmethod
    def guardar(cls, input_dto: CrearAtencionInputDTO) -> AtencionDTO:
        atention = Atention.objects.create(
            request_id=input_dto.solicitud_id,
            created_by=input_dto.creado_por_id,
            status=EstadoAtencion.AGENDADA,
        )
        for i, consultor_id in enumerate(input_dto.consultor_ids):
            AtentionConsultant.objects.create(
                atention=atention,
                consultant_id=consultor_id,
                is_leader=(i == 0),
            )
        if input_dto.mensaje_preliminar:
            MonitoringNote.objects.create(
                atention=atention,
                consultant_id=input_dto.creado_por_id,
                content=input_dto.mensaje_preliminar,
            )
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atention.pk))

    @classmethod
    def programar(cls, input_dto: ProgramarAtencionInputDTO) -> AtencionDTO:
        atention = Atention.objects.get(pk=input_dto.atencion_id)
        atention.scheduled_date = input_dto.fecha_programada
        atention.closing_date = input_dto.fecha_fin
        atention.save(update_fields=["scheduled_date", "closing_date", "updated_at"])
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atention.pk))

    @classmethod
    def finalizar(cls, input_dto: FinalizarAtencionInputDTO) -> AtencionDTO:
        atention = Atention.objects.get(pk=input_dto.atencion_id)
        atention.status = EstadoAtencion.FINALIZADA
        atention.final_note = input_dto.notas_finales
        atention.closing_date = datetime.now(tz=atention.created_at.tzinfo)
        atention.save(
            update_fields=["status", "final_note", "closing_date", "updated_at"],
        )
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atention.pk))

    @classmethod
    def anular(cls, input_dto: AnularAtencionInputDTO) -> AtencionDTO:
        atention = Atention.objects.get(pk=input_dto.atencion_id)
        atention.status = EstadoAtencion.ANULADA
        atention.cancellation_reason = input_dto.motivo_anulacion
        atention.save(update_fields=["status", "cancellation_reason", "updated_at"])
        return AtencionDTO.from_orm(cls._base_qs().get(pk=atention.pk))

    @classmethod
    def buscar_cruces(
        cls,
        consultor_ids: list[int],
        fecha_inicio: datetime,
        fecha_fin: datetime,
        excluir_atencion_id: int | None = None,
    ) -> list[tuple[int, datetime, datetime]]:
        qs = Atention.objects.filter(
            consultants_rel__consultant_id__in=consultor_ids,
            scheduled_date__isnull=False,
            closing_date__isnull=False,
        ).exclude(status=EstadoAtencion.ANULADA)
        if excluir_atencion_id:
            qs = qs.exclude(pk=excluir_atencion_id)
        qs = qs.filter(
            Q(scheduled_date__lt=fecha_fin) & Q(closing_date__gt=fecha_inicio),
        )
        result = []
        for a in qs.prefetch_related("consultants_rel"):
            for rel in a.consultants_rel.all():
                if rel.consultant_id in consultor_ids:
                    if a.scheduled_date is None or a.closing_date is None:
                        continue
                    result.append((rel.consultant_id, a.scheduled_date, a.closing_date))
        return result
