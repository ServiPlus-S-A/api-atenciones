from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from django.core.cache import cache

from atenciones.constants import EstadoAtencion
from atenciones.exceptions.custom_exceptions import (
    AnticipacionInsuficiente,
    ConsultorNoDisponible,
    SolicitudNoAutorizada,
    TransicionInvalidaException,
)
from atenciones.integrations.solicitudes_client import SolicitudInfo
from atenciones.models import AtentionConsultant
from atenciones.services.atencion_service import AtencionService
from tests.factories.atencion_factory import AtencionFactory, AtencionFinalizadaFactory


def _fechas_programacion():
    inicio = datetime.now(timezone.utc) + timedelta(days=3)
    inicio = inicio.replace(minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(hours=1)
    return inicio, fin


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_crear_valida_solicitud_pendiente(mock_param, mock_sol, api_client_coordinador):
    mock_sol.return_value = SolicitudInfo(id=1, estado="Pendiente", consultor_ids=[1])
    from atenciones.integrations.parametrizacion_client import ConsultorInfo

    mock_param.return_value = ConsultorInfo(id=1, disponible=True, aptitudes=[])
    user = api_client_coordinador.test_user
    dto = AtencionService.crear(
        {
            "solicitud_id": 1,
            "consultor_ids": [1],
            "mensaje_preliminar": "Mensaje preliminar de prueba.",
        },
        user,
    )
    assert dto.estado == EstadoAtencion.AGENDADA


@pytest.mark.django_db
def test_transicion_invalida_finalizada_a_anulada(api_client_coordinador):
    atencion = AtencionFinalizadaFactory()
    user = api_client_coordinador.test_user
    with pytest.raises(TransicionInvalidaException):
        AtencionService.anular(
            atencion.pk,
            {"motivo_anulacion": "Motivo válido de anulación."},
            user,
        )


@pytest.mark.django_db
def test_programar_falla_menos_24h(api_client_coordinador):
    from datetime import datetime, timedelta, timezone

    atencion = AtencionFactory()
    user = api_client_coordinador.test_user
    inicio = datetime.now(timezone.utc) + timedelta(hours=2)
    fin = inicio + timedelta(hours=1)
    with pytest.raises(AnticipacionInsuficiente):
        AtencionService.programar(
            atencion.pk,
            {"fecha_programada": inicio, "fecha_fin": fin},
            user,
        )


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.enviar_notificacion_programacion.delay")
@patch("atenciones.services.atencion_service.validar_transicion_estado")
def test_programar_ok(mock_transicion, mock_delay, api_client_coordinador):
    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=1, is_leader=True
    )
    inicio, fin = _fechas_programacion()
    user = api_client_coordinador.test_user
    dto = AtencionService.programar(
        atencion.pk,
        {"fecha_programada": inicio, "fecha_fin": fin},
        user,
    )
    assert dto.fecha_programada == inicio
    mock_delay.assert_called_once()


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
def test_crear_rechaza_solicitud_no_pendiente(mock_sol, api_client_coordinador):
    mock_sol.return_value = SolicitudInfo(id=1, estado="Cerrada", consultor_ids=[1])
    user = api_client_coordinador.test_user
    with pytest.raises(SolicitudNoAutorizada):
        AtencionService.crear(
            {
                "solicitud_id": 1,
                "consultor_ids": [1],
                "mensaje_preliminar": "Mensaje preliminar válido.",
            },
            user,
        )


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
def test_crear_rechaza_consultor_no_disponible(
    mock_param, mock_sol, api_client_coordinador
):
    mock_sol.return_value = SolicitudInfo(id=1, estado="Pendiente", consultor_ids=[1])
    from atenciones.integrations.parametrizacion_client import ConsultorInfo

    mock_param.return_value = ConsultorInfo(id=1, disponible=False, aptitudes=[])
    user = api_client_coordinador.test_user
    with pytest.raises(ConsultorNoDisponible):
        AtencionService.crear(
            {
                "solicitud_id": 1,
                "consultor_ids": [1],
                "mensaje_preliminar": "Mensaje preliminar válido.",
            },
            user,
        )


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.enviar_email_cliente.delay")
def test_finalizar_ok(mock_delay, api_client_consultor):
    atencion = AtencionFactory()
    user = api_client_consultor.test_user
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )
    dto = AtencionService.finalizar(
        atencion.pk,
        {"notas_finales": "Notas finales válidas con más de veinte caracteres."},
        user,
    )
    assert dto.estado == EstadoAtencion.FINALIZADA
    mock_delay.assert_called_once()


@pytest.mark.django_db
@patch("atenciones.services.atencion_service.enviar_email_anulacion.delay")
def test_anular_ok(mock_delay, api_client_coordinador):
    atencion = AtencionFactory()
    user = api_client_coordinador.test_user
    dto = AtencionService.anular(
        atencion.pk,
        {"motivo_anulacion": "Motivo de anulación válido para prueba."},
        user,
    )
    assert dto.estado == EstadoAtencion.ANULADA
    mock_delay.assert_called_once()


@pytest.mark.django_db
def test_detalle(api_client_coordinador):
    atencion = AtencionFactory()
    dto = AtencionService.detalle(atencion.pk)
    assert dto.id == atencion.pk


@pytest.mark.django_db
def test_listar_usa_cache_sin_filtros(api_client_coordinador):
    AtencionFactory()
    user = api_client_coordinador.test_user
    cache.clear()
    first = AtencionService.listar_para_usuario(user, {})
    second = AtencionService.listar_para_usuario(user, {})
    assert first == second


@pytest.mark.django_db
def test_listar_consultor_excluye_anuladas_y_filtra_por_consultor(api_client_consultor):
    user = api_client_consultor.test_user
    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion, consultant_id=user.id, is_leader=True
    )
    from tests.factories.atencion_factory import AtencionAnuladaFactory

    otra = AtencionAnuladaFactory()
    AtentionConsultant.objects.create(
        atention=otra, consultant_id=user.id, is_leader=True
    )
    result = AtencionService.listar_para_usuario(user, {})
    assert all(d.estado != EstadoAtencion.ANULADA for d in result)
