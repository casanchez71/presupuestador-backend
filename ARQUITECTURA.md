# Presupuestador Backend — Arquitectura y Reglas de Construcción

## Stack
- **Backend:** Python 3.11 + FastAPI
- **DB:** Supabase (PostgreSQL + RLS)
- **Deploy:** Render (free tier → `https://presupuestador-backend-adm1.onrender.com`)
- **Frontend que consume esta API:** React 18 + Vite (repo `eos-saas`, NO es Next.js)

## Reglas obligatorias

### Seguridad
- JWT se valida con **JWKS endpoint** (`/auth/v1/.well-known/jwks.json`) — NO usar shared secret
- Algoritmos soportados: `ES256` (actual) y `HS256` (legacy) — Supabase usa ECC P-256
- CORS siempre via `ALLOWED_ORIGINS` env var, nunca `"*"` en producción
- Nunca subir `.env` real a git — solo `.env.example`
- `SUPABASE_KEY` debe tener permisos suficientes para leer `memberships` en backend server-side

### Schema de Supabase (NO inventar tablas o columnas)
- Tenant = `org_id` en tabla `memberships` (NO existe `profiles.tenant_id`)
- Todo `get_current_user()` resuelve `user_id → memberships.org_id`
- RLS policies usan `IN (SELECT public.get_my_org_ids())` — NO `= ANY(...)` (da error SETOF)

### Código Python
- Pydantic v2: usar `model.model_dump()` — NO `model.dict()` (deprecado)
- Type hints: `str | None` (Python 3.10+ union syntax)
- Supabase SDK: siempre filtrar por `org_id` en queries (multi-tenant)

### Deploy en Render
- Build command: `pip install --upgrade pip && pip install --prefer-binary -r requirements.txt`
- `--prefer-binary` es obligatorio: evita compilar `pydantic-core` desde Rust (Cargo no tiene permisos en Render free)
- `render.yaml` solo aplica al CREAR el servicio — cambios posteriores van por Render Settings UI
- Variables de entorno activas esperadas: `SUPABASE_URL`, `SUPABASE_KEY`, `ALLOWED_ORIGINS`, `OPENAI_API_KEY`

## Tablas creadas (Sprint 0)
| Tabla | Descripción |
|-------|-------------|
| `price_snapshots` | Snapshots de listas de precios importadas desde Excel |
| `audit_logs` | Log de cambios en ítems de presupuestos |
| `budgets` | Presupuestos (cabecera) |
| `budget_items` | Ítems del árbol jerárquico |
| `budget_versions` | Versiones/snapshots completos de un presupuesto |
| `indirect_config` | Configuración de % de indirectos por organización |

Todas tienen RLS con `org_id IN (SELECT public.get_my_org_ids())`.

## Log de Sprints

### Sprint 0 — Setup y Conexión ✅ CERRADO (2026-03-18)
- Repo creado: `github.com/casanchez71/presupuestador-backend`
- Deploy live en Render: `https://presupuestador-backend-adm1.onrender.com`
- Health check OK: `{"status":"OK","timestamp":"2026-03-18T04:46:23.677665"}`
- 6 tablas migradas en Supabase con RLS
- Endpoints base: `/health`
- Python 3.11.9 + Dockerfile en repo (build exitoso)

### Sprint 1 — Núcleo + Árbol + Edición ✅ CERRADO (2026-03-18)
- CRUD budgets, árbol jerárquico con parent_id, carga de ítems y parser inicial de Excel
- Endpoints implementados: `POST /budgets`, `GET /budgets`, `GET /budget/{id}`, `DELETE /budget/{id}`, `POST /budget/{id}/items`, `GET /budget/{id}/tree`, `POST /budget/import-excel`

### Sprint 2 — IA + Lectura de Planos ✅ CERRADO (2026-03-18)
- GPT-4o Vision para planos, indirectos ponderados, vista análisis
- Columnas `indirecto` y `total_con_indirecto` agregadas a `budget_items`
- Variable `OPENAI_API_KEY` en Render

### Sprint 2 — IA + Lectura de Planos (alcance pendiente)
- Robustecer lectura de PDF real y formatos CAD
- Parametría automática por IA
- Validación con archivos reales de cliente

### Sprint 3 — Análisis + Export + Versionado (parcial)
- Implementado en backend: `GET /budget/{id}/export/excel`, `POST /budget/{id}/version`, `GET /budget/{id}/versions`, `GET /budget/{id}/version/{version_id}`
- Pendiente: export PDF
- Pendiente: análisis desagregado real por MAT / MO / Equipos / Indirectos
- Pendiente: integración React+Vite

### Sprint 4 — Pruebas + Pulido (pendiente)
- Validar con Excel real "Las Heras"
- Onboarding IA para nuevos clientes
- Pruebas automatizadas backend

## Estado actual del backend

Endpoints principales disponibles hoy:
- `GET /health`
- `POST /budgets`
- `GET /budgets`
- `GET /budget/{budget_id}`
- `DELETE /budget/{budget_id}`
- `POST /budget/{budget_id}/items`
- `PATCH /budget/{budget_id}/item/{item_id}`
- `GET /budget/{budget_id}/tree`
- `POST /budget/import-excel`
- `POST /budget/{budget_id}/analyze-plan`
- `POST /budget/{budget_id}/items/from-ai`
- `POST /budget/{budget_id}/indirects`
- `GET /budget/{budget_id}/analysis`
- `GET /budget/{budget_id}/export/excel`
- `POST /budget/{budget_id}/version`
- `GET /budget/{budget_id}/versions`
- `GET /budget/{budget_id}/version/{version_id}`

Pendientes importantes para próximas iteraciones:
- Import Excel que persista árbol jerárquico real en `budget_items`
- Export PDF
- Análisis por categorías reales
- Pruebas automatizadas y validación end-to-end contra datos reales

## Problemas resueltos (para no repetir)

| Problema | Causa | Solución |
|----------|-------|----------|
| Build falla con error Rust/Cargo | Render usa Python 3.14 por defecto, sin wheels para pydantic-core | Setear `PYTHON_VERSION=3.11.9` en Render Environment |
| `--prefer-binary` no alcanza solo | Render free buildpack igual intenta compilar | Agregar `Dockerfile` con `python:3.11-slim` en repo |
| `python-jose[cryptography]` conflicto | Dependencias Rust en Render free | Reemplazar por `pyjwt[crypto]` |
| RLS policy error SETOF | `get_my_org_ids()` es set-returning | Usar `IN (SELECT ...)` no `= ANY(...)` |
| JWT inválido con tokens nuevos | Supabase migró a ECC P-256 | JWKS client con `PyJWKClient` |
| `item.dict()` deprecation warning | Pydantic v2 | Usar `item.model_dump()` |
