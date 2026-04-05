import { useEffect, useState } from 'react'
import { Library, ChevronDown, ChevronRight, Trash2, Plus } from 'lucide-react'
import { templateApi } from '../lib/api'

// ─── Types ─────────────────────────────────────────────────────────────────────

interface TemplateResource {
  tipo: string
  codigo?: string
  descripcion?: string
  unidad?: string
  cantidad_por_unidad?: number
  desperdicio_pct?: number
  trabajadores_por_unidad?: number
  dias_por_unidad?: number
  cargas_sociales_pct?: number
}

interface Template {
  id: string
  org_id: string
  nombre: string
  descripcion?: string
  unidad?: string
  categoria?: string
  recursos: TemplateResource[] | string
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

const TIPO_LABELS: Record<string, string> = {
  material: 'Materiales',
  mano_obra: 'Mano de Obra',
  equipo: 'Equipos',
  mo_material: 'Mat. Indirectos',
  subcontrato: 'Subcontratos',
}

const TIPO_ORDER = ['material', 'mano_obra', 'equipo', 'mo_material', 'subcontrato']

function parseRecursos(recursos: TemplateResource[] | string): TemplateResource[] {
  if (typeof recursos === 'string') {
    try {
      return JSON.parse(recursos)
    } catch {
      return []
    }
  }
  return recursos || []
}

function groupByTipo(recursos: TemplateResource[]): Record<string, TemplateResource[]> {
  const groups: Record<string, TemplateResource[]> = {}
  for (const r of recursos) {
    const tipo = r.tipo || 'material'
    if (!groups[tipo]) groups[tipo] = []
    groups[tipo].push(r)
  }
  return groups
}

// ─── TemplateCard ──────────────────────────────────────────────────────────────

function TemplateCard({
  template,
  onDelete,
}: {
  template: Template
  onDelete: (id: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const recursos = parseRecursos(template.recursos)
  const groups = groupByTipo(recursos)

  async function handleDelete() {
    if (!confirmDelete) {
      setConfirmDelete(true)
      return
    }
    setDeleting(true)
    try {
      await templateApi.remove(template.id)
      onDelete(template.id)
    } catch {
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border overflow-hidden hover:shadow-md transition-shadow">
      {/* Card header */}
      <div
        className="p-4 flex items-start justify-between cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <div className="flex-1 min-w-0 mr-3">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-semibold text-sm text-gray-900">{template.nombre}</span>
            {template.unidad && (
              <span className="bg-blue-100 text-blue-700 rounded text-xs px-2 py-0.5 font-medium">
                {template.unidad}
              </span>
            )}
            {template.categoria && (
              <span className="bg-purple-100 text-purple-700 rounded text-xs px-2 py-0.5 font-medium">
                {template.categoria}
              </span>
            )}
          </div>
          {template.descripcion && (
            <p className="text-xs text-gray-400 mt-0.5 truncate">{template.descripcion}</p>
          )}
          <p className="text-xs text-gray-400 mt-1">
            {recursos.length} {recursos.length === 1 ? 'recurso' : 'recursos'}
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Delete button */}
          <button
            onClick={(e) => { e.stopPropagation(); handleDelete() }}
            disabled={deleting}
            className={`text-xs px-2 py-1 rounded transition-colors flex items-center gap-1 ${
              confirmDelete
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
            } disabled:opacity-50`}
            title={confirmDelete ? 'Confirmar eliminacion' : 'Eliminar template'}
          >
            {deleting ? (
              <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : (
              <Trash2 size={13} />
            )}
            {confirmDelete && !deleting && <span>Confirmar</span>}
          </button>

          {/* Expand icon */}
          {open
            ? <ChevronDown size={16} className="text-gray-400" />
            : <ChevronRight size={16} className="text-gray-400" />
          }
        </div>
      </div>

      {/* Expandable recursos section */}
      {open && (
        <div className="border-t fade-in">
          {recursos.length === 0 ? (
            <p className="p-4 text-xs text-gray-400 italic">Sin recursos definidos</p>
          ) : (
            TIPO_ORDER.filter((tipo) => groups[tipo]?.length).map((tipo) => (
              <div key={tipo}>
                {/* Group header */}
                <div className="px-4 py-1.5 bg-[#F0FAF5] border-b border-t text-[10px] font-bold text-[#1B5E4B] tracking-wide">
                  {TIPO_LABELS[tipo] || tipo}
                </div>

                <table className="w-full text-[11px]">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Codigo</th>
                      <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Descripcion</th>
                      {tipo === 'mano_obra' ? (
                        <>
                          <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Trabaj.</th>
                          <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Dias</th>
                          <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Cargas %</th>
                        </>
                      ) : (
                        <>
                          <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Cant./Unid.</th>
                          <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Unidad</th>
                          <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Desperd. %</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {groups[tipo].map((r, i) => (
                      <tr key={i} className="border-b last:border-0 hover:bg-gray-50">
                        <td className="px-3 py-1.5 font-mono text-gray-400">{r.codigo || '—'}</td>
                        <td className="px-3 py-1.5 text-gray-800">{r.descripcion || '—'}</td>
                        {tipo === 'mano_obra' ? (
                          <>
                            <td className="px-3 py-1.5 text-right text-gray-700">{r.trabajadores_por_unidad ?? '—'}</td>
                            <td className="px-3 py-1.5 text-right text-gray-700">{r.dias_por_unidad ?? '—'}</td>
                            <td className="px-3 py-1.5 text-right text-gray-700">{r.cargas_sociales_pct ?? 25}%</td>
                          </>
                        ) : (
                          <>
                            <td className="px-3 py-1.5 text-right text-gray-700">{r.cantidad_por_unidad ?? '—'}</td>
                            <td className="px-3 py-1.5 text-gray-500">{r.unidad || '—'}</td>
                            <td className="px-3 py-1.5 text-right text-gray-700">{r.desperdicio_pct ?? 0}%</td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

// ─── Templates page ────────────────────────────────────────────────────────────

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [activeCategory, setActiveCategory] = useState<string>('Todos')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    templateApi.categories()
      .then(setCategories)
      .catch(() => {/* silently ignore */})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    const categoria = activeCategory === 'Todos' ? undefined : activeCategory
    templateApi.list(categoria)
      .then((data) => setTemplates(data as Template[]))
      .catch((err) => setError(err instanceof Error ? err.message : 'Error al cargar templates'))
      .finally(() => setLoading(false))
  }, [activeCategory])

  function handleDelete(id: string) {
    setTemplates((prev) => prev.filter((t) => t.id !== id))
  }

  return (
    <div className="p-6 fade-in">
      {/* Header */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Library size={14} /> COMPOSICIONES
      </div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">BIBLIOTECA DE TEMPLATES</h1>
        <span className="bg-[#E8F5EE] text-[#1B5E4B] text-xs font-medium px-2 py-0.5 rounded-full">
          {templates.length} templates
        </span>
      </div>

      {/* Category filter pills */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-5">
          {['Todos', ...categories].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${
                activeCategory === cat
                  ? 'bg-[#2D8D68] text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando templates...
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 text-sm text-red-700">
          <p className="font-semibold mb-1">Error al cargar templates</p>
          <p className="text-xs">{error}</p>
        </div>
      )}

      {/* Content */}
      <div className="max-w-3xl space-y-3">
        {!loading && !error && templates.length === 0 && (
          <div className="bg-white rounded-xl border p-8 text-center text-gray-400">
            <Library size={32} className="mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No hay templates cargados.</p>
            <p className="text-xs mt-1">
              {activeCategory !== 'Todos'
                ? `No hay templates en la categoria "${activeCategory}".`
                : 'Importa un Excel con composiciones para crear templates.'}
            </p>
          </div>
        )}

        {templates.map((t) => (
          <TemplateCard key={t.id} template={t} onDelete={handleDelete} />
        ))}

        {/* Nuevo Template button — placeholder */}
        <button
          disabled
          className="w-full border-2 border-dashed border-gray-200 text-gray-400 py-3 rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2 cursor-not-allowed"
          title="Proximamente"
        >
          <Plus size={16} /> Nuevo Template (proximamente)
        </button>
      </div>
    </div>
  )
}
