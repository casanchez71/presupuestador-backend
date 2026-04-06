# BRIEFING: Revisión antes del deploy pendiente

> Fecha: 2026-04-06
> De: Agente Opus (sesión de auditoría en eos-saas)
> Para: Agente Opus (sesión serene-wozniak en presupuestador-backend)
> Contexto: Carlos me pidió analizar TODO el historial de git + la conversación completa para detectar regresiones antes de que ejecutes el deploy pendiente.

---

## DEPLOY PENDIENTE

Los 3 comandos que Carlos va a correr:
```bash
cd /Users/carlossanchez/Downloads/presupuestador-backend/.claude/worktrees/serene-wozniak
git push origin claude/serene-wozniak

cd /Users/carlossanchez/Downloads/presupuestador-backend
git merge claude/serene-wozniak
git push origin main

cd /Users/carlossanchez/Downloads/presupuestador-backend/.claude/worktrees/serene-wozniak/frontend
npx vercel deploy --prod --force
```

---

## LO QUE VA A MERGEAR (6 archivos frontend cambian)

| Archivo | Cambio | ¿OK? |
|---------|--------|------|
| `ItemDetail.tsx` | De v3.1.0 (básico) → 5 secciones de recursos + "Cargar template" | ✅ CORRECTO |
| `MarkupChain.tsx` | De 4 campos → 9 campos (imprevistos, IIBB, cheque, IVA) | ✅ CORRECTO |
| `TreeView.tsx` | Click separado: flecha=expandir, nombre=seleccionar | ✅ CORRECTO |
| `MarkupChainDisplay.tsx` | border-b de negro → border-gray-100 | ✅ CORRECTO |
| **`index.css`** | **ELIMINA** `html, body, #root { height: 100%; margin: 0; overflow: hidden; }` | 🔴 **BUG CRÍTICO** |
| **`Catalogs.tsx`** | De 751 líneas (CRUD completo) → 239 líneas (versión básica) | 🔴 **REGRESIÓN** |

---

## 🔴 BUG 1: index.css pierde el scroll fix

La rama `serene-wozniak` tiene una versión VIEJA de `index.css` que NO tiene el fix de scroll global. Al mergear, se va a BORRAR esto:

```css
html, body, #root {
  height: 100%;
  margin: 0;
  overflow: hidden;
}
```

**Impacto**: Toda la página va a hacer scroll (header, sidebar, contenido) en vez de que solo scrollee el contenido interno. Carlos trabajó horas para arreglar esto y lo aprobó. Se va a enojar si se pierde.

**Fix necesario**: ANTES del merge, actualizar `index.css` en serene-wozniak para que incluya ese bloque CSS. O DESPUÉS del merge, restaurar esas 4 líneas.

---

## 🔴 BUG 2: Catalogs.tsx se degrada

La rama `serene-wozniak` tiene la versión VIEJA de Catalogs (239 líneas, solo listar + aplicar).
La versión actual en `main` tiene 751 líneas con:

- `UploadForm` — componente inline para subir CSV como catálogo nuevo
- Tabla completa de entradas (sin `.slice(0,5)`)
- Búsqueda debounced por catálogo
- Edición inline por fila (pencil + save/cancel)
- Eliminar entrada individual
- `AddEntryRow` para agregar entradas manualmente
- Eliminar catálogo completo con confirmación
- Dropdown "Aplicar a presupuesto"

**Impacto**: Se pierde TODO el CRUD de catálogos que se construyó en el sprint 3b26df1. Carlos no va a poder subir CSVs, editar entradas, ni buscar dentro de catálogos.

**Fix necesario**: NO mergear Catalogs.tsx. La versión de main es la correcta. Antes del merge, copiar la versión de main a serene-wozniak, o hacer `git checkout main -- frontend/src/pages/Catalogs.tsx` después del merge.

---

## ⚠️ ARCHIVOS QUE NO CAMBIAN (CONFIRMO QUE NO SE PISAN)

| Archivo | Estado en main | ¿Se pisa? |
|---------|---------------|-----------|
| CostSummaryBar.tsx | v3.1.0 (5 cards gradient) | NO — no cambia |
| DataTable.tsx | v3.1.0 (FileText + Trash2, teal header) | NO — no cambia |
| Analysis.tsx | v3.1.0 | NO — no cambia |
| Editor.tsx | v3.1.0 + Recalcular + indirectConfig | NO — no cambia |
| Dashboard.tsx | v3.1.0 + búsqueda + filtros | NO — no cambia |
| Templates.tsx | Página nueva en sidebar | NO — no cambia |

---

## ⚠️ FEATURES QUE SIGUEN FALTANDO (NO SE RESUELVEN CON ESTE DEPLOY)

Estas mejoras se construyeron en los sprints pero se perdieron cuando se restauró v3.1.0. NO están ni en main ni en serene-wozniak:

1. **Columna "Beneficio"** en DataTable (entre Indirecto y Neto) — se construyó en commit `d7fa64e` pero se restauró la versión sin ella
2. **CostSummaryBar 7 tarjetas** (beneficio + totalFinal) — solo tiene 5 tarjetas
3. **DataTable sticky header/footer** — se intentó 3 veces (`d9a05e7`, `83222df`, `9c74939`) y nunca quedó funcionando. La v3.1.0 tiene `sticky` en el código pero no funciona porque el contenedor padre no tiene altura definida
4. **Footer opaco** — main tiene `bg-[#E8F5EE]` (opaco) que está OK, pero el sticky no funciona por la razón anterior
5. **Botón "Recalcular" con applyIndirects** — Editor tiene `handleRecalculate` pero solo llama `budgetApi.recalculate(id)`, NO llama `budgetApi.applyIndirects(id)`. Los indirectos no se recalculan realmente.
6. **Status badge dropdown** — Editor tiene `handleStatusChange` pero la UI del dropdown de estados (Borrador→Revisión→Aprobado→Enviado) puede no estar completa

---

## RECOMENDACIÓN DE ACCIÓN

### ANTES del deploy, corregir en serene-wozniak:

1. **index.css**: Agregar el bloque CSS del scroll fix
2. **Catalogs.tsx**: Copiar la versión de main (751 líneas) al worktree para que no se degrade

### DESPUÉS del deploy:

3. Verificar visualmente: ¿la página scrollea entera o solo el contenido?
4. Verificar: ¿Catálogos tiene búsqueda, upload CSV, editar/borrar?
5. Verificar: ¿ItemDetail muestra 5 secciones de recursos y botón "Cargar template"?
6. Verificar: ¿TreeView separa click flecha vs click nombre?

### EN UN PRÓXIMO SPRINT (no ahora):

7. Agregar columna Beneficio a DataTable
8. CostSummaryBar con 7 tarjetas
9. Sticky header/footer real (requiere fix del contenedor con altura)
10. Recalcular que también aplique indirectos

---

## HISTORIAL COMPLETO DE COMMITS (referencia)

### v3.1.0 — La versión dorada (commits `691b251` a `d0d2c3f`)
- Scroll global fix
- TreeView click separado
- DataTable con FileText + Trash2 por fila, teal header
- CostSummaryBar 5 cards gradient
- Analysis unificada con Editor
- Memoria de cálculo
- Marca "Editado por humano"
- Dashboard búsqueda + filtros
- CRUD catálogos completo

### Sprints 1-6 (commit `0afb5c4` + `3b26df1`)
- Backend: motor de cálculo cascada, IA con catálogo, recursos, templates
- Frontend: ItemDetail 5 secciones, MarkupChain 9 campos, Catalogs CRUD, Dashboard filtros, Editor Recalcular

### El desastre (commit `0b32a6d`)
- `git checkout --theirs` sobreescribió frontend v3.1.0 con versiones sprint
- 8 intentos de restauración parcial
- Restauración final desde `d0d2c3f` (commit `03afa49`) recuperó estética pero perdió features sprint

### Estado actual en main (`1e8e597`)
- Frontend: v3.1.0 restaurado + Templates.tsx + format.ts null-safety
- Backend: COMPLETO con todo (sprints + fixes)
