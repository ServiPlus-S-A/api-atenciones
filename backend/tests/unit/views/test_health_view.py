from unittest.mock import patch

import pytest

from atenciones.views.health_view import HealthView


@pytest.mark.unit
def test_health_todos_ok():
    view = HealthView()
    with (
        patch.object(HealthView, "_check_db", return_value=True),
        patch.object(HealthView, "_check_cache", return_value=True),
        patch.object(HealthView, "_check_solicitudes", return_value=True),
    ):
        request = type("R", (), {})()
        response = view.get(request)
    assert response.status_code == 200
    assert response.data["status"] == "healthy"


@pytest.mark.unit
def test_health_check_db_falla():
    view = HealthView()
    with patch("atenciones.views.health_view.connection") as mock_conn:
        mock_conn.cursor.side_effect = Exception("db down")
        assert view._check_db() is False


@pytest.mark.unit
def test_health_check_cache_falla():
    view = HealthView()
    with patch("atenciones.views.health_view.cache.set", side_effect=Exception("cache")):
        assert view._check_cache() is False


@pytest.mark.unit
@patch("atenciones.views.health_view.requests.head", side_effect=Exception("timeout"))
def test_health_check_solicitudes_falla(mock_head):
    assert HealthView()._check_solicitudes() is False
