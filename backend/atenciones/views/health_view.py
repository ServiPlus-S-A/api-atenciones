import requests
import time
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: dict})
    def get(self, request):
        critical_checks = {
            "db": self._check_db(),
            "cache": self._check_cache(),
            "celery_worker": self._check_celery_worker(),
            "celery_beat": self._check_celery_beat(),
        }
        solicitudes_check = self._check_solicitudes()

        checks = {
            **critical_checks,
            "solicitudes": solicitudes_check,
        }

        status_value = "healthy" if all(v == "ok" for v in critical_checks.values()) else "degraded"
        code = 200 if status_value == "healthy" else 503
        return Response({"status": status_value, "checks": checks}, status=code)

    def _check_db(self) -> str:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return "ok"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_cache(self) -> str:
        try:
            cache.set("health_check", "ok", 5)
            if cache.get("health_check") == "ok":
                return "ok"
            return "error: no se pudo recuperar la clave del caché"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_solicitudes(self) -> str:
        try:
            r = requests.head(settings.SOLICITUDES_HEALTH_URL, timeout=3)
            if r.status_code >= 500:
                return f"error: status code {r.status_code}"
            return "ok"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_celery_worker(self) -> str:
        try:
            from config.celery import app as celery_app
            insp = celery_app.control.inspect(timeout=2.0)
            res = insp.ping()
            if not res:
                return "error: no hay workers activos"
            return "ok"
        except Exception as e:
            return f"error: {str(e)}"

    def _check_celery_beat(self) -> str:
        try:
            last_heartbeat = cache.get("celery_beat_last_heartbeat")
            if last_heartbeat is None:
                return "error: no se ha registrado ningún heartbeat"
            elapsed = time.time() - last_heartbeat
            if elapsed > 120:
                return f"error: último heartbeat hace {int(elapsed)} segundos"
            return "ok"
        except Exception as e:
            return f"error: {str(e)}"

