# Guía de contribución

Este documento describe el flujo de trabajo para colaborar en ServiPlus — Módulo de Atenciones. Toda contribución debe seguir este proceso.

## Estrategia de ramas

```
main           ──●──────────●──────●──── (releases tagged: v0.1.0, v0.2.0)
                  ↑          ↑      ↑
                  PR         PR     PR
                  │          │      │
develop        ──●──●──●──●──●──●──●──── (integración estable)
                  ↑  ↑  ↑     ↑  ↑
                  PR PR PR    PR PR
                  │  │  │     │  │
ncordoba       ──●──●──●──────────────── (rama personal)
aquintero      ──●──●─────────────────── (rama personal)
jampudia       ──●──●──●─────────────── (rama personal)
svega          ──●────────────────────── (rama personal)
aramirez       ──●──●─────────────────── (rama personal)
mtaquez        ──●──●──●─────────────── (rama personal)
```

### Ramas principales

- **`main`**: rama de producción. Solo se actualiza al cerrar un sprint completo y validado. Cada merge a `main` lleva un tag semántico (`v0.1.0`, `v0.2.0`, etc.). Protegida.
- **`develop`**: rama de integración. Aquí confluye el trabajo validado y listo para integración. Protegida con regla de PR obligatorio.
- **Ramas personales** (`ncordoba`, `aquintero`, `jampudia`, `svega`, `aramirez`, `mtaquez`): cada integrante desarrolla su trabajo en su propia rama antes de promoverlo a `develop`.

### Reglas de los flujos

#### Trabajo dentro de la rama personal

- Hacer commits frecuentes con mensajes claros (ver Conventional Commits abajo).
- Validar localmente antes de cada push.
- Push directo a la rama personal permitido (no requiere PR).
- Mantener la rama personal sincronizada con `develop`: hacer `git pull origin develop` y rebase al menos una vez por semana.

#### Promoción de rama personal a `develop`

- Solo cuando la historia de usuario o tarea del sprint esté completa y estable.
- Apertura de PR desde la rama personal a `develop`.
- El PR debe describir las historias de usuario completadas.
- CI debe pasar todos los gates (ver abajo).
- Qodo Merge revisa automáticamente y publica observaciones.
- Atender hallazgos de Qodo antes de mergear.
- Squash merge (un commit limpio en `develop` por historia o tarea).

#### Promoción de `develop` a `main`

- Solo al cierre de un sprint validado y con demo funcional.
- PR desde `develop` a `main` con tag semántico (`v0.X.0`).
- Actualizar `CHANGELOG.md` con los cambios del sprint.
- Actualizar documentos de arquitectura si hubo nuevos ADRs.

## Gates de calidad

### Gate 1: validación local antes de push a rama personal

Antes de cualquier push, ejecutar localmente en PowerShell:

```powershell
# Linter y formateo (Ruff)
$env:PYTHONPATH = "backend"; ruff check backend/atenciones backend/config backend/tests --fix

# Type checker (Mypy)
mypy backend/atenciones backend/config backend/tests --explicit-package-bases

# Tests con coverage
$env:PYTHONPATH = "."; pytest --cov=atenciones --cov-report=term-missing
```

Si cualquiera falla, no hacer push.

### Gate 2: pipeline CI al abrir PR a `develop`

GitHub Actions ejecuta automáticamente:

1. Instalación de dependencias.
2. `ruff check` (linter).
3. `mypy` (type checker estricto).
4. `pytest --cov` (cobertura mínima 80% sobre código nuevo).
5. Build de imágenes Docker.
6. Qodo Merge analiza el diff y publica review en el PR.

Si el pipeline falla, el PR no puede mergearse.

### Gate 3: revisión humana antes de merge

Aunque CI pase, al menos un integrante del equipo distinto al autor debe:

1. Leer el diff completo línea por línea.
2. Revisar las observaciones de Qodo Merge.
3. Atender al menos las observaciones marcadas como "critical" o "major".
4. Verificar que los criterios de aceptación de las HUs están cubiertos.
5. Aprobar el PR explícitamente antes de mergear.

## Convención de commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<alcance opcional>): <descripción corta>

[cuerpo opcional con detalle]

[footer opcional con referencias]
```

### Tipos permitidos

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad (corresponde a una HU) |
| `fix` | Corrección de bug |
| `docs` | Cambios de documentación |
| `refactor` | Refactor sin cambio funcional |
| `test` | Añadir o ajustar tests |
| `chore` | Tareas de mantenimiento (deps, configs) |
| `style` | Formato, sin cambio de lógica |
| `perf` | Mejora de performance |
| `ci` | Cambios en CI/CD |

### Ejemplos

```
feat(atenciones): implementa CRUD de atenciones con cambio de estado

Cierra HU-05. Incluye:
- Endpoints POST /atenciones y PATCH /atenciones/{id}/estado
- Validación con InputSerializer
- Lógica de transición de estados en Service Layer
- Repository como único punto de acceso al ORM

Refs: HU-05
```

```
fix(notificaciones): corrige polling al endpoint de notificaciones

El hook useNotificaciones no limpiaba el intervalo al desmontar.
Ahora se aplica cleanup en el return del useEffect.
```

```
docs(adr): añade decisión sobre Circuit Breaker para integración con Solicitudes
```

## Plantilla de PR

Al abrir un PR, llenar la plantilla `pull_request_template.md` que aparece automáticamente. Debe incluir:

- Historias de usuario cerradas.
- Criterios de aceptación verificados.
- Tests añadidos.
- Documentación actualizada (si aplica).
- ADR creado (si la PR introduce decisión arquitectónica).
- Screenshots o evidencia de pruebas manuales.

## Issues

Cada historia de usuario del backlog se materializa como un Issue en GitHub:

- Título: `[HU-NN] Título de la historia`.
- Cuerpo: usar la plantilla `historia-usuario.md`.
- Labels: `epic:E1`, `priority:must`, `points:5`.
- Milestone: `Sprint NN`.

## Definición de Listo (DoR)

Una historia está Ready cuando:

- Tiene narrativa Mike Cohn completa.
- Tiene al menos 5 criterios de aceptación verificables.
- Está estimada en story points.
- Tiene prioridad MoSCoW.
- Sus dependencias están resueltas o planificadas antes.

## Definición de Hecho (DoD)

Una historia está Done cuando:

- Código commiteado en rama personal.
- PR abierto y descripción enlazada al Issue.
- Todos los criterios de aceptación pasan (verificados con tests).
- Cobertura mínima 80% sobre código nuevo.
- `ruff` y `mypy` pasan sin errores.
- Qodo Merge revisó el PR y los hallazgos relevantes fueron atendidos.
- OpenAPI actualizado si aplica.
- ADR actualizado si introduce decisión arquitectónica.
- PR aprobado y mergeado a `develop`.
- Demo funcional registrado en bitácora.

## Soporte y dudas

- Issues técnicos: abrir issue en GitHub con label `question`.
- Dudas arquitectónicas: discutir antes de codear, no después.