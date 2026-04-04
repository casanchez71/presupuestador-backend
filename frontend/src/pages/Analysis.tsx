import { useEffect, useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { BarChart2, Download } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import CostSummaryBar from '../components/ui/CostSummaryBar'
import ViewModeSelector from '../components/ui/ViewModeSelector'
import { groupByFloor, groupByMaterial, groupByWorkType } from '../lib/viewModes'
import type { ViewMode } from '../lib/viewModes'
import type { AnalysisResponse, Budget, BudgetItem, TreeNode } from '../types'

interface SectionRow {
  name: string
  mat: number
  mo: number
  directo: number
  indirecto: number
  benef: number
  neto: number
}

/** Build section-level summaries from a flat items list.
 *  Section headers are items whose code matches "N-" pattern (e.g. "1- TAREAS PRELIMINARES").
 *  Line items have codes like "1.1", "1.2", etc.
 */
function buildSections(items: BudgetItem[]): SectionRow[] {
  // Identify section headers by code pattern: digit(s) followed by dash or text-only codes
  const sectionHeaders: { prefix: string; name: string }[] = []
  for (const item of items) {
    const code = item.code ?? ''
    const m = code.match(/^(\d+)\s*[-.]?\s*(.*)/)
    // A section header has no dot in the code (like "1- TAREAS PRELIMINARES")
    if (m && !code.includes('.')) {
      const prefix = m[1]
      const label = (m[2] || item.description || '').trim()
      sectionHeaders.push({ prefix, name: `${prefix}. ${label}` })
    }
  }

  if (sectionHeaders.length === 0) {
    // Fallback: treat all items as one section
    const totals = sumItems(items)
    return [{ name: 'Total', ...totals }]
  }

  return sectionHeaders.map(({ prefix, name }) => {
    const sectionItems = items.filter((i) => {
      const c = i.code ?? ''
      return c.startsWith(prefix + '.')
    })
    const totals = sumItems(sectionItems)
    return { name, ...totals }
  })
}

/** Build section rows from virtual tree nodes (used by non-rubro modes) */
function buildSectionsFromTree(nodes: TreeNode[]): SectionRow[] {
  return nodes.map((node) => {
    return {
      name: node.description ?? 'Sin nombre',
      mat: node.mat_total,
      mo: node.mo_total,
      directo: node.directo_total,
      indirecto: node.indirecto_total,
      benef: node.beneficio_total,
      neto: node.neto_total,
    }
  })
}

function sumItems(items: BudgetItem[]) {
  let mat = 0, mo = 0, directo = 0, indirecto = 0, benef = 0, neto = 0
  for (const i of items) {
    mat += i.mat_total
    mo += i.mo_total
    directo += i.directo_total
    indirecto += i.indirecto_total
    benef += i.beneficio_total
    neto += i.neto_total
  }
  return { mat, mo, directo, indirecto, benef, neto }
}

export default function Analysis() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<AnalysisResponse | null>(null)
  const [budget, setBudget] = useState<Budget | null>(null)
  const [allItems, setAllItems] = useState<BudgetItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('rubro')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    setError(null)
    Promise.all([
      budgetApi.get(id),
      budgetApi.getItems(id).catch(() => [] as BudgetItem[]),
      budgetApi.getAnalysis(id).catch(() => null),
    ])
      .then(([b, items, analysis]) => {
        setBudget(b)
        setAllItems(items)
        setData(analysis)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Error al cargar el presupuesto')
      })
      .finally(() => setLoading(false))
  }, [id])

  const sections = useMemo(() => {
    if (viewMode === 'rubro') {
      return buildSections(allItems)
    }
    // For other modes, use the grouping functions and convert tree nodes to section rows
    let grouped: TreeNode[]
    switch (viewMode) {
      case 'piso':
        grouped = groupByFloor(allItems)
        break
      case 'material':
        grouped = groupByMaterial(allItems)
        break
      case 'tipo':
        grouped = groupByWorkType(allItems)
        break
      default:
        grouped = []
    }
    if (grouped.length === 0) {
      return []
    }
    return buildSectionsFromTree(grouped)
  }, [allItems, viewMode])

  const VIEW_MODE_LABELS: Record<ViewMode, string> = {
    rubro: 'Rubro',
    piso: 'Piso',
    material: 'Material',
    tipo: 'Tipo de Trabajo',
  }

  const budgetName = budget?.name ?? 'Presupuesto'
  const itemsCount = data?.items_count ?? allItems.length
  const netoTotal = data?.neto_total ?? 0
  const matTotal = data?.mat_total ?? 0
  const moTotal = data?.mo_total ?? 0
  const directoTotal = data?.directo_total ?? 0
  const indirectoTotal = data?.indirecto_total ?? 0
  const beneficioTotal = data?.beneficio_total ?? 0

  return (
    <div className="p-4 fade-in h-full flex flex-col">
      {/* Fixed header area */}
      <div className="flex-shrink-0">
        {/* Section label */}
        <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
          <BarChart2 size={14} /> VISTA DE ANALISIS
        </div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
            <h1 className="text-xl font-extrabold text-gray-900">ANALISIS — {budgetName.toUpperCase()}</h1>
          </div>
          <button
            onClick={() => navigate(`/app/budgets/${id ?? '1'}/export`)}
            className="bg-white border text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-50 flex items-center gap-1.5 transition-colors"
          >
            <Download size={13} /> Exportar
          </button>
        </div>

        {/* View Mode Selector */}
        <div className="mb-3">
          <ViewModeSelector mode={viewMode} onChange={setViewMode} />
        </div>

        {loading && (
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-3">
            <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
            Cargando analisis...
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-3 text-sm text-red-700">
            <p className="font-semibold mb-1">Error al cargar el analisis</p>
            <p className="text-xs">{error}</p>
          </div>
        )}

        {/* Summary bar — same CostSummaryBar as Editor */}
        <div className="rounded-xl border mb-3 overflow-hidden">
          <CostSummaryBar mat={matTotal} mo={moTotal} directo={directoTotal} indirecto={indirectoTotal} neto={netoTotal} />
        </div>
      </div>

      {/* Scrollable table area */}
      <div className="flex-1 min-h-0 bg-white rounded-xl border overflow-hidden flex flex-col">
        <div className="bg-gray-50 px-3 py-2 border-b flex-shrink-0">
          <span className="text-[10px] font-bold text-gray-500 tracking-wide">
            DESGLOSE POR {VIEW_MODE_LABELS[viewMode].toUpperCase()}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-xs">
            <thead className="bg-gray-50 text-gray-600 sticky top-0">
              <tr>
                <th className="px-3 py-2 text-left font-semibold border-b">Seccion</th>
                <th className="px-3 py-2 text-right font-semibold border-b">MAT</th>
                <th className="px-3 py-2 text-right font-semibold border-b">MO</th>
                <th className="px-3 py-2 text-right font-semibold border-b">Directo</th>
                <th className="px-3 py-2 text-right font-semibold border-b">Indirecto</th>
                <th className="px-3 py-2 text-right font-semibold border-b">Beneficio</th>
                <th className="px-3 py-2 text-right font-bold border-b">Neto</th>
              </tr>
            </thead>
            <tbody>
              {sections.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-3 py-8 text-center text-gray-400">
                    No hay datos para agrupar con esta vista.
                  </td>
                </tr>
              ) : (
                sections.map((s, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="px-3 py-2 font-medium text-gray-800">{s.name}</td>
                    <td className="px-3 py-2 cost-cell">{fmtCurrency(s.mat)}</td>
                    <td className="px-3 py-2 cost-cell">{fmtCurrency(s.mo)}</td>
                    <td className="px-3 py-2 cost-cell text-blue-700 font-medium">{fmtCurrency(s.directo)}</td>
                    <td className="px-3 py-2 cost-cell">{fmtCurrency(s.indirecto)}</td>
                    <td className="px-3 py-2 cost-cell">{fmtCurrency(s.benef)}</td>
                    <td className="px-3 py-2 cost-cell font-bold">{fmtCurrency(s.neto)}</td>
                  </tr>
                ))
              )}
            </tbody>
            <tfoot className="bg-[#2D8D68] text-white font-semibold sticky bottom-0">
              <tr>
                <td className="px-3 py-3">TOTAL OBRA</td>
                <td className="px-3 py-3 cost-cell">{fmtCurrency(matTotal)}</td>
                <td className="px-3 py-3 cost-cell">{fmtCurrency(moTotal)}</td>
                <td className="px-3 py-3 cost-cell text-green-200">{fmtCurrency(directoTotal)}</td>
                <td className="px-3 py-3 cost-cell">{fmtCurrency(indirectoTotal)}</td>
                <td className="px-3 py-3 cost-cell">{fmtCurrency(beneficioTotal)}</td>
                <td className="px-3 py-3 cost-cell text-[#E0A33A] text-base font-bold">{fmtCurrency(netoTotal)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  )
}
