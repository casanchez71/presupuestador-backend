// ─── Generic Construction Tasks Template ────────────────────────────────────
// Tareas tipicas de obra residencial/comercial en Argentina.
// Cada item tiene unidad estandar y cantidad sugerida (null = definir en obra).

export interface GenericTaskItem {
  descripcion: string
  unidad: 'm2' | 'm3' | 'ml' | 'gl' | 'kg' | 'un' | 'mes'
  cantidad_sugerida: number | null
}

export interface GenericTaskCategory {
  code: string
  nombre: string
  items: GenericTaskItem[]
}

export const GENERIC_TASK_TEMPLATE: GenericTaskCategory[] = [
  {
    code: '0',
    nombre: 'Tareas Preliminares',
    items: [
      { descripcion: 'Obrador e instalaciones provisorias', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Limpieza y preparacion del terreno', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Cerco perimetral de obra', unidad: 'ml', cantidad_sugerida: null },
      { descripcion: 'Movimiento de suelos (excavacion, relleno, compactacion)', unidad: 'm3', cantidad_sugerida: null },
      { descripcion: 'Seguridad e higiene', unidad: 'mes', cantidad_sugerida: null },
      { descripcion: 'Limpieza periodica de obra', unidad: 'mes', cantidad_sugerida: null },
      { descripcion: 'Proyecto y direccion tecnica', unidad: 'gl', cantidad_sugerida: 1 },
    ],
  },
  {
    code: '1',
    nombre: 'Estructura',
    items: [
      { descripcion: 'Fundaciones (bases, zapatas, plateas)', unidad: 'm3', cantidad_sugerida: null },
      { descripcion: 'Columnas de hormigon armado', unidad: 'm3', cantidad_sugerida: null },
      { descripcion: 'Vigas de hormigon armado', unidad: 'm3', cantidad_sugerida: null },
      { descripcion: 'Losas (macizas, viguetas, steel deck)', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Escaleras de hormigon', unidad: 'un', cantidad_sugerida: null },
      { descripcion: 'Tanque de agua', unidad: 'un', cantidad_sugerida: 1 },
    ],
  },
  {
    code: '2',
    nombre: 'Albanileria',
    items: [
      { descripcion: 'Mamposteria de ladrillos (exterior)', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Mamposteria de ladrillos (interior/divisorias)', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Revoques gruesos', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Revoques finos', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Contrapiso', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Carpeta de nivelacion', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Aislaciones hidraulicas', unidad: 'm2', cantidad_sugerida: null },
    ],
  },
  {
    code: '3',
    nombre: 'Instalaciones',
    items: [
      { descripcion: 'Instalacion sanitaria (agua fria y caliente)', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Instalacion cloacal y pluvial', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Instalacion electrica', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Instalacion de gas', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Instalacion de aire acondicionado (provision de canerias)', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Instalacion contra incendio', unidad: 'gl', cantidad_sugerida: 1 },
    ],
  },
  {
    code: '4',
    nombre: 'Terminaciones',
    items: [
      { descripcion: 'Pisos (ceramicos, porcelanatos)', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Revestimientos de paredes', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Pintura interior', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Pintura exterior', unidad: 'm2', cantidad_sugerida: null },
      { descripcion: 'Carpinteria de aluminio (ventanas)', unidad: 'un', cantidad_sugerida: null },
      { descripcion: 'Carpinteria de madera (puertas)', unidad: 'un', cantidad_sugerida: null },
      { descripcion: 'Mesadas', unidad: 'ml', cantidad_sugerida: null },
      { descripcion: 'Muebles de cocina y banos', unidad: 'gl', cantidad_sugerida: 1 },
      { descripcion: 'Vidrios', unidad: 'm2', cantidad_sugerida: null },
    ],
  },
  {
    code: '5',
    nombre: 'Instalaciones Especiales',
    items: [
      { descripcion: 'Ascensor', unidad: 'un', cantidad_sugerida: null },
      { descripcion: 'Grupo electrogeno', unidad: 'un', cantidad_sugerida: null },
      { descripcion: 'Bombas', unidad: 'un', cantidad_sugerida: null },
      { descripcion: 'Portero electrico / videoportero', unidad: 'un', cantidad_sugerida: 1 },
      { descripcion: 'Sistema de seguridad (CCTV)', unidad: 'gl', cantidad_sugerida: 1 },
    ],
  },
]
