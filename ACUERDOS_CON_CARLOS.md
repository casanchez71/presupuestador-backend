# Acuerdos con Carlos — NO BORRAR hasta que diga OK
# Actualizado: 2026-04-04 18:30

## COMPROMISOS CLAUDE (lo que prometí hacer)
- Responder PUNTO POR PUNTO cada mensaje de Carlos
- Status cada 2 cambios
- No olvidar nada — todo queda acá hasta OK de Carlos
- Hacer deploy SIEMPRE después de cada fix (merge + push + vercel)
- Actualizar CHANGELOG.md con CADA cambio (SemVer)
- Tracking completo en este archivo

## COMPLETADOS (verificados) ✅
1. ~~Wizard IA automático~~ — items se insertan al crear presupuesto con plano
2. ~~Lista genérica 42 tareas comunes~~ — integrado en wizard paso 3
3. ~~4 vistas múltiples~~ — Rubro/Piso/Material/Gremio en Editor + Analysis
4. ~~Exportar PDF/Excel~~ — botones conectados al backend
5. ~~Catálogos aplicar~~ — dropdown + botón aplicar
6. ~~Actividad reciente~~ — datos reales en Dashboard
7. ~~Analysis sin hardcode~~ — muestra datos del presupuesto actual
8. ~~Ver detalle sin crash~~ — ya no pantalla blanca
9. ~~Sidebar contextual~~ — links cambian según presupuesto
10. ~~CHANGELOG.md~~ — actualizado a v3.1.0
11. ~~Selector con contraste~~ — activo=teal, inactivo=gris
12. ~~Botón ? con popover~~ — explicación de cada vista
13. ~~Renombrar Tipo→Gremio~~ — más claro
14. ~~Selector vistas en Analysis~~ — con reagrupación de tabla
15. ~~Fix error 422 al agregar item~~ — backend espera lista, frontend mandaba objeto
16. ~~Renombrar pedidos→acuerdos~~ — incluye compromisos Claude
17. ~~Fix "Ver detalle" navega al item equivocado~~ — ícono ojo por fila
18. ~~Fix scroll global~~ — html/body/root height:100% overflow:hidden
19. ~~Compactar KPIs en Analysis~~ — barra horizontal con divide-x
20. ~~TreeView click separado~~ — flecha=expandir, texto=seleccionar
21. ~~Fix getItemsForNode~~ — leaf-first, no muestra hijos erróneos
22. ~~Fix handleAddItem parent_id~~ — findSectionParent busca sección correcta
23. ~~Estética unificada~~ — CostSummaryBar = Analysis summary bar
24. ~~DataTable header~~ — teal suave bg-[#E8F5EE] sin líneas negras
25. ~~Botón borrar items~~ — Trash2 con confirmación inline

## COMPLETADOS RECIENTES ✅
26. ~~Fase A+B Memoria de Cálculo~~ — notas_calculo en items, visible y editable en Ver Detalle
27. ~~CostSummaryBar restaurado~~ — 5 cards gradient (azul/púrpura/teal/coral/dorado) = diseño aprobado por Carlos
28. ~~Analysis unificado con Editor~~ — usa mismo CostSummaryBar component
29. ~~Línea negra divisoria~~ — MarkupChainDisplay border suavizado a gray-100
30. ~~Marca "editado por humano"~~ — badge sutil en ItemDetail cuando item tiene edits manuales

## SESION 2026-04-06 (madrugada ~01:00 a ~05:00 AR) ✅
31. ~~Analisis de Excels TERRAC~~ — 4 Excels analizados formula por formula (55 hojas)
32. ~~Motor calculo cascada~~ — calc_resource_subtotal, calc_item_from_resources, calc_cascade_indirects
33. ~~IA con contexto de catalogo~~ — prompt incluye codigos del catalogo del usuario
34. ~~IA genera recursos~~ — items CON composicion (materiales, MO, equipos, subcontratos)
35. ~~Migracion 003~~ — tipos mo_material, campos MO, impuestos, tabla item_templates
36. ~~12 templates TERRAC~~ — con codigos reales (H30, ARG, LP18, MO-OF, SUB-PI, etc.)
37. ~~Pagina Templates en sidebar~~ — CRUD completo con filtro por categoria
38. ~~Boton "Cargar template" en ItemDetail~~ — modal de seleccion, aplica recursos
39. ~~Cadena Markups completa~~ — 9 campos: 5 indirectos + beneficio + IIBB + cheque + IVA
40. ~~Backend templates router~~ — CRUD + apply endpoint
41. ~~CHANGELOG v3.0.0~~ — documentada toda la sesion
42. ~~Arquitectura 3 capas~~ — Universal (85%) / Sector (10%) / Cliente (5%)
43. ~~MANUAL_REVISION_SOLE.md~~ — para colaboradora de revision
44. ~~Null safety en format.ts~~ — fmtCurrency/fmtNumber/fmtPercent toleran null
45. ~~RESTAURACION v3.1.0~~ — archivos frontend restaurados del commit d0d2c3f (pre-merge)

### LECCION APRENDIDA (04-06):
Los agentes de los Sprints sobreescribieron archivos de estetica aprobados.
**REGLA NUEVA:** Antes de deployar cambios de frontend, verificar diff de archivos de estetica contra la version aprobada.

## EN CURSO (trabajando ahora) 🔧
(restauracion completa — verificando deploy)

## BACKLOG PRIORITARIO (próximos) 🔴
27. **Vista por planta REAL** — Items se REPITEN por piso (PB, Piso 1, Piso 2... Azotea) cada uno con su cantidad. CRITICO para Terrac.
28. **Separar universal/parametrizable/Terrac** — Config por cliente, parser Excel configurable
29. **Edición inline de precios** — Verificar que funciona en producción

## BACKLOG FUNCIONAL 🟡
30. Comparar versiones lado a lado
31. Tag v3.1.0 en repo presupuestador
32. Aplicar mismo esquema versionado a EOS SaaS

---

## PLAN DETALLADO: FASE C — AGENTE VERIFICADOR INTHEGROW 🧠
### Fecha: 2026-04-04
### Status: EN PLANIFICACIÓN

### 1. Concepto
Triple control de calidad para presupuestos de obra:
- **Nivel 1 — Cálculo (Python/GPT-4o Vision)**: Analiza el plano, extrae medidas, calcula cantidades
- **Nivel 2 — Verificación (Agente INTHEGROW)**: Revisa coherencia automáticamente
- **Nivel 3 — Aprobación (Arquitecto humano)**: Ve cálculo + alertas, aprueba/corrige

### 2. Arquitectura técnica

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  GPT-4o     │     │  Agente SOLE     │     │  Arquitecto     │
│  Vision     │────▶│  (Verificador)   │────▶│  (Humano)       │
│             │     │                  │     │                 │
│ Calcula     │     │ Verifica         │     │ Aprueba/Corrige │
│ cantidades  │     │ coherencia       │     │ cada línea      │
└─────────────┘     └──────────────────┘     └─────────────────┘
      │                     │                        │
      ▼                     ▼                        ▼
┌─────────────────────────────────────────────────────────┐
│              Supabase (misma instancia)                 │
│  budget_items.notas_calculo  │  verification_reports    │
│  item_audits                 │  verification_alerts     │
└─────────────────────────────────────────────────────────┘
```

### 3. Agente Verificador — Detalle

**Ubicación**: Servicio en SOLE (no en Presupuestador). Se conecta al mismo Supabase.

**Trigger**: Se dispara automáticamente cuando:
- Se crea un presupuesto desde un plano (post-AI analysis)
- El usuario solicita "Verificar presupuesto" manualmente

**Qué verifica**:
| Check | Ejemplo | Severidad |
|-------|---------|-----------|
| Ratio m² revoque vs m² planta | 400m² revoque / 80m² planta = 5x → ALTO | 🟡 Warning |
| Items faltantes por tipo de obra | Edificio sin instalación de gas → FALTA | 🔴 Error |
| Cantidades cero en items críticos | Hormigón = 0 m³ en Estructura → CRÍTICO | 🔴 Error |
| Cantidades absurdas | 50 inodoros para 2 baños → ERROR | 🔴 Error |
| Precios unitarios fuera de rango | Hormigón $500/m³ cuando mercado es $45.000 → REVISAR | 🟡 Warning |
| Coherencia entre items | m² pintura ≈ m² revoque → OK | ✅ Pass |
| Secciones vacías | "Instalación Eléctrica" sin items → FALTA | 🟡 Warning |

**Output**: Un `verification_report` con:
```json
{
  "budget_id": "xxx",
  "timestamp": "2026-04-04T18:30:00Z",
  "agent_version": "1.0.0",
  "score": 72,
  "alerts": [
    { "severity": "error", "item_id": "yyy", "message": "0 m³ hormigón en Estructura", "suggestion": "Verificar plano" },
    { "severity": "warning", "item_id": "zzz", "message": "Ratio revoque/planta = 5x (esperado 2.5-3x)", "suggestion": "Revisar cálculo" }
  ],
  "passed_checks": 18,
  "total_checks": 24
}
```

### 4. UI en Presupuestador

**Dashboard del presupuesto**: Badge con score (72/100) y color (verde/amarillo/rojo)
**Panel de verificación**: Lista de alertas agrupadas por severidad
**Por item**: Indicador visual (checkmark verde, warning amarillo, error rojo)
**Acción**: Cada alerta tiene botón "Corregir" que lleva al item correspondiente

### 5. Implementación por etapas

**Etapa C.1 (backend, 2-3 días)**:
- Tabla `verification_reports` y `verification_alerts` en Supabase
- Endpoint POST /budgets/{id}/verify que corre las reglas
- Reglas hardcodeadas iniciales (ratios, checks de coherencia)

**Etapa C.2 (frontend, 2-3 días)**:
- Panel de verificación en el Editor
- Badges de score por presupuesto
- Indicadores por item

**Etapa C.3 (agente SOLE, 1-2 semanas)**:
- Servicio separado en SOLE que se conecta al mismo Supabase
- Usa Claude/GPT para verificaciones semánticas (no solo reglas)
- Se dispara por webhook cuando se crea/modifica presupuesto
- NO requiere segunda instancia de admin — es un endpoint API en SOLE

### 6. Decisión clave: NO dos instancias de admin
El agente verificador es un **servicio backend en SOLE** que:
- Lee datos de Supabase (el mismo que usa Presupuestador)
- Escribe resultados en tablas de verificación
- Se expone como API endpoint que Presupuestador llama
- NO tiene su propia UI de admin — el admin es el Presupuestador mismo

---

## BACKLOG TÉCNICO 🟢
33. Tests test_excel_parser.py
34. Tests test_api.py
35. Parser Excel multi-formato (Lugones, El Encuentro)
36. Moneda/idioma/unidades configurables
