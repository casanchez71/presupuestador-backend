# Manual de Revisión — Presupuestador Inteligente SOLE
**Para:** Colaboradora de revisión
**Fecha:** 5 de Abril 2026
**App:** https://presupuestador-sole.vercel.app/app

---

## Qué es SOLE

SOLE es una app web que genera presupuestos de obra de construcción. El flujo es:

1. Subís un plano de obra (imagen o PDF)
2. La inteligencia artificial analiza el plano y genera los items del presupuesto
3. Cada item tiene un desglose de recursos (materiales, mano de obra, equipos, subcontratos)
4. Los precios se toman automáticamente de los catálogos de precios cargados
5. Se calcula todo: costo directo + indirectos + beneficio + impuestos + IVA = total final

---

## Cómo entrar

1. Ir a **https://presupuestador-sole.vercel.app/app**
2. Si aparece una pantalla de login, ir directo a la URL con `/app` al final
3. No se necesitan credenciales (modo demo activo)

---

## Recorrido de la app — qué revisar en cada sección

### 1. Dashboard (pantalla principal)

**URL:** `/app`

Qué se ve:
- Resumen general: obras activas, pendientes revisión, items totales, neto total
- Tarjetas de presupuestos existentes (hay 3 de prueba)
- Cada tarjeta muestra: nombre, cantidad de items, directo y neto total
- Badge de estado: Borrador (gris), Activo (verde), Aprobado (verde oscuro), Enviado (azul)

Qué revisar:
- [ ] Los badges dicen "Borrador" / "Activo" en español (no "draft" / "active")
- [ ] Los montos se muestran en formato argentino ($1.500.000 o $1,5M)
- [ ] Se puede buscar por nombre de presupuesto
- [ ] Click en una tarjeta lleva al editor de esa obra

---

### 2. Editor de Obra

**URL:** `/app/budgets/{id}`

Qué se ve:
- Árbol de secciones a la izquierda (ej: 1. Estructura, 2. Albañilería)
- Tabla de items a la derecha con columnas:
  - Descripción | Unidad | Cantidad | MAT Unit | MO Unit | Directo | Indirecto | Beneficio | Neto
- Barra de resumen arriba con tarjetas de costos (MAT, MO, Directo, Indirecto, Beneficio, Neto, Total c/IVA)
- Botón "Recálculo" arriba a la derecha
- Selector de vistas: Rubro, Piso, Material, Gremio

Qué revisar:
- [ ] Las columnas se ven completas (no cortadas)
- [ ] El encabezado y pie de tabla quedan fijos al hacer scroll
- [ ] El pie muestra totales de: Directo, Indirecto, Beneficio, Neto
- [ ] Al hacer click en un item, se abre el detalle
- [ ] El botón "Recálculo" recalcula y actualiza los números
- [ ] Se puede editar una cantidad haciendo doble click → los totales se recalculan solos

---

### 3. Detalle de Item (la pantalla nueva más importante)

**URL:** `/app/budgets/{id}/item/{item_id}`

Cómo llegar: desde el Editor, click en el ícono de un item (ícono de documento)

Qué se ve:
- Header: código, descripción, unidad, cantidad
- 5 mini tarjetas: MAT Unit, MO Unit, EQ Unit, MAT.IND Unit, SUB Unit
- 5 secciones expandibles:
  1. **Materiales** — los materiales físicos (cemento, arena, hierro, etc.)
  2. **Mano de Obra - Personas** — oficiales, ayudantes, capataz
  3. **Mano de Obra - Equipos** — maquinaria, bombas
  4. **Materiales Indirectos** — clavos, encofrado, alambre
  5. **Subcontratos** — pintor, electricista, pisero
- Resumen de costos al final: Directo → Indirectos → Beneficio → Impuestos → Neto → IVA → Total Final
- Botón verde **"Cargar template"** arriba

Qué revisar:
- [ ] Las 5 secciones se expanden y colapsan con el chevron (>)
- [ ] Si no hay recursos, dice "No hay recursos cargados. Agregá recursos para calcular el precio unitario."
- [ ] El botón **"+ Agregar recurso"** muestra una fila editable
- [ ] Se pueden llenar los campos: código, descripción, unidad, cantidad, desperdicio %, precio unitario
- [ ] Al guardar un recurso (ícono de disquete), se crea y el total se recalcula
- [ ] El ícono de lápiz permite editar un recurso existente
- [ ] El ícono de tacho permite eliminar un recurso
- [ ] Para Mano de Obra las columnas son: Código, Descripción, Trabajadores, Días, Cargas %, Jornales Efect., Jornal, Subtotal
- [ ] El pie de cada sección muestra: Total + "÷ cantidad = Precio Unitario"

---

### 4. Cargar Template (dentro del Detalle de Item)

Cómo probar:
1. Entrar al detalle de cualquier item
2. Click en **"Cargar template"** (botón verde arriba)
3. Se abre un modal "Biblioteca de Templates"

Qué se ve:
- Tabs de categorías: Todos, estructura, albañilería, terminaciones, instalaciones
- Tarjetas de templates con: nombre, unidad (badge azul), categoría (badge violeta), cantidad de recursos
- Botón "Aplicar" en cada template

Qué revisar:
- [ ] Aparecen 12 templates de TERRAC
- [ ] Se puede filtrar por categoría
- [ ] Al clickear "Aplicar" en un template → se crean los recursos en el item
- [ ] Después de aplicar, las 5 secciones se llenan con los recursos del template
- [ ] Los precios se asignan automáticamente desde el catálogo (si coinciden los códigos)
- [ ] Los totales se recalculan

**Probar con:** Ir a un item de tipo "m3" (ej: Hormigón) → Cargar template "Hormigón H-30 columnas" → verificar que se carguen 12 recursos (materiales + MO + equipos)

---

### 5. Página de Templates

**URL:** `/app/templates` (también desde la sidebar: Configuración → Templates)

Qué se ve:
- Lista de todos los templates disponibles
- Cada tarjeta muestra: nombre, unidad, categoría, descripción, cantidad de recursos
- Se puede expandir cada template para ver el detalle de recursos
- Botón de eliminar (tacho) con confirmación en 2 clicks

Qué revisar:
- [ ] Se ven 12 templates
- [ ] Al expandir (click en >) se ven los recursos agrupados por tipo
- [ ] Los recursos de Materiales muestran: código, descripción, cantidad, unidad, desperdicio %
- [ ] Los recursos de Mano de Obra muestran: código, descripción, trabajadores, días, cargas %
- [ ] El botón eliminar pide confirmación antes de borrar

---

### 6. Cadena de Markups

**URL:** `/app/settings/markups` (sidebar: Configuración → Cadena de Markups)

Qué se ve:
- 4 secciones de porcentajes editables:
  1. **Costos Indirectos**: Imprevistos, Estructura, Jefatura, Logística, Herramientas
  2. **Beneficio**: porcentaje sobre subtotal con indirectos
  3. **Impuestos**: Ingresos Brutos, Impuesto al Cheque
  4. **IVA**: porcentaje de IVA
- Botón "Guardar"

Qué revisar:
- [ ] Los campos se pueden editar (cambiar números)
- [ ] Muestra el subtotal de indirectos (suma de los 5 campos)
- [ ] Dice "sobre Subt. con Indirectos" al lado de Beneficio
- [ ] Dice "sobre Subt. con Beneficio" al lado de Impuestos
- [ ] Al guardar, los cambios se aplican al presupuesto
- [ ] Valores por defecto razonables: Imprevistos 3%, Estructura 15%, Jefatura 8%, etc.

---

### 7. Catálogos

**URL:** `/app/catalogs` (sidebar: Configuración → Catálogos)

Qué se ve:
- Lista de catálogos de precios cargados
- Cada catálogo muestra sus entradas (código, descripción, unidad, precio)
- Botones para: buscar, agregar entrada, editar, eliminar
- Upload de CSV
- Botón "Aplicar a presupuesto"

Qué revisar:
- [ ] Se ven los catálogos existentes (materiales, mano de obra, equipos, subcontratos)
- [ ] Se puede buscar dentro de un catálogo
- [ ] Se puede agregar una entrada nueva
- [ ] Se puede editar una entrada (ícono lápiz)
- [ ] Se puede eliminar una entrada (ícono tacho)
- [ ] "Aplicar a presupuesto" muestra un dropdown con los presupuestos disponibles

---

### 8. Análisis

**URL:** `/app/budgets/{id}/analysis` (dentro de un presupuesto → sidebar → Análisis)

Qué se ve:
- KPIs arriba: Materiales, Mano de Obra, Directo, Indirecto, Beneficio, Neto, Total c/IVA
- Tabla resumen por sección con totales
- Barra de desglose de costos

Qué revisar:
- [ ] Los KPIs muestran valores correctos
- [ ] La tabla tiene todas las secciones del presupuesto
- [ ] Los totales cuadran: Directo + Indirecto + Beneficio = Neto (aproximadamente)

---

### 9. IA + Planos

**URL:** `/app/budgets/{id}/ai` (dentro de un presupuesto → sidebar → IA + Planos)

Qué se ve:
- Zona para subir un plano (imagen o PDF)
- Indicador de si hay catálogos cargados (verde) o no (amarillo)
- Botón para analizar

Qué revisar:
- [ ] Si hay catálogos cargados, muestra badge verde "Catálogos cargados — La IA usará tus precios"
- [ ] Si no hay catálogos, muestra badge amarillo de advertencia
- [ ] Se puede subir una imagen o PDF
- [ ] (No probar el análisis completo por ahora — consume créditos de IA)

---

## Cálculos — cómo verificar que los números son correctos

### Dentro de un item con recursos:
```
Precio Unitario MAT = Σ(subtotal materiales) ÷ cantidad del item
Precio Unitario MO = Σ(subtotal MO + equipos + mat.ind + subcontratos) ÷ cantidad del item

Directo = (MAT Unit + MO Unit) × Cantidad
```

### Subtotal de un recurso material:
```
Cantidad efectiva = Cantidad × (1 + Desperdicio% / 100)
Subtotal = Cantidad efectiva × Precio unitario
```

### Subtotal de un recurso mano de obra:
```
Jornales efectivos = Trabajadores × Días × (1 + Cargas sociales% / 100)
Subtotal = Jornales efectivos × Precio del jornal
```

### Cascada de indirectos (para todo el presupuesto):
```
Subtotal 01 = Σ(Directo de cada item)
+ Imprevistos % + Estructura % + Jefatura % + Logística % + Herramientas %
= Subtotal 02

+ Beneficio % sobre Subtotal 02
= Subtotal 03

+ Ingresos Brutos % + Imp. Cheque % sobre Subtotal 03
= NETO

+ IVA % sobre NETO
= TOTAL FINAL
```

---

## Errores conocidos / limitaciones

1. **Items existentes no tienen recursos** — Los items que ya estaban creados no tienen recursos cargados. Hay que cargarles un template o agregar recursos manualmente.
2. **No hay dropdown de catálogo al agregar recurso** — Cuando agregás un recurso a mano, tenés que escribir el código. No hay autocompletado todavía.
3. **El login puede fallar** — Si aparece pantalla de login, ir directo a `/app`. No se necesitan credenciales.
4. **Render (backend) tarda** — A veces el backend se "duerme" por ser plan gratuito. La primera carga puede tardar 30-50 segundos.

---

## Glosario

| Término | Significado |
|---------|-------------|
| MAT Unit | Precio unitario de materiales (por m2, m3, etc.) |
| MO Unit | Precio unitario de mano de obra |
| EQ Unit | Precio unitario de equipos |
| MAT.IND Unit | Precio unitario de materiales indirectos (clavos, encofrado) |
| SUB Unit | Precio unitario de subcontratos |
| Directo | Costo directo = (MAT + MO) × cantidad |
| Indirecto | Costos indirectos de obra (estructura, jefatura, etc.) |
| Beneficio | Ganancia del constructor |
| Neto | Total antes de IVA |
| Total Final | Neto + IVA |
| Template | Composición estándar de recursos para un tipo de trabajo |
| Catálogo | Lista de precios de materiales, mano de obra, equipos o subcontratos |
| Cascada | Los porcentajes se aplican uno sobre el resultado del anterior, no todos sobre el directo |
