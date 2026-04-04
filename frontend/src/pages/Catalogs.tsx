import { useEffect, useState } from 'react'
import { BookOpen, Check, ChevronDown, ChevronRight, Plus, Zap } from 'lucide-react'
import { budgetApi, catalogApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { Budget, PriceCatalog, CatalogEntry } from '../types'
import { useNavigate } from 'react-router-dom'

function CatalogRow({ catalog, budgets }: { catalog: PriceCatalog; budgets: Budget[] }) {
  const [open, setOpen] = useState(false)
  const [entries, setEntries] = useState<CatalogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [applying, setApplying] = useState(false)
  const [applyResult, setApplyResult] = useState<{ success: boolean; message: string } | null>(null)
  const [selectedBudgetId, setSelectedBudgetId] = useState<string>('')

  function toggle() {
    setOpen(!open)
    if (!open && entries.length === 0) {
      setLoading(true)
      catalogApi.getEntries(catalog.id)
        .then(setEntries)
        .catch(() => {/* no entries */})
        .finally(() => setLoading(false))
    }
  }

  async function handleApply() {
    if (!selectedBudgetId) return
    setApplying(true)
    setApplyResult(null)
    try {
      const result = await catalogApi.apply(selectedBudgetId, catalog.id)
      setApplyResult({
        success: true,
        message: `Catalogo aplicado: ${result.items_matched} recursos actualizados, ${result.items_unmatched} sin coincidencia`,
      })
      setTimeout(() => setApplyResult(null), 5000)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al aplicar catalogo'
      setApplyResult({ success: false, message: msg })
      setTimeout(() => setApplyResult(null), 5000)
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border overflow-hidden">
      <div
        className="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={toggle}
      >
        <div>
          <div className="font-semibold text-sm text-gray-900 flex items-center gap-2">
            {catalog.name}
            {catalog.source_file && (
              <span className="bg-orange-50 text-orange-700 text-[10px] px-1.5 py-0.5 rounded border border-orange-200 font-normal">
                {catalog.source_file}
              </span>
            )}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">
            Creado: {new Date(catalog.created_at).toLocaleDateString('es-AR')}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-[#E8F5EE] text-[#1B5E4B] text-[10px] font-semibold px-2 py-0.5 rounded-full">Activo</span>
          {open ? <ChevronDown size={16} className="text-gray-400" /> : <ChevronRight size={16} className="text-gray-400" />}
        </div>
      </div>

      {open && (
        <div className="border-t fade-in">
          {loading ? (
            <div className="p-4 text-xs text-gray-400 flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
              Cargando entradas...
            </div>
          ) : entries.length > 0 ? (
            <>
              <table className="w-full text-[11px]">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Codigo</th>
                    <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Descripcion</th>
                    <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Unidad</th>
                    <th className="px-3 py-1.5 text-right text-gray-500 font-medium">P. con IVA</th>
                    <th className="px-3 py-1.5 text-right text-gray-500 font-medium">P. sin IVA</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.slice(0, 5).map((e) => (
                    <tr key={e.id} className="border-b hover:bg-gray-50">
                      <td className="px-3 py-1.5 font-mono text-gray-400">{e.codigo}</td>
                      <td className="px-3 py-1.5 text-gray-800">{e.descripcion}</td>
                      <td className="px-3 py-1.5 text-gray-500">{e.unidad}</td>
                      <td className="px-3 py-1.5 text-right">{e.precio_con_iva ? fmtCurrency(e.precio_con_iva) : '--'}</td>
                      <td className="px-3 py-1.5 text-right font-medium">{e.precio_sin_iva ? fmtCurrency(e.precio_sin_iva) : '--'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="px-3 py-2 bg-gray-50 text-[10px] text-gray-400 border-t">
                Mostrando {Math.min(entries.length, 5)} de {entries.length}
              </div>
            </>
          ) : (
            <div className="p-4 text-xs text-gray-400 italic">Sin entradas para este catalogo</div>
          )}

          {/* Apply to budget section */}
          <div className="border-t p-4 bg-gray-50">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={14} className="text-[#2D8D68]" />
              <span className="text-xs font-semibold text-gray-700">Aplicar a presupuesto</span>
            </div>
            {budgets.length > 0 ? (
              <div className="flex items-center gap-2">
                <select
                  value={selectedBudgetId}
                  onChange={(e) => setSelectedBudgetId(e.target.value)}
                  className="flex-1 text-xs border rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[#2D8D68] focus:border-transparent"
                  onClick={(e) => e.stopPropagation()}
                >
                  <option value="">Seleccionar presupuesto...</option>
                  {budgets.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
                <button
                  onClick={(e) => { e.stopPropagation(); handleApply() }}
                  disabled={!selectedBudgetId || applying}
                  className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5"
                >
                  {applying ? (
                    <>
                      <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Aplicando...
                    </>
                  ) : (
                    <>
                      <Zap size={12} /> Aplicar
                    </>
                  )}
                </button>
              </div>
            ) : (
              <p className="text-xs text-gray-400">No hay presupuestos disponibles. Crea uno primero.</p>
            )}
            {applyResult && (
              <div className={`mt-2 text-xs px-3 py-2 rounded-lg flex items-center gap-1.5 ${
                applyResult.success
                  ? 'bg-[#E8F5EE] text-[#166534] border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}>
                {applyResult.success && <Check size={12} />}
                {applyResult.message}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Catalogs() {
  const navigate = useNavigate()
  const [catalogs, setCatalogs] = useState<PriceCatalog[]>([])
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      catalogApi.list(),
      budgetApi.list(),
    ])
      .then(([cats, buds]) => {
        setCatalogs(cats)
        setBudgets(buds)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Error al cargar catalogos')
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <BookOpen size={14} /> GESTION DE PRECIOS
      </div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">CATALOGOS DE PRECIOS</h1>
        <span className="bg-[#E8F5EE] text-[#1B5E4B] text-xs font-medium px-2 py-0.5 rounded-full">
          {catalogs.length} catalogos
        </span>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando catalogos...
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 text-sm text-red-700">
          <p className="font-semibold mb-1">Error al cargar catalogos</p>
          <p className="text-xs">{error}</p>
        </div>
      )}

      <div className="max-w-3xl space-y-3">
        {!loading && catalogs.length === 0 && !error && (
          <div className="bg-white rounded-xl border p-8 text-center text-gray-400">
            <BookOpen size={32} className="mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No hay catalogos de precios todavia.</p>
            <p className="text-xs mt-1">Importa un Excel para crear tu primer catalogo.</p>
          </div>
        )}

        {catalogs.map((c) => (
          <CatalogRow key={c.id} catalog={c} budgets={budgets} />
        ))}

        <button
          onClick={() => navigate('/app/import')}
          className="w-full bg-[#2D8D68] hover:bg-[#1B5E4B] text-white py-3 rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2"
        >
          <Plus size={16} /> Importar nuevo catalogo de precios
        </button>
      </div>
    </div>
  )
}
