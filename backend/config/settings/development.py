import os
from . import base

globals().update({k: v for k, v in vars(base).items() if k.isupper()})

DATABASES = globals()["DATABASES"]
INSTALLED_APPS = globals()["INSTALLED_APPS"]
MIDDLEWARE = globals()["MIDDLEWARE"]

DEBUG = True

_direct_url = os.environ.get("DATABASE_URL_DIRECT")
if _direct_url:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(
        _direct_url,
        conn_max_age=0,
        ssl_require=True,
    )
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

CORS_ALLOW_ALL_ORIGINS = True
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Mock responses para desarrollo (evita requerir microservicios externos levantados)
class MockSolicitud:
    def __init__(self, id):
        self.id = str(id)
        self.estado = "Pendiente"
        self.servicio_id = "servicio-mock"
        self.aptitud_requerida = None
        self.cliente_id = "cliente-mock"
        self.consultor_ids = []


class MockConsultor:
    def __init__(self, id):
        self.id = str(id)
        self.disponible = True
        self.aptitudes = ()
        self.nombre = f"Consultor Mock {id}"
        self.role = "CONSULTOR"
        self.rol = "CONSULTOR"
        self.is_authenticated = True


class DefaultMockDict(dict):
    def __init__(self, mock_class):
        super().__init__()
        self.mock_class = mock_class

    def __eq__(self, other):
        if not isinstance(other, DefaultMockDict):
            return NotImplemented
        return self.mock_class == other.mock_class and dict.__eq__(self, other)

    def get(self, key, default=None):
        return self.mock_class(key)


SOLICITUDES_MOCK_RESPONSES = DefaultMockDict(MockSolicitud)
PARAMETRIZACION_MOCK_RESPONSES = DefaultMockDict(MockConsultor)

# Habilitar autenticación mock en desarrollo
ALLOW_MOCK_AUTH = True
