import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { RefreshCw, Eye, GitCompare, Plus } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { BudgetVersion } from '../types'

const DEMO_VERSIONS: (BudgetVersion & { neto: number; label: string; author: string; date: string })[] = [
  { id: 'v3', budget_id: '1', version: 3, data: {}, created_at: '2026-04-03T14:30:00', neto: 372_700_000, label: 'Precios actualizados Mar-2026', author: 'Carlos', date: '03/04/2026 14:30' },
  { id: 'v2', budget_id: '1', version: 2, data: {}, created_at: '2026-03-28T00:00:00', neto: 358_100_000, label: 'Ajuste cantidades P2-P8', author: 'Carlos', date: '28/03/2026' },
  { id: 'v1', budget_id: '1', version: 1, data: {}, created_at: '2026-03-20T00:00:00', neto: 341_500_000, label: 'Importación inicial Excel', author: 'Carlos', date: '20/03/2026' },
]

export default function Versions() {
  const { id } = useParams<{ id: string }>()
  const [versions, setVersions] = useState(DEMO_VERSIONS)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (!id) return
    budgetApi.getVersions(id)
      .then((data) => {
        if (data.length > 0) {
          // map to display format (neto comes from data blob)
          const mapped = data.map((v) => ({
            ...v,
            neto: (v.data as Record<string, number>)?.neto_total ?? 0,
            label: `v${v.version}`,
            author: 'Carlos',
            date: new Date(v.created_at).toLocaleDateString('es-AR'),
          }))
          setVersions(mapped as typeof DEMO_VERSIONS)
        }
      })
      .catch(() => {/* use demo */})
      .finally(() => setLoading(false))
  }, [id])

  async function createVersion() {
    if (!id) return
    setCreating(true)
    try {
      await budgetApi.createVersion(id)
      const data = await budgetApi.getVersions(id)
      setVersions(data.map((v) => ({
        ...v,
        neto: (v.data as Record<string, number>)?.neto_total ?? 0,
        label: `v${v.version}`,
        author: 'Carlos',
        date: new Date(v.created_at).toLocaleDateString('es-AR'),
      })) as typeof DEMO_VERSIONS)
    } catch {
      // ignore
    }
    setCreating(false)
  }

  const current = versions[0]

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <RefreshCw size={14} /> HISTORIAL
      </div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
          <h1 className="text-xl font-extrabold text-gray-900">VERSIONES — LAS HERAS</h1>
        </div>
        <button
          onClick={createVersion}
          disabled={creating}
          className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-60 text-white font-semibold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 transition-colors"
        >
          {creating ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Plus size={14} />
          )}
          Guardar versión actual
        </button>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando versiones...
        </div>
      )}

      {versions.length === 0 ? (
        <div className="max-w-2xl bg-white rounded-xl border p-8 text-center text-gray-400">
          <RefreshCw size={32} className="mx-auto mb-3 text-gray-300" />
          <p className="text-sm">No hay versiones guardadas todavía.</p>
          <p className="text-xs mt-1">Guardá una versión para crear un punto de restauración.</p>
        </div>
      ) : (
        <div className="max-w-2xl space-y-3">
          {versions.map((v, i) => {
            const isCurrent = i === 0
            const deltaNeto = current && !isCurrent ? v.neto - current.neto : 0
            const deltaPct = current && !isCurrent && current.neto !== 0
              ? ((v.neto - current.neto) / current.neto) * 100
              : 0

            return (
              <div
                key={v.id}
                className={`bg-white rounded-xl border overflow-hidden ${isCurrent ? 'border-l-4 border-l-[#2D8D68]' : ''}`}
              >
                <div className="p-4 flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-sm text-gray-900">
                      v{v.version} — {v.label}
                    </div>
                    <div className="text-[10px] text-gray-400 mt-0.5">
                      {v.author} · {v.date} · Neto: {fmtCurrency(v.neto)}
                    </div>
                    {!isCurrent && deltaNeto !== 0 && (
                      <div className={`text-[10px] mt-0.5 ${deltaNeto < 0 ? 'text-red-500' : 'text-green-600'}`}>
                        {deltaNeto < 0 ? '' : '+'}
                        {fmtCurrency(deltaNeto)} ({deltaPct >= 0 ? '+' : ''}{deltaPct.toFixed(1)}%) vs v{current.version}
                      </div>
                    )}
                  </div>
                  {isCurrent ? (
                    <span className="text-[10px] text-[#2D8D68] font-semibold bg-[#E8F5EE] px-2 py-0.5 rounded-full">
                      Actual
                    </span>
                  ) : (
                    <div className="flex gap-2">
                      <button className="text-xs text-[#2D8D68] border border-[#2D8D68] px-2.5 py-1 rounded-lg font-medium hover:bg-[#E8F5EE] transition-colors flex items-center gap-1">
                        <Eye size={12} /> Ver
                      </button>
                      <button className="text-xs text-blue-600 border px-2.5 py-1 rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-1">
                        <GitCompare size={12} /> Comparar
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="mt-4 max-w-2xl bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-800">
        <p className="font-semibold mb-1">Acerca de las versiones</p>
        <p>Cada versión guarda una copia completa del presupuesto. Podés comparar netos entre versiones y restaurar cualquier punto anterior.</p>
      </div>
    </div>
  )
}
