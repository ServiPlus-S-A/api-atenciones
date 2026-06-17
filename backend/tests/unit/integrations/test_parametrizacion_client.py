from unittest.mock import Mock, patch

import pytest
import requests
from django.test import override_settings

from atenciones.integrations.parametrizacion_client import (
    ConsultorInfoDTO,
    ParametrizacionClient,
)


@pytest.mark.unit
@override_settings(
    PARAMETRIZACION_MOCK_RESPONSES={
        "consultor-1": ConsultorInfoDTO(
            id="consultor-1",
            disponible=True,
            aptitudes=("redes",),
            nombre="Ada Lovelace",
        )
    }
)
def test_obtener_consultor_usa_stub_configurado():
    info = ParametrizacionClient().obtener_consultor("consultor-1")

    assert info is not None
    assert info.id == "consultor-1"
    assert info.disponible is True
    assert info.aptitudes == ("redes",)
    assert info.nombre == "Ada Lovelace"


@pytest.mark.unit
@override_settings(PARAMETRIZACION_MOCK_RESPONSES=None)
@patch("atenciones.integrations.base_client.requests.get")
def test_obtener_consultor_desde_http(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.raise_for_status = lambda: None
    mock_get.return_value.json.return_value = {
        "id": "consultor-2",
        "disponible": True,
        "aptitudes": ["redes", "soporte"],
        "nombre": "Grace Hopper",
        "role": "CONSULTOR",
    }

    info = ParametrizacionClient().obtener_consultor("consultor-2")

    assert info is not None
    assert info.id == "consultor-2"
    assert info.aptitudes == ("redes", "soporte")
    assert info.nombre == "Grace Hopper"


@pytest.mark.unit
@override_settings(PARAMETRIZACION_MOCK_RESPONSES=None)
@patch("atenciones.integrations.base_client.requests.get")
def test_obtener_consultor_404_retorna_none(mock_get):
    response = Mock(status_code=404)
    error = requests.HTTPError(response=response)
    mock_get.return_value.raise_for_status.side_effect = error

    assert ParametrizacionClient().obtener_consultor("no-existe") is None


@pytest.mark.unit
@override_settings(PARAMETRIZACION_MOCK_RESPONSES=None)
@patch(
    "atenciones.integrations.base_client.requests.get",
    side_effect=requests.RequestException("down"),
)
def test_get_fallback_consultor_no_disponible(mock_get):
    info = ParametrizacionClient().get("consultor-caido")

    assert info.id == "consultor-caido"
    assert info.disponible is False
    assert info.aptitudes == ()
