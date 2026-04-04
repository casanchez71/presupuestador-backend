# Archivos de entrada - Edificio Las Heras (Obra Gris)

Estos archivos representan lo que un usuario TRAE al sistema para crear un presupuesto. El sistema combina: estructura + listas de precios + costos indirectos = presupuesto completo.

## Archivos

### Listas de precios (lo que da el proveedor / subcontratista)

| Archivo | Contenido | Columnas |
|---------|-----------|----------|
| `lista_precios_materiales.csv` | 250 materiales de corralon, acero, plomeria, aislacion, fenolicos, etc. | codigo, descripcion, unidad, precio_unitario |
| `lista_precios_mano_obra.csv` | 4 categorias de mano de obra (capataz, puntero, oficial, ayudante) | codigo, descripcion, unidad, precio_hora |
| `lista_precios_equipos.csv` | 24 equipos y maquinaria (minicargadora, excavadora, etc.) | codigo, descripcion, unidad, precio_unitario |
| `lista_precios_subcontratos.csv` | 56 subcontratos (pintura, durlock, electricidad, pisos, yesero, etc.) | codigo, descripcion, unidad, precio_unitario |

### Estructura de la obra (lo que define el ingeniero / arquitecto)

| Archivo | Contenido |
|---------|-----------|
| `estructura_obra.json` | Desglose de la obra en 14 secciones con sus items. Cada item tiene codigo, descripcion, unidad y cantidad. NO incluye precios. |

Las secciones son:
1. Tareas Preliminares (obrador, banos quimicos, limpieza, ayuda de gremios, encofrado)
2. Excavacion (bases, tensores, troneras)
3. Obra Gris - Fundaciones (bases, troncos, tensores, submuracion)
4. Obra Gris - Sobre Subsuelo (columnas, vigas, losa, mamposteria, contrapiso, carpeta, revoques)
5. Obra Gris - Sobre Planta Baja
6. Obra Gris - Sobre Primer Piso
7. Obra Gris - Sobre Segundo Piso
8. Obra Gris - Sobre Tercer Piso
9. Obra Gris - Sobre Cuarto Piso
10. Obra Gris - Sobre Quinto Piso
11. Obra Gris - Sobre Sexto Piso
12. Obra Gris - Sobre Septimo Piso
13. Obra Gris - Sobre Octavo Piso
14. Obra Gris - Sobre Azotea

### Configuracion de costos indirectos

| Archivo | Contenido |
|---------|-----------|
| `costos_indirectos.json` | Porcentajes de markup (gastos generales 14.2%, beneficio 25%, financiero 8.2%) y costos fijos mensuales de obra (jefatura, estructura, nafta, herramientas). |

## Como se usa

```
estructura_obra.json  -->  Define QUE se construye y CUANTO
listas_precios_*.csv  -->  Define CUANTO CUESTA cada recurso
costos_indirectos.json --> Define los RECARGOS sobre el costo directo

Sistema presupuestador:
  costo_directo = SUM(cantidad * precio_unitario) por item
  costo_indirecto = costo_directo * (1 + gastos_generales_pct/100)
  precio_venta = costo_indirecto * (1 + beneficio_pct/100)
  precio_final = precio_venta * (1 + financiero_pct/100)
```

## Datos del proyecto

- Proyecto: Edificio Las Heras - Obra Gris
- Superficie: 2,663.25 m2
- Duracion: 16 meses
- Fuente: EDIFICIO LAS HERAS-OBRA GRIS_Computo y Presupuesto.xlsx
