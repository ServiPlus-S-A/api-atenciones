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
        # Filtrado por request_id único o por lista de request_ids
        if request_id := filtros.get("request_id"):
            qs = qs.filter(request_id=str(request_id))
        if request_ids := filtros.get("request_ids"):
            qs = qs.filter(request_id__in=[str(r) for r in request_ids])
        if fecha_inicio := filtros.get("fecha_inicio"):
            qs = qs.filter(scheduled_date__date__gte=fecha_inicio)
        if fecha_fin := filtros.get("fecha_fin"):
            qs = qs.filter(scheduled_date__date__lte=fecha_fin)
        # Fecha de registro (created_at)
        if fecha_registro := filtros.get("fecha_registro"):
            qs = qs.filter(created_at__date=fecha_registro)
        if consultant_id := filtros.get("consultor_id"):
            qs = qs.filter(consultants_rel__consultant_id=str(consultant_id))
        if consultant_ids := filtros.get("consultant_ids"):
            qs = qs.filter(consultants_rel__consultant_id__in=[str(c) for c in consultant_ids])
        qs = qs.order_by("-created_at")
        return [AtencionDTO.from_orm(a) for a in qs.distinct()]

    @classmethod
    def guardar(
        cls, input_dto: CrearAtencionInputDTO, consultores_info=None
    ) -> AtencionDTO:
        atention = Atention.objects.create(
            request_id=str(input_dto.solicitud_id),
            created_by=str(input_dto.creado_por_id)
            if input_dto.creado_por_id
            else None,
            status=EstadoAtencion.AGENDADA,
        )
        for i, consultor_id in enumerate(input_dto.consultor_ids):
            AtentionConsultant.objects.create(
                atention=atention,
                consultant_id=str(consultor_id),
                is_leader=(i == 0),
            )
        if input_dto.mensaje_preliminar:
            leader_id = (
                str(input_dto.consultor_ids[0]) if input_dto.consultor_ids else None
            )
            author_id = (
                str(input_dto.creado_por_id) if input_dto.creado_por_id else leader_id
            )
            MonitoringNote.objects.create(
                atention=atention,
                consultant_id=author_id,
                content=input_dto.mensaje_preliminar,
            )
        nombres_consultores = {
            str(info.id): info.nombre
            for info in (consultores_info or [])
            if getattr(info, "nombre", None)
        }
        return AtencionDTO.from_orm(
            cls._base_qs().get(pk=atention.pk),
            nombres_consultores=nombres_consultores,
        )

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
        consultor_ids: list[str] | list[int],
        fecha_inicio: datetime,
        fecha_fin: datetime,
        excluir_atencion_id: int | None = None,
    ) -> list[tuple[str, datetime, datetime]]:
        str_consultor_ids = [str(cid) for cid in consultor_ids]
        qs = Atention.objects.filter(
            consultants_rel__consultant_id__in=str_consultor_ids,
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
                if str(rel.consultant_id) in str_consultor_ids:
                    if a.scheduled_date is None or a.closing_date is None:
                        continue
                    result.append(
                        (str(rel.consultant_id), a.scheduled_date, a.closing_date)
                    )
        return result
