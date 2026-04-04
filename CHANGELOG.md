# Changelog

Todas las versiones notables del proyecto se documentan aca.
Formato basado en [Keep a Changelog](https://keepachangelog.com/).
Versionado segun [Semantic Versioning](https://semver.org/).

## [3.1.0] — 2026-04-04

### Agregado
- **Botón borrar items**: icono Trash2 por fila con confirmación inline (Si/No)
- **Botón ver detalle por fila**: icono Eye por cada item, reemplaza botón global ambiguo
- **Selector de vistas en Analysis**: 4 vistas (Rubro/Piso/Material/Gremio) con reagrupación de tabla
- **Botón ? popover**: explicación de cada vista, reemplaza tooltips cortados
- **Separación click flecha vs texto en árbol**: flecha expande/contrae, texto selecciona

### Cambiado
- **CostSummaryBar rediseñado**: de 5 cards individuales a barra horizontal con divide-x (igual que Analysis)
- **DataTable header**: de negro bg-[#143D34] a teal suave bg-[#E8F5EE] — consistente con la estética
- **DataTable filas**: sin bordes pesados, alternado sutil, hover teal
- **DataTable footer**: teal suave en vez de gradient gris
- **Analysis layout**: h-full flex flex-col, solo las filas scrollean, header fijo
- **Analysis summary**: barra horizontal compacta con divide-x
- **Renombrado Tipo → Gremio**: más claro para el usuario
- **Scroll global corregido**: html/body/#root height:100% overflow:hidden

### Corregido
- **Fix error 422**: createItem envía array como espera el backend
- **Fix items mostrando datos equivocados**: getItemsForNode prioriza leaf-first
- **Fix parent_id al agregar items**: findSectionParent busca la sección, no usa leaf seleccionado
- **Fix "Ver detalle" navegaba al item equivocado**: eliminado botón global, reemplazado por ojo por fila

## [3.0.0] — 2026-04-04

### Agregado
- **Frontend completo**: React 19 + Vite + Tailwind + TypeScript (10 pantallas)
- **Wizard nuevo proyecto**: 5 pasos (datos, precios, estructura, indirectos, resultado)
- **IA + Planos**: GPT-4o Vision analiza planos arquitectonicos y sugiere items automaticamente
- **Lista generica de tareas**: 42 tareas comunes de construccion en 6 categorias (obrador, estructura, albanileria, instalaciones, terminaciones, especiales)
- **4 vistas multiples en Editor**: por rubro, por piso/planta, por material, por tipo de trabajo
- **Edicion inline**: click en celdas punteadas, recalculo automatico de totales
- **Audit trail**: tabla item_audits registra cada cambio manual (campo, valor viejo/nuevo, usuario)
- **Sidebar contextual**: detecta si estas dentro de un presupuesto y muestra links relevantes
- **Exportar PDF/Excel**: botones conectados al backend con manejo de errores
- **Catalogos**: aplicar lista de precios a presupuesto desde frontend
- **Actividad reciente**: Dashboard muestra ultimos presupuestos reales con timestamps
- **Deploy**: Vercel (frontend) + Render (backend) con CORS configurado

### Cambiado
- Analysis.tsx usa datos reales del API (no hardcodeados)
- Editor.tsx agrupa items por codigo de seccion para arboles planos
- ItemDetail.tsx muestra costos del item directamente (no solo de recursos)
- Todas las paginas limpiadas de datos demo "Las Heras"

### Infraestructura
- Modelo C: auth compartida (EOS Supabase) + data separada (Supabase propio)
- Dual Supabase client: `AUTH_SUPABASE_*` y `DATA_SUPABASE_*`
- Fallback automatico a `SUPABASE_URL/KEY` si no estan las nuevas variables
- DEMO_ORG_ID mode para desarrollo sin JWT

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


Documentación de versionado

Te recomiendo 3 lugares, cada uno con un propósito distinto:

Dónde	Qué va	Para quién
ARQUITECTURA.md (en el repo)	Reglas técnicas, modelo de datos, endpoints, decisiones de diseño	Para cualquier IA o dev que toque el código
CHANGELOG.md (en el repo)	Lista cronológica de cambios por versión — qué se agregó, qué se arregló, qué se rompió	Para vos, para saber qué cambió y cuándo
Memory de Claude (ya existe)	Contexto del proyecto, tus preferencias, lo que no debe repetirse	Para mí, para no olvidar entre conversaciones
No necesitás hacer nada — yo mantengo los tres actualizados cada vez que hago un cambio.

2. Versionado
El estándar se llama Semantic Versioning (SemVer). Funciona así:

MAYOR.MENOR.PARCHE
  │      │      │
  │      │      └── Arreglo de bugs, cambios chicos (no cambia comportamiento)
  │      └────────── Feature nuevo (algo que antes no existía)
  └───────────────── Cambio que rompe compatibilidad (ej: cambio de base de datos)

Ejemplo práctico para tu proyecto:
Versión	Qué pasó
1.0.0	Monolito original (lo que hizo Grok/Codex)
2.0.0	Reescritura completa que hicimos hoy (rompe todo lo anterior)
2.1.0	Modelo C: dual Supabase (feature nuevo)
2.1.1	Fix: corregir parseo de Excel para otro formato
2.2.0	Nuevo endpoint de export PDF
3.0.0	Cambio de Supabase a otro proveedor (rompe compatibilidad)
Regla simple:
Arreglé un bug → sumo el último número (2.1.0 → 2.1.1)
Agregué algo nuevo → sumo el del medio, reseteo el último (2.1.1 → 2.2.0)
Cambié algo que rompe lo anterior → sumo el primero, reseteo los otros (2.2.0 → 3.0.0)
En la práctica:
Cada vez que hago un commit importante, actualizo la versión en pyproject.toml y agrego la entrada en CHANGELOG.md. Vos no tenés que hacer nada.

Hoy estamos en 2.0.0. Cuando implemente el Modelo C, pasa a 2.1.0.