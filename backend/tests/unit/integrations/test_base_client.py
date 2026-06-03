from unittest.mock import MagicMock, patch

import pytest
import requests

from atenciones.integrations.base_client import BaseIntegrationClient, CircuitState, circuit_breaker


@pytest.mark.unit
def test_circuit_breaker_abre_tras_umbral():
    state = CircuitState(threshold=2, recovery_timeout=60.0)

    @circuit_breaker(state)
    def falla():
        raise requests.RequestException("error")

    with pytest.raises(requests.RequestException):
        falla()
    with pytest.raises(requests.RequestException):
        falla()
    with pytest.raises(requests.RequestException, match="Circuit breaker abierto"):
        falla()


@pytest.mark.unit
@patch("atenciones.integrations.base_client.requests.get")
def test_base_client_get_ok(mock_get):
    mock_get.return_value = MagicMock(status_code=200, raise_for_status=MagicMock())
    mock_get.return_value.json.return_value = {"id": 1}
    client = BaseIntegrationClient("http://example.com")
    assert client._get("/ruta") == {"id": 1}
    assert client.circuit.failure_count == 0
