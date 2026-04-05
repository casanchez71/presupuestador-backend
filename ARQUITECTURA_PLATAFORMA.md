# ARQUITECTURA DE PLATAFORMA SOLE
## Universal vs Sector vs Cliente

---

## Las 3 capas

```
┌─────────────────────────────────────────────────────────┐
│                    CAPA 3: CLIENTE                       │
│                      (~5%)                               │
│                                                          │
│  Catálogos de precios propios (CSV)                     │
│  Templates con SUS códigos de material                  │
│  % indirectos personalizados                            │
│  Logo, nombre de empresa                                │
│  Historial de presupuestos                              │
│                                                          │
│  Ejemplo TERRAC:                                         │
│    ARG=Arena granel, LP18=Ladrillo portante             │
│    H-PL-m=Bomba pluma por m3                            │
│    Estructura 5.6%, Jefatura 5.6%, Beneficio 25%        │
│                                                          │
│  Ejemplo YOPACTO:                                        │
│    (sus propios códigos, sus propios proveedores)        │
│    Beneficio 20%, sin imp.cheque, etc.                   │
├─────────────────────────────────────────────────────────┤
│                    CAPA 2: SECTOR                        │
│                      (~10%)                              │
│                                                          │
│  Templates genéricos de construcción AR                  │
│  Unidades estándar (m2, m3, ml, gl, u)                  │
│  Categorías: estructura, albañilería, terminaciones,     │
│              instalaciones, movimiento de suelos         │
│  Rendimientos típicos (60 m2/día mampostería)           │
│  Cargas sociales estándar (25%)                         │
│  Estructura de indirectos (imprevistos, estructura,      │
│    jefatura, logística, herramientas)                    │
│  Impuestos AR (IIBB 7%, Cheque 1.2%, IVA 21%)          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                    CAPA 1: UNIVERSAL                     │
│                      (~85%)                              │
│                                                          │
│  Motor de cálculo cascada                               │
│  IA análisis de planos                                  │
│  Editor de presupuestos                                 │
│  CRUD de catálogos                                      │
│  Sistema de templates                                    │
│  Gestión de recursos por item                           │
│  Dashboard y reportes                                    │
│  Versionado de presupuestos                             │
│  Auditoría de cambios                                   │
│  Exportación (futuro)                                    │
│  Multi-usuario (futuro)                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Qué es de cada capa (detallado)

### CAPA 1: UNIVERSAL (el producto — no cambia por cliente)

| Componente | Descripción |
|-----------|-------------|
| Motor de cálculo | recursos → unitarios → directo → cascada indirectos → neto → total |
| IA de planos | GPT-4o Vision analiza plano y genera items |
| Editor | Árbol de secciones/items, edición inline, vistas |
| Catálogos CRUD | Subir CSV, editar entradas, asignar a presupuesto |
| Templates CRUD | Crear, editar, aplicar composiciones |
| Recursos CRUD | Agregar/editar recursos por item |
| Dashboard | Lista presupuestos, filtros, estados |
| Análisis | Resumen por sección, KPIs |
| Versionado | Snapshots del presupuesto |
| Auditoría | Quién cambió qué y cuándo |
| Auth | Login, org_id, multi-usuario |

**Esto es el 85% del código. No se toca para cada cliente.**

### CAPA 2: SECTOR (construcción Argentina — configurable por mercado)

| Componente | Valor por defecto | Configurable? |
|-----------|-------------------|---------------|
| Templates genéricos | 10 composiciones (H30, mampostería, etc.) | Sí, cada org puede crear los suyos |
| Unidades | m2, m3, ml, gl, u, kg, bolsa, barra | Se pueden agregar |
| Categorías | estructura, albañilería, terminaciones, instalaciones | Se pueden agregar |
| Cargas sociales | 25% | Por recurso |
| Imprevistos | 3% | Por org |
| IVA | 21% | Por org |
| IIBB | 7% | Por org |
| Imp. Cheque | 1.2% | Por org |

**Esto se configura UNA VEZ al instalar la plataforma para un mercado (AR, Chile, Uruguay, etc.).
Hoy está hardcodeado para Argentina pero es fácilmente parametrizable.**

### CAPA 3: CLIENTE (datos particulares — cada org tiene los suyos)

| Componente | Ejemplo TERRAC | Ejemplo futuro YOPACTO |
|-----------|----------------|----------------------|
| Catálogo materiales | 251 items (H30, LP18, ARG...) | Sus proveedores, sus precios |
| Catálogo MO | 4 categorías (CA, PU, OF, AY) | Quizás 6 categorías |
| Catálogo equipos | 25 items (mini cargadora, etc.) | Los que use |
| Catálogo subcontratos | 57 items (SUB-PI, SUB-E-BOC...) | Sus subcontratistas |
| Templates propios | 12 composiciones con SUS códigos | Las que armen |
| Indirectos | Estr 5.6%, Jef 5.6%, Ben 25% | Su estructura de costos |
| Presupuestos | Sus obras | Sus obras |
| Historial | Sus versiones | Sus versiones |

**Esto es lo que cada cliente sube al darse de alta.**

---

## Cómo se vende

### A TERRAC (primer cliente):
"Ya tenemos tu catálogo de 330+ items cargado, 12 templates de composición listos con tus códigos, y tu estructura de indirectos configurada. Subís un plano y te sale el presupuesto."

### A YOPACTO, YANIBELLI (próximos clientes):
"La plataforma es la misma. Nos mandás tus listas de precios en CSV, nos decís tus % de indirectos y beneficio, y en 1 hora estás presupuestando."

### A cualquier constructor nuevo:
"Empezás con los templates genéricos y precios de referencia. Después subís TUS listas cuando las tengas."

---

## Separación técnica en el código

### Lo UNIVERSAL vive en:
```
app/calculations.py          → Motor de cálculo
app/routers/budgets.py       → CRUD presupuestos/items/recursos
app/routers/analysis.py      → Análisis y cascada indirectos
app/routers/ai.py            → IA análisis planos
app/routers/templates.py     → CRUD templates
app/routers/catalogs.py      → CRUD catálogos
frontend/src/pages/*.tsx      → Todas las páginas
frontend/src/components/*.tsx → Todos los componentes
```

### Lo de SECTOR vive en:
```
branding/templates_seed.json  → Templates genéricos (AR)
app/routers/analysis.py       → Defaults de indirectos (líneas con DEFAULT)
migrations/003_*.sql           → Defaults de impuestos (IIBB 7%, IVA 21%)
```

### Lo de CLIENTE vive en:
```
Base de datos (Supabase)      → Todo filtrado por org_id
branding/templates_terrac.json → Templates específicos de TERRAC
seed_data/inputs_las_heras/    → CSVs de precios de TERRAC
```

**Clave: TODO en la DB se filtra por `org_id`. Cada cliente ve solo sus datos.**

---

## Flujo de onboarding de un cliente nuevo

### Paso 1: Crear la organización
- Se crea un registro en la tabla `organizations` (o se usa el auth de Supabase)
- Se asigna un `org_id`

### Paso 2: Subir catálogos de precios
- El cliente (o nosotros) sube 4 CSVs:
  1. Materiales (código, descripción, unidad, precio sin IVA)
  2. Mano de obra (código, descripción, jornal diario)
  3. Equipos (código, descripción, unidad, precio/día)
  4. Subcontratos (código, descripción, unidad, precio)
- La app los procesa y crea `price_catalogs` + `catalog_entries`

### Paso 3: Configurar indirectos
- Desde la UI "Cadena de Markup":
  - Imprevistos: X%
  - Estructura: X%
  - Jefatura: X%
  - Logística: X%
  - Herramientas: X%
  - Beneficio: X%
  - IIBB: X% (o 0 si no aplica)
  - Imp. Cheque: X% (o 0)
  - IVA: X% (o 10.5% si es vivienda social)

### Paso 4: Cargar templates (opcional)
- Si el cliente tiene composiciones propias → importar JSON
- Si no → usar los templates genéricos como base y ajustar

### Paso 5: Listo para presupuestar
- Sube un plano → IA analiza con SUS catálogos → presupuesto completo

---

## Lo que falta construir para el onboarding masivo

| Feature | Prioridad | Esfuerzo |
|---------|-----------|----------|
| Pantalla de onboarding "Bienvenido, configurá tu empresa" | Alta | 1 sprint |
| Import masivo de templates desde JSON | Media | Ya existe (endpoint POST /templates) |
| Import masivo de catálogos desde múltiples CSV en un paso | Media | 1 sprint |
| Página de configuración de empresa (logo, nombre, datos) | Baja | 1 sprint |
| Clonar templates genéricos al org del cliente | Media | Medio sprint |
| Vista "Admin" para gestionar múltiples clientes | Baja | 2 sprints |
