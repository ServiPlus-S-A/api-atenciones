"""
Settings para pruebas. Usa el pooler de Supabase (puerto 6543) que sí resuelve
DNS desde local, a diferencia del host directo (puerto 5432) que solo resuelve
desde dentro de la red de Supabase.
"""

import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = True

# En tests NO se deben hardcodear credenciales.
# Debes proveer DATABASE_URL vía entorno (idealmente apuntando al pooler :6543).
_pooler_url = os.environ.get("DATABASE_URL")
if not _pooler_url:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.parse(
            _pooler_url,
            conn_max_age=0,
            ssl_require=True,
        )
    }
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

# Cache en memoria local para tests (sin Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery síncrono — no necesita broker para las pruebas
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Habilitar autenticación mock en pruebas
ALLOW_MOCK_AUTH = True
