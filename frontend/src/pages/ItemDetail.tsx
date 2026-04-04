import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronRight, ChevronDown, ClipboardList, History, Pencil, Upload, Cpu, BookOpen, Calculator, Check, X } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency, fmtNumber, fmtPercent } from '../lib/format'
import type { ItemResource, BudgetItem, Budget, ItemAudit } from '../types'


type Tipo = ItemResource['tipo']

const TIPO_LABELS: Record<Tipo, string> = {
  material: 'Materiales',
  mano_obra: 'Mano de Obra',
  equipo: 'Equipos',
  subcontrato: 'Subcontratos',
}

const FIELD_LABELS: Record<string, string> = {
  cantidad: 'Cantidad',
  mat_unitario: 'MAT Unitario',
  mo_unitario: 'MO Unitario',
  description: 'Descripcion',
  unidad: 'Unidad',
  code: 'Codigo',
  notas_calculo: 'Memoria de Calculo',
}

const SOURCE_CONFIG: Record<string, { label: string; icon: typeof Pencil; color: string }> = {
  manual_edit: { label: 'Edicion manual', icon: Pencil, color: 'text-blue-600' },
  ai_suggestion: { label: 'Sugerencia IA', icon: Cpu, color: 'text-purple-600' },
  excel_import: { label: 'Importacion Excel', icon: Upload, color: 'text-green-600' },
  catalog_update: { label: 'Catalogo de precios', icon: BookOpen, color: 'text-orange-600' },
}

function timeAgo(dateStr: string): string {
  const now = new Date()
  const date = new Date(dateStr)
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHr = Math.floor(diffMin / 60)
  const diffDays = Math.floor(diffHr / 24)

  if (diffMin < 1) return 'hace un momento'
  if (diffMin < 60) return `hace ${diffMin} min`
  if (diffHr < 24) return `hace ${diffHr}h`
  if (diffDays < 7) return `hace ${diffDays}d`
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function ResourceTable({ recursos, tipo }: { recursos: ItemResource[]; tipo: Tipo }) {
  const filtered = recursos.filter((r) => r.tipo === tipo)
  const total = filtered.reduce((s, r) => s + r.subtotal, 0)

  return (
    <div className="bg-white rounded-xl border overflow-hidden">
      <div className="bg-gray-100 px-4 py-2 flex justify-between items-center border-b">
        <span className="font-bold text-sm text-gray-800">{TIPO_LABELS[tipo]}</span>
        <span className="text-[10px] text-gray-400">{filtered.length} recursos</span>
      </div>
      {filtered.length === 0 ? (
        <div className="p-4 text-xs text-gray-400 italic">Sin {TIPO_LABELS[tipo].toLowerCase()} para este item</div>
      ) : (
        <table className="w-full text-xs">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Codigo</th>
              <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Descripcion</th>
              <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Cant</th>
              <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Desp%</th>
              <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Cant+Desp</th>
              <th className="px-3 py-1.5 text-right text-gray-500 font-medium">P.Unit</th>
              <th className="px-3 py-1.5 text-right text-gray-500 font-medium">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-b hover:bg-gray-50">
                <td className="px-3 py-1.5 font-mono text-gray-400">{r.codigo}</td>
                <td className="px-3 py-1.5 text-gray-800">{r.descripcion}</td>
                <td className="px-3 py-1.5 cost-cell">{r.cantidad !== undefined ? fmtNumber(r.cantidad, 0) : '—'}</td>
                <td className="px-3 py-1.5 cost-cell text-orange-500">{fmtPercent(r.desperdicio_pct)}</td>
                <td className="px-3 py-1.5 cost-cell font-medium">
                  {r.cantidad_efectiva !== undefined ? fmtNumber(r.cantidad_efectiva, 0) : '—'}
                </td>
                <td className="px-3 py-1.5 cost-cell">
                  {r.precio_unitario !== undefined ? fmtCurrency(r.precio_unitario) : '—'}
                </td>
                <td className="px-3 py-1.5 cost-cell font-bold">{fmtCurrency(r.subtotal)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-[#E8F5EE]">
            <tr>
              <td colSpan={6} className="px-3 py-2 text-right font-bold text-xs text-[#1B5E4B]">
                TOTAL {TIPO_LABELS[tipo].toUpperCase()}
              </td>
              <td className="px-3 py-2 cost-cell font-bold text-[#2D8D68]">{fmtCurrency(total)}</td>
            </tr>
          </tfoot>
        </table>
      )}
    </div>
  )
}

function AuditHistory({ audits, loading }: { audits: ItemAudit[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-400 p-4">
        <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
        Cargando historial...
      </div>
    )
  }

  if (audits.length === 0) {
    return (
      <div className="p-6 text-center text-gray-400 text-sm">
        Sin cambios registrados para este item.
      </div>
    )
  }

  return (
    <div className="divide-y">
      {audits.map((audit) => {
        const config = SOURCE_CONFIG[audit.source] ?? SOURCE_CONFIG.manual_edit
        const Icon = config.icon
        const fieldLabel = FIELD_LABELS[audit.field] ?? audit.field

        return (
          <div key={audit.id} className="px-4 py-3 flex items-start gap-3 hover:bg-gray-50">
            <div className={`mt-0.5 p-1 rounded-full bg-gray-100 ${config.color}`}>
              <Icon size={12} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs text-gray-800">
                <span className="font-medium">{fieldLabel}</span>
                {' cambio de '}
                <span className="font-mono bg-red-50 text-red-700 px-1 rounded text-[10px]">
                  {audit.old_value ?? '—'}
                </span>
                {' a '}
                <span className="font-mono bg-green-50 text-green-700 px-1 rounded text-[10px]">
                  {audit.new_value ?? '—'}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[10px] text-gray-400">{timeAgo(audit.created_at)}</span>
                <span className={`text-[10px] ${config.color}`}>{config.label}</span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function ItemDetail() {
  const { id, itemId } = useParams<{ id: string; itemId: string }>()
  const navigate = useNavigate()
  const [budget, setBudget] = useState<Budget | null>(null)
  const [item, setItem] = useState<BudgetItem | null>(null)
  const [recursos, setRecursos] = useState<ItemResource[]>([])
  const [audits, setAudits] = useState<ItemAudit[]>([])
  const [loading, setLoading] = useState(true)
  const [auditsLoading, setAuditsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [memoriaOpen, setMemoriaOpen] = useState(false)
  const [editingMemoria, setEditingMemoria] = useState(false)
  const [memoriaDraft, setMemoriaDraft] = useState('')
  const [memoriaSaving, setMemoriaSaving] = useState(false)

  useEffect(() => {
    if (!id || !itemId) {
      setLoading(false)
      setAuditsLoading(false)
      setError('Faltan parametros de presupuesto o item.')
      return
    }

    let cancelled = false

    // Load budget, item info, and resources in parallel
    Promise.all([
      budgetApi.get(id).catch(() => null),
      budgetApi.getItems(id).then((items) => items.find((i) => i.id === itemId) ?? null).catch(() => null),
      budgetApi.getItemResources(id, itemId).catch(() => [] as ItemResource[]),
    ]).then(([b, it, res]) => {
      if (cancelled) return
      if (b) setBudget(b)
      if (it) setItem(it)
      setRecursos(Array.isArray(res) ? res : [])
      if (!it) {
        setError('No se encontro el item. Puede ser una seccion sin detalle de recursos.')
      }
    }).catch(() => {
      if (!cancelled) setError('Error cargando datos del item.')
    }).finally(() => {
      if (!cancelled) setLoading(false)
    })

    // Load audits separately (may fail if table doesn't exist)
    budgetApi.getItemAudits(id, itemId)
      .then((data) => { if (!cancelled) setAudits(Array.isArray(data) ? data : []) })
      .catch(() => { if (!cancelled) setAudits([]) })
      .finally(() => { if (!cancelled) setAuditsLoading(false) })

    return () => { cancelled = true }
  }, [id, itemId])

  // Use the item's own cost fields (from BudgetItem) as the source of truth for the summary.
  // Only fall back to summing resources if the item fields are zero/missing.
  const resourceMat = recursos.filter((r) => r.tipo === 'material').reduce((s, r) => s + r.subtotal, 0)
  const resourceMO = recursos.filter((r) => r.tipo === 'mano_obra').reduce((s, r) => s + r.subtotal, 0)
  const totalMat = (item?.mat_total ?? 0) !== 0 ? (item?.mat_total ?? 0) : resourceMat
  const totalMO = (item?.mo_total ?? 0) !== 0 ? (item?.mo_total ?? 0) : resourceMO
  const costoDirecto = (item?.directo_total ?? 0) !== 0 ? (item?.directo_total ?? 0) : totalMat + totalMO
  const cantidad = item?.cantidad ?? 0
  const desperdicio = 10

  // Show loading spinner while fetching
  if (loading) {
    return (
      <div className="p-6 fade-in">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando detalle del item...
        </div>
      </div>
    )
  }

  // Show error state with a back button
  if (error && !item) {
    return (
      <div className="p-6 fade-in">
        <div className="flex items-center gap-1.5 text-xs mb-4">
          <span className="text-gray-400 cursor-pointer hover:text-[#2D8D68]" onClick={() => navigate('/app/dashboard')}>Presupuestos</span>
          <ChevronRight size={12} className="text-gray-300" />
          <span className="text-gray-400 cursor-pointer hover:text-[#2D8D68]" onClick={() => navigate(`/app/budgets/${id ?? '1'}/editor`)}>{budget?.name ?? 'Presupuesto'}</span>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-6 text-center">
          <div className="text-orange-700 font-medium text-sm mb-2">{error}</div>
          <button
            onClick={() => navigate(`/app/budgets/${id ?? '1'}/editor`)}
            className="text-xs bg-[#2D8D68] hover:bg-[#1B5E4B] text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Volver al editor
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 fade-in">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs mb-2">
        <span className="text-gray-400 cursor-pointer hover:text-[#2D8D68]" onClick={() => navigate('/app/dashboard')}>Presupuestos</span>
        <ChevronRight size={12} className="text-gray-300" />
        <span className="text-gray-400 cursor-pointer hover:text-[#2D8D68]" onClick={() => navigate(`/app/budgets/${id ?? '1'}/editor`)}>{budget?.name ?? 'Presupuesto'}</span>
        <ChevronRight size={12} className="text-gray-300" />
        <span className="font-semibold text-gray-900">{item ? `${item.code ?? ''} ${item.description ?? ''}`.trim() : 'Item'}</span>
      </div>

      {/* Section label */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <ClipboardList size={14} /> DETALLE DE RECURSOS
      </div>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">{item ? `${item.code ?? ''} ${item.description ?? ''}`.trim().toUpperCase() : 'DETALLE DE ITEM'}</h1>
      </div>

      {/* Item summary */}
      <div className="bg-white rounded-xl border p-4 mb-4 flex items-center gap-8 flex-wrap">
        <div>
          <div className="text-[10px] text-gray-400">Unidad</div>
          <div className="font-bold text-gray-800">{item?.unidad ?? '—'}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400">Cantidad</div>
          <div className="font-bold text-gray-800">{fmtNumber(cantidad, 2)}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400">Desperdicio</div>
          <div className="font-bold text-orange-600">{desperdicio}%</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400">Cantidad Efectiva</div>
          <div className="font-bold text-[#2D8D68]">{fmtNumber(cantidad * (1 + desperdicio / 100), 0)} {item?.unidad ?? ''}</div>
        </div>
        <div className="ml-auto text-right">
          <div className="text-[10px] text-gray-400">Formula</div>
          <div className="font-mono text-xs text-gray-600">
            {fmtNumber(cantidad, 2)} x (1 + 0.{desperdicio}) ={' '}
            <strong>{fmtNumber(cantidad * (1 + desperdicio / 100), 0)} {item?.unidad ?? ''}</strong>
          </div>
        </div>
      </div>

      {/* Cost quick summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gray-50 rounded-lg p-3 border text-center">
          <div className="text-[10px] text-gray-400">MAT Unitario</div>
          <div className="font-bold text-gray-800">{fmtCurrency(item?.mat_unitario ?? 0)}</div>
          <div className="text-[10px] text-gray-400 mt-1">Total MAT</div>
          <div className="font-semibold text-gray-700 text-sm">{fmtCurrency(totalMat)}</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border text-center">
          <div className="text-[10px] text-gray-400">MO Unitario</div>
          <div className="font-bold text-gray-800">{fmtCurrency(item?.mo_unitario ?? 0)}</div>
          <div className="text-[10px] text-gray-400 mt-1">Total MO</div>
          <div className="font-semibold text-gray-700 text-sm">{fmtCurrency(totalMO)}</div>
        </div>
        <div className="bg-[#E8F5EE] rounded-lg p-3 border border-[#2D8D68] text-center">
          <div className="text-[10px] text-[#1B5E4B]">Costo Directo</div>
          <div className="font-bold text-[#2D8D68]">{fmtCurrency(costoDirecto)}</div>
          {(item?.neto_total ?? 0) > 0 && (
            <>
              <div className="text-[10px] text-[#1B5E4B] mt-1">Neto Total</div>
              <div className="font-semibold text-[#2D8D68] text-sm">{fmtCurrency(item?.neto_total ?? 0)}</div>
            </>
          )}
        </div>
      </div>

      {/* Resource tables 2x2 */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <ResourceTable recursos={recursos} tipo="material" />
        <ResourceTable recursos={recursos} tipo="mano_obra" />
        <ResourceTable recursos={recursos} tipo="equipo" />
        <ResourceTable recursos={recursos} tipo="subcontrato" />
      </div>

      {/* Memoria de Calculo */}
      <div className="bg-white rounded-xl border overflow-hidden mb-6">
        <button
          onClick={() => setMemoriaOpen(!memoriaOpen)}
          className="w-full bg-gray-100 px-4 py-2.5 flex items-center gap-2 border-b hover:bg-gray-200 transition-colors"
        >
          <Calculator size={14} className="text-[#2D8D68]" />
          <span className="font-bold text-sm text-gray-800">Memoria de Calculo</span>
          {item?.notas_calculo && (
            <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full font-medium">
              con datos
            </span>
          )}
          <span className="ml-auto">
            {memoriaOpen ? <ChevronDown size={14} className="text-gray-400" /> : <ChevronRight size={14} className="text-gray-400" />}
          </span>
        </button>
        {memoriaOpen && (
          <div className="p-4">
            {editingMemoria ? (
              <div className="space-y-3">
                <textarea
                  value={memoriaDraft}
                  onChange={(e) => setMemoriaDraft(e.target.value)}
                  rows={8}
                  className="w-full border rounded-lg p-3 text-sm font-mono text-gray-700 focus:ring-2 focus:ring-[#2D8D68] focus:border-[#2D8D68] outline-none resize-y"
                  placeholder="Ej: Largo 4.50m x Ancho 3.20m = 14.40 m2&#10;Desperdicio 5%: 14.40 x 1.05 = 15.12 m2"
                />
                <div className="flex items-center gap-2">
                  <button
                    disabled={memoriaSaving}
                    onClick={async () => {
                      if (!id || !itemId) return
                      setMemoriaSaving(true)
                      try {
                        const result = await budgetApi.updateItem(id, itemId, { notas_calculo: memoriaDraft } as Partial<BudgetItem>)
                        if (result && typeof result === 'object' && 'item' in result) {
                          const updatedItem = (result as { item: BudgetItem }).item
                          setItem(updatedItem)
                        } else {
                          setItem((prev) => prev ? { ...prev, notas_calculo: memoriaDraft } : prev)
                        }
                        setEditingMemoria(false)
                        // Refresh audits to show the new entry
                        budgetApi.getItemAudits(id, itemId)
                          .then((data) => setAudits(Array.isArray(data) ? data : []))
                          .catch(() => {})
                      } catch {
                        // silently fail
                      } finally {
                        setMemoriaSaving(false)
                      }
                    }}
                    className="flex items-center gap-1 bg-[#2D8D68] hover:bg-[#1B5E4B] text-white text-xs px-3 py-1.5 rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    <Check size={12} />
                    {memoriaSaving ? 'Guardando...' : 'Guardar'}
                  </button>
                  <button
                    disabled={memoriaSaving}
                    onClick={() => setEditingMemoria(false)}
                    className="flex items-center gap-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs px-3 py-1.5 rounded-lg font-medium transition-colors"
                  >
                    <X size={12} />
                    Cancelar
                  </button>
                </div>
              </div>
            ) : (
              <div>
                {item?.notas_calculo ? (
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono bg-gray-50 rounded-lg p-3 mb-3">{item.notas_calculo}</pre>
                ) : (
                  <p className="text-sm text-gray-400 italic mb-3">Sin memoria de calculo para este item.</p>
                )}
                <button
                  onClick={() => {
                    setMemoriaDraft(item?.notas_calculo ?? '')
                    setEditingMemoria(true)
                  }}
                  className="flex items-center gap-1 text-xs text-[#2D8D68] hover:text-[#1B5E4B] font-medium transition-colors"
                >
                  <Pencil size={12} />
                  {item?.notas_calculo ? 'Editar memoria' : 'Agregar memoria de calculo'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Audit History */}
      <div className="bg-white rounded-xl border overflow-hidden">
        <div className="bg-gray-100 px-4 py-2.5 flex items-center gap-2 border-b">
          <History size={14} className="text-[#2D8D68]" />
          <span className="font-bold text-sm text-gray-800">Historial de cambios</span>
          {audits.length > 0 && (
            <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full font-medium">
              {audits.length}
            </span>
          )}
        </div>
        <AuditHistory audits={audits} loading={auditsLoading} />
      </div>
    </div>
  )
}
