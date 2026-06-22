import pytest
import time
from unittest.mock import patch
from django.urls import reverse
from django.db import Error as DBError

from atenciones.models import NotaSeguimiento
from tests.factories import (
    AtencionFactory,
    AtencionFinalizadaFactory,
    AtencionAnuladaFactory,
)


@pytest.mark.django_db
@pytest.mark.integration
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_get_detalle_coordinador_retorna_200_con_datos_completos(
    mock_get_contacto,
    mock_get_solicitud,
    client,
):
    atencion = AtencionFactory()

    mock_get_solicitud.return_value = {
        "id": str(atencion.request_id),
        "estado": "PENDIENTE",
        "client_id": "client-123",
        "nombre": f"Solicitud #{atencion.request_id}",
    }
    mock_get_contacto.return_value = {
        "nombre_completo": "Carlos Alberto Ramírez Pérez",
        "telefono": "3000000000",
        "correo_electronico": "carlos@test.com",
    }

    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="1",
        content="Diagnostico inicial",
    )
    time.sleep(0.01)
    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="2",
        content="Nota intermedia",
    )

    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == atencion.id
    assert data["solicitud_nombre"] == f"Solicitud #{atencion.request_id}"
    assert data["cliente_nombre"] == "Carlos Alberto Ramírez Pérez"
    assert data["diagnostico_inicial"] == "Diagnostico inicial"
    assert len(data["notas"]) == 2
    assert data["notas"][0]["content"] == "Nota intermedia"
    assert data["notas"][0]["created_by"] == "2"
    assert data["mensaje_bitacora"] is None
    assert data["acciones_disponibles"] == {
        "editar": True,
        "finalizar": True,
        "cancelar": True,
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_get_detalle_rol_consultor_retorna_403(client):
    atencion = AtencionFactory()
    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(
        url, HTTP_X_USER_ID="consultor-1", HTTP_X_USER_ROLE="CONSULTOR"
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "No tiene permisos para consultar el detalle de esta atención."
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_get_detalle_rol_cliente_retorna_403(client):
    atencion = AtencionFactory()
    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(url, HTTP_X_USER_ID="cliente-1", HTTP_X_USER_ROLE="CLIENTE")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "No tiene permisos para consultar el detalle de esta atención."
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_get_detalle_sin_headers_retorna_401(client):
    atencion = AtencionFactory()
    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(url)
    assert response.status_code == 401
    assert response.json() == {"detail": "Cabeceras de autenticación ausentes."}


@pytest.mark.django_db
@pytest.mark.integration
def test_get_detalle_atencion_inexistente_retorna_404(client):
    url = reverse("atencion-detail", kwargs={"pk": 99999})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Atención no encontrada."}


@pytest.mark.django_db
@pytest.mark.integration
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_get_detalle_bitacora_vacia_retorna_mensaje(
    mock_get_contacto, mock_get_solicitud, client
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["notas"] == []
    assert data["diagnostico_inicial"] is None
    assert (
        data["mensaje_bitacora"]
        == "Esta atención no tiene notas de seguimiento registradas."
    )


@pytest.mark.django_db
@pytest.mark.integration
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_get_detalle_servicio_externo_caido_retorna_200_degradado(
    mock_get_contacto,
    mock_get_solicitud,
    client,
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.side_effect = Exception("Service unavailable")

    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["solicitud_nombre"] == "S"
    assert data["cliente_nombre"] is None


@pytest.mark.django_db
@pytest.mark.integration
@patch("atenciones.services.atencion_detalle_service.AtencionRepository.obtener_por_id")
def test_get_detalle_fallo_bd_retorna_503(mock_get_by_id, client):
    mock_get_by_id.side_effect = DBError("Simulated DB connection issue")

    url = reverse("atencion-detail", kwargs={"pk": 1})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "No fue posible cargar el detalle de la atención. Intente de nuevo más tarde."
    }


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    "estado,acciones_esperadas",
    [
        ("AGENDADA", {"editar": True, "finalizar": True, "cancelar": True}),
        ("FINALIZADA", {"editar": False, "finalizar": False, "cancelar": False}),
        ("ANULADA", {"editar": False, "finalizar": False, "cancelar": False}),
    ],
)
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_get_detalle_acciones_disponibles_segun_estado(
    mock_get_contacto,
    mock_get_solicitud,
    estado,
    acciones_esperadas,
    client,
):
    if estado == "FINALIZADA":
        atencion = AtencionFinalizadaFactory()
    elif estado == "ANULADA":
        atencion = AtencionAnuladaFactory()
    else:
        atencion = AtencionFactory()

    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["acciones_disponibles"] == acciones_esperadas


@pytest.mark.django_db
@pytest.mark.integration
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_get_detalle_segunda_llamada_usa_cache(
    mock_get_contacto, mock_get_solicitud, client
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    url = reverse("atencion-detail", kwargs={"pk": atencion.id})

    # Call 1
    response1 = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )
    assert response1.status_code == 200

    # Call 2
    response2 = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )
    assert response2.status_code == 200

    # Verify clients are only called once because it has cache hit
    assert mock_get_solicitud.call_count == 1
    assert mock_get_contacto.call_count == 1


@pytest.mark.django_db
@pytest.mark.integration
@patch("atenciones.services.atencion_detalle_service.solicitudes_client.get_solicitud")
@patch(
    "atenciones.services.atencion_detalle_service.clientes_client.get_contacto_cliente"
)
def test_get_detalle_diagnostico_inicial_es_primer_nota_no_la_ultima(
    mock_get_contacto,
    mock_get_solicitud,
    client,
):
    atencion = AtencionFactory()
    mock_get_solicitud.return_value = {"nombre": "S", "client_id": "C"}
    mock_get_contacto.return_value = {"nombre_completo": "Carlos"}

    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="1",
        content="Primer Nota (Antigua)",
    )
    time.sleep(0.01)
    NotaSeguimiento.objects.create(
        atention=atencion,
        consultant_id="2",
        content="Ultima Nota (Reciente)",
    )

    url = reverse("atencion-detail", kwargs={"pk": atencion.id})
    response = client.get(
        url, HTTP_X_USER_ID="coord-uuid-099", HTTP_X_USER_ROLE="COORDINADOR"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["diagnostico_inicial"] == "Primer Nota (Antigua)"
    assert data["notas"][0]["content"] == "Ultima Nota (Reciente)"
    assert data["notas"][1]["content"] == "Primer Nota (Antigua)"
