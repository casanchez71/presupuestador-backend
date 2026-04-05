# PLAN MAESTRO — Flujo Automático de Presupuestos
**Fecha:** 2026-04-05
**Objetivo:** Que del plano salga un presupuesto completo, calculado y costeado automáticamente

---

## CÓMO FUNCIONA HOY (incompleto)

```
Plano ──(IA)──→ Items genéricos ──→ STOP ❌
                 (sin recursos,          (no hay precios,
                  sin códigos,            no hay cálculo,
                  nombres inventados)     no hay nada)
```

## CÓMO VA A FUNCIONAR (el plan)

```
                    ┌─────────────────────────────┐
                    │     CATÁLOGOS DEL USUARIO    │
                    │  00_Mat: MAT-001..MAT-280    │
                    │  00_MO:  MO-CA, MO-OF...     │
                    │  00_Eq:  EQ-001..EQ-024      │
                    │  00_Sub: SUB-PI, SUB-E...    │
                    └──────────┬──────────────────┘
                               │ (se pasan al prompt)
                               ▼
Plano ──(IA con catálogo)──→ Items + Recursos por item
                               │
                               │ Cada item tiene:
                               │  ├─ Materiales: código, qty, desperdicio
                               │  ├─ MO Personas: trabajadores, días, cargas
                               │  ├─ MO Equipos: código, qty
                               │  ├─ MO Mat.Indirectos: clavos, fenólicos
                               │  └─ Subcontratos: código, qty
                               │
                               ▼
                    ┌─────────────────────────────┐
                    │   AUTO-MATCH DE PRECIOS      │
                    │  código recurso → catálogo   │
                    │  → asigna precio_unitario    │
                    └──────────┬──────────────────┘
                               │
                               ▼
                    ┌─────────────────────────────┐
                    │   CÁLCULO EN CASCADA         │
                    │                              │
                    │  Recursos:                   │
                    │   qty × desperdicio × precio │
                    │   = subtotal por recurso     │
                    │                              │
                    │  → sum(materiales) / qty_item │
                    │    = mat_unitario             │
                    │  → sum(MO+EQ+MatInd+Sub)/qty │
                    │    = mo_unitario              │
                    │                              │
                    │  × cantidad del plano        │
                    │  = DIRECTO                   │
                    │                              │
                    │  + Imprevistos 3%            │
                    │  + Estructura 5.6%           │
                    │  + Jefatura 5.6%             │
                    │  = SUBTOTAL 02 (con indir.)  │
                    │                              │
                    │  + Beneficio 25% s/Subt.02   │
                    │  = SUBTOTAL 03               │
                    │                              │
                    │  + IIBB 7% s/Subt.03         │
                    │  + Imp.Cheque 1.2% s/Subt.03 │
                    │  = NETO                      │
                    │                              │
                    │  + IVA 21% s/Neto            │
                    │  = TOTAL FINAL               │
                    └─────────────────────────────┘
```

---

## SPRINT 1: Base de Datos + Motor de Cálculo (Backend)

### Lo que existe hoy y sirve:
- Tabla `item_resources` YA tiene: tipo (material/mano_obra/equipo/subcontrato), codigo, desperdicio_pct, cantidad_efectiva, precio_unitario, subtotal
- Tabla `budget_items` YA tiene: mat_unitario, mo_unitario, directo_total, indirecto_total, beneficio_total, neto_total
- Tabla `indirect_config` YA tiene: estructura_pct, jefatura_pct, logistica_pct, herramientas_pct, beneficio_pct

### Cambios en DB necesarios:

```sql
-- 1. Agregar tipo 'mo_material' a item_resources (materiales indirectos: clavos, fenólicos, alambre)
ALTER TABLE item_resources DROP CONSTRAINT IF EXISTS item_resources_tipo_check;
ALTER TABLE item_resources ADD CONSTRAINT item_resources_tipo_check
  CHECK (tipo IN ('material', 'mano_obra', 'equipo', 'subcontrato', 'mo_material'));

-- 2. Columnas para mano de obra (trabajadores × días × cargas sociales)
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS trabajadores numeric DEFAULT 0;
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS dias numeric DEFAULT 0;
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS cargas_sociales_pct numeric DEFAULT 25;

-- 3. Vincular recurso a entrada de catálogo
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS catalog_entry_id uuid REFERENCES catalog_entries(id);

-- 4. Campos de impuestos en indirect_config
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS imprevistos_pct numeric DEFAULT 3;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS ingresos_brutos_pct numeric DEFAULT 7;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS imp_cheque_pct numeric DEFAULT 1.2;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS iva_pct numeric DEFAULT 21;

-- 5. Campos de totales expandidos en budget_items
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS impuestos_total numeric DEFAULT 0;
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS iva_total numeric DEFAULT 0;
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS total_final numeric DEFAULT 0;

-- 6. Asegurar que notas_calculo y beneficio_pct estén en migraciones
-- (ya existen en prod por ALTER TABLE manual, pero formalizamos)
```

### Nuevos endpoints backend:

```
POST   /budgets/{id}/items/{item_id}/resources       → Crear recurso + auto-recalcular
PATCH  /budgets/{id}/items/{item_id}/resources/{rid}  → Editar recurso + auto-recalcular
DELETE /budgets/{id}/items/{item_id}/resources/{rid}  → Eliminar recurso + auto-recalcular
POST   /budgets/{id}/items/{item_id}/resources/bulk   → Crear múltiples recursos (para IA)
POST   /budgets/{id}/cascade-recalculate              → Recalcular TODO desde recursos
```

### Motor de cálculo (función calc_from_resources):

```python
def calc_from_resources(item, resources):
    """Calcula precios unitarios desde los recursos del item."""
    mat_total = sum(r.subtotal for r in resources if r.tipo == 'material')
    mo_total = sum(r.subtotal for r in resources if r.tipo == 'mano_obra')
    eq_total = sum(r.subtotal for r in resources if r.tipo == 'equipo')
    mat_ind_total = sum(r.subtotal for r in resources if r.tipo == 'mo_material')
    sub_total = sum(r.subtotal for r in resources if r.tipo == 'subcontrato')

    qty = item.cantidad or 1

    # Precio unitario = total sección / cantidad del item
    item.mat_unitario = round(mat_total / qty, 2)
    item.mo_unitario = round((mo_total + eq_total + mat_ind_total + sub_total) / qty, 2)

    # Totales directos
    item.mat_total = round(item.mat_unitario * qty, 2)
    item.mo_total = round(item.mo_unitario * qty, 2)
    item.directo_total = item.mat_total + item.mo_total

def calc_resource_subtotal(resource):
    """Calcula el subtotal de un recurso individual."""
    if resource.tipo == 'mano_obra':
        # trabajadores × días × (1 + cargas/100) × precio_unitario (jornal)
        dias_totales = (resource.trabajadores or 0) * (resource.dias or 0)
        con_cargas = dias_totales * (1 + (resource.cargas_sociales_pct or 25) / 100)
        resource.cantidad_efectiva = round(con_cargas, 2)
        resource.subtotal = round(con_cargas * (resource.precio_unitario or 0), 2)
    else:
        # cantidad × (1 + desperdicio/100) × precio_unitario
        qty_efectiva = (resource.cantidad or 0) * (1 + (resource.desperdicio_pct or 0) / 100)
        resource.cantidad_efectiva = round(qty_efectiva, 2)
        resource.subtotal = round(qty_efectiva * (resource.precio_unitario or 0), 2)

def apply_cascade_indirects(budget_id, config):
    """Aplica indirectos escalonados estilo Excel real."""
    # Para cada item:
    directo = item.directo_total

    # Paso 1: Indirectos
    pct_ind = (config.imprevistos_pct + config.estructura_pct
               + config.jefatura_pct + config.logistica_pct
               + config.herramientas_pct) / 100
    indirecto = round(directo * pct_ind, 2)
    subtotal_02 = directo + indirecto

    # Paso 2: Beneficio SOBRE subtotal_02
    beneficio = round(subtotal_02 * (config.beneficio_pct / 100), 2)
    subtotal_03 = subtotal_02 + beneficio

    # Paso 3: Impuestos SOBRE subtotal_03
    impuestos = round(subtotal_03 * ((config.ingresos_brutos_pct + config.imp_cheque_pct) / 100), 2)
    neto = subtotal_03 + impuestos

    # Paso 4: IVA SOBRE neto
    iva = round(neto * (config.iva_pct / 100), 2)
    total_final = neto + iva
```

---

## SPRINT 2: IA con Contexto de Catálogo

### Modificar el prompt de la IA para incluir catálogos

Antes de llamar a GPT-4o Vision, cargar TODOS los catálogos del usuario y pasarlos como contexto:

```
"Tenés disponibles estos catálogos de precios:

MATERIALES:
- H30: Hormigón H-30, m3, $158,000
- HADN6: Hierro ADN Ø6, barra 12m, $5,250
- LP18: Ladrillo portante 18cm, u, $1,377
- CEM: Cemento bolsa 50kg, bolsa, $7,000
...

MANO DE OBRA:
- MO-CA: Capataz, jornal, $120,000
- MO-OF: Oficial, jornal, $90,000
- MO-AY: Ayudante, jornal, $60,000
...

EQUIPOS:
- EQ-MINI: Mini cargadora, día, $85,000
...

SUBCONTRATOS:
- SUB-PI: Pintura interior, m2, $15,000
...

Para cada item que generes, DEBÉS incluir la composición de recursos usando
los códigos de arriba. Ejemplo para Hormigón H30 columnas:
{
  'codigo': '1.1',
  'descripcion': 'Hormigón H-30 columnas',
  'unidad': 'm3',
  'cantidad': 23,
  'recursos': {
    'materiales': [
      {'codigo': 'H30', 'cantidad_por_unidad': 1.0, 'desperdicio_pct': 10},
      {'codigo': 'HADN6', 'cantidad_por_unidad': 9.0, 'desperdicio_pct': 10}
    ],
    'mano_obra': [
      {'codigo': 'MO-OF', 'trabajadores': 4, 'dias_por_unidad': 0.33, 'cargas_sociales_pct': 25}
    ],
    'equipos': [...],
    'mo_materiales': [...],
    'subcontratos': [...]
  }
}"
```

### Nuevo flujo del endpoint from-ai:

```
1. IA retorna items + recursos
2. Backend crea budget_items
3. Backend crea item_resources por cada recurso
4. Backend busca cada codigo en catalog_entries → asigna precio y catalog_entry_id
5. Backend ejecuta calc_resource_subtotal() por cada recurso
6. Backend ejecuta calc_from_resources() por cada item
7. Backend ejecuta apply_cascade_indirects() para todo el presupuesto
8. → Presupuesto completo, calculado, listo
```

---

## SPRINT 3: Frontend — Editor de Recursos

### ItemDetail.tsx renovado:
- 5 secciones colapsables: Materiales | MO Personas | MO Equipos | MO Mat.Indirectos | Subcontratos
- Cada sección muestra tabla:
  | Código | Descripción | Unidad | Cantidad | Desperdicio | Qty.Efectiva | Precio | Subtotal |
- Para MO: | Código | Descripción | Trabajadores | Días | Cargas | Jornales | Precio | Subtotal |
- Pie de cada sección: Total → ÷ cantidad del item = Precio unitario
- Botón "Agregar recurso" con selector de catálogo
- Al editar cualquier campo → auto-recalcular
- Al eliminar recurso → auto-recalcular

### DataTable.tsx ampliado:
- Agregar columnas: Impuestos, IVA, Total Final (opcionales, toggle)
- O simplificar: Directo | Indirecto | Beneficio | Impuestos | Total Final

### MarkupChain.tsx ampliado:
- Agregar filas: Imprevistos %, Ingresos Brutos %, Imp. Cheque %, IVA %
- Mostrar la cascada: "Beneficio se aplica sobre Subtotal con Indirectos"

---

## SPRINT 4: Cascada de Indirectos Real

### Cambiar apply_indirects para usar el modelo escalonado:
```
Subtotal 01 = Σ(directo de cada item)
+ Imprevistos (3% de Subt.01)
+ Estructura (5.6% de Subt.01)
+ Jefatura (5.6% de Subt.01)
+ Logística + Herramientas
= Subtotal 02

+ Beneficio (25% de Subtotal 02)    ← HOY se aplica sobre Directo, DEBE ser sobre Subt.02
= Subtotal 03

+ Ingresos Brutos (7% de Subt.03)   ← HOY NO EXISTE
+ Imp. Cheque (1.2% de Subt.03)     ← HOY NO EXISTE
= NETO

+ IVA (21% de NETO)                 ← HOY NO EXISTE
= TOTAL FINAL
```

### Impacto en frontend:
- CostSummaryBar muestra: Directo → Indirecto → Beneficio → Impuestos → NETO → IVA → TOTAL
- La vista VENTA (para el cliente) muestra solo TOTAL FINAL
- La vista COSTO (para el arquitecto) muestra todo el desglose

---

## SPRINT 5: Biblioteca de Templates + Historial

### Importar composiciones de los Excels:
- Parsear cada hoja X.Y de los 4 Excels
- Crear tabla `item_templates`:
  | id | nombre | unidad | categoria | recursos (jsonb) |
  | -- | "Hormigón H30 columnas" | m3 | estructura | [{codigo: "H30", qty_per_unit: 1.0, waste: 10}, ...] |

### Uso:
- Al crear un item manualmente → "Cargar desde template" → seleccionar → carga recursos
- La IA también puede referenciar templates en vez de inventar composiciones

---

## SPRINT 6: Pulido + Auto-todo

- Auto-recalcular al editar CUALQUIER celda (sin botón)
- Dashboard badges en español
- Progress indicator del flujo IA: "Analizando plano → Generando items → Costeando → Listo"
- Auth guard activar
- Wizard renovado con el nuevo flujo

---

## ORDEN DE EJECUCIÓN

| Sprint | Qué | Dependencias | Prioridad |
|--------|-----|-------------|-----------|
| 1 | DB + Motor cálculo | Ninguna | 🔴 CRÍTICO |
| 2 | IA con catálogo | Sprint 1 | 🔴 CRÍTICO |
| 3 | Frontend recursos | Sprint 1 | 🟡 ALTO |
| 4 | Indirectos cascada | Sprint 1 | 🟡 ALTO |
| 5 | Templates | Sprint 1 | 🟢 MEDIO |
| 6 | Pulido | Sprints 1-4 | 🟢 MEDIO |

**Sprints 1 es la base de todo. Sprint 2 depende de 1. Sprints 3 y 4 pueden ir en paralelo después de 1.**
