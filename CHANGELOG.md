# Changelog

Todas las versiones notables del proyecto se documentan aca.
Formato basado en [Keep a Changelog](https://keepachangelog.com/).
Versionado segun [Semantic Versioning](https://semver.org/).

## [3.1.1] — 2026-04-06

### Corregido
- Frontend restaurado a v3.1.0 (commit d0d2c3f) tras regresion estetica causada por Sprints
- Null safety en format.ts (fmtCurrency/fmtNumber/fmtPercent aceptan null/undefined)
- ACUERDOS_CON_CARLOS.md restaurado con historial completo (sobreescrito por error)

### Nota
- Todos los cambios backend de v3.0.0 se mantienen (motor calculo, IA, templates, etc.)
- Solo se restauro el frontend a la estetica aprobada por Carlos en v3.1.0

---

## [3.0.0] — 2026-04-05

### Agregado
- Motor de calculo cascada: recursos → unitarios → directo → indirectos → beneficio → impuestos → IVA → total final (`app/calculations.py`)
- IA con contexto de catalogo: GPT-4o Vision recibe los catalogos del usuario y genera items CON recursos desglosados (`app/routers/ai.py`)
- CRUD de recursos por item: crear, editar, eliminar, bulk (`app/routers/budgets.py`)
- Endpoint cascade-recalculate: recalcula TODO desde recursos hasta total final (`app/routers/analysis.py`)
- Sistema de templates reutilizables: CRUD + aplicar a items (`app/routers/templates.py`)
- 12 templates TERRAC con codigos reales (H30, LP18, ARG, MO-OF, SUB-PI, etc.)
- Pagina Templates en sidebar (`frontend/src/pages/Templates.tsx`)
- Boton "Cargar template" en detalle de item con modal de seleccion
- ItemDetail reescrito: 5 secciones de recursos (Materiales, MO Personas, MO Equipos, Mat. Indirectos, Subcontratos)
- Cadena de Markups completa: 9 campos editables (Imprevistos, Estructura, Jefatura, Logistica, Herramientas, Beneficio, IIBB, Imp.Cheque, IVA)
- CostSummaryBar expandible: 5 tarjetas base + Beneficio y Total c/IVA cuando hay datos
- Auto-recalculo al editar celdas (sin boton)
- Boton "Recalculo completo" para cascada desde recursos
- Indicador de catalogos en wizard IA (verde si hay, amarillo si no)
- Badges de estado en espanol (Borrador, En Revision, Aprobado, Enviado)
- Migracion 003: tipos mo_material, campos MO (trabajadores/dias/cargas), impuestos, tabla item_templates
- Documentacion: PLAN_FLUJO_AUTOMATICO.md, INSTRUCTIVO_EJEMPLO_COMPLETO.md, ARQUITECTURA_PLATAFORMA.md, MANUAL_REVISION_SOLE.md

### Corregido
- NewProject crash: StepEstructura no destructuraba templateTasks de props (bug pre-existente)
- Boton detalle por fila invisible: Editor no pasaba onViewDetail a DataTable
- Analysis KPIs desaparecidos: restauradas 3 tarjetas grandes + 6 KPI mini
- Pantalla en blanco por null en format: fmtCurrency/fmtNumber/fmtPercent ahora toleran null
- CostSummaryBar crash: props beneficio/totalFinal no aceptadas por version vieja
- Deploy Render fallaba: CatalogEntryCreate/Update schemas perdidas durante merge
- Altura hardcodeada calc(100vh-340px) reemplazada por flex layout responsive

### Cambiado
- Cascada indirectos: beneficio ahora se aplica sobre Subtotal con Indirectos (no sobre Directo)
- Indirectos incluyen: imprevistos_pct, ingresos_brutos_pct, imp_cheque_pct, iva_pct

---

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
