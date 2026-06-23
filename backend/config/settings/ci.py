"""
Settings para GitHub Actions y act local.
Postgres del servicio de CI sin SSL; cache en memoria y Celery eager como en testing.
"""

import os

import dj_database_url

from . import base

globals().update({k: v for k, v in vars(base).items() if k.isupper()})

DEBUG = True

_database_url = os.environ.get("DATABASE_URL")
if not _database_url:
    raise RuntimeError("Falta DATABASE_URL para ejecutar tests en CI.")

DATABASES = {
    "default": dj_database_url.parse(
        _database_url,
        conn_max_age=0,
        ssl_require=False,
    )
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Habilitar autenticación mock en CI
ALLOW_MOCK_AUTH = True
