import { useEffect, useState } from 'react'
import { BookOpen, ChevronDown, ChevronRight, Plus } from 'lucide-react'
import { catalogApi } from '../lib/api'
import { fmtCurrency } from '../lib/format'
import type { PriceCatalog, CatalogEntry } from '../types'
import { useNavigate } from 'react-router-dom'

function CatalogRow({ catalog }: { catalog: PriceCatalog }) {
  const [open, setOpen] = useState(false)
  const [entries, setEntries] = useState<CatalogEntry[]>([])
  const [loading, setLoading] = useState(false)

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
        </div>
      )}
    </div>
  )
}

export default function Catalogs() {
  const navigate = useNavigate()
  const [catalogs, setCatalogs] = useState<PriceCatalog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    catalogApi.list()
      .then(setCatalogs)
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
          <CatalogRow key={c.id} catalog={c} />
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
