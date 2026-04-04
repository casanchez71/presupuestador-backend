import { useEffect, useState } from 'react'
import { BookOpen, ChevronDown, ChevronRight, Plus } from 'lucide-react'
import { catalogApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { PriceCatalog, CatalogEntry } from '../types'
import { useNavigate } from 'react-router-dom'

const DEMO_CATALOGS: PriceCatalog[] = [
  { id: 'c1', org_id: 'demo', name: 'Materiales Corralón — Mar 2026', source_file: 'Las Heras.xlsx', created_at: '2026-03-01' },
  { id: 'c2', org_id: 'demo', name: 'Mano de Obra — Mar 2026', created_at: '2026-03-01' },
  { id: 'c3', org_id: 'demo', name: 'Equipos — Mar 2026', created_at: '2026-03-01' },
  { id: 'c4', org_id: 'demo', name: 'Subcontratos — Mar 2026', created_at: '2026-03-01' },
]

const DEMO_ENTRIES: Record<string, CatalogEntry[]> = {
  c1: [
    { id: 'e1', catalog_id: 'c1', tipo: 'material', codigo: 'ARG', descripcion: 'Arena a granel (1m³)', unidad: 'm³', precio_con_iva: 29_403, precio_sin_iva: 24_300 },
    { id: 'e2', catalog_id: 'c1', tipo: 'material', codigo: 'CEM', descripcion: 'Cemento "Loma Negra" (25kg)', unidad: 'u', precio_con_iva: 8_470, precio_sin_iva: 7_000 },
    { id: 'e3', catalog_id: 'c1', tipo: 'material', codigo: 'H30', descripcion: 'Hormigón H-30 elaborado', unidad: 'm³', precio_con_iva: 114_950, precio_sin_iva: 95_000 },
    { id: 'e4', catalog_id: 'c1', tipo: 'material', codigo: 'PIEG', descripcion: 'Piedra partida a granel', unidad: 'm³', precio_con_iva: 58_995, precio_sin_iva: 48_756 },
    { id: 'e5', catalog_id: 'c1', tipo: 'material', codigo: 'HADN12', descripcion: 'Hierro ADN 420 ø12mm', unidad: 'u', precio_con_iva: 15_488, precio_sin_iva: 12_800 },
  ],
}

const CATALOG_SUBTITLES: Record<string, string> = {
  c1: '325 ítems · Importado del Excel Las Heras · Hoja 00_Mat',
  c2: '4 categorías: Capataz =80000×1.5, Oficial =60000×1.5, Ayudante =40000×1.5',
  c3: '27 ítems: Retroexcavadora, Mini cargadora, Compactador, Grúa...',
  c4: '70 ítems: Pintura, Durlock, Plomería, Electricidad, Vidrios...',
}

function CatalogRow({ catalog }: { catalog: PriceCatalog }) {
  const [open, setOpen] = useState(catalog.id === 'c1')
  const [entries, setEntries] = useState<CatalogEntry[]>(DEMO_ENTRIES[catalog.id] ?? [])
  const [loading, setLoading] = useState(false)

  function toggle() {
    setOpen(!open)
    if (!open && entries.length === 0) {
      setLoading(true)
      catalogApi.getEntries(catalog.id)
        .then(setEntries)
        .catch(() => {/* use demo */})
        .finally(() => setLoading(false))
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
                📊 {catalog.source_file}
              </span>
            )}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">{CATALOG_SUBTITLES[catalog.id]}</div>
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
                    <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Código</th>
                    <th className="px-3 py-1.5 text-left text-gray-500 font-medium">Descripción</th>
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
                      <td className="px-3 py-1.5 text-right">{e.precio_con_iva ? fmtCurrency(e.precio_con_iva) : '—'}</td>
                      <td className="px-3 py-1.5 text-right font-medium">{e.precio_sin_iva ? fmtCurrency(e.precio_sin_iva) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="px-3 py-2 bg-gray-50 text-[10px] text-gray-400 border-t">
                Mostrando {Math.min(entries.length, 5)} de {entries.length} · Precios actualizados Mar 2026
              </div>
            </>
          ) : (
            <div className="p-4 text-xs text-gray-400 italic">Sin entradas para este catálogo</div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Catalogs() {
  const navigate = useNavigate()
  const [catalogs, setCatalogs] = useState<PriceCatalog[]>(DEMO_CATALOGS)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    catalogApi.list()
      .then((data) => { if (data.length > 0) setCatalogs(data) })
      .catch(() => {/* use demo */})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <BookOpen size={14} /> GESTIÓN DE PRECIOS
      </div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">CATÁLOGOS DE PRECIOS</h1>
        <span className="bg-[#E8F5EE] text-[#1B5E4B] text-xs font-medium px-2 py-0.5 rounded-full">
          {catalogs.length} catálogos
        </span>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando catálogos...
        </div>
      )}

      <div className="max-w-3xl space-y-3">
        {catalogs.map((c) => (
          <CatalogRow key={c.id} catalog={c} />
        ))}

        <button
          onClick={() => navigate('/app/import')}
          className="w-full bg-[#2D8D68] hover:bg-[#1B5E4B] text-white py-3 rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2"
        >
          <Plus size={16} /> Importar nuevo catálogo de precios
        </button>
      </div>
    </div>
  )
}
