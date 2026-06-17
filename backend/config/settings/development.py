from .base import *  # noqa: F403
import os  # Migraciones locales: conexión directa PG puerto 5432

DEBUG = True

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

class DefaultMockDict(dict):
    def __init__(self, mock_class):
        super().__init__()
        self.mock_class = mock_class

    def get(self, key, default=None):
        return self.mock_class(key)

SOLICITUDES_MOCK_RESPONSES = DefaultMockDict(MockSolicitud)
PARAMETRIZACION_MOCK_RESPONSES = DefaultMockDict(MockConsultor)
