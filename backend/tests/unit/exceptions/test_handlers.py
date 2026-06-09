import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from atenciones.exceptions.custom_exceptions import (
    AtencionNoEncontrada,
    BaseAtencionException,
    ParametrosFiltroInvalidos,
)
from atenciones.exceptions.handlers import _build_response, custom_exception_handler


@pytest.mark.unit
def test_build_response_incluye_field_errors():
    response = _build_response("code", "msg", 400, field_errors={"estado": ["inválido"]})
    assert response.status_code == 400
    assert response.data["field_errors"]["estado"] == ["inválido"]


@pytest.mark.unit
def test_handler_base_atencion_exception():
    request = APIRequestFactory().get("/")
    request.user = type("U", (), {"id": 1})()
    exc = AtencionNoEncontrada()
    response = custom_exception_handler(exc, {"request": request, "view": APIView()})
    assert response.status_code == 404
    assert response.data["error"] == "atencion_no_encontrada"


@pytest.mark.unit
def test_handler_parametros_filtro_invalidos():
    request = APIRequestFactory().get("/")
    request.user = type("U", (), {"id": 1})()
    exc = ParametrosFiltroInvalidos(field_errors={"estado": ["Seleccione una opción válida."]})
    response = custom_exception_handler(exc, {"request": request, "view": APIView()})
    assert response.status_code == 400
    assert "field_errors" in response.data


@pytest.mark.unit
def test_handler_validation_error():
    exc = ValidationError({"page": ["Enter a valid integer."]})
    response = custom_exception_handler(exc, {"request": None, "view": APIView()})
    assert response.status_code == 400
    assert response.data["error"] == "validation_error"


@pytest.mark.unit
def test_handler_validation_error_lista():
    exc = ValidationError(["error general"])
    response = custom_exception_handler(exc, {"request": None, "view": APIView()})
    assert response.data["field_errors"]["non_field_errors"] == ["error general"]


@pytest.mark.unit
def test_base_exception_con_codigo_personalizado():
    exc = BaseAtencionException(detail="detalle", code="mi_codigo")
    assert exc.default_code == "mi_codigo"
