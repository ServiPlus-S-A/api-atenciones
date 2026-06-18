import pytest
from unittest.mock import patch
from uuid import uuid4

from atenciones.constants import EstadoAtencion
from atenciones.integrations.parametrizacion_client import ConsultorInfo
from atenciones.integrations.solicitudes_client import SolicitudInfo
from atenciones.models import AuditLog, Atencion


@pytest.mark.django_db(transaction=True)
@patch("atenciones.services.atencion_service.solicitudes_client.obtener_solicitud")
@patch("atenciones.services.atencion_service.parametrizacion_client.obtener_consultor")
@patch("atenciones.services.atencion_service.enviar_notificacion_programacion.delay")
def test_crear_atencion_transaccion_view_serializer_service_repository_output_serializer(
    mock_delay,
    mock_param_get,
    mock_solicitudes_get,
    api_client_coordinador,
):
    solicitud_id = str(uuid4())
    consultor_id = str(uuid4())
    mensaje = "Mensaje preliminar de prueba."

    mock_solicitudes_get.return_value = SolicitudInfo(
        id=solicitud_id,
        estado="Pendiente",
        consultor_ids=[consultor_id],
    )
    mock_param_get.return_value = ConsultorInfo(
        id=consultor_id,
        disponible=True,
        aptitudes=[],
    )

    payload = {
        "solicitud_id": solicitud_id,
        "consultor_ids": [consultor_id],
        "mensaje_preliminar": mensaje,
    }

    response = api_client_coordinador.post("/api/atenciones/", payload, format="json")
    assert response.status_code == 201
    data = response.json()

    assert isinstance(data["id"], int)
    assert data["status"] == EstadoAtencion.AGENDADA
    assert data["request_id"] == solicitud_id
    assert data["scheduled_date"] is None
    assert data["closing_date"] is None
    assert data["consultants"][0]["id"] == consultor_id
    assert data["consultants"][0]["is_leader"] is True
    assert data["consultants"][0]["role"] == "CONSULTOR"

    atencion = Atencion.objects.get(pk=data["id"])
    assert atencion.request_id == solicitud_id
    assert AuditLog.objects.filter(operation="CREAR", atention_id=atencion.pk).exists()

    mock_delay.assert_called_once()
