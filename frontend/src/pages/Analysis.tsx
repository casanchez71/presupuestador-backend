import { useEffect, useState, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { BarChart2, Download } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { AnalysisResponse, Budget, BudgetItem } from '../types'

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

  const sections = useMemo(() => buildSections(allItems), [allItems])

  const budgetName = budget?.name ?? 'Presupuesto'
  const itemsCount = data?.items_count ?? allItems.length
  const netoTotal = data?.neto_total ?? 0
  const matTotal = data?.mat_total ?? 0
  const moTotal = data?.mo_total ?? 0
  const directoTotal = data?.directo_total ?? 0
  const indirectoTotal = data?.indirecto_total ?? 0
  const beneficioTotal = data?.beneficio_total ?? 0

  return (
    <div className="p-6 fade-in">
      {/* Section label */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <BarChart2 size={14} /> VISTA DE ANÁLISIS
      </div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
          <h1 className="text-xl font-extrabold text-gray-900">ANÁLISIS — {budgetName.toUpperCase()}</h1>
        </div>
        <button
          onClick={() => navigate(`/app/budgets/${id ?? '1'}/export`)}
          className="bg-white border text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-50 flex items-center gap-1.5 transition-colors"
        >
          <Download size={13} /> Exportar
        </button>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-3">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando análisis...
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 text-sm text-red-700">
          <p className="font-semibold mb-1">Error al cargar el análisis</p>
          <p className="text-xs">{error}</p>
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white rounded-xl border p-4">
          <div className="text-[10px] text-gray-400 mb-1">ÍTEMS TOTALES</div>
          <div className="text-2xl font-bold text-gray-900">{itemsCount}</div>
          <div className="text-[10px] text-gray-500 mt-1">En {sections.length} secciones principales</div>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <div className="text-[10px] text-gray-400 mb-1">COSTO DIRECTO</div>
          <div className="text-2xl font-bold text-gray-900">{fmtCurrency(directoTotal)}</div>
          <div className="text-[10px] text-gray-500 mt-1">MAT {fmtCurrency(matTotal)} + MO {fmtCurrency(moTotal)}</div>
        </div>
        <div className="bg-[#2D8D68] rounded-xl p-4 text-white">
          <div className="text-[10px] text-[#E0A33A] mb-1">NETO TOTAL</div>
          <div className="text-2xl font-bold">{fmtCurrency(netoTotal)}</div>
        </div>
      </div>

      {/* 6 KPI cards */}
      <div className="grid grid-cols-6 gap-2 mb-4">
        <div className="bg-white rounded-lg border p-3 text-center">
          <div className="text-[10px] text-gray-400">Materiales</div>
          <div className="text-lg font-bold text-gray-800">{fmtCurrency(matTotal)}</div>
        </div>
        <div className="bg-white rounded-lg border p-3 text-center">
          <div className="text-[10px] text-gray-400">Mano de Obra</div>
          <div className="text-lg font-bold text-gray-800">{fmtCurrency(moTotal)}</div>
        </div>
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-3 text-center">
          <div className="text-[10px] text-blue-500">Directo</div>
          <div className="text-lg font-bold text-blue-700">{fmtCurrency(directoTotal)}</div>
        </div>
        <div className="bg-orange-50 rounded-lg border border-orange-200 p-3 text-center">
          <div className="text-[10px] text-orange-500">Indirectos</div>
          <div className="text-lg font-bold text-orange-600">{fmtCurrency(indirectoTotal)}</div>
        </div>
        <div className="bg-white rounded-lg border p-3 text-center">
          <div className="text-[10px] text-gray-400">Beneficio</div>
          <div className="text-lg font-bold text-gray-800">{fmtCurrency(beneficioTotal)}</div>
        </div>
        <div className="bg-[#2D8D68] rounded-lg p-3 text-center text-white">
          <div className="text-[10px] text-[#E0A33A]">NETO</div>
          <div className="text-lg font-bold">{fmtCurrency(netoTotal)}</div>
        </div>
      </div>

      {/* Section table */}
      <div className="bg-white rounded-xl border overflow-hidden">
        <table className="w-full text-xs">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="px-3 py-2 text-left font-semibold">Sección</th>
              <th className="px-3 py-2 text-right font-semibold">MAT</th>
              <th className="px-3 py-2 text-right font-semibold">MO</th>
              <th className="px-3 py-2 text-right font-semibold">Directo</th>
              <th className="px-3 py-2 text-right font-semibold">Indirecto</th>
              <th className="px-3 py-2 text-right font-semibold">Beneficio</th>
              <th className="px-3 py-2 text-right font-bold">Neto</th>
            </tr>
          </thead>
          <tbody>
            {sections.map((s, i) => (
              <tr key={i} className="border-b hover:bg-gray-50">
                <td className="px-3 py-2 font-medium text-gray-800">{s.name}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.mat)}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.mo)}</td>
                <td className="px-3 py-2 cost-cell text-blue-700 font-medium">{fmtCurrency(s.directo)}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.indirecto)}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.benef)}</td>
                <td className="px-3 py-2 cost-cell font-bold">{fmtCurrency(s.neto)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-[#2D8D68] text-white font-semibold">
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
  )
}
