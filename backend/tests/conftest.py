
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from typing import Any, cast

from atenciones.constants import Rol


def _client_with_rol(rol: str) -> APIClient:
    user = User.objects.create_user(username=f"user_{rol.lower()}", password="testpass123")
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
