import os
import dj_database_url
from . import base

globals().update({k: v for k, v in vars(base).items() if k.isupper()})

DATABASES = globals()["DATABASES"]

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# CONN_MAX_AGE=0 obligatorio con pooler (puerto 6543)
CONN_MAX_AGE = 0

DATABASES["default"] = dj_database_url.parse(
    os.environ["DATABASE_URL"],
    conn_max_age=0,
    ssl_require=True,
)
DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
