from datetime import datetime, timedelta, timezone

import pytest

from atenciones.constants import EstadoAtencion
from atenciones.dtos.input.anular_atencion_input_dto import AnularAtencionInputDTO
from atenciones.dtos.input.finalizar_atencion_input_dto import FinalizarAtencionInputDTO
from atenciones.dtos.input.programar_atencion_input_dto import ProgramarAtencionInputDTO
from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.models import AtentionConsultant
from atenciones.repositories.atencion_repository import AtencionRepository
from tests.factories.atencion_factory import AtencionAnuladaFactory, AtencionFactory


def _fechas_programacion():
    inicio = datetime.now(timezone.utc) + timedelta(days=3)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)
    return inicio, fin


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
def test_obtener_por_id_existe():
    atencion = AtencionFactory()
    dto = AtencionRepository.obtener_por_id(atencion.pk)
    assert dto.id == atencion.pk


@pytest.mark.django_db
def test_obtener_por_id_no_existe():
    with pytest.raises(AtencionNoEncontrada):
        AtencionRepository.obtener_por_id(99999)


@pytest.mark.django_db
def test_listar_filtros_estado_y_request_id():
    a1 = AtencionFactory(status=EstadoAtencion.AGENDADA, request_id=100)
    AtencionFactory(status=EstadoAtencion.FINALIZADA, request_id=200)
    result = AtencionRepository.listar(
        {"estado": EstadoAtencion.AGENDADA, "request_id": 100}
    )
    assert len(result) == 1
    assert result[0].id == a1.pk


@pytest.mark.django_db
def test_listar_filtro_consultor_id():
    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=42, is_leader=True
    )
    AtencionFactory()
    result = AtencionRepository.listar({"consultor_id": 42})
    assert len(result) == 1
    assert result[0].id == atencion.pk


@pytest.mark.django_db
def test_programar_finalizar_anular():
    atencion = AtencionFactory()
    inicio, fin = _fechas_programacion()
    dto_prog = AtencionRepository.programar(
        ProgramarAtencionInputDTO(
            atencion_id=atencion.pk,
            fecha_programada=inicio,
            fecha_fin=fin,
            programado_por_id=1,
        ),
    )
    assert dto_prog.fecha_programada == inicio

    dto_fin = AtencionRepository.finalizar(
        FinalizarAtencionInputDTO(
            atencion_id=atencion.pk,
            estado=EstadoAtencion.FINALIZADA,
            notas_finales="Notas finales válidas con más de veinte caracteres.",
            consultor_id=1,
        ),
    )
    assert dto_fin.estado == EstadoAtencion.FINALIZADA
    assert dto_fin.fecha_cierre is not None

    otra = AtencionFactory()
    dto_anul = AtencionRepository.anular(
        AnularAtencionInputDTO(
            atencion_id=otra.pk,
            motivo_anulacion="Motivo de anulación válido para prueba.",
            coordinador_id=1,
        ),
    )
    assert dto_anul.estado == EstadoAtencion.ANULADA


@pytest.mark.django_db
def test_buscar_cruces_detecta_solapamiento():
    inicio, fin = _fechas_programacion()
    a1 = AtencionFactory(scheduled_date=inicio, closing_date=fin)
    AtentionConsultant.objects.create(atention=a1, consultant_id=7, is_leader=True)
    cruces = AtencionRepository.buscar_cruces([7], inicio, fin)
    assert len(cruces) >= 1


@pytest.mark.django_db
def test_buscar_cruces_excluye_atencion():
    inicio, fin = _fechas_programacion()
    a1 = AtencionFactory(scheduled_date=inicio, closing_date=fin)
    AtentionConsultant.objects.create(atention=a1, consultant_id=7, is_leader=True)
    cruces = AtencionRepository.buscar_cruces(
        [7], inicio, fin, excluir_atencion_id=a1.pk
    )
    assert cruces == []
