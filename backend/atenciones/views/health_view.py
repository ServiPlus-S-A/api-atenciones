import requests
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        checks = {
            "db": self._check_db(),
            
        }
        status_value = "healthy" if all(checks.values()) else "degraded"
        code = 200 if status_value == "healthy" else 503
        return Response({"status": status_value, "checks": checks}, status=code)

    def _check_db(self) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    def _check_cache(self) -> bool:
        try:
            cache.set("health_check", "ok", 5)
            return cache.get("health_check") == "ok"
        except Exception:
            return False

    def _check_solicitudes(self) -> bool:
        try:
            r = requests.head(settings.SOLICITUDES_HEALTH_URL, timeout=3)
            return r.status_code < 500
        except Exception:
            return False
