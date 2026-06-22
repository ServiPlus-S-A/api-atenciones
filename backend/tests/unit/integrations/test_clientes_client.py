from unittest.mock import patch

import pytest
import requests
from django.test import override_settings

from atenciones.integrations.clientes_client import ClientesClient


@pytest.mark.unit
@override_settings(CLIENTES_MOCK_ENABLED=False)
@patch(
    "atenciones.integrations.base_client.requests.get",
    side_effect=requests.RequestException("down"),
)
def test_get_contacto_cliente_circuit_abre_tras_5_fallos_consecutivos(mock_get):
    client = ClientesClient()

    for _ in range(5):
        assert client.get_contacto_cliente("client-1") is None

    assert client.get_contacto_cliente("client-1") is None
    assert mock_get.call_count == 5
