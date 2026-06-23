import pytest
import time
from unittest.mock import patch
from django.db import Error as DBError

from atenciones.constants import EstadoAtencion
from atenciones.exceptions import (
    AtencionDoesNotExist,
    AtencionPermissionDenied,
    AtencionServiceUnavailableError,
)
from atenciones.integrations.parametrizacion_client import ConsultorInfoDTO
from atenciones.models import AtentionConsultant, NotaSeguimiento
from atenciones.services.atencion_detalle_service import AtencionDetalleService
from atenciones.repositories.atencion_repository import AtencionRepository
from tests.factories import AtencionFactory


@pytest.fixture(autouse=True)
def patch_cache_in_detalle_service(monkeypatch, isolated_test_cache):
    monkeypatch.setattr(
        "atenciones.services.atencion_detalle_service.cache", isolated_test_cache
    )
    yield isolated_test_cache
    isolated_test_cache.clear()


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_obtener_detalle_exitoso_con_notes(mock_get_contacto, mock_get_solicitud):
    atencion = AtencionFactory(status=EstadoAtencion.AGENDADA)

    mock_get_solicitud.return_value = {
        "id": str(atencion.request_id),
        "estado": "PENDIENTE",
        "client_id": "client-uuid-1",
        "nombre": "Solicitud Test",
    }
    mock_get_contacto.return_value = {
        "nombre_completo": "Carlos Perez",
        "telefono": "3000000000",
        "correo_electronico": "carlos@test.com",
    }

    n1 = NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="1",
        content="Nota antigua",
    )
    time.sleep(0.01)
    n2 = NotaSeguimiento.objects.create(
        atention=atencion, consultant_id="2", content="Nota nueva"
    )

    dto = AtencionDetalleService.obtener_detalle_coordinador(atencion.id)

    assert dto.id == atencion.id
    assert dto.diagnostico_inicial == "Nota antigua"
    assert len(dto.notas) == 2
    assert dto.notas[0].id == n2.id  # Ordered DESC by default
    assert dto.notas[1].id == n1.id
    assert dto.mensaje_bitacora is None
    assert dto.solicitud_nombre == "Solicitud Test"
    assert dto.cliente_nombre == "Carlos Perez"
    assert dto.acciones_disponibles == {
        "editar": True,
        "finalizar": True,
        "cancelar": True,
    }


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_diagnostico_inicial_es_la_nota_mas_antigua(
    mock_get_contacto, mock_get_solicitud
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    NotaSeguimiento.objects.create(
        atention=atencion, consultant_id="1", content="Nota 1"
    )
    time.sleep(0.01)
    NotaSeguimiento.objects.create(
        atention=atencion, consultant_id="2", content="Nota 2"
    )
    time.sleep(0.01)
    NotaSeguimiento.objects.create(
        atention=atencion, consultant_id="3", content="Nota 3"
    )

    dto = AtencionDetalleService.obtener_detalle_coordinador(atencion.id)
    assert dto.diagnostico_inicial == "Nota 1"


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_nota_inicial_tambien_aparece_en_bitacora_completa(
    mock_get_contacto, mock_get_solicitud
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    NotaSeguimiento.objects.create(
        atention=atencion, consultant_id="1", content="Nota Inicial"
    )

    dto = AtencionDetalleService.obtener_detalle_coordinador(atencion.id)
    assert dto.diagnostico_inicial == "Nota Inicial"
    assert len(dto.notas) == 1
    assert dto.notas[0].content == "Nota Inicial"


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_atencion_sin_notas_diagnostico_inicial_none(
    mock_get_contacto, mock_get_solicitud
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    dto = AtencionDetalleService.obtener_detalle_coordinador(atencion.id)
    assert dto.diagnostico_inicial is None
    assert dto.notas == []
    assert (
        dto.mensaje_bitacora
        == "Esta atención no tiene notas de seguimiento registradas."
    )


@pytest.mark.unit
def test_bitacora_vacia_genera_mensaje():
    res = AtencionDetalleService._mensaje_bitacora_vacia([])
    assert res == "Esta atención no tiene notas de seguimiento registradas."


@pytest.mark.unit
def test_bitacora_con_notas_no_genera_mensaje():
    res = AtencionDetalleService._mensaje_bitacora_vacia([1])
    assert res is None


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_solicitudes_client_circuit_abierto_degrada_sin_fallar(
    mock_get_contacto,
    mock_get_solicitud,
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = None  # open circuit

    dto = AtencionDetalleService.obtener_detalle_coordinador(atencion.id)
    assert dto.solicitud_nombre is None
    assert dto.cliente_nombre is None


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_clientes_client_circuit_abierto_degrada_sin_fallar(
    mock_get_contacto, mock_get_solicitud
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = None  # open circuit

    dto = AtencionDetalleService.obtener_detalle_coordinador(atencion.id)
    assert dto.solicitud_nombre == "S"
    assert dto.cliente_nombre is None


@pytest.mark.django_db
@pytest.mark.unit
def test_atencion_inexistente_lanza_atencion_does_not_exist():
    with pytest.raises(AtencionDoesNotExist):
        AtencionDetalleService.obtener_detalle_coordinador(9999)


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.AtencionRepository.obtener_por_id")
def test_error_de_bd_lanza_atencion_service_unavailable(mock_get_by_id):
    mock_get_by_id.side_effect = DBError("Simulated DB connection issue")
    with pytest.raises(AtencionServiceUnavailableError):
        AtencionDetalleService.obtener_detalle_coordinador(1)


@pytest.mark.unit
@pytest.mark.parametrize(
    "status_atencion,esperado",
    [
        ("AGENDADA", {"editar": True, "finalizar": True, "cancelar": True}),
        ("FINALIZADA", {"editar": False, "finalizar": False, "cancelar": False}),
        ("ANULADA", {"editar": False, "finalizar": False, "cancelar": False}),
    ],
)
def test_acciones_disponibles_por_estado(status_atencion, esperado):
    res = AtencionDetalleService._calcular_acciones_disponibles(status_atencion)
    assert res == esperado


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_cache_hit_evita_llamadas_a_repos_y_clientes(
    mock_get_contacto, mock_get_solicitud
):
    atencion = AtencionFactory()
    real_dto = AtencionRepository.obtener_por_id(atencion.id)
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    with patch(
        "atenciones.services.atencion_detalle_service.AtencionRepository.obtener_por_id"
    ) as mock_get_by_id:
        mock_get_by_id.return_value = real_dto

        # First call
        AtencionDetalleService.obtener_detalle_coordinador(atencion.id)

        # Second call should hit cache
        AtencionDetalleService.obtener_detalle_coordinador(atencion.id)

        # Repos and client should only be called once
        assert mock_get_by_id.call_count == 1
        assert mock_get_solicitud.call_count == 1
        assert mock_get_contacto.call_count == 1


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_respuesta_degradada_no_se_cachea(mock_get_contacto, mock_get_solicitud):
    atencion = AtencionFactory()
    real_dto = AtencionRepository.obtener_por_id(atencion.id)
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = None  # Degraded response

    with patch(
        "atenciones.services.atencion_detalle_service.AtencionRepository.obtener_por_id"
    ) as mock_get_by_id:
        mock_get_by_id.return_value = real_dto

        # First call
        AtencionDetalleService.obtener_detalle_coordinador(atencion.id)

        # Second call
        AtencionDetalleService.obtener_detalle_coordinador(atencion.id)

        # Should NOT hit cache because of degradation
        assert mock_get_by_id.call_count == 2
        assert mock_get_solicitud.call_count == 2
        assert mock_get_contacto.call_count == 2


@pytest.mark.django_db
@pytest.mark.unit
@patch(
    "atenciones.services.atencion_detalle_service.parametrizacion_client.obtener_consultor"
)
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
def test_obtener_detalle_cliente_exitoso(
    mock_get_solicitud,
    mock_obtener_consultor,
):
    atencion = AtencionFactory()
    AtentionConsultant.objects.create(
        atention=atencion,
        consultant_id="consultor-1",
        is_leader=True,
    )
    mock_get_solicitud.return_value = {
        "id": str(atencion.request_id),
        "client_id": "cliente-123",
        "nombre": "Solicitud Test",
    }
    mock_obtener_consultor.return_value = ConsultorInfoDTO(
        id="consultor-1",
        disponible=True,
        nombre="Ana Consultora",
    )
    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="consultor-1",
        content="Diagnostico inicial",
    )

    dto = AtencionDetalleService.obtener_detalle_cliente(atencion.id, "cliente-123")

    assert dto.id == atencion.id
    assert dto.request_id == str(atencion.request_id)
    assert dto.solicitud_nombre == "Solicitud Test"
    assert dto.consultores[0].name == "Ana Consultora"
    assert dto.diagnostico_inicial == "Diagnostico inicial"
    assert len(dto.notas) == 1
    assert dto.mensaje_bitacora is None


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
def test_obtener_detalle_cliente_no_asociado_lanza_permiso(mock_get_solicitud):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {
        "id": str(atencion.request_id),
        "client_id": "otro-cliente",
        "nombre": "Solicitud Test",
    }

    with pytest.raises(AtencionPermissionDenied):
        AtencionDetalleService.obtener_detalle_cliente(atencion.id, "cliente-123")


@pytest.mark.django_db
@pytest.mark.unit
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
def test_obtener_detalle_cliente_solicitudes_no_disponible_lanza_503(
    mock_get_solicitud,
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = None

    with pytest.raises(AtencionServiceUnavailableError):
        AtencionDetalleService.obtener_detalle_cliente(atencion.id, "cliente-123")
