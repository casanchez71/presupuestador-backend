# INSTRUCTIVO: Cómo funciona el Presupuestador SOLE
## Ejemplo completo paso a paso

---

## EJEMPLO: Presupuestar un departamento de 2 ambientes

Imaginemos que un cliente te pide presupuestar un depto de 45 m² con:
- Living-comedor (25 m²)
- Dormitorio (12 m²)
- Baño (4 m²)
- Cocina (4 m²)

---

## PASO 1: Cargás tus listas de precios (una sola vez)

Entrás a **Catálogos** y subís tus CSVs:

| CSV | Ejemplo de contenido |
|-----|---------------------|
| Materiales | H30: Hormigón H-30, m3, $158,000 / LP18: Ladrillo 18cm, u, $1,377 / CEM: Cemento 50kg, bolsa, $7,000 |
| Mano de obra | MO-OF: Oficial, jornal, $90,000 / MO-AY: Ayudante, jornal, $60,000 |
| Equipos | BOMBA-H: Bomba hormigón, día, $85,000 |
| Subcontratos | SUB-PI: Pintor interior, m2, $15,000 / SUB-E-BOC: Electricista por boca, u, $45,000 |

**Esto se hace UNA VEZ. Después solo actualizás precios cuando cambien.**

---

## PASO 2: Subís el plano

Entrás a **Nuevo Presupuesto** → subís la imagen/PDF del plano → la IA lo analiza.

---

## PASO 3: La IA genera los items CON composición de recursos

**ANTES (lo viejo):** La IA decía:

```
Item 1.1: Hormigón columnas — 8 m3 — $0 ← sin precio, sin desglose
Item 1.2: Mampostería — 120 m2 — $0 ← idem
```

**AHORA (lo nuevo):** La IA dice:

```
Item 1.1: Hormigón H-30 columnas — 8 m3

  📦 MATERIALES:
  ┌──────────┬─────────────────────┬───────┬──────┬────────┬──────────┬───────────┬────────────┐
  │ Código   │ Descripción         │ Uidad │ Cant │ Desp.% │ Cant.Ef. │ Precio    │ Subtotal   │
  ├──────────┼─────────────────────┼───────┼──────┼────────┼──────────┼───────────┼────────────┤
  │ H30      │ Hormigón H-30       │ m3    │ 8.0  │ 10%    │ 8.8      │ $158,000  │ $1,390,400 │
  │ HADN6    │ Hierro Ø6mm         │ barra │ 72   │ 10%    │ 80       │ $5,250    │ $420,000   │
  │ HADN12   │ Hierro Ø12mm        │ barra │ 18   │ 10%    │ 20       │ $20,443   │ $408,860   │
  │ F-GR2    │ Fenólico encofrado  │ placa │ 16   │ 25%    │ 20       │ $45,454   │ $909,080   │
  └──────────┴─────────────────────┴───────┴──────┴────────┴──────────┴───────────┴────────────┘
  Total Materiales: $3,128,340 ÷ 8 m3 = $391,043 /m3

  👷 MANO DE OBRA:
  ┌──────────┬─────────────┬──────────────┬──────┬──────────┬──────────┬───────────┬────────────┐
  │ Código   │ Descripción │ Trabajadores │ Días │ Cargas%  │ Jornales │ Jornal    │ Subtotal   │
  ├──────────┼─────────────┼──────────────┼──────┼──────────┼──────────┼───────────┼────────────┤
  │ MO-OF    │ Oficial      │ 3           │ 5    │ 25%      │ 18.75    │ $90,000   │ $1,687,500 │
  │ MO-AY    │ Ayudante     │ 3           │ 5    │ 25%      │ 18.75    │ $60,000   │ $1,125,000 │
  └──────────┴─────────────┴──────────────┴──────┴──────────┴──────────┴───────────┴────────────┘
  Total MO: $2,812,500 ÷ 8 m3 = $351,563 /m3

  🏗️ EQUIPOS:
  ┌──────────┬─────────────────┬───────┬──────┬────────┬──────────┬───────────┬────────────┐
  │ BOMBA-H  │ Bomba hormigón  │ m3    │ 8.0  │ 10%    │ 8.8      │ $6,000    │ $52,800    │
  └──────────┴─────────────────┴───────┴──────┴────────┴──────────┴───────────┴────────────┘
  Total Equipos: $52,800 ÷ 8 m3 = $6,600 /m3

  ══════════════════════════════════════════════════════════════
  PRECIO UNITARIO del m3:
    MAT: $391,043  +  MO: $351,563  +  EQ: $6,600  =  $749,206 /m3

  DIRECTO del item (8 m3 × $749,206):              $5,993,640
  ══════════════════════════════════════════════════════════════
```

**¿De dónde sacó los precios?** De TUS catálogos que cargaste en el Paso 1.
**¿De dónde sacó las cantidades de material?** La IA las estima (ej: 1 m3 de H30 + 9 barras de hierro por m3 de columna).
**¿De dónde sacó el desperdicio?** La IA aplica % estándar (10% materiales, 25% encofrado).

---

## PASO 4: Se repite para TODOS los items

La IA genera así cada item del presupuesto:

```
SECCIÓN 1: ESTRUCTURA
├── 1.1 Hormigón H-30 columnas    8 m3    → Directo: $5,993,640
├── 1.2 Hormigón H-21 losa        5 m3    → Directo: $3,200,000
└── 1.3 Hormigón H-21 vigas       3 m3    → Directo: $1,920,000

SECCIÓN 2: ALBAÑILERÍA
├── 2.1 Mampostería LP18        120 m2    → Directo: $12,480,000
├── 2.2 Revoque grueso interior  95 m2    → Directo: $2,850,000
├── 2.3 Revoque fino interior    95 m2    → Directo: $1,425,000
├── 2.4 Contrapiso               45 m2    → Directo: $675,000
└── 2.5 Carpeta nivelación       45 m2    → Directo: $540,000

SECCIÓN 3: TERMINACIONES
├── 3.1 Cerámica pisos           45 m2    → Directo: $1,575,000
├── 3.2 Cerámica baño paredes    16 m2    → Directo: $560,000
└── 3.3 Pintura látex interior  190 m2    → Directo: $2,280,000

SECCIÓN 4: INSTALACIONES
├── 4.1 Electricidad             25 bocas → Directo: $1,750,000
├── 4.2 Sanitaria                  1 gl   → Directo: $2,800,000
└── 4.3 Gas                        1 gl   → Directo: $1,200,000
                                           ─────────────────────
                              SUBTOTAL 01: $39,248,640 (Costos Directos)
```

---

## PASO 5: Se aplica la cascada de indirectos AUTOMÁTICAMENTE

Esto es lo que el Excel del arquitecto hace al final de la planilla.
Ahora el sistema lo hace solo:

```
SUBTOTAL 01 — Costos Directos                     $39,248,640
   │
   ├── + Imprevistos (3%)                          + $1,177,459
   ├── + Estructura (5.6%)                         + $2,197,924
   ├── + Jefatura de Obra (5.6%)                   + $2,197,924
   ├── + Logística (5%)                            + $1,962,432
   └── + Herramientas (3%)                         + $1,177,459
                                                   ─────────────
SUBTOTAL 02 — Con Indirectos (22.2%)               $47,961,838
   │
   └── + Beneficio (25% sobre Subt.02)             + $11,990,460
                                                   ─────────────
SUBTOTAL 03 — Con Beneficio                        $59,952,298
   │
   ├── + Ingresos Brutos (7% sobre Subt.03)       + $4,196,661
   └── + Impuesto al Cheque (1.2% sobre Subt.03)  + $719,427
                                                   ─────────────
NETO                                               $64,868,386
   │
   └── + IVA (21% sobre Neto)                     + $13,622,361
                                                   ═════════════
TOTAL FINAL                                        $78,490,747
```

**Todo esto pasa AUTOMÁTICAMENTE cuando la IA termina de analizar el plano.**

---

## PASO 6: Vos revisás y ajustás

En el **Editor de Obra** ves todo armado. Podés:

### Ajustar cantidades
Si la IA estimó 120 m2 de mampostería pero vos sabés que son 135 m2:
→ Editás el número → el sistema recalcula solo (directo + indirectos + beneficio + todo)

### Ajustar recursos de un item
Entrás al detalle de un item y ves las 5 secciones (Materiales, MO, Equipos, etc.).
Podés agregar, quitar o modificar recursos. Ejemplo:
- "La IA no puso hierro Ø16, le agrego 12 barras" → se recalcula
- "El desperdicio no es 10%, es 15% porque es obra de altura" → se recalcula

### Cargar un template
Si la IA no desglosó bien un item, podés aplicar un template predefinido:
→ Click en "Cargar template" → elegís "Hormigón H-30 columnas" → se cargan todos los recursos del template

### Ajustar la cadena de costos
En **Cadena de Markup** podés cambiar cualquier porcentaje:
- Beneficio: 25% → 30%
- IVA: 21% → 10.5% (si aplica)
- Imprevistos: 3% → 5%
→ Click "Guardar" → se recalcula todo

---

## RESUMEN VISUAL DEL FLUJO

```
   TUS CATÁLOGOS                          TU PLANO
   (precios actuales)                     (imagen/PDF)
        │                                      │
        │         ┌──────────────────┐         │
        └────────→│    IA (GPT-4o)   │←────────┘
                  │                  │
                  │ "Conozco tus     │
                  │  precios, analizo│
                  │  el plano y      │
                  │  armo todo"      │
                  └────────┬─────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  ITEMS + RECURSOS      │
              │  (desglose por item)   │
              │                        │
              │  1.1 Hormigón columnas │
              │    ├─ H30: 8.8 m3     │
              │    ├─ HADN6: 80 barras │
              │    ├─ 3 oficiales×5d   │
              │    └─ Bomba: 8.8 m3   │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  MATCH CON CATÁLOGO    │
              │  código → precio       │
              │  H30 → $158,000/m3     │
              │  HADN6 → $5,250/barra  │
              │  MO-OF → $90,000/día   │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  CÁLCULO AUTOMÁTICO    │
              │                        │
              │  Recursos → Unitario   │
              │  × Cantidad → Directo  │
              │  + Indirectos          │
              │  + Beneficio           │
              │  + Impuestos           │
              │  + IVA                 │
              │  = TOTAL FINAL         │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  PRESUPUESTO LISTO     │
              │  para revisar/ajustar  │
              │  y entregar al cliente │
              └────────────────────────┘
```

---

## ¿QUÉ FALTARÍA PARA QUE ESTO FUNCIONE?

Hoy, TODO el código está escrito y listo. Para activarlo necesitás:

### Paso A: Correr un SQL en Supabase (2 minutos)
Abrís Supabase → SQL Editor → pegás un bloque de SQL → ejecutás.
Esto crea las columnas nuevas en tu base de datos.

### Paso B: Subir el código (yo lo hago)
Hago git push → Render deploya el backend automáticamente.

### Paso C: Deployar el frontend (1 minuto)
Corrés un comando desde la terminal para subir a Vercel.

### Paso D: Probar el flujo completo
1. Verificás que tus catálogos estén cargados
2. Creás un presupuesto nuevo
3. Subís un plano
4. Ves cómo la IA genera todo desglosado y costeado
5. Ajustás lo que haga falta

---

## TEMPLATES: TU BIBLIOTECA DE COMPOSICIONES

Además, armé 10 templates estándar que ya vienen precargados:

| Template | Unidad | Categoría |
|----------|--------|-----------|
| Hormigón H-30 columnas | m3 | Estructura |
| Hormigón H-21 losa | m3 | Estructura |
| Mampostería LP18 | m2 | Albañilería |
| Revoque grueso interior | m2 | Albañilería |
| Revoque fino interior | m2 | Albañilería |
| Contrapiso | m2 | Albañilería |
| Carpeta nivelación | m2 | Albañilería |
| Pintura interior látex | m2 | Terminaciones |
| Cerámica piso | m2 | Terminaciones |
| Instalación eléctrica por boca | u | Instalaciones |

Si la IA no desglosó bien un item, con un click le aplicás un template y listo.

Con el tiempo vas a poder crear tus propios templates desde composiciones que ya hayas armado.
