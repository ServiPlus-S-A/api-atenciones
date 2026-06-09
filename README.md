# ServiPlus Atenciones

Módulo de Atenciones de solicitudes para la plataforma ServiPlus S.A., implementado con arquitectura en capas según el DAS (Django + DRF + Celery + Next.js).

## Requisitos

- Docker Compose 2.27+
- Python 3.12+ (desarrollo local sin Docker)
- Node.js 20+ (frontend)

## Setup local

```bash
cp .env.example .env
# Editar .env con credenciales reales

docker compose up --build
```

Backend: http://localhost:8000  
Swagger: http://localhost:8000/api/schema/swagger-ui/  
Frontend: http://localhost:3000

### Migraciones (puerto 5432 directo)

Las migraciones deben ejecutarse contra `DATABASE_URL_DIRECT` (puerto 5432), no contra el pooler (6543):

```bash
cd backend
export DATABASE_URL=$DATABASE_URL_DIRECT
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py seed_estados
```

### Tests backend

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

### Tests frontend

```bash
cd frontend
npm install
npm test
npm run test:e2e
```

## Decisiones arquitectónicas

| Capa        | Patrón                   | Tecnología                     |
| ----------- | ------------------------ | ------------------------------ |
| View        | Orquestación             | DRF APIView                    |
| Application | Serializers puros        | DRF Serializer                 |
| Logic       | Service Layer            | Python + `@transaction.atomic` |
| Data Access | Repository + DTO         | Django ORM                     |
| Async       | Producer-Consumer        | Celery 5.4 + Redis             |
| Integration | Circuit Breaker          | HTTP clients con fallback      |
| Security    | RBAC + Audit append-only | SimpleJWT + AuditLog           |

## Known limitations

### CONCERN-02 — Notificaciones sin SSE

El frontend usa **polling cada 30s** (`useNotificaciones`) porque SSE no es compatible con despliegue stateless multi-instancia sin sticky sessions. TTL de caché en Redis: 30s. Ruta de upgrade documentada: Redis Pub/Sub + WebSocket gateway.

### CONCERN-03 — Archival audit_log

Registros de `audit_log` > 6 meses se exportan a CSV+gzip en Supabase Storage y luego se eliminan. Tarea programada: Celery Beat `archival_audit_log` (día 1 de cada mes, 02:00 UTC).

### CONCERN-09 — Producción

`ALLOWED_HOSTS`, `CONN_MAX_AGE=0`, `DATABASE_URL` puerto 6543, `sslmode=require`, HSTS y cookies seguras configurados en `config/settings/production.py`.

## Estructura

```
backend/          # Django + DRF
frontend/         # Next.js 14 App Router
docker-compose.yml
```

# Comandos para evaluar la calidad del codigo

## Ruff (lint)

Verificador y formateador de código ultra rápido. Detecta errores de estilo, imports no utilizados, variables no usadas y otros problemas comunes. Con `--fix` corrige automáticamente los problemas que puede resolver.

Ejecutar desde la raiz del repo:

```powershell
$env:PYTHONPATH = "backend"
echo $env:PYTHONPATH
ruff check backend/atenciones backend/config backend/tests --fix
```

## Mypy (type check)

Verificador de tipos estático. Valida que las anotaciones de tipos sean correctas y detecta errores potenciales sin ejecutar el código. Ayuda a prevenir bugs relacionados con tipos.

Ejecutar desde la raiz del repo:

```powershell
mypy backend/atenciones backend/config backend/tests --explicit-package-bases
```

## Coverage

Ejecuta los tests y genera un reporte de cobertura de código. Muestra qué porcentaje del código está siendo probado y qué líneas no tienen tests.

Ejecutar desde el backend:

```powershell
$env:PYTHONPATH = "."; pytest --cov=atenciones --cov-report=term-missing
```
