from unittest.mock import patch
import pytest
import time

from atenciones.views.health_view import HealthView


@pytest.mark.unit
def test_health_todos_ok():
    view = HealthView()
    with (
        patch.object(HealthView, "_check_db", return_value="ok"),
        patch.object(HealthView, "_check_cache", return_value="ok"),
        patch.object(HealthView, "_check_solicitudes", return_value="ok"),
        patch.object(HealthView, "_check_celery_worker", return_value="ok"),
        patch.object(HealthView, "_check_celery_beat", return_value="ok"),
    ):
        request = type("R", (), {})()
        response = view.get(request)
    assert response.status_code == 200
    assert response.data["status"] == "healthy"
    assert response.data["checks"]["db"] == "ok"
    assert response.data["checks"]["cache"] == "ok"
    assert response.data["checks"]["celery_worker"] == "ok"
    assert response.data["checks"]["celery_beat"] == "ok"
    assert response.data["checks"]["solicitudes"] == "ok"


@pytest.mark.unit
def test_health_algun_critico_falla_degrada():
    view = HealthView()
    with (
        patch.object(HealthView, "_check_db", return_value="ok"),
        patch.object(HealthView, "_check_cache", return_value="error: redis down"),
        patch.object(HealthView, "_check_solicitudes", return_value="ok"),
        patch.object(HealthView, "_check_celery_worker", return_value="ok"),
        patch.object(HealthView, "_check_celery_beat", return_value="ok"),
    ):
        request = type("R", (), {})()
        response = view.get(request)
    assert response.status_code == 503
    assert response.data["status"] == "degraded"
    assert response.data["checks"]["cache"] == "error: redis down"


@pytest.mark.unit
def test_health_solicitudes_falla_no_degrada():
    view = HealthView()
    with (
        patch.object(HealthView, "_check_db", return_value="ok"),
        patch.object(HealthView, "_check_cache", return_value="ok"),
        patch.object(HealthView, "_check_solicitudes", return_value="error: conn error"),
        patch.object(HealthView, "_check_celery_worker", return_value="ok"),
        patch.object(HealthView, "_check_celery_beat", return_value="ok"),
    ):
        request = type("R", (), {})()
        response = view.get(request)
    assert response.status_code == 200
    assert response.data["status"] == "healthy"
    assert response.data["checks"]["solicitudes"] == "error: conn error"


@pytest.mark.unit
def test_health_check_db_ok_y_falla():
    view = HealthView()
    with patch("atenciones.views.health_view.connection") as mock_conn:
        # Falla
        mock_conn.cursor.side_effect = Exception("db down")
        assert "error: db down" in view._check_db()
        # OK
        mock_conn.cursor.side_effect = None
        assert view._check_db() == "ok"


@pytest.mark.unit
def test_health_check_cache_ok_y_falla():
    view = HealthView()
    with patch("atenciones.views.health_view.cache") as mock_cache:
        # OK
        mock_cache.get.return_value = "ok"
        assert view._check_cache() == "ok"
        # Falla set
        mock_cache.set.side_effect = Exception("cache error")
        assert "error: cache error" in view._check_cache()
        # Falla get (desajuste de valor)
        mock_cache.set.side_effect = None
        mock_cache.get.return_value = "not_ok"
        assert "error" in view._check_cache()


@pytest.mark.unit
def test_health_check_solicitudes_ok_y_falla():
    view = HealthView()
    with patch("atenciones.views.health_view.requests.head") as mock_head:
        # OK
        mock_head.return_value.status_code = 200
        assert view._check_solicitudes() == "ok"
        # Falla status code
        mock_head.return_value.status_code = 500
        assert "error: status code 500" in view._check_solicitudes()
        # Falla excepcion
        mock_head.side_effect = Exception("timeout")
        assert "error: timeout" in view._check_solicitudes()


@pytest.mark.unit
def test_health_check_celery_worker_ok_y_falla():
    view = HealthView()
    with patch("config.celery.app.control.inspect") as mock_inspect:
        # OK
        mock_inspect.return_value.ping.return_value = {"worker1": {"ok": "pong"}}
        assert view._check_celery_worker() == "ok"
        # Falla no workers
        mock_inspect.return_value.ping.return_value = None
        assert "error: no hay workers activos" in view._check_celery_worker()
        # Falla excepcion
        mock_inspect.side_effect = Exception("redis down")
        assert "error: redis down" in view._check_celery_worker()


@pytest.mark.unit
def test_health_check_celery_beat_ok_y_falla():
    view = HealthView()
    with patch("atenciones.views.health_view.cache") as mock_cache:
        # OK
        mock_cache.get.return_value = time.time() - 30
        assert view._check_celery_beat() == "ok"
        # Falla no heartbeat registrado
        mock_cache.get.return_value = None
        assert "error: no se ha registrado ningún heartbeat" in view._check_celery_beat()
        # Falla heartbeat obsoleto
        mock_cache.get.return_value = time.time() - 150
        assert "error: último heartbeat hace 150 segundos" in view._check_celery_beat()
        # Falla excepcion
        mock_cache.get.side_effect = Exception("redis connection error")
        assert "error: redis connection error" in view._check_celery_beat()

