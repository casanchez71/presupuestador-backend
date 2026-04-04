import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronRight, ClipboardList } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency, fmtNumber, fmtPercent } from '../lib/format'
import type { ItemResource, BudgetItem, Budget } from '../types'


type Tipo = ItemResource['tipo']

const TIPO_LABELS: Record<Tipo, string> = {
  material: 'Materiales',
  mano_obra: 'Mano de Obra',
  equipo: 'Equipos',
  subcontrato: 'Subcontratos',
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
        <div className="p-4 text-xs text-gray-400 italic">Sin {TIPO_LABELS[tipo].toLowerCase()} para este ítem</div>
      ) : (
        <table className="w-full text-xs">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Código</th>
              <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Descripción</th>
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

export default function ItemDetail() {
  const { id, itemId } = useParams<{ id: string; itemId: string }>()
  const navigate = useNavigate()
  const [budget, setBudget] = useState<Budget | null>(null)
  const [item, setItem] = useState<BudgetItem | null>(null)
  const [recursos, setRecursos] = useState<ItemResource[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id || !itemId) return
    // Load budget, item info, and resources in parallel
    Promise.all([
      budgetApi.get(id).catch(() => null),
      budgetApi.getItems(id).then((items) => items.find((i) => i.id === itemId) ?? null).catch(() => null),
      budgetApi.getItemResources(id, itemId).catch(() => [] as ItemResource[]),
    ]).then(([b, it, res]) => {
      if (b) setBudget(b)
      if (it) setItem(it)
      setRecursos(res)
    }).finally(() => setLoading(false))
  }, [id, itemId])

  const totalMat = recursos.filter((r) => r.tipo === 'material').reduce((s, r) => s + r.subtotal, 0)
  const totalMO = recursos.filter((r) => r.tipo === 'mano_obra').reduce((s, r) => s + r.subtotal, 0)
  const cantidad = item?.cantidad ?? 0
  const desperdicio = 10

  return (
    <div className="p-6 fade-in">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs mb-2">
        <span className="text-gray-400 cursor-pointer hover:text-[#2D8D68]" onClick={() => navigate('/app/dashboard')}>Presupuestos</span>
        <ChevronRight size={12} className="text-gray-300" />
        <span className="text-gray-400 cursor-pointer hover:text-[#2D8D68]" onClick={() => navigate(`/app/budgets/${id ?? '1'}/editor`)}>{budget?.name ?? 'Presupuesto'}</span>
        <ChevronRight size={12} className="text-gray-300" />
        <span className="font-semibold text-gray-900">{item ? `${item.code ?? ''} ${item.description ?? ''}`.trim() : 'Ítem'}</span>
      </div>

      {/* Section label */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <ClipboardList size={14} /> DETALLE DE RECURSOS
      </div>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">{item ? `${item.code ?? ''} ${item.description ?? ''}`.trim().toUpperCase() : 'DETALLE DE ÍTEM'}</h1>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-3">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando recursos...
        </div>
      )}

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
          <div className="text-[10px] text-gray-400">Fórmula</div>
          <div className="font-mono text-xs text-gray-600">
            {fmtNumber(cantidad, 2)} × (1 + 0.{desperdicio}) ={' '}
            <strong>{fmtNumber(cantidad * (1 + desperdicio / 100), 0)} {item?.unidad ?? ''}</strong>
          </div>
        </div>
      </div>

      {/* Cost quick summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gray-50 rounded-lg p-3 border text-center">
          <div className="text-[10px] text-gray-400">Total MAT</div>
          <div className="font-bold text-gray-800">{fmtCurrency(totalMat)}</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border text-center">
          <div className="text-[10px] text-gray-400">Total MO</div>
          <div className="font-bold text-gray-800">{fmtCurrency(totalMO)}</div>
        </div>
        <div className="bg-[#E8F5EE] rounded-lg p-3 border border-[#2D8D68] text-center">
          <div className="text-[10px] text-[#1B5E4B]">Costo Directo</div>
          <div className="font-bold text-[#2D8D68]">{fmtCurrency(totalMat + totalMO)}</div>
        </div>
      </div>

      {/* Resource tables 2x2 */}
      <div className="grid grid-cols-2 gap-4">
        <ResourceTable recursos={recursos} tipo="material" />
        <ResourceTable recursos={recursos} tipo="mano_obra" />
        <ResourceTable recursos={recursos} tipo="equipo" />
        <ResourceTable recursos={recursos} tipo="subcontrato" />
      </div>
    </div>
  )
}
