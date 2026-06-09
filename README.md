# ServiPlus — Módulo de Atenciones

Gestión del ciclo de vida de atenciones técnicas para la plataforma ServiPlus S.A., 
como parte de un ecosistema de cinco módulos para la administración integral de servicios.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-En%20Desarrollo-orange.svg)]()
[![Quality Gate](https://img.shields.io/badge/quality%20gate-passed-brightgreen.svg)]()
[![Coverage Backend](https://img.shields.io/badge/coverage%20backend-83%25-brightgreen.svg)]()
## Descripción

**ServiPlus** es una plataforma de gestión de servicios técnicos compuesta por cuatro módulos independientes que colaboran entre sí:

| Módulo | Repositorio |
|---|---|
| Atenciones | *(este repositorio)* |
| Solicitudes | [serviplus-solicitudes](<https://github.com/ServiPlus-S-A/api-solicitudes>) |
| Finanzas | [serviplus-finanzas](<URL_REPO_FINANZAS>) |
| Parametrización | [serviplus-parametrizacion](<URL_REPO_PARAMETRIZACION>) |
| Reportes | [serviplus-reportes](<https://github.com/ServiPlus-S-A/api-reportes>) |

Este repositorio implementa el **módulo de Atenciones**: la instancia concreta de solución entregada a una solicitud. Una solicitud puede generar una o múltiples atenciones, cada una atendida por uno o varios técnicos asignados. El módulo gestiona el ciclo de vida completo de cada atención, incluyendo roles de seguridad (RBAC), control de auditoría append-only, procesamiento asíncrono de notificaciones y comunicación resiliente con otros módulos mediante Circuit Breaker.

## Arquitectura
```text
[ Cliente / Navegador ]
          ↓
[ Frontend (Next.js 14) ] ←── Interfaz de usuario (SSR/CSR)
          ↓ (HTTPS)
[ API Gateway (Kong) ] ←── Punto de entrada centralizado — gestionado por el módulo de Parametrización
          |                  Enrutamiento entre módulos · Autenticación JWT · Rate limiting
          ↓ (API REST interna)
[ Backend Atenciones (Django/DRF) ] ←── Lógica de negocio · Service Layer · Repository
      ↙                  ↘
[ Worker (Celery/Redis) ]  [ Base de Datos (PostgreSQL) ]
```

### Decisiones arquitectónicas

| Capa        | Patrón                   | Tecnología                     |
| ----------- | ------------------------ | ------------------------------ |
| View        | Orquestación             | DRF APIView                    |
| Application | Serializers puros        | DRF Serializer                 |
| Logic       | Service Layer            | Python + `@transaction.atomic` |
| Data Access | Repository + DTO         | Django ORM                     |
| Async       | Producer-Consumer        | Celery 5.4 + Redis             |
| Integration | Circuit Breaker          | HTTP clients con fallback      |
| Security    | RBAC + Audit append-only | SimpleJWT + AuditLog           |

## Enlaces a Documentación
Puedes encontrar la documentación ampliada del proyecto en nuestro repositorio compartido de Google Drive: https://drive.google.com/drive/folders/1R7gsT0mqxRyMiWNWh0sNd9ZavzcMcg6M?usp=sharing 

## Stack tecnológico

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12+ | Lenguaje principal |
| Django + DRF | 5.x | Framework web y API REST |
| Celery | 5.4+ | Procesamiento asíncrono (workers y Beat) |
| SimpleJWT | — | Autenticación y emisión de tokens |

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| Node.js | 20+ | Entorno de ejecución |
| Next.js | 14 (App Router) | Framework React (SSR/CSR) |
| Tailwind CSS | 3.x | Estilos y UI |

### Infraestructura y datos
| Tecnología | Versión | Uso |
|---|---|---|
| PostgreSQL (Supabase) | 15+ | Base de datos relacional con PgBouncer (puerto 6543) |
| Supabase Storage | — | Archivo de logs de auditoría (CSV + gzip) |
| Redis Cloud | — | Caché compartida (Cache Aside) |
| Redis (local por EC2) | 7+ | Broker de Celery por instancia |
| Docker Compose | 2.27+ | Orquestación de contenedores local |
| AWS EC2 + ALB | — | Cómputo y balanceo de carga en producción |
| Kong (API Gateway) | — | Enrutamiento y seguridad — gestionado por Parametrización |

## Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado y configurado:

- **Docker Compose** 2.27+
- **Python** 3.12+ (para desarrollo local sin Docker en el backend)
- **Node.js** 20+ (para desarrollo local en el frontend)
- **Cuenta en Supabase** — se necesita un proyecto activo con base de datos PostgreSQL y Storage habilitado

---

## Inicio rápido (Quick Start)

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd serviplus-atenciones
```

### 2. Crear y configurar el proyecto en Supabase

Ingresa a [supabase.com](https://supabase.com) y crea un nuevo proyecto. Una vez creado, obtén los siguientes valores desde el panel de Supabase:

| Variable | Dónde encontrarla en Supabase |
|---|---|
| `DATABASE_URL` | *Project Settings → Database → Connection string → Transaction pooler* (puerto 6543) |
| `DATABASE_URL_DIRECT` | *Project Settings → Database → Connection string → Direct connection* (puerto 5432) |
| `SUPABASE_URL` | *Project Settings → API → Project URL* |
| `SUPABASE_SERVICE_KEY` | *Project Settings → API → service_role key* |

Luego, en *Storage*, crea un bucket llamado **`audit-archives`** (privado) para el archival de audit logs.

### 3. Configurar variables de entorno
```bash
cp .env.example .env
```

Edita el archivo `.env` y reemplaza los siguientes valores con los obtenidos en el paso anterior:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:6543/<db>?sslmode=require
DATABASE_URL_DIRECT=postgresql://<user>:<password>@<host>:5432/<db>?sslmode=require
SUPABASE_URL=https://<tu-proyecto>.supabase.co
SUPABASE_SERVICE_KEY=<tu-service-role-key>
SUPABASE_STORAGE_BUCKET=audit-archives

SECRET_KEY=<clave-django-aleatoria-min-50-chars>
SIMPLE_JWT_SIGNING_KEY=<clave-jwt-aleatoria>
```

> **⚠️ Importante:** `DATABASE_URL` usa el puerto **6543** (pooler PgBouncer) para tráfico de aplicación. `DATABASE_URL_DIRECT` usa el puerto **5432** (conexión directa) exclusivamente para migraciones.

### 4. Construir y levantar contenedores Docker
```bash
docker compose up --build -d
```

### 5. Ejecutar migraciones y datos iniciales

Las migraciones deben ejecutarse contra la conexión directa (puerto 5432), no contra el pooler:
```bash
cd backend
export DATABASE_URL=$DATABASE_URL_DIRECT
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py seed_estados
```

### 6. Crear usuario administrador
```bash
python manage.py createsuperuser
```

### 7. Verificar que todo está corriendo
```bash
docker compose ps
```

Debes ver todos los servicios en estado `Up (healthy)`:

| Servicio | Puerto |
|---|---|
| serviplus-backend | - |
| serviplus-frontend | - |
| serviplus-worker | — |
| serviplus-redis | - |

**Endpoints principales:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Swagger Docs:** http://localhost:8000/api/schema/swagger-ui/

## Comandos útiles
### Backend
- **Ver logs:** `docker logs serviplus-atenciones-backend-1 -f`
- **Linter y Formateo (Ruff):** 
  ```powershell
  $env:PYTHONPATH = "backend"; ruff check backend/atenciones backend/config backend/tests --fix
  ```
- **Type Checking (Mypy):**
  ```powershell
  mypy backend/atenciones backend/config backend/tests --explicit-package-bases
  ```
- **Tests con Coverage:** 
  ```powershell
  $env:PYTHONPATH = "."; pytest --cov=atenciones --cov-report=term-missing
  ```

## Estructura del repositorio
```text
serviplus-atenciones/
├── backend/                  # Código fuente Django + DRF
├── frontend/                 # Aplicación Next.js 14 (App Router)
├── docker-compose.yml        # Orquestación de contenedores
├── docker-compose.override.yml # Sobrescritura para hot-reload local
├── LICENSE                   # Licencia MIT del proyecto
└── README.md                 # Documentación principal
```

## Estado del proyecto

| Sprint | Estado | Descripción |
|---|---|---|
| S0 | ✅ Completado | Arquetipo base, configuración DAS, CI/CD y DevOps inicial |
| S1 | 🔜 Pendiente | Por definir |
| S2 | 🔜 Pendiente | Por definir |
| S3 | 🔜 Pendiente | Por definir |
| S4 | 🔜 Pendiente | Por definir |

## Flujo de trabajo

Ver `CONTRIBUTING.md` para el detalle completo. Resumen:

1. Trabajar en rama personal (`ncordoba`).
2. Validar localmente: `ruff`, `mypy`, `pytest --cov`.
3. Push y PR a `develop`. CI ejecuta pipeline y Qodo revisa.
4. Atender hallazgos, mergear a `develop`.
5. Al cerrar sprint, PR de `develop` a `main` con tag semántico.

## Créditos

Desarrollado por el equipo LUCIERNAGAS — Universidad del Valle, Escuela de Ingeniería de Sistemas y Computación:

- Nicolás Córdoba — 2343576-3743
- Alejandro Quintero — 2342181-3743
- Juan Manuel Ampudia — 2342174-3743
- Santiago Vega — 2064614-2724
- Andrés Ramírez — 1926987
- Maycol Taquez — 2375000-3743

## Licencia

MIT — ver [`LICENSE`](LICENSE).