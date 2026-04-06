# Acuerdos con Carlos — Seguimiento del Proyecto SOLE
**Ultima actualizacion:** 2026-04-06 04:30 AM (hora Argentina)

---

## REGLAS DE TRABAJO ACORDADAS

| # | Regla | Fecha acordada |
|---|-------|---------------|
| R1 | Claude Opus PLANIFICA y AUDITA. Sonnet PROGRAMA. Opus NO programa. | 2026-04-04 |
| R2 | Autonomia total: no hacer de mensajero entre IAs | 2026-04-04 |
| R3 | Responder punto por punto, sin rodeos | 2026-04-04 |
| R4 | Documentar todo en este archivo con fecha y hora | 2026-04-06 |
| R5 | Actualizar CHANGELOG.md con cada version | 2026-04-06 |
| R6 | NO deployar sin verificar que la estetica no se rompa | 2026-04-06 |
| R7 | Antes de corregir, EXPLICAR que se hara y por que | 2026-04-06 |

---

## SESION 2026-04-04 / 04-05 (noche completa)

### Logros
- Arreglados 10+ bugs de calculo y estetica (ver CHANGELOG 2.x)
- Unificada estetica Editor/Analysis (header verde #E8F5EE, footer sticky, sin divisores)
- Beneficio separado de Indirecto en calculo y en columna
- Catalogos CRUD completo + CSV upload flexible
- CostSummaryBar con 5 tarjetas gradient
- Dashboard con busqueda y filtros

### Lo que Carlos pidio y quedo pendiente
- Flujo automatico de punta a punta (IA → recursos → precios → calculo)
- Templates reutilizables con codigos TERRAC
- Cascada de indirectos real (beneficio sobre subtotal, no sobre directo)
- Impuestos (IIBB, cheque) e IVA en la cadena

---

## SESION 2026-04-05 / 04-06 (madrugada)

### 04-05 ~01:00 — Carlos explica el flujo real del arquitecto
- Del plano salen cantidades (m3, m2, ml)
- Cada item tiene composicion unitaria (materiales por m3, MO por m2, etc.)
- Lista de precios pasa por el valor unitario compuesto
- Planilla final hace el producto

### 04-05 ~01:30 — Analisis de Excels
- Agente analizo los 4 Excels de TERRAC (Las Heras, Lugones, El Encuentro)
- Identifico estructura de 6 capas: catalogos → analisis unitario → presupuesto → indirectos → venta → resumenes
- 5 secciones por analisis: materiales, MO personas, MO equipos, MO materiales, subcontratos

### 04-05 ~02:00 — Plan de 6 Sprints armado y aprobado
Carlos autorizo arrancar todos los sprints.

| Sprint | Que | Estado |
|--------|-----|--------|
| 1 | DB migrations + motor calculo cascada | COMPLETADO |
| 2 | IA con contexto de catalogo + recursos | COMPLETADO |
| 3 | Frontend editor de recursos (ItemDetail) | COMPLETADO |
| 4 | Cascada indirectos frontend (MarkupChain, CostSummaryBar) | COMPLETADO |
| 5 | Biblioteca de templates + 12 templates TERRAC | COMPLETADO |
| 6 | Pulido: badges espanol, auto-recalc, indicador catalogos | COMPLETADO |

### 04-05 ~03:00 — Deploys y problemas
- SQL migracion 003 ejecutada OK en Supabase
- INSERT 12 templates TERRAC ejecutado OK
- Deploy frontend Vercel OK
- Deploy backend Render FALLABA: CatalogEntryCreate schema perdida en merge → corregido
- Templates no aparecian: habia que mergear a main para que Render deploye → corregido

### 04-05 ~03:30 — Errores de estetica
- Agentes de Sprint 4 SOBREESCRIBIERON la estetica aprobada del Editor/Analysis
- Se hicieron multiples intentos de restauracion
- Causa raiz: los agentes no tenian contexto de la estetica aprobada y la reescribieron
- LECCION APRENDIDA: siempre verificar diff de estetica antes de deployar

### 04-06 ~04:00 — Investigacion y fixes finales
- Auditoria completa: diff de 956894a vs HEAD para cada archivo
- 4 bugs identificados y explicados a Carlos ANTES de corregir:
  1. NewProject crash (bug pre-existente, templateTasks sin destructurar)
  2. Boton detalle por fila invisible (Editor no pasaba onViewDetail)
  3. Analysis KPIs desaparecidos (agente los reemplazo con CostSummaryBar)
  4. Altura hardcodeada (calc 100vh-340px) cortaba contenido

### 04-06 ~04:30 — Documentacion
- CHANGELOG.md actualizado con version 3.0.0
- ACUERDOS_CON_CARLOS.md creado (este archivo)
- MANUAL_REVISION_SOLE.md creado para colaboradora

---

## ARQUITECTURA ACORDADA: 3 CAPAS

| Capa | % | Que incluye |
|------|---|-------------|
| UNIVERSAL | 85% | Motor calculo, IA, editor, dashboard, CRUD, auth |
| SECTOR | 10% | Templates genericos AR, impuestos AR, unidades estandar |
| CLIENTE | 5% | Catalogos propios, templates con sus codigos, % indirectos |

**Primer cliente: TERRAC** — catalogos cargados (330+ items), 12 templates con sus codigos
**Proximos:** YOPACTO, YANIBELLI (pendiente recibir cotizaciones)

---

## PENDIENTES INMEDIATOS

| # | Tarea | Prioridad | Estado |
|---|-------|-----------|--------|
| P1 | Verificar que los 4 fixes esten correctos post-deploy | URGENTE | En curso |
| P2 | Probar flujo completo: plano → IA con catalogo → recursos → calculo | ALTA | Pendiente |
| P3 | Dropdown de catalogo al agregar recurso manualmente | MEDIA | Pendiente |
| P4 | Activar auth guard (login real) | MEDIA | Pendiente |
| P5 | Crear mas templates TERRAC (faltan muchos items) | MEDIA | Pendiente |
| P6 | Importar historial de presupuestos TERRAC | BAJA | Pendiente |
| P7 | Flujo onboarding para nuevos clientes | BAJA | Pendiente |

---

## PENDIENTES FUTUROS (post-demo)

| # | Tarea | Prioridad |
|---|-------|-----------|
| F1 | Vista VENTA (planilla para el cliente, solo Total Final) | Media |
| F2 | Resumen por m2 (USD/m2 como Excel Las Heras) | Media |
| F3 | Templates Durlock, Steel Frame, instalaciones completas | Media |
| F4 | Multi-usuario con roles (arquitecto, contratista, cliente) | Baja |
| F5 | Calculo automatico de cantidades desde plano (IA mide dimensiones) | Baja |
| F6 | Export PDF profesional | Media |
