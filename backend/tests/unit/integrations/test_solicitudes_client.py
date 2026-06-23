from unittest.mock import patch

import pytest
import requests
from django.test import override_settings

from atenciones.integrations.solicitudes_client import SolicitudesClient


@pytest.mark.unit
@override_settings(SOLICITUDES_MOCK_RESPONSES=None)
@patch("atenciones.integrations.base_client.requests.get")
def test_get_retorna_info(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.raise_for_status = lambda: None
    mock_get.return_value.json.return_value = {
        "id": 5,
        "estado": "Pendiente",
        "consultor_ids": [1, 2],
    }
    info = SolicitudesClient().get(5)
    assert info.estado == "Pendiente"
    assert info.consultor_ids == [1, 2]


@pytest.mark.unit
@override_settings(SOLICITUDES_MOCK_RESPONSES=None)
@patch(
    "atenciones.integrations.base_client.requests.get",
    side_effect=requests.RequestException("down"),
)
def test_get_fallback_desconocido(mock_get):
    info = SolicitudesClient().get(9)
    assert info.estado == "DESCONOCIDO"


@pytest.mark.unit
@override_settings(SOLICITUDES_MOCK_ENABLED=False)
@patch(
    "atenciones.integrations.base_client.requests.get",
    side_effect=requests.RequestException("down"),
)
def test_get_solicitud_circuit_abre_tras_5_fallos_consecutivos(mock_get):
    client = SolicitudesClient()

    for _ in range(5):
        assert client.get_solicitud("sol-1") is None

    assert client.get_solicitud("sol-1") is None
    assert mock_get.call_count == 5
    
