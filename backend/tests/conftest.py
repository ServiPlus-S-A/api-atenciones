import os

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from atenciones.constants import Rol

os.environ.setdefault("DATABASE_URL", "sqlite:///test_db.sqlite3")


def _client_with_rol(rol: str) -> APIClient:
    user = User.objects.create_user(username=f"user_{rol.lower()}", password="testpass123")
    user.rol = rol
    client = APIClient()
    client.force_authenticate(user=user)
    client.test_user = user
    return client


@pytest.fixture
def api_client_consultor(db):
    return _client_with_rol(Rol.CONSULTOR)


@pytest.fixture
def api_client_coordinador(db):
    return _client_with_rol(Rol.COORDINADOR)


@pytest.fixture
def api_client_cliente(db):
    return _client_with_rol(Rol.CLIENTE)
