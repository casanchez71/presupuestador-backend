import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Edit3, ChevronRight, Plus, CheckCircle, AlertCircle, X } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency, fmtNumber } from '../lib/format'
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

const FIELD_LABELS: Record<string, string> = {
  cantidad: 'Cantidad',
  mat_unitario: 'MAT Unit',
  mo_unitario: 'MO Unit',
}

interface Toast {
  id: number
  message: string
  type: 'success' | 'error'
}

let toastIdCounter = 0

export default function Editor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [budget, setBudget] = useState<Budget | null>(null)
  const [tree, setTree] = useState<TreeNode[]>([])
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null)
  const [allItems, setAllItems] = useState<BudgetItem[]>([])
  const [items, setItems] = useState<BudgetItem[]>([])
  const [loading, setLoading] = useState(true)
  const [toasts, setToasts] = useState<Toast[]>([])

  /** Return items that belong to a given tree node.
   *  If the node has children (nested tree), use parent_id matching.
   *  If the tree is flat, use code-prefix matching to group section items.
   */
  const getItemsForNode = useCallback((node: TreeNode, all: BudgetItem[]): BudgetItem[] => {
    // First try parent_id matching (works when tree is properly nested)
    const byParent = all.filter((i) => i.parent_id === node.id)
    if (byParent.length > 0) return byParent

    // For flat trees: if the node looks like a section header (code has no dot),
    // find items whose code starts with the section number prefix
    const code = node.code ?? ''
    // Extract leading number from codes like "1- TAREAS PRELIMINARES" or "3-ESTRUCTURA"
    const sectionMatch = code.match(/^(\d+)\s*[-.]/)
    if (sectionMatch) {
      const prefix = sectionMatch[1] + '.'
      return all.filter((i) => i.code?.startsWith(prefix) && i.id !== node.id)
    }

    // Fallback: just return the node itself
    return all.filter((i) => i.id === node.id)
  }, [])

  const addToast = useCallback((message: string, type: 'success' | 'error' = 'success') => {
    const tid = ++toastIdCounter
    setToasts((prev) => [...prev, { id: tid, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== tid))
    }, 4000)
  }, [])

  const removeToast = useCallback((tid: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== tid))
  }, [])

  useEffect(() => {
    if (!id) return
    Promise.all([
      budgetApi.getFull(id),
      budgetApi.getItems(id),
    ])
      .then(([{ budget: b, tree: t }, fetchedItems]) => {
        setBudget(b)
        setTree(t)
        setAllItems(fetchedItems)
        // Auto-select first section node and show its items
        const firstNode = t[0] ?? null
        if (firstNode) {
          setSelectedNode(firstNode)
          setItems(getItemsForNode(firstNode, fetchedItems))
        }
      })
      .catch(() => {/* keep empty state */})
      .finally(() => setLoading(false))
  }, [id])

  // Handle inline cell edit
  const handleEditItem = useCallback(async (itemId: string, field: string, oldValue: number, newValue: number) => {
    if (!id) throw new Error('No budget ID')

    const fieldLabel = FIELD_LABELS[field] ?? field
    const formatVal = field === 'cantidad' ? (v: number) => fmtNumber(v, 2) : fmtCurrency

    // Call the API
    const result = await budgetApi.updateItem(id, itemId, { [field]: newValue })

    // The API returns { message, item } — extract the updated item
    const updatedItem = (result as unknown as { item: BudgetItem }).item
    if (!updatedItem) throw new Error('No updated item in response')

    // Update allItems and current items with recalculated values
    setAllItems((prev) =>
      prev.map((item) => (item.id === itemId ? { ...item, ...updatedItem } : item)),
    )
    setItems((prev) =>
      prev.map((item) => (item.id === itemId ? { ...item, ...updatedItem } : item)),
    )

    addToast(`${fieldLabel} actualizado: ${formatVal(oldValue)} → ${formatVal(newValue)}`)
  }, [id, addToast])

  const selectedLabel = selectedNode
    ? `${selectedNode.code ? selectedNode.code + ' ' : ''}${selectedNode.description ?? ''}`
    : '—'

  const mat = items.reduce((s, i) => s + i.mat_total, 0)
  const mo = items.reduce((s, i) => s + i.mo_total, 0)
  const directo = items.reduce((s, i) => s + i.directo_total, 0)
  const indirecto = items.reduce((s, i) => s + i.indirecto_total, 0)
  const neto = items.reduce((s, i) => s + i.neto_total, 0)

  return (
    <div className="p-4 fade-in">
      {/* Toast notifications */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg shadow-lg text-xs font-medium animate-slide-in ${
              toast.type === 'success'
                ? 'bg-[#E8F5EE] text-[#1B5E4B] border border-[#2D8D68]/30'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle size={14} className="text-[#2D8D68] flex-shrink-0" />
            ) : (
              <AlertCircle size={14} className="text-red-500 flex-shrink-0" />
            )}
            <span>{toast.message}</span>
            <button onClick={() => removeToast(toast.id)} className="ml-1 opacity-50 hover:opacity-100">
              <X size={12} />
            </button>
          </div>
        ))}
      </div>

      {/* Slide-in animation for toasts */}
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-in { animation: slideIn 0.3s ease-out; }
      `}</style>

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
            {budget?.name?.toUpperCase() ?? 'PRESUPUESTO'}
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
            Guardar version
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
              <Plus size={12} /> Seccion
            </button>
          </div>
          <div className="p-1.5 max-h-[520px] overflow-y-auto">
            <TreeView
              nodes={tree}
              selectedId={selectedNode?.id}
              onSelect={(node) => {
                setSelectedNode(node)
                setItems(getItemsForNode(node, allItems))
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
                {items.length} items · {fmtCurrency(directo)} costo directo
              </p>
            </div>
            {items.length === 1 ? (
              <button
                onClick={() => navigate(`/app/budgets/${id ?? '1'}/item/${items[0].id}`)}
                className="text-xs bg-[#2D8D68] hover:bg-[#1B5E4B] text-white px-2.5 py-1 rounded font-medium transition-colors"
              >
                Ver detalle
              </button>
            ) : selectedNode && (!selectedNode.children || selectedNode.children.length === 0) ? (
              <button
                onClick={() => navigate(`/app/budgets/${id ?? '1'}/item/${selectedNode.id}`)}
                className="text-xs bg-[#2D8D68] hover:bg-[#1B5E4B] text-white px-2.5 py-1 rounded font-medium transition-colors"
              >
                Ver detalle
              </button>
            ) : null}
          </div>

          <CostSummaryBar mat={mat} mo={mo} directo={directo} indirecto={indirecto} neto={neto} indirectoPct={31} />
          <MarkupChainDisplay directo={directo} neto={neto} links={MARKUP_LINKS} />

          {items.length === 0 ? (
            <div className="p-8 text-center text-gray-400 text-sm">
              Selecciona una seccion para ver sus items.
            </div>
          ) : (
            <DataTable items={items} onEditItem={handleEditItem} />
          )}

          <div className="p-2 bg-[#E8F5EE] text-[10px] text-[#1B5E4B] border-t">
            Click en celdas punteadas para editar. Totales se recalculan automaticamente por la cadena de markups.
          </div>
        </div>
      </div>
    </div>
  )
}
