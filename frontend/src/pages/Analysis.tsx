import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { BarChart2, Download } from 'lucide-react'
import { budgetApi } from '../lib/api'
import { fmtCurrency, fmtNumber } from '../lib/format'
import type { AnalysisResponse } from '../types'

const DEMO: AnalysisResponse = {
  mat_total: 142_200_000,
  mo_total: 85_300_000,
  directo_total: 284_500_000,
  indirecto_total: 88_200_000,
  beneficio_total: 24_600_000,
  neto_total: 372_700_000,
  items_count: 108,
}

const SECTIONS = [
  { name: '0. Tareas Preliminares', mat: 3_200_000, mo: 2_100_000, eq: 1_800_000, sub: 0, directo: 7_100_000, indirecto: 2_200_000, benef: 700_000, neto: 10_000_000 },
  { name: '1. Subsuelo', mat: 18_500_000, mo: 9_200_000, eq: 3_100_000, sub: 500_000, directo: 31_300_000, indirecto: 9_700_000, benef: 3_100_000, neto: 44_100_000 },
  { name: '2. Planta Baja', mat: 22_300_000, mo: 11_800_000, eq: 4_200_000, sub: 1_200_000, directo: 39_500_000, indirecto: 12_200_000, benef: 4_000_000, neto: 55_700_000 },
  { name: '3. Pisos 1-8 (×8)', mat: 85_400_000, mo: 52_800_000, eq: 16_200_000, sub: 6_800_000, directo: 161_200_000, indirecto: 50_000_000, benef: 16_100_000, neto: 227_300_000 },
  { name: '4. Azotea', mat: 12_800_000, mo: 9_400_000, eq: 3_200_000, sub: 0, directo: 25_400_000, indirecto: 7_900_000, benef: 2_500_000, neto: 35_800_000 },
]

export default function Analysis() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<AnalysisResponse>(DEMO)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    budgetApi.getAnalysis(id)
      .then(setData)
      .catch(() => {/* use demo */})
      .finally(() => setLoading(false))
  }, [id])

  const superficie = 2663.25
  const duracion = 16
  const costPerM2 = data.neto_total / superficie

  return (
    <div className="p-6 fade-in">
      {/* Section label */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <BarChart2 size={14} /> VISTA DE ANÁLISIS
      </div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
          <h1 className="text-xl font-extrabold text-gray-900">ANÁLISIS — LAS HERAS</h1>
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

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="bg-white rounded-xl border p-4">
          <div className="text-[10px] text-gray-400 mb-1">SUPERFICIE TOTAL</div>
          <div className="text-2xl font-bold text-gray-900">
            {fmtNumber(superficie, 2)} <span className="text-sm font-normal text-gray-400">m²</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Subsuelo 410 + PB 144 + P1-8 1.848 + Azotea 43 + Circ. 218,25</div>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <div className="text-[10px] text-gray-400 mb-1">DURACIÓN</div>
          <div className="text-2xl font-bold text-gray-900">
            {duracion} <span className="text-sm font-normal text-gray-400">meses</span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">Edificio 8 pisos + subsuelo</div>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <div className="text-[10px] text-gray-400 mb-1">ÍTEMS TOTALES</div>
          <div className="text-2xl font-bold text-gray-900">{data.items_count}</div>
          <div className="text-[10px] text-gray-500 mt-1">En {SECTIONS.length} secciones principales</div>
        </div>
        <div className="bg-[#2D8D68] rounded-xl p-4 text-white">
          <div className="text-[10px] text-[#E0A33A] mb-1">NETO TOTAL</div>
          <div className="text-2xl font-bold">{fmtCurrency(data.neto_total)}</div>
          <div className="text-[10px] text-green-200 mt-1">{fmtCurrency(costPerM2)} / m²</div>
        </div>
      </div>

      {/* 6 KPI cards */}
      <div className="grid grid-cols-6 gap-2 mb-4">
        <div className="bg-white rounded-lg border p-3 text-center">
          <div className="text-[10px] text-gray-400">Materiales</div>
          <div className="text-lg font-bold text-gray-800">{fmtCurrency(data.mat_total)}</div>
        </div>
        <div className="bg-white rounded-lg border p-3 text-center">
          <div className="text-[10px] text-gray-400">Mano de Obra</div>
          <div className="text-lg font-bold text-gray-800">{fmtCurrency(data.mo_total)}</div>
        </div>
        <div className="bg-white rounded-lg border p-3 text-center">
          <div className="text-[10px] text-gray-400">Equipos</div>
          <div className="text-lg font-bold text-gray-800">{fmtCurrency(28_500_000)}</div>
        </div>
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-3 text-center">
          <div className="text-[10px] text-blue-500">Directo</div>
          <div className="text-lg font-bold text-blue-700">{fmtCurrency(data.directo_total)}</div>
        </div>
        <div className="bg-orange-50 rounded-lg border border-orange-200 p-3 text-center">
          <div className="text-[10px] text-orange-500">Indirectos</div>
          <div className="text-lg font-bold text-orange-600">{fmtCurrency(data.indirecto_total)}</div>
          <div className="text-[9px] text-orange-400">Cadena: 31%</div>
        </div>
        <div className="bg-[#2D8D68] rounded-lg p-3 text-center text-white">
          <div className="text-[10px] text-[#E0A33A]">NETO</div>
          <div className="text-lg font-bold">{fmtCurrency(data.neto_total)}</div>
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
              <th className="px-3 py-2 text-right font-semibold">Equipo</th>
              <th className="px-3 py-2 text-right font-semibold">Sub</th>
              <th className="px-3 py-2 text-right font-semibold">Directo</th>
              <th className="px-3 py-2 text-right font-semibold">Indirecto</th>
              <th className="px-3 py-2 text-right font-semibold">Beneficio</th>
              <th className="px-3 py-2 text-right font-bold">Neto</th>
            </tr>
          </thead>
          <tbody>
            {SECTIONS.map((s, i) => (
              <tr key={i} className="border-b hover:bg-gray-50">
                <td className="px-3 py-2 font-medium text-gray-800">{s.name}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.mat)}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.mo)}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.eq)}</td>
                <td className="px-3 py-2 cost-cell">{fmtCurrency(s.sub)}</td>
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
              <td className="px-3 py-3 cost-cell">{fmtCurrency(data.mat_total)}</td>
              <td className="px-3 py-3 cost-cell">{fmtCurrency(data.mo_total)}</td>
              <td className="px-3 py-3 cost-cell">{fmtCurrency(28_500_000)}</td>
              <td className="px-3 py-3 cost-cell">{fmtCurrency(8_500_000)}</td>
              <td className="px-3 py-3 cost-cell text-green-200">{fmtCurrency(data.directo_total)}</td>
              <td className="px-3 py-3 cost-cell">{fmtCurrency(data.indirecto_total)}</td>
              <td className="px-3 py-3 cost-cell">{fmtCurrency(data.beneficio_total)}</td>
              <td className="px-3 py-3 cost-cell text-[#E0A33A] text-base font-bold">{fmtCurrency(data.neto_total)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  )
}
