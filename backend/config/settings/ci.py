"""
Settings para GitHub Actions y act local.
Postgres del servicio de CI sin SSL; cache en memoria y Celery eager como en testing.
"""

import os

import dj_database_url

from .base import *  # noqa: F403

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
