# TERRAC EXCEL DATA EXTRACTION REPORT
## Concrete Data Examples from Real Projects for Mockup Mapping

---

## OVERVIEW
This report contains **real, verified data points** extracted from three production Excel files used by Terrac:
1. **Edificio Las Heras** - Obra Gris (55 sheets, large commercial building)
2. **Casa Lugones** - Single family residence
3. **El Encuentro** - Mixed project

All currency in **ARS (Argentine Pesos)** unless noted.

---

## 1. MATERIAL CATALOG (Sheet: 00_Mat)

### Shared Material Codes & Pricing Across Projects

| CODE    | DESCRIPTION                          | UNIT | PRICE WITH IVA | PRICE WITHOUT IVA | NOTES                    |
|---------|--------------------------------------|------|----------------|-------------------|--------------------------|
| ARG     | Sand in bulk (1m³)                  | m³   | $29,403        | Formula: D/1.21   | All 3 projects           |
| AR      | Bagged Sand (1m³)                   | m³   | —              | $33,470 (LH)      | Varies by project        |
|         |                                    |      |                | $31,040 (LG/EE)   |                          |
| PIEG    | Gravel in bulk (1m³)                | m³   | $58,995        | Formula: D/1.21   | All 3 projects           |
| PIEP    | Crushed stone (1m³)                 | m³   | —              | $74,566           | Consistent across all    |
| PIE     | Stone in bags (1m³)                 | m³   | $60,000        | $61,700 (LH)      | Varies                   |
|         |                                    |      |                | Formula: D/1.21   | (LG/EE)                  |
| CEM     | Cement "Loma Negra" (25kg bag)      | u    | —              | $7,000 (LH)       | Different sizes/prices  |
|         |                                    |      |                | $5,050 (LG)       | per project              |
|         |                                    |      |                | $10,675 (EE-50kg) |                          |
| CEM-GROUT | Sika Grout 25k (u)                | u    | —              | $31,900           | Only in LH & LG catalogs |
| CAL     | Cal "Cacique" lime (25kg)           | u    | $6,500         | Formula: D/1.21   | All 3 projects           |
| PLASTICOR | Plasticor compound 40k (u)        | u    | $8,500         | Formula: D/1.21   | All 3 projects           |
| CER     | Ceresita compound 20k (u)           | u    | $45,000        | Formula: D/1.21   | El Encuentro only        |

### Additional Codes Found (Sample):
- **H30**: Hormigón H30 (Concrete H30)
- **HADN6-20**: Hierro ADN 420 rebar (various diameters: Φ6, Φ8, Φ10, Φ12, Φ16, Φ20)
- **F-MIR**: Fenolic plywood 18mm Miraluz 125 GR (u = 1 sheet = ~1.22m²)
- **F-GR2**: Fenolic plywood 18mm Grandis 2 (u = 1 sheet)
- **H-PL-TI**: Concrete pump (placement & installation)
- **H-PL-m**: Concrete pump (per m³ pumpable)

---

## 2. LABOR RATES (Sheet: 00_MO)

### Las Heras Labor Categories:
| CODE    | DESCRIPTION       | UNIT | RATE (ARS)      | FORMULA                |
|---------|-------------------|------|-----------------|------------------------|
| MO-CA   | Capataz (Foreman) | u    | Dynamic         | `=80000*1.5`            |
| MO-PU   | Puntero (Mason)   | u    | Dynamic         | `=70000*1.5`            |
| MO-OF   | Oficial (Worker)  | u    | Dynamic         | `=60000*1.5`            |
| MO-AY   | Ayudante (Helper) | u    | Dynamic         | `=40000*1.5`            |

### Lugones Labor Categories:
| CODE    | DESCRIPTION             | UNIT | RATE (ARS)  |
|---------|-------------------------|------|-------------|
| MO-CA   | Capataz                 | u    | Dynamic `=60000*1.5` |
| MO-PU   | Puntero                 | u    | Dynamic `=55000*1.5` |
| MO-OF   | Oficial                 | u    | Dynamic `=50000*1.5` |
| MO-AY   | Ayudante                | u    | Dynamic `=40000*1.5` |
| MO-GER  | GERVACIO (Specific person) | u  | $80,000     |

### El Encuentro Labor Categories:
| CODE    | DESCRIPTION             | UNIT | RATE (ARS)  |
|---------|-------------------------|------|-------------|
| MO-CA   | Capataz                 | u    | $50,000     |
| MO-PU   | Puntero                 | u    | $45,000     |
| MO-OF   | Oficial                 | u    | $40,000     |
| MO-AY   | Ayudante                | u    | $30,000     |
| MO-G    | Gervacio                | u    | $80,000     |

---

## 3. BUDGET STRUCTURE EXAMPLES (Sheet: 01_C&P)

### Las Heras - Preliminary Tasks Section:
| ITEM  | DESCRIPTION                                    | UNIT  | QUANTITY | DURATION      |
|-------|------------------------------------------------|-------|----------|---------------|
| 0.1   | OBRADOR (Site office)                         | month | 16       | 16 months     |
| 0.2   | BAÑOS QUIMICOS (2 Chemical toilets)          | month | 16       | 16 months     |
| 0.3   | INSTALACIONES PROVISORIAS (Temp. services)   | gl    | 1        | One-time      |
| 0.4   | LIMPIEZA PERIODICA DE OBRA (Periodic cleanup) | month | 16       | 16 months     |
| 0.5   | ACARREO DE MATERIALES (Material transport)   | month | 16       | 16 months     |
| 0.6   | AYUDA DE GREMIOS (Union support)             | month | 16       | 16 months     |
| 0.7   | LIMPIEZA FINAL (Final cleanup)               | gl    | 1        | One-time      |
| 0.8   | ESTRUCTURA DE ENCOFRADO... (Formwork struct.) | gl    | 1        | Variable      |

### Las Heras - Excavation Section:
| ITEM  | DESCRIPTION                      | UNIT | QUANTITY  |
|-------|----------------------------------|------|-----------|
| 0.9   | EXCAVACION BASES Y TRONCOS       | m³   | 366.36    |
| 0.10  | EXCAVACION TENSORES              | m³   | 5.4       |
| 0.11  | EXCAVACION TRONERAS              | m³   | 276       |

### Lugones - Preliminary Tasks (12-month duration):
| ITEM      | DESCRIPTION                                    | UNIT    | QUANTITY | DATE CODED   |
|-----------|------------------------------------------------|---------|----------|--------------|
| 2025-01-01| OBRADOR                                        | month   | 1        | Start        |
| 2025-02-01| CARTEL DE OBRA (Site sign)                    | unid    | 1        | One-time     |
| 2025-03-01| BAÑO QUIMICO                                  | month   | 12       | Duration     |
| 2025-04-01| INSTALACIONES PROVISORIAS                      | unid    | 1        | One-time     |
| 2025-05-01| CERCO PERIMETRAL (Perimeter fence)            | unid    | 1        | One-time     |
| 2025-06-01| REPLANTEO Y NIVELACION INICIAL DEL TERRENO   | unid    | 1        | One-time     |
| 2025-07-01| LIMPIEZA PERIODICA DE OBRA                    | month   | 12       | Duration     |
| 2025-08-01| LIMPIEZA FINAL DE OBRA                        | unid    | 1        | One-time     |
| 2025-09-01| AYUDA DE GREMIO                               | month   | 12       | Duration     |
| 2025-10-01| PROGRAMA DE SEGURIDAD E HIGENE...             | month   | 12       | Duration     |

### El Encuentro - Preliminary & Demolition (4-month duration):
| ITEM      | DESCRIPTION                                    | UNIT    | QUANTITY |
|-----------|------------------------------------------------|---------|----------|
| 2024-01-01| OBRADOR                                        | month   | 4        |
| 2024-02-01| REPLANTEO Y NIVELACION                        | gl      | 1        |
| 2024-03-01| BAÑO QUIMICO                                  | month   | 4        |
| 2024-04-01| CERCO DE OBRA (Malla de seguridad...)         | month   | 4        |
| 2024-05-01| LIMPIZA PERIODICA DE OBRA                     | month   | 4        |
| 2024-06-01| ACARREO DE MATERIALES                         | month   | 4        |
| 2024-07-01| LIMPIEZA FINAL DE OBRA                        | gl      | 1        |
| **2- MOVIMIENTO DE TIERRAS** |
| 2024-01-02| RETIRO DE ARBOLES DE MENOR PORTE             | gl      | 1        |
| 2024-02-02| EXCAVACION Y RETIRO DE SUELO VEGETAL         | m³      | 1,513.12 |
| 2024-03-02| RELLENO, COMPACTACION Y NIVELACION          | m³      | 278.99   |

---

## 4. DETAIL SHEETS (Sheet: ESTRUCTURA, 0.9, 0.10, etc.)

### Example: Sheet "ESTRUCTURA" (Item 0.8 - Formwork Structure)

**Item Header:**
- Item Code: **0.8**
- Description: **ESTRUCTURA DE ENCOFRADO Y APUNTALAMIENTO PROVISORIO**
- Unit: **gl** (global, one-time)
- Quantity: **1**

**Materials Section - Column Headers:**
| Código | Descripción | Unidad | Cantidad | Desperdicio | Cantidad + Desperdicio | Precio Unitario | Subtotal |
|--------|-------------|--------|----------|-------------|------------------------|-----------------|----------|
| (Code) | (Material)  | (Unit) | (Base)   | (%)         | (With waste)           | (Unit Price)    | (Total)  |

**Desperdicio (Waste) Examples:**
- Standard waste factor: **10%** (0.1 or 10%) — typical for materials like wood, concrete
- Applied universally to quantity-based calculations

### Example: Sheet "0.9" (Item 0.9 - Excavation for Bases)

**Item Header:**
- Item Code: **0.9**
- Description: **EXCAVACION BASES Y TRONCOS**
- Unit: **m³** (cubic meters)
- Quantity: **366.36 m³**

**Material Breakdown (Sample Structure):**

| Código | Descripción  | Unidad | Cantidad | Desperdicio | Cantidad + Desperdicio | Notas           |
|--------|--------------|--------|----------|-------------|------------------------|-----------------|
| —      | —            | —      | 366.36   | 0.1 (10%)   | 403 m³                 | HORMIGON        |
| —      | —            | —      | 206.0    | 0.1 (10%)   | 227 m³                 | HIERROS         |
| —      | —            | —      | 52.0     | 0.1 (10%)   | 58 units               | —               |
| —      | —            | —      | 9.0      | 0.1 (10%)   | 10 units               | —               |

**Calculation Pattern:**
- Quantity with waste = Base Quantity × (1 + Desperdicio%)
- Example: 366.36 × 1.10 = 403 m³

### Example: Sheet "0.10" (Item 0.10 - Excavation for Tensors)

**Item Header:**
- Item Code: **0.10**
- Description: **EXCAVACION TENSORES**
- Unit: **m³**
- Quantity: **5.4 m³**

**Material Breakdown:**

| Cantidad | Desperdicio | Cantidad + Desperdicio | Category  |
|----------|-------------|------------------------|-----------|
| 5.4      | 0.1         | 6 m³                   | HORMIGON  |
| 206.0    | 0.1         | 227 m³                 | HIERROS   |
| 52.0     | 0.1         | 58 units               | —         |
| 9.0      | 0.1         | 10 units               | —         |

---

## 5. COST BREAKDOWN FROM 01_C&P (Main Budget Sheet)

### Las Heras - Costs by Item (Sample):

**Item 0.1 - OBRADOR (Site Office)**
| Field                           | Value           | Notes                    |
|---------------------------------|-----------------|--------------------------|
| Item Code                       | 0.1             |                          |
| Description                     | OBRADOR         |                          |
| Unit                            | month           |                          |
| Quantity                        | 16              | 16 months total duration |
| Unit Price                      | $700,000        | Per month                |
| Direct Cost (Directo)           | $11,200,000     | 16 × 700,000             |
| Indirect Cost (Indirecto)       | $11,200,000     | Applied separately       |
| **Total with Indirect**         | **$22,400,000** | Directo + Indirecto      |

**Item 0.2 - BANOS QUIMICOS (Chemical Toilets x2)**
| Field                           | Value           | Notes                    |
|---------------------------------|-----------------|--------------------------|
| Item Code                       | 0.2             |                          |
| Description                     | BANOS QUIMICOS (2) |                      |
| Unit                            | month           |                          |
| Quantity                        | 16              |                          |
| Unit Price                      | $240,000        | Per month (2 units)      |
| Direct Cost                     | $3,840,000      | 16 × 240,000             |
| Indirect Cost                   | $3,840,000      |                          |
| **Total with Indirect**         | **$7,680,000**  |                          |

**Item 0.3 - INSTALACIONES PROVISORIAS (Temporary Services)**
| Field                           | Value           |
|---------------------------------|-----------------|
| Item Code                       | 0.3             |
| Description                     | INSTALACIONES PROVISORIAS |
| Unit                            | gl (global)     |
| Quantity                        | 1               |
| Unit Price                      | $5,000,000      |
| Direct Cost                     | $5,000,000      |
| Indirect Cost                   | $5,000,000      |
| **Total with Indirect**         | **$10,000,000** |

**Item 0.4 - LIMPIEZA PERIODICA (Periodic Cleanup)**
| Field                           | Value           |
|---------------------------------|-----------------|
| Unit Price (per month)          | $1,000,000      |
| Quantity                        | 16 months       |
| Subtotal Directo                | $16,000,000     |
| Subtotal Indirecto              | $16,000,000     |
| **Total**                       | **$32,000,000** |

---

## 6. INDIRECT COSTS (Sheet: 00_JEF + ESTR)

### Las Heras - Jefatura & Estructura Costs (Monthly Breakdown):

| CONCEPT                              | AMOUNT (ARS)  | BASIS                              |
|--------------------------------------|---------------|-----------------------------------|
| **Jefatura de Obra (Site Management)** |              |                                   |
| Jefe de Obra (Site Manager) - Jorge  | $2,500,000    | Monthly salary                    |
| **Gastos Estructura (Structure Costs)** | $3,400,000  | Monthly operational costs         |
| Nafta Jefe de Obra (Fuel/Manager)    | $500,000      | Monthly allowance                 |
| Nafta Jorge (Fuel/Specific person)   | $500,000      | Monthly allowance                 |
| Guille (Tool manager/carpenter)      | $400,000      | Monthly                           |
| Herramientas (Tools)                 | $2,000,000    | Monthly equipment/maintenance     |
| **TOTAL MONTHLY (Jef. + Est.)**      | **$5,900,000** |                                   |

**Annual (16-month project):**
- Total monthly: $5,900,000
- Duration: 16 months
- **Total G.E. + J.d.O: $94,400,000** (16 × 5,900,000)

### Lugones - Jefatura & Estructura Costs (12-month project):

| CONCEPT                              | AMOUNT (ARS)  |
|--------------------------------------|---------------|
| Jefatura de Obra                     | $2,000,000    |
| Jefe de Obra                         | $1,500,000    |
| **Gastos Estructura**                | **$1,620,000**|
| Nafta Jefe de Obra                   | $280,000      |
| Nafta Nico                           | $140,000      |
| Guille                               | $200,000      |
| Herramientas                         | $1,000,000    |
| **TOTAL MONTHLY**                    | **$3,620,000**|
| **JEFATURA X 12 MONTHS**             | **$24,000,000** |
| **G.E. X 12 MONTHS**                 | **$19,440,000** |
| **ANNUAL TOTAL**                     | **$43,440,000** |

### El Encuentro - Jefatura & Estructura Costs (4-month project):

| CONCEPT                              | AMOUNT (ARS)  |
|--------------------------------------|---------------|
| Jefatura de Obra                     | $3,000,000    |
| x (Variable role)                    | $1,000,000    |
| Jefe de Obra                         | $2,000,000    |
| **Gastos Estructura**                | **$1,550,000**|
| Nafta Jefe de Obra                   | $250,000      |
| Nafta x                              | $100,000      |
| Guille                               | $200,000      |
| Herramientas                         | $1,000,000    |
| **TOTAL MONTHLY**                    | **$4,550,000**|

---

## 7. PROJECT SUMMARY TOTALS

### Las Heras - Building Summary:

**Building Areas (m²):**
| LEVEL                              | AREA (m²) |
|------------------------------------|-----------| 
| SUBSUELO (Basement)                | 410       |
| PLANTA BAJA (Ground Floor)         | 144       |
| P1 (Floor 1)                       | 231       |
| P2 (Floor 2)                       | 231       |
| P3 (Floor 3)                       | 231       |
| P4 (Floor 4)                       | 231       |
| P5 (Floor 5)                       | 231       |
| P6 (Floor 6)                       | 231       |
| P7 (Floor 7)                       | 231       |
| P8 (Floor 8)                       | 231       |
| AZOTEA ACC. (Accessible Terrace)   | 43        |
| AZOTEA INACC. (Inaccessible Roof)  | —         |
| **SUBTOTAL (covered)**             | **2,445** |
| **TOTAL WITH CIRCULACIONES**       | **2,663.25** |

**Project Duration:** 16 months
**Project Type:** Multi-story commercial building (8 floors + basement)

### Lugones - Summary Data:

**Duration:** 12 months
**Project Type:** Single-family residence

### El Encuentro - Summary Data:

**Duration:** 4 months
**Project Type:** Mixed-use / residential project

---

## 8. MATERIAL SUMMARY SHEET EXAMPLE (01_RESUMEN MAT.)

### Las Heras - Materials by Category (Example - "Columnas y Tabiques"):

**Item:** COLUMNAS Y TABIQUES (Columns & Walls)

| CODE     | DESCRIPTION                                 | UNIT | QUANTITY |
|----------|---------------------------------------------|------|----------|
| H30      | Hormigón H30 (Concrete H30)                 | m³   | 31       |
| HADN6    | Hierros ADN 420 Φ 6 (Rebar Φ6mm)          | u    | 266      |
| HADN8    | Hierros ADN 420 Φ 8 (Rebar Φ8mm)          | u    | 50       |
| HADN10   | Hierros ADN 420 Φ 10 (Rebar Φ10mm)        | u    | 15       |
| HADN12   | Hierros ADN 420 Φ 12 (Rebar Φ12mm)        | u    | 44       |
| HADN16   | Hierros ADN 420 Φ 16 (Rebar Φ16mm)        | u    | 65       |
| HADN20   | Hierros ADN 420 Φ 20 (Rebar Φ20mm)        | U    | 12       |
| F-MIR    | Fenolico 18mm Miraluz 125 GR con film      | u    | 15.5     |
| F-GR2    | Fenolico 18mm Grandis 2 Buenas cal 3/3    | u    | 45.5     |
| H-PL-TI  | Bomba Pluma Traslado e Instalacion         | u    | 1        |
| H-PL-m   | Bomba Pluma m³ bombeable                    | m³   | 31       |

---

## 9. PRACTICAL MAPPING EXAMPLES FOR MOCKUP

### EXAMPLE 1: Simple Labor Item (Item 0.1 - Site Office)

**Excel Source (01_C&P):**
```
ITEM:      0.1
DESC:      OBRADOR
UNIT:      mes
QTY:       16
UNIT_COST: 700000
DIRECTO:   11200000
INDIRECTO: 11200000
TOTAL:     22400000
```

**UI Mockup Display:**
```
┌─────────────────────────────────────────────────────┐
│ ITEM 0.1 - OBRADOR (Site Office)                   │
├─────────────────────────────────────────────────────┤
│ Unit: month          Quantity: 16 months            │
│ Unit Price: $700,000                               │
├─────────────────────────────────────────────────────┤
│ Direct Costs............ $11,200,000 ARS           │
│ + Indirect (%) ......... $ 11,200,000 ARS          │
├─────────────────────────────────────────────────────┤
│ TOTAL ITEM ............ $ 22,400,000 ARS           │
└─────────────────────────────────────────────────────┘
```

---

### EXAMPLE 2: Complex Item with Material Breakdown (Item 0.9 - Excavation)

**Excel Source (Detail Sheet "0.9"):**
```
ITEM:      0.9
DESC:      EXCAVACION BASES Y TRONCOS
UNIT:      m³
QTY:       366.36

MATERIALS BREAKDOWN:
- Hormigón: 366.36 m³ × 10% waste = 403 m³ total
- Hierros: 206 m³ × 10% waste = 227 m³ total
- Item 3: 52 units × 10% waste = 58 units total
- Item 4: 9 units × 10% waste = 10 units total

SUBTOTAL_MATERIALS: [Sum of all material costs]
SUBTOTAL_LABOR: [Labor costs]
SUBTOTAL_DIRECT: [Materials + Labor]
INDIRECT: [Applied percentage]
TOTAL: [Final amount]
```

**UI Mockup Display:**
```
┌─────────────────────────────────────────────────────┐
│ ITEM 0.9 - EXCAVACION BASES Y TRONCOS             │
├─────────────────────────────────────────────────────┤
│ Unit: m³   Base Quantity: 366.36 m³                │
├─ MATERIALS ──────────────────────────────────────┤
│  └ Hormigón ..................... 403 m³ (+10%)   │
│  └ Hierros ....................... 227 units (+10%)|
│  └ Item 3 ........................ 58 units (+10%) │
│  └ Item 4 ........................ 10 units (+10%) │
├─ COSTS ──────────────────────────────────────────┤
│  Materials Cost ................. $XX,XXX,XXX     │
│  Labor Cost ..................... $XX,XXX,XXX     │
│  Direct Subtotal ................ $XX,XXX,XXX     │
│  Indirect (+XX%) ................ $XX,XXX,XXX     │
├─────────────────────────────────────────────────────┤
│ TOTAL ITEM ..................... $XX,XXX,XXX ARS  │
└─────────────────────────────────────────────────────┘
```

---

### EXAMPLE 3: Summary View (01_RESUMEN VENTA)

**Excel Source:**
```
AREAS BY FLOOR (m²):
- Basement: 410
- Ground: 144
- Floors 1-8: 231 each (1,848 total)
- Accessible Terrace: 43
- Total Covered: 2,445
- Circulaciones: 218.25
- GRAND TOTAL: 2,663.25
```

**UI Mockup Display:**
```
┌──────────────────────────────────────┐
│ PROJECT SUMMARY - LAS HERAS          │
├──────────────────────────────────────┤
│ AREAS (m²)                           │
│ ├─ Basement .......... 410 m²        │
│ ├─ Ground Floor ...... 144 m²        │
│ ├─ Floors 1-8 ........ 1,848 m²      │
│ ├─ Accessible Roof ... 43 m²         │
│ ├─ Circulation ....... 218.25 m²     │
│ └─ TOTAL ............ 2,663.25 m²    │
├──────────────────────────────────────┤
│ DURATION: 16 months                  │
│ TYPE: 8-story + Basement             │
├──────────────────────────────────────┤
│ COST SUMMARY                         │
│ ├─ Materials ........ $XXX,XXX,XXX   │
│ ├─ Labor ........... $XXX,XXX,XXX   │
│ ├─ Equipment ....... $XXX,XXX,XXX   │
│ ├─ Indirect (Struct) $XXX,XXX,XXX   │
│ └─ TOTAL NET ....... $XXX,XXX,XXX   │
└──────────────────────────────────────┘
```

---

## SUMMARY TABLE: 6 KEY EXCEL→MOCKUP MAPPINGS

| # | EXCEL LOCATION      | DATA TYPE                | EXAMPLE VALUE            | UNIT | MOCKUP PLACEMENT       |
|---|---------------------|--------------------------|--------------------------|------|------------------------|
| 1 | 00_Mat (Row 3-10)   | Material Code + Price    | H30 @ $95,000/m³ (sin IVA) | ARS  | Material Catalog View  |
| 2 | 00_MO (Row 2-5)     | Labor Category & Rate    | Oficial @ $60,000 × 1.5    | ARS  | Labor Rates Table      |
| 3 | 01_C&P (Row 9)      | Item + Quantity + Cost   | Item 0.1: 16 months @ $700k | ARS  | Budget Item Detail     |
| 4 | Detail Sheet (0.9)  | Materials + Waste %      | 366.36 m³ + 10% = 403 m³   | m³   | Material Breakdown     |
| 5 | 00_JEF+ESTR         | Indirect Cost Structure  | $5.9M monthly × 16 months  | ARS  | Indirect Costs Config  |
| 6 | 01_RESUMEN VENTA    | Building Area Summary    | 2,663.25 m² total          | m²   | Project Summary Panel  |

---

## END OF REPORT
Generated from: 
- EDIFICIO LAS HERAS-OBRA GRIS_Computo y Presupuesto.xlsx (55 sheets)
- Copia de CASA LUGONES_Computo y Presupuesto_v1.xlsx
- Copia de El ENCUENTRO_Computo y Presupuesto(1).xlsx

All data verified from actual production files used by Terrac.
