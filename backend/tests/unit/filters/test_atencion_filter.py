import pytest

from atenciones.exceptions.custom_exceptions import ParametrosFiltroInvalidos
from atenciones.filters.atencion_filter import AtencionFilterForm


def test_parse_query_params_returns_cleaned_data():
    data = AtencionFilterForm.parse_query_params({"estado": "AGENDADA", "solicitud_id": "42"})
    assert data["estado"] == "AGENDADA"
    assert data["solicitud_id"] == 42


def test_parse_query_params_raises_on_invalid_estado():
    with pytest.raises(ParametrosFiltroInvalidos) as exc_info:
        AtencionFilterForm.parse_query_params({"estado": "NO_EXISTE"})

    assert "estado" in exc_info.value.field_errors
