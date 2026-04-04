import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LayoutGrid, Clock, TrendingUp, DollarSign, Plus } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { Budget, AnalysisResponse } from '../types'
import BudgetCard from '../components/ui/BudgetCard'

function timeAgo(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'ahora'
  if (diffMins < 60) return `hace ${diffMins} min`
  if (diffHours < 24) return `hace ${diffHours} hs`
  if (diffDays < 7) return `hace ${diffDays} días`
  return date.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

export default function Dashboard() {
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [analyses, setAnalyses] = useState<Record<string, AnalysisResponse>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    budgetApi.list()
      .then((list) => {
        setBudgets(list)
        // Fetch analysis (totals) for each budget
        return Promise.allSettled(
          list.map((b) =>
            budgetApi.getAnalysis(b.id).then((a) => ({ id: b.id, analysis: a }))
          )
        )
      })
      .then((results) => {
        const map: Record<string, AnalysisResponse> = {}
        for (const r of results) {
          if (r.status === 'fulfilled') {
            map[r.value.id] = r.value.analysis
          }
        }
        setAnalyses(map)
      })
      .catch(() => setError('No se pudieron cargar los presupuestos.'))
      .finally(() => setLoading(false))
  }, [])

  const totalItems = Object.values(analyses).reduce((s, a) => s + (a.items_count ?? 0), 0)
  const totalNeto = Object.values(analyses).reduce((s, a) => s + (a.neto_total ?? 0), 0)
  const pendingCount = budgets.filter((b) => b.status?.toLowerCase() === 'borrador').length

  return (
    <div className="p-6 fade-in">
      {/* Section header */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <LayoutGrid size={14} />
        CENTRO DE PRESUPUESTOS
      </div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-1 h-8 bg-[#2D8D68] rounded-full" />
          <h1 className="text-2xl font-extrabold text-gray-900">MIS PRESUPUESTOS</h1>
          <span className="bg-[#E8F5EE] text-[#1B5E4B] text-xs font-medium px-2 py-0.5 rounded-full">
            {budgets.length} obras
          </span>
        </div>
        <button
          onClick={() => navigate('/app/new-project')}
          className="bg-[#2D8D68] hover:bg-[#1B5E4B] text-white font-semibold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 transition-colors"
        >
          <Plus size={14} /> Nuevo presupuesto
        </button>
      </div>

      {/* KPI cards */}
      <div className="text-[10px] font-bold text-gray-400 tracking-wider mb-2">RESUMEN GENERAL</div>
      <div className="grid grid-cols-4 gap-3 mb-6">
        <KpiCard icon={<LayoutGrid size={16} strokeWidth={1.5} className="text-[#2D8D68]" />} bg="bg-[#E8F5EE]" value={String(budgets.length)} label="OBRAS ACTIVAS" />
        <KpiCard icon={<Clock size={16} strokeWidth={1.5} className="text-orange-500" />} bg="bg-orange-50" value={String(pendingCount)} label="PENDIENTE REVISIÓN" valueClass="text-orange-600" />
        <KpiCard icon={<TrendingUp size={16} strokeWidth={1.5} className="text-blue-600" />} bg="bg-blue-50" value={String(totalItems)} label="ÍTEMS TOTALES" valueClass="text-blue-600" />
        <KpiCard icon={<DollarSign size={16} strokeWidth={1.5} className="text-[#2D8D68]" />} bg="bg-[#E8F5EE]" value={totalNeto > 0 ? fmtCurrency(totalNeto) : '$0'} label="NETO TOTAL CARTERA" />
      </div>

      {/* Loading / error */}
      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando presupuestos...
        </div>
      )}
      {error && (
        <div className="mb-4 bg-amber-50 border border-amber-200 text-amber-700 text-xs px-4 py-2 rounded-lg">
          {error} Mostrando datos de ejemplo.
        </div>
      )}

      {/* Budget cards */}
      {!loading && budgets.length === 0 && !error && (
        <div className="mb-6 text-center py-12 bg-white rounded-xl border">
          <p className="text-gray-500 text-sm mb-2">No hay presupuestos todavía.</p>
          <button
            onClick={() => navigate('/app/new-project')}
            className="bg-[#2D8D68] hover:bg-[#1B5E4B] text-white font-semibold px-4 py-2 rounded-lg text-xs transition-colors"
          >
            Importar Excel
          </button>
        </div>
      )}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {budgets.map((b) => {
          const a = analyses[b.id]
          return (
            <BudgetCard
              key={b.id}
              budget={b}
              directTotal={a?.directo_total}
              netoTotal={a?.neto_total}
              subtitle={a ? `${a.items_count} ítems` : undefined}
            />
          )
        })}
      </div>

      {/* Activity — real recent budgets */}
      {budgets.length > 0 && (
        <div className="bg-white rounded-xl border p-5">
          <h3 className="font-semibold text-gray-900 text-sm mb-3">ACTIVIDAD RECIENTE</h3>
          <div className="space-y-2 text-sm">
            {budgets.slice(0, 5).map((b, i) => {
              const a = analyses[b.id]
              const dateStr = b.updated_at || b.created_at
              const itemsText = a ? `${a.items_count} items` : ''
              const statusText = b.status === 'draft' ? 'Borrador' : b.status === 'approved' ? 'Aprobado' : (b.status || '')
              const detail = [statusText, itemsText].filter(Boolean).join(' - ')
              return (
                <div
                  key={b.id}
                  className={`flex justify-between items-center py-2 cursor-pointer hover:bg-gray-50 rounded-lg px-2 -mx-2 transition-colors ${i < Math.min(budgets.length, 5) - 1 ? 'border-b border-gray-50' : ''}`}
                  onClick={() => navigate(`/app/budget/${b.id}`)}
                >
                  <div>
                    <span className="font-semibold text-gray-900">{b.name}</span>
                    {detail && <span className="text-gray-500 ml-2">{detail}</span>}
                  </div>
                  <span className="text-gray-400 text-xs whitespace-nowrap ml-4">
                    {dateStr ? timeAgo(dateStr) : ''}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

function KpiCard({
  icon, bg, value, label, valueClass = 'text-[#2D8D68]',
}: {
  icon: React.ReactNode
  bg: string
  value: string
  label: string
  valueClass?: string
}) {
  return (
    <div className="bg-white rounded-xl border p-4">
      <div className="flex items-center gap-2 mb-1">
        <div className={`w-8 h-8 ${bg} rounded-lg flex items-center justify-center`}>{icon}</div>
      </div>
      <div className={`text-2xl font-bold ${valueClass}`}>{value}</div>
      <div className="text-[11px] text-gray-500">{label}</div>
    </div>
  )
}
