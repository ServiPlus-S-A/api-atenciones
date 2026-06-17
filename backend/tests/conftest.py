import pytest
from django.core.cache import caches
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APIClient
from typing import Any, cast

from atenciones.constants import Rol


def _client_with_rol(rol: str) -> APIClient:
    user = User.objects.create_user(
        username=f"user_{rol.lower()}", password="testpass123"
    )
    setattr(user, "rol", rol or "Cliente")
    client: Any = APIClient()
    client.force_authenticate(user=user)
    setattr(client, "test_user", user or f"Usuario con rol {rol}")
    return cast(APIClient, client)


@pytest.fixture
def api_client_consultor(db):
    return _client_with_rol(Rol.CONSULTOR)


@pytest.fixture
def api_client_coordinador(db):
    return _client_with_rol(Rol.COORDINADOR)


@pytest.fixture
def api_client_cliente(db):
    return _client_with_rol(Rol.CLIENTE)


@pytest.fixture(autouse=True)
def isolated_test_cache(monkeypatch):
    """Usa LocMemCache aunque el entorno cargue variables de Redis."""
    cache_settings = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests",
        }
    }
    with override_settings(CACHES=cache_settings):
        caches.close_all()
        test_cache = caches["default"]
        monkeypatch.setattr("atenciones.services.atencion_service.cache", test_cache)
        monkeypatch.setattr(
            "atenciones.services.atencion_cache_service.cache", test_cache
        )
        monkeypatch.setattr("atenciones.views.health_view.cache", test_cache)
        monkeypatch.setattr("atenciones.tasks.notificacion_tasks.cache", test_cache)
        yield test_cache
        test_cache.clear()
        caches.close_all()
