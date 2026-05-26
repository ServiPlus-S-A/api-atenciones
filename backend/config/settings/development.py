from .base import *  # noqa: F403

DEBUG = True

# Migraciones locales: conexión directa PG puerto 5432
import os

_direct_url = os.environ.get("DATABASE_URL_DIRECT")
if _direct_url:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(  # noqa: F405
        _direct_url,
        conn_max_age=0,
        ssl_require=True,
    )
    DATABASES["default"].setdefault("OPTIONS", {})  # noqa: F405
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"  # noqa: F405

CORS_ALLOW_ALL_ORIGINS = True
INSTALLED_APPS += ["corsheaders"]  # noqa: F405
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
