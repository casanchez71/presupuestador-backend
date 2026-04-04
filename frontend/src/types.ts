export interface Budget {
  id: string
  org_id: string
  name: string
  description?: string
  source_file?: string
  status: string
  created_at: string
  updated_at: string
}

export interface BudgetItem {
  id: string
  budget_id: string
  org_id: string
  parent_id?: string
  code?: string
  description?: string
  unidad?: string
  cantidad?: number
  mat_unitario: number
  mo_unitario: number
  mat_total: number
  mo_total: number
  directo_total: number
  indirecto_total: number
  beneficio_total: number
  neto_total: number
  notas?: string
  notas_calculo?: string
  sort_order: number
  children?: BudgetItem[]
}

export interface ItemResource {
  id: string
  item_id: string
  org_id: string
  tipo: 'material' | 'mano_obra' | 'equipo' | 'subcontrato'
  codigo?: string
  descripcion?: string
  unidad?: string
  cantidad?: number
  desperdicio_pct: number
  cantidad_efectiva?: number
  precio_unitario?: number
  subtotal: number
}

export interface PriceCatalog {
  id: string
  org_id: string
  name: string
  tipo?: string
  source_file?: string
  created_at: string
}

export interface CatalogEntry {
  id: string
  catalog_id: string
  tipo: string
  codigo?: string
  descripcion?: string
  unidad?: string
  precio_con_iva?: number
  precio_sin_iva?: number
}

export interface AnalysisResponse {
  mat_total: number
  mo_total: number
  directo_total: number
  indirecto_total: number
  beneficio_total: number
  neto_total: number
  items_count: number
}

export interface IndirectConfig {
  id: string
  org_id: string
  estructura_pct: number
  jefatura_pct: number
  logistica_pct: number
  herramientas_pct: number
  beneficio_pct?: number
}

export interface BudgetVersion {
  id: string
  budget_id: string
  version: number
  data: unknown
  created_at: string
}

export interface ItemAudit {
  id: string
  item_id: string
  budget_id: string
  org_id: string
  user_id: string
  field: string
  old_value: string | null
  new_value: string | null
  source: string
  created_at: string
}

export type TreeNode = BudgetItem & { children: TreeNode[] }

// ─── AI Plan Analysis ─────────────────────────────────────────────────────────

export interface AIProyecto {
  descripcion: string
  superficie_total_m2: number
  ambientes_detectados: string[]
}

export interface AIItem {
  codigo: string
  descripcion: string
  unidad: string
  cantidad: number
  confianza: 'alta' | 'media' | 'baja'
  notas: string
  notas_calculo: string
}

export interface AISeccion {
  codigo: string
  nombre: string
  items: AIItem[]
}

export interface AIAnalysisResult {
  budget_id: string
  proyecto: AIProyecto
  secciones: AISeccion[]
  total_items: number
}

export interface AIItemToInsert {
  seccion_nombre: string
  seccion_codigo: string
  codigo: string
  descripcion: string
  unidad: string
  cantidad: number
  notas: string
  notas_calculo: string
}
