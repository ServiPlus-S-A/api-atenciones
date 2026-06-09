# CONCERN-09: configuración de producción
from .base import *  # noqa: F403
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")  # noqa: F405

# CONN_MAX_AGE=0 obligatorio con pooler (puerto 6543)
CONN_MAX_AGE = 0

DATABASES["default"] = dj_database_url.parse(  # noqa: F405
    os.environ["DATABASE_URL"],  # noqa: F405
    conn_max_age=0,
    ssl_require=True,
)
DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}  # noqa: F405

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
