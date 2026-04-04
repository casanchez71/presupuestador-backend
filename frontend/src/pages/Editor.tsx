import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Edit3, ChevronRight, Plus } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { Budget, TreeNode, BudgetItem } from '../types'
import TreeView from '../components/ui/TreeView'
import DataTable from '../components/ui/DataTable'
import CostSummaryBar from '../components/ui/CostSummaryBar'
import MarkupChainDisplay from '../components/ui/MarkupChainDisplay'


const MARKUP_LINKS = [
  { label: 'Estr', pct: 15 },
  { label: 'Jef', pct: 8 },
  { label: 'Log', pct: 5 },
  { label: 'Herr', pct: 3 },
  { label: 'Benef', pct: 10 },
]

export default function Editor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [budget, setBudget] = useState<Budget | null>(null)
  const [tree, setTree] = useState<TreeNode[]>([])
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null)
  const [allItems, setAllItems] = useState<BudgetItem[]>([])
  const [items, setItems] = useState<BudgetItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    Promise.all([
      budgetApi.getFull(id),
      budgetApi.getItems(id),
    ])
      .then(([{ budget, tree }, fetchedItems]) => {
        setBudget(budget)
        setTree(tree)
        setAllItems(fetchedItems)
        // Auto-select first child node and filter its items
        const firstNode = tree[0]?.children?.[0] ?? tree[0] ?? null
        if (firstNode) {
          setSelectedNode(firstNode)
          setItems(fetchedItems.filter((i) => i.parent_id === firstNode.id || i.id === firstNode.id))
        }
      })
      .catch(() => {/* keep empty state */})
      .finally(() => setLoading(false))
  }, [id])

  const selectedLabel = selectedNode
    ? `${selectedNode.code ? selectedNode.code + ' ' : ''}${selectedNode.description}`
    : '—'

  const mat = items.reduce((s, i) => s + i.mat_total, 0)
  const mo = items.reduce((s, i) => s + i.mo_total, 0)
  const directo = items.reduce((s, i) => s + i.directo_total, 0)
  const indirecto = items.reduce((s, i) => s + i.indirecto_total, 0)
  const neto = items.reduce((s, i) => s + i.neto_total, 0)

  return (
    <div className="p-4 fade-in">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-xs mb-1">
        <span
          className="text-gray-400 cursor-pointer hover:text-[#2D8D68]"
          onClick={() => navigate('/app/dashboard')}
        >
          Presupuestos
        </span>
        <ChevronRight size={12} className="text-gray-300" />
        <span className="font-semibold text-gray-900">
          {budget?.name ?? 'Edificio Las Heras — Obra Gris'}
        </span>
        <span className="bg-[#E8F5EE] text-[#1B5E4B] text-[10px] font-medium px-1.5 py-0.5 rounded">v3</span>
      </div>

      {/* Section label */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Edit3 size={14} /> EDITOR DE OBRA
      </div>

      {/* Title bar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
          <h1 className="text-xl font-extrabold text-gray-900">
            {budget?.name?.toUpperCase() ?? 'EDIFICIO LAS HERAS'}
          </h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate(`/app/budgets/${id ?? '1'}/ai`)}
            className="bg-white border text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-50 transition-colors"
          >
            IA + Plano
          </button>
          <button
            onClick={() => navigate(`/app/budgets/${id ?? '1'}/export`)}
            className="bg-white border text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-gray-50 transition-colors"
          >
            Exportar
          </button>
          <button
            onClick={() => id && budgetApi.createVersion(id)}
            className="bg-[#2D8D68] hover:bg-[#1B5E4B] text-white font-semibold px-4 py-1.5 rounded-lg text-xs transition-colors"
          >
            Guardar versión
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-3">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando...
        </div>
      )}

      <div className="flex gap-3">
        {/* Tree */}
        <div className="w-60 bg-white rounded-xl border flex-shrink-0 overflow-hidden">
          <div className="bg-[#2D8D68] text-white px-3 py-2 flex justify-between items-center">
            <span className="font-semibold text-xs">Estructura de Obra</span>
            <button className="text-[#E0A33A] text-xs font-medium flex items-center gap-0.5">
              <Plus size={12} /> Sección
            </button>
          </div>
          <div className="p-1.5 max-h-[520px] overflow-y-auto">
            <TreeView
              nodes={tree}
              selectedId={selectedNode?.id}
              onSelect={(node) => {
                setSelectedNode(node)
                // Filter items for this node from cached list
                setItems(allItems.filter((i) => i.parent_id === node.id || i.id === node.id))
              }}
            />
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 bg-white rounded-xl border overflow-hidden">
          <div className="bg-gray-50 border-b px-4 py-2.5 flex justify-between items-center">
            <div>
              <h2 className="font-bold text-gray-900 text-sm">{selectedLabel}</h2>
              <p className="text-[10px] text-gray-400 mt-0.5">
                {items.length} ítems · {fmtCurrency(directo)} costo directo
              </p>
            </div>
            <button
              onClick={() => navigate(`/app/budgets/${id ?? '1'}/item/${selectedNode?.id ?? '1'}`)}
              className="text-xs bg-[#2D8D68] hover:bg-[#1B5E4B] text-white px-2.5 py-1 rounded font-medium transition-colors"
            >
              Ver detalle
            </button>
          </div>

          <CostSummaryBar mat={mat} mo={mo} directo={directo} indirecto={indirecto} neto={neto} indirectoPct={31} />
          <MarkupChainDisplay directo={directo} neto={neto} links={MARKUP_LINKS} />

          {items.length === 0 ? (
            <div className="p-8 text-center text-gray-400 text-sm">
              Seleccioná una sección para ver sus ítems.
            </div>
          ) : (
            <DataTable items={items} />
          )}

          <div className="p-2 bg-[#E8F5EE] text-[10px] text-[#1B5E4B] border-t">
            Click en celdas punteadas para editar. Totales se recalculan automáticamente por la cadena de markups.
          </div>
        </div>
      </div>
    </div>
  )
}
