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

// Demo tree for fallback
const DEMO_TREE: TreeNode[] = [
  {
    id: 'root', budget_id: '1', org_id: 'demo', description: 'Edificio Las Heras',
    code: '', mat_unitario: 0, mo_unitario: 0, mat_total: 142_200_000, mo_total: 85_300_000,
    directo_total: 284_500_000, indirecto_total: 88_200_000, beneficio_total: 0, neto_total: 372_700_000, sort_order: 0,
    children: [
      {
        id: 's0', budget_id: '1', org_id: 'demo', parent_id: 'root',
        code: '0', description: '0. Tareas Preliminares',
        mat_unitario: 0, mo_unitario: 0, mat_total: 3_200_000, mo_total: 2_100_000,
        directo_total: 7_100_000, indirecto_total: 2_200_000, beneficio_total: 700_000, neto_total: 10_000_000, sort_order: 0,
        children: [
          { id: 'i01', budget_id: '1', org_id: 'demo', parent_id: 's0', code: '0.1', description: 'Obrador', unidad: 'mes', cantidad: 16, mat_unitario: 700_000, mo_unitario: 0, mat_total: 11_200_000, mo_total: 0, directo_total: 11_200_000, indirecto_total: 3_472_000, beneficio_total: 0, neto_total: 14_672_000, sort_order: 1, children: [] },
          { id: 'i02', budget_id: '1', org_id: 'demo', parent_id: 's0', code: '0.2', description: 'Baños Químicos', unidad: 'mes', cantidad: 16, mat_unitario: 150_000, mo_unitario: 0, mat_total: 2_400_000, mo_total: 0, directo_total: 2_400_000, indirecto_total: 744_000, beneficio_total: 0, neto_total: 3_144_000, sort_order: 2, children: [] },
        ],
      },
      {
        id: 's1', budget_id: '1', org_id: 'demo', parent_id: 'root',
        code: '1', description: '1. Subsuelo',
        mat_unitario: 0, mo_unitario: 0, mat_total: 18_500_000, mo_total: 9_200_000,
        directo_total: 31_300_000, indirecto_total: 9_700_000, beneficio_total: 3_100_000, neto_total: 44_100_000, sort_order: 1,
        children: [
          { id: 'i11', budget_id: '1', org_id: 'demo', parent_id: 's1', code: '1.1', description: 'Columnas y Tabiques', unidad: 'm³', cantidad: 85, mat_unitario: 99_588, mo_unitario: 37_647, mat_total: 8_465_000, mo_total: 3_200_000, directo_total: 11_650_500, indirecto_total: 3_611_655, beneficio_total: 0, neto_total: 15_262_155, sort_order: 1, children: [] },
          { id: 'i12', budget_id: '1', org_id: 'demo', parent_id: 's1', code: '1.2', description: 'Vigas', unidad: 'm³', cantidad: 42, mat_unitario: 95_000, mo_unitario: 32_000, mat_total: 3_990_000, mo_total: 1_344_000, directo_total: 5_334_000, indirecto_total: 1_653_540, beneficio_total: 0, neto_total: 6_987_540, sort_order: 2, children: [] },
          { id: 'i13', budget_id: '1', org_id: 'demo', parent_id: 's1', code: '1.3', description: 'Losa', unidad: 'm²', cantidad: 410, mat_unitario: 18_000, mo_unitario: 6_500, mat_total: 7_380_000, mo_total: 2_665_000, directo_total: 10_045_000, indirecto_total: 3_113_950, beneficio_total: 0, neto_total: 13_158_950, sort_order: 3, children: [] },
        ],
      },
    ],
  },
]

const DEFAULT_ITEMS: BudgetItem[] = [
  { id: 'i11', budget_id: '1', org_id: 'demo', parent_id: 's1', code: '1.1.1', description: 'Hormigón H-30 elaborado', unidad: 'm³', cantidad: 42.5, mat_unitario: 85_000, mo_unitario: 32_000, mat_total: 3_612_500, mo_total: 1_360_000, directo_total: 4_972_500, indirecto_total: 1_541_475, beneficio_total: 0, neto_total: 6_513_975, sort_order: 1 },
  { id: 'i12', budget_id: '1', org_id: 'demo', parent_id: 's1', code: '1.1.2', description: 'Acero ADN 420 ø12', unidad: 'kg', cantidad: 3200, mat_unitario: 1_250, mo_unitario: 380, mat_total: 4_000_000, mo_total: 1_216_000, directo_total: 5_216_000, indirecto_total: 1_616_960, beneficio_total: 0, neto_total: 6_832_960, sort_order: 2 },
  { id: 'i13', budget_id: '1', org_id: 'demo', parent_id: 's1', code: '1.1.3', description: 'Encofrado metálico', unidad: 'm²', cantidad: 85, mat_unitario: 12_000, mo_unitario: 5_200, mat_total: 1_020_000, mo_total: 442_000, directo_total: 1_462_000, indirecto_total: 453_220, beneficio_total: 0, neto_total: 1_915_220, sort_order: 3 },
]

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
  const [tree, setTree] = useState<TreeNode[]>(DEMO_TREE)
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(DEMO_TREE[0]?.children?.[1] ?? null)
  const [items, setItems] = useState<BudgetItem[]>(DEFAULT_ITEMS)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    budgetApi.getFull(id)
      .then(({ budget, tree }) => {
        setBudget(budget)
        setTree(tree)
        if (tree[0]) setSelectedNode(tree[0])
      })
      .catch(() => {/* use demo data */})
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
                // Load items for this node
                if (id && node.id !== 'root') {
                  budgetApi.getItems(id)
                    .then((all) => setItems(all.filter((i) => i.parent_id === node.id || i.id === node.id)))
                    .catch(() => setItems(DEFAULT_ITEMS))
                }
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
