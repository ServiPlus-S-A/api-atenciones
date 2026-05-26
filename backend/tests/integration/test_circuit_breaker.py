from unittest.mock import patch

import pytest

from atenciones.exceptions.custom_exceptions import ServicioExternoNoDisponible
from atenciones.integrations.solicitudes_client import SolicitudInfo
from atenciones.services.atencion_service import AtencionService


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@patch("atenciones.services.atencion_service.solicitudes_client.get")
def test_fallback_retorna_503_controlado(mock_get, api_client_coordinador):
    mock_get.return_value = SolicitudInfo(id=1, estado="DESCONOCIDO", consultor_ids=[])
    user = api_client_coordinador.test_user
    with pytest.raises(ServicioExternoNoDisponible):
        AtencionService.crear(
            {
                "solicitud_id": 1,
                "consultor_ids": [1],
                "mensaje_preliminar": "Mensaje preliminar de prueba.",
            },
            user,
        )
