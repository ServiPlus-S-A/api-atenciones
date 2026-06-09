# Changelog

Todos los cambios notables del módulo de Atenciones — ServiPlus se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
El versionado sigue [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### En progreso

- Módulo de autenticación (RBAC) y Audit Log (Sprint 1).
- CRUD de atenciones y lógica de estados (Sprint 2).

---

## [0.1.0] — Sprint 0

### Añadido

- Estructura inicial del repositorio: `backend/`, `frontend/`.
- `docker-compose.yml` con servicio Django, worker Celery, Redis local y configuración base.
- Arquetipo Django + DRF con settings separados por entorno (`development`, `production`, `ci`).
- Arquetipo Next.js 14 (App Router) con Tailwind CSS y estructura base de páginas.
- Pipeline CI `.github/workflows/ci-pr-to-develop.yml` con jobs de `ruff`, `mypy`, `pytest --cov` y build Docker. Settings de CI configurados con `DJANGO_SETTINGS_MODULE=config.settings.ci`.
- Configuración de calidad de código: `mypy.ini` y `pytest.ini` con umbral de cobertura mínima 80% en CI. Linter (Ruff) con sus reglas por defecto.
- Documentación base: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`.
- Estrategia de ramas: `main` ← `develop` ← ramas personales del equipo.

### Decisiones arquitectónicas

- Arquitectura en capas estricta: View → Application (Serializers) → Logic (Service) → Data (Repository + DTO).
- `DATABASE_URL` (puerto 6543, PgBouncer) para tráfico de aplicación; `DATABASE_URL_DIRECT` (puerto 5432) exclusivo para migraciones.
- Redis local por instancia como broker de Celery; Redis Cloud separado para caché (Cache Aside).

---

[Unreleased]: https://github.com/<org>/serviplus-atenciones/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/<org>/serviplus-atenciones/releases/tag/v0.1.0