# Changelog

Todas las versiones notables del proyecto se documentan aca.
Formato basado en [Keep a Changelog](https://keepachangelog.com/).
Versionado segun [Semantic Versioning](https://semver.org/).

## [2.1.0] — En desarrollo

### Agregado
- Modelo C: auth compartida (EOS Supabase) + data separada (Supabase propio)
- Dual Supabase client: `AUTH_SUPABASE_*` y `DATA_SUPABASE_*`
- Fallback automatico a `SUPABASE_URL/KEY` si no estan las nuevas variables
- Migracion SQL sin dependencia de `get_my_org_ids()`

### Cambiado
- `app/config.py` — 4 variables nuevas con fallback
- `app/db.py` — dos clientes: `get_auth_db()` y `get_data_db()`
- `app/auth.py` — usa cliente auth
- Todos los routers — usan cliente data

## [2.0.0] — 2026-04-03

### Cambiado (breaking)
- Reescritura completa del backend
- Monolito de 537 lineas → 12 archivos modulares en 5 routers
- Modelo de datos nuevo: budget_items con desglose MAT/MO/directo/indirecto/beneficio/neto
- `get_current_user()` devuelve `org_id` (ya no `tenant_id`)
- URLs RESTful consistentes: todo bajo `/budgets/`
- OpenAI lazy: servidor arranca sin API key

### Agregado
- Tablas nuevas: `item_resources`, `price_catalogs`, `catalog_entries`
- Import Excel lee TODAS las hojas del formato Las Heras (catalogos + 01_C&P + detalle)
- Analisis IA con prompt JSON estructurado y validacion de respuesta
- 31 tests automatizados
- `ARQUITECTURA.md` reescrito
- `pyproject.toml` con config de pytest

### Eliminado
- `main-sprint2.py` (backup muerto)
- `utils/supabase_client.py` (reemplazado por `app/auth.py` + `app/db.py`)
- `migration_sprint2.sql` (absorbido en `001_base.sql`)

## [1.0.0] — 2026-03-18

### Agregado (version original por Grok/Codex)
- Sprint 0: Setup FastAPI + Supabase + Render + 6 tablas
- Sprint 1: CRUD presupuestos, arbol jerarquico, parser Excel basico
- Sprint 2: GPT-4o Vision para planos, indirectos ponderados
- Sprint 3: Export Excel, versionado/snapshots
- Deploy en Render free tier
- Auth JWT con JWKS (ES256)

### Problemas conocidos (resueltos en 2.0.0)
- Monolito sin estructura
- Import Excel solo leia 2 de 55 hojas
- OpenAI crasheaba si faltaba API key
- N+1 queries en calculo de indirectos
- Naming confuso (tenant_id vs org_id)
- Sin tests
