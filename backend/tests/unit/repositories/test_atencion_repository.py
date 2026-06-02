from datetime import timedelta

import pytest
from django.utils import timezone

from atenciones.constants import EstadoAtencion
from atenciones.dtos.input.anular_atencion_input_dto import AnularAtencionInputDTO
from atenciones.dtos.input.finalizar_atencion_input_dto import FinalizarAtencionInputDTO
from atenciones.dtos.input.programar_atencion_input_dto import ProgramarAtencionInputDTO
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.models import AtentionConsultant, MonitoringNote
from atenciones.repositories.atencion_repository import AtencionRepository
from tests.factories.atencion_factory import AtencionAnuladaFactory, AtencionFactory


@pytest.mark.django_db
def test_listar_excluye_anulada_para_consultor():
    AtencionFactory()
    AtencionAnuladaFactory()
    result = AtencionRepository.listar({}, estados_excluidos=[EstadoAtencion.ANULADA])
    assert all(d.estado != EstadoAtencion.ANULADA for d in result)


@pytest.mark.django_db
def test_listar_incluye_anulada_para_coordinador():
    AtencionAnuladaFactory()
    result = AtencionRepository.listar({}, estados_excluidos=None)
    assert any(d.estado == EstadoAtencion.ANULADA for d in result)


@pytest.mark.django_db
def test_guardar_retorna_dto_no_model():
    from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO

    dto = AtencionRepository.guardar(
        CrearAtencionInputDTO(
            solicitud_id=99,
            consultor_ids=[1],
            mensaje_preliminar="Mensaje preliminar válido.",
            creado_por_id=1,
        ),
    )
    assert hasattr(dto, "id")
    assert dto.estado == EstadoAtencion.AGENDADA


@pytest.mark.django_db
def test_obtener_por_id_lanza_no_encontrada():
    with pytest.raises(AtencionNoEncontrada):
        AtencionRepository.obtener_por_id(9999)


@pytest.mark.django_db
def test_listar_filtra_por_estado_request_fecha_y_consultor():
    base = AtencionFactory(status=EstadoAtencion.AGENDADA)
    base.request_id = 123
    base.scheduled_date = timezone.now() + timedelta(days=2)
    base.save(update_fields=["request_id", "scheduled_date"])
    AtentionConsultant.objects.create(atention=base, consultant_id=10, is_leader=True)

    other = AtencionFactory(status=EstadoAtencion.ANULADA)
    other.request_id = 999
    other.scheduled_date = timezone.now() + timedelta(days=10)
    other.save(update_fields=["request_id", "scheduled_date"])
    AtentionConsultant.objects.create(atention=other, consultant_id=99, is_leader=True)

    filtros = {
        "estado": EstadoAtencion.AGENDADA,
        "request_id": 123,
        "fecha_inicio": (timezone.now() + timedelta(days=1)).date(),
        "fecha_fin": (timezone.now() + timedelta(days=5)).date(),
        "consultor_id": 10,
    }
    result = AtencionRepository.listar(filtros, estados_excluidos=None)

    assert len(result) == 1
    assert result[0].id == base.id


@pytest.mark.django_db
def test_guardar_crea_nota_si_mensaje_preliminar():
    from atenciones.dtos.input.crear_atencion_input_dto import CrearAtencionInputDTO

    dto = CrearAtencionInputDTO(
        solicitud_id=55,
        consultor_ids=[1, 2],
        mensaje_preliminar="Nota inicial.",
        creado_por_id=2,
    )

    created = AtencionRepository.guardar(dto)

    assert MonitoringNote.objects.filter(atention_id=created.id).exists()


@pytest.mark.django_db
def test_programar_actualiza_fechas():
    atencion = AtencionFactory()
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(hours=1)

    dto = ProgramarAtencionInputDTO(
        atencion_id=atencion.id,
        fecha_programada=start,
        fecha_fin=end,
        programado_por_id=1,
    )
    result = AtencionRepository.programar(dto)

    assert result.fecha_programada == start
    assert result.fecha_fin == end


@pytest.mark.django_db
def test_finalizar_actualiza_estado_y_notas():
    atencion = AtencionFactory()
    dto = FinalizarAtencionInputDTO(
        atencion_id=atencion.id,
        notas_finales="Cierre con notas.",
        consultor_id=1,
    )

    result = AtencionRepository.finalizar(dto)

    assert result.estado == EstadoAtencion.FINALIZADA
    assert result.notas_finales == "Cierre con notas."
    assert result.fecha_fin is not None


@pytest.mark.django_db
def test_anular_actualiza_motivo():
    atencion = AtencionFactory()
    dto = AnularAtencionInputDTO(
        atencion_id=atencion.id,
        motivo_anulacion="Motivo de prueba.",
        coordinador_id=1,
    )

    result = AtencionRepository.anular(dto)

    assert result.estado == EstadoAtencion.ANULADA
    atencion.refresh_from_db()
    assert atencion.cancellation_reason == "Motivo de prueba."


@pytest.mark.django_db
def test_buscar_cruces_considera_consultor_y_exclusion():
    base = AtencionFactory()
    base.scheduled_date = timezone.now() + timedelta(days=1)
    base.closing_date = base.scheduled_date + timedelta(hours=2)
    base.save(update_fields=["scheduled_date", "closing_date"])
    AtentionConsultant.objects.create(atention=base, consultant_id=5, is_leader=True)

    other = AtencionFactory()
    other.scheduled_date = base.scheduled_date + timedelta(minutes=30)
    other.closing_date = other.scheduled_date + timedelta(hours=1)
    other.save(update_fields=["scheduled_date", "closing_date"])
    AtentionConsultant.objects.create(atention=other, consultant_id=5, is_leader=True)

    overlaps = AtencionRepository.buscar_cruces(
        consultor_ids=[5],
        fecha_inicio=base.scheduled_date,
        fecha_fin=base.closing_date,
        excluir_atencion_id=None,
    )

    assert overlaps

    excluded = AtencionRepository.buscar_cruces(
        consultor_ids=[5],
        fecha_inicio=base.scheduled_date,
        fecha_fin=base.closing_date,
        excluir_atencion_id=other.id,
    )

    assert all(item[0] == 5 for item in excluded)
