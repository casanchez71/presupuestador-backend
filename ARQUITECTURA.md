# Presupuestador Backend v2

Backend para estimacion de presupuestos de obra de construccion.

## Stack
- Python 3.11 + FastAPI
- Supabase (PostgreSQL + RLS)
- Deploy: Render (free tier)
- Frontend: React 18 + Vite (repo aparte)

## Estructura
```
app/
  config.py       # Env vars tipadas (pydantic-settings)
  main.py         # App factory, CORS, routers
  auth.py         # JWT JWKS (ES256/HS256)
  db.py           # Supabase client
  schemas.py      # Modelos Pydantic (request/response)
  tree.py         # Utilidades: arbol, normalizacion, parseo
  routers/
    health.py     # GET /, GET /health
    budgets.py    # CRUD budgets + items + tree
    excel.py      # Import/export Excel
    ai.py         # Analisis de planos (GPT-4o Vision)
    analysis.py   # Indirectos + analisis + versiones
migrations/
  001_base.sql    # 8 tablas con RLS
tests/
```

## Modelo de datos (8 tablas)

| Tabla | Funcion |
|-------|---------|
| `budgets` | Cabecera del presupuesto |
| `budget_items` | Items con desglose: MAT/MO/directo/indirecto/beneficio/neto |
| `item_resources` | Detalle por item: materiales, MO, equipos, subcontratos |
| `price_catalogs` | Catalogos de precios importados |
| `catalog_entries` | Entradas del catalogo (material/MO/equipo/subcontrato) |
| `indirect_config` | Porcentajes de indirectos por organizacion |
| `budget_versions` | Snapshots completos |
| `audit_logs` | Registro de cambios en items |

Todas con RLS: `org_id IN (SELECT public.get_my_org_ids())`

## Formato Excel soportado (Las Heras)

El import lee todas estas hojas:

**Catalogos de precios:**
- `00_Mat` — Materiales (~323 items): CODIGO, descripcion, UNIDAD, PRECIO CON/SIN IVA
- `00_MO` — Mano de obra (4 categorias): Capataz, Puntero, Oficial, Ayudante
- `00_Eq` — Equipos (~27): Mini Cargadora, Retropala, etc.
- `00_Sub` — Subcontratos (~70): Pintura, Enduido, etc.

**Computo y presupuesto:**
- `01_C&P` — Hoja principal con 26 columnas:
  - Col 0-3: ITEM, DESCRIPCION, UNIDAD, CANTIDAD
  - Col 4-10: Gastos directos unitarios (MAT, MO desglosada, GENERAL)
  - Col 11-13: Gastos directos totales
  - Col 14-16: Gastos indirectos
  - Col 17-19: Beneficios
  - Col 20-25: Total neto (unitario y general)

**Detalle por item (hojas numeradas: 1.1, 1.2, etc.):**
- Seccion MATERIALES: codigo, descripcion, unidad, cantidad, desperdicio%, precio, subtotal
- Seccion MANO DE OBRA: idem con dias
- Seccion EQUIPOS y SUBCONTRATOS

## Reglas obligatorias

### Seguridad
- JWT via JWKS endpoint (ES256 actual, HS256 legacy)
- CORS: `ALLOWED_ORIGINS` env var, nunca `"*"` en produccion
- `.env` nunca en git

### Supabase
- Tenant = `org_id` en `memberships`
- RLS: `IN (SELECT public.get_my_org_ids())` — NO `= ANY(...)`
- Todas las queries filtran por `org_id`

### Python
- Pydantic v2: `model_dump()` (no `dict()`)
- `get_current_user()` devuelve `{"user_id", "org_id"}` (no "tenant_id")
- OpenAI lazy: si falta `OPENAI_API_KEY`, el server arranca igual

### Render
- `PYTHON_VERSION=3.11.9` obligatorio
- `--prefer-binary` en build command
- Dockerfile incluido como fallback

## Variables de entorno

| Key | Requerida | Default |
|-----|-----------|---------|
| `SUPABASE_URL` | Si | — |
| `SUPABASE_KEY` | Si | — |
| `ALLOWED_ORIGINS` | Si | `http://localhost:5173` |
| `OPENAI_API_KEY` | No | — (endpoints IA devuelven 503) |
| `PORT` | No | `8000` |

## Endpoints

### Sistema
- `GET /` — Landing page
- `GET /health` — Health check

### Presupuestos (`/budgets`)
- `POST /budgets` — Crear
- `GET /budgets` — Listar
- `GET /budgets/{id}` — Detalle
- `DELETE /budgets/{id}` — Eliminar
- `POST /budgets/{id}/items` — Agregar items
- `PATCH /budgets/{id}/items/{item_id}` — Editar item (con auditoria)
- `GET /budgets/{id}/tree` — Arbol jerarquico
- `GET /budgets/{id}/full` — Budget + tree + analysis + versions

### Excel (`/budgets`)
- `POST /budgets/import-excel` — Importar Excel completo
- `GET /budgets/{id}/export/excel` — Exportar a Excel

### IA (`/budgets`)
- `POST /budgets/{id}/analyze-plan` — Analizar plano (solo imagenes)
- `POST /budgets/{id}/items/from-ai` — Insertar sugerencias IA

### Analisis (`/budgets`)
- `POST /budgets/{id}/indirects` — Aplicar indirectos
- `GET /budgets/{id}/analysis` — Desglose MAT/MO/Directo/Indirecto/Beneficio/Neto
- `POST /budgets/{id}/versions` — Crear version
- `GET /budgets/{id}/versions` — Listar versiones
- `GET /budgets/{id}/versions/{vid}` — Ver version
