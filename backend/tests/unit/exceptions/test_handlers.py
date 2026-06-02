import pytest
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.test import APIRequestFactory

from atenciones.exceptions.custom_exceptions import AtencionNoEncontrada
from atenciones.exceptions.handlers import custom_exception_handler
from atenciones.security.secure_logger import SecureLogger


@pytest.mark.unit
def test_custom_exception_handler_base_exception_logs_and_formats(monkeypatch):
    called = {}

    def fake_registrar_fallo(*args, **kwargs):
        called["kwargs"] = kwargs

    monkeypatch.setattr(SecureLogger, "registrar_fallo", staticmethod(fake_registrar_fallo))
    request = APIRequestFactory().get("/api/atenciones/")
    request.user = object()

    response = custom_exception_handler(AtencionNoEncontrada(), {"request": request})

    assert response.status_code == 404
    assert response.data["error"] == "atencion_no_encontrada"
    assert "message" in response.data
    assert called["kwargs"]["operation"] == "exception"


@pytest.mark.unit
def test_custom_exception_handler_validation_error_fields():
    request = APIRequestFactory().get("/api/atenciones/")
    exc = ValidationError({"field": ["invalid"]})

    response = custom_exception_handler(exc, {"request": request})

    assert response.status_code == 400
    assert response.data["error"] == "validation_error"
    assert "field_errors" in response.data


@pytest.mark.unit
def test_custom_exception_handler_logs_default_exception(monkeypatch):
    called = {"count": 0}

    def fake_registrar_fallo(*args, **kwargs):
        called["count"] += 1

    monkeypatch.setattr(SecureLogger, "registrar_fallo", staticmethod(fake_registrar_fallo))
    request = APIRequestFactory().get("/api/atenciones/")

    response = custom_exception_handler(NotAuthenticated(), {"request": request})

    assert response.status_code == 401
    assert called["count"] == 1
