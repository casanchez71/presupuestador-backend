import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Settings, Plus, X } from 'lucide-react'
import { budgetApi } from '../lib/api'
import type { IndirectConfig } from '../types'

interface Link {
  key: keyof Omit<IndirectConfig, 'id' | 'org_id'>
  label: string
  pct: number
  color: string
}

const DEMO_CONFIG: IndirectConfig = {
  id: 'cfg1',
  org_id: 'demo',
  estructura_pct: 15,
  jefatura_pct: 8,
  logistica_pct: 5,
  herramientas_pct: 3,
}

const USA_EXAMPLE = [
  { label: 'Overhead', pct: 12 },
  { label: 'Contingency', pct: 8 },
  { label: 'Profit', pct: 15, green: true },
  { label: 'Bond', pct: 2 },
  { label: 'Tax', pct: 10, red: true },
]

export default function MarkupChain() {
  const { id } = useParams<{ id: string }>()
  const [config, setConfig] = useState<IndirectConfig>(DEMO_CONFIG)
  const [links, setLinks] = useState<Link[]>([
    { key: 'estructura_pct', label: 'Estructura', pct: DEMO_CONFIG.estructura_pct, color: 'orange' },
    { key: 'jefatura_pct', label: 'Jefatura', pct: DEMO_CONFIG.jefatura_pct, color: 'orange' },
    { key: 'logistica_pct', label: 'Logística', pct: DEMO_CONFIG.logistica_pct, color: 'orange' },
    { key: 'herramientas_pct', label: 'Herramientas', pct: DEMO_CONFIG.herramientas_pct, color: 'orange' },
  ])
  const [beneficio, setBeneficio] = useState(10)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    budgetApi.getIndirects(id)
      .then((cfg) => {
        setConfig(cfg)
        setLinks([
          { key: 'estructura_pct', label: 'Estructura', pct: cfg.estructura_pct, color: 'orange' },
          { key: 'jefatura_pct', label: 'Jefatura', pct: cfg.jefatura_pct, color: 'orange' },
          { key: 'logistica_pct', label: 'Logística', pct: cfg.logistica_pct, color: 'orange' },
          { key: 'herramientas_pct', label: 'Herramientas', pct: cfg.herramientas_pct, color: 'orange' },
        ])
      })
      .catch(() => {/* use demo */})
      .finally(() => setLoading(false))
  }, [id])

  function updateLink(idx: number, val: string) {
    const n = parseFloat(val) || 0
    setLinks((prev) => prev.map((l, i) => i === idx ? { ...l, pct: n } : l))
  }

  function removeLink(idx: number) {
    setLinks((prev) => prev.filter((_, i) => i !== idx))
  }

  function addLink() {
    setLinks((prev) => [...prev, { key: 'estructura_pct', label: 'Nuevo cargo', pct: 0, color: 'orange' }])
  }

  async function handleSave() {
    setSaving(true)
    const data: Partial<IndirectConfig> = {}
    links.forEach((l) => { data[l.key] = l.pct })
    try {
      if (id) {
        await budgetApi.updateIndirects(id, data)
      }
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      // ignore
    }
    setSaving(false)
  }

  const totalPct = links.reduce((s, l) => s + l.pct, 0) + beneficio

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Settings size={14} /> CONFIGURACIÓN
      </div>
      <div className="flex items-center gap-3 mb-2">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">CADENA DE MARKUPS</h1>
      </div>
      <p className="text-gray-500 text-sm mb-6 ml-4">
        Definí qué cargos se aplican sobre el costo directo. Podés agregar, quitar o reordenar.
      </p>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando...
        </div>
      )}

      <div className="max-w-3xl">
        {/* Visual chain */}
        <div className="bg-white rounded-xl border p-5 mb-4">
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            <div className="bg-blue-100 text-blue-800 px-3 py-2 rounded-lg font-medium text-sm whitespace-nowrap">
              Costo Directo
            </div>
            <span className="text-gray-300 text-lg">→</span>

            {links.map((link, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="bg-orange-50 text-orange-800 px-3 py-2 rounded-lg text-sm border border-orange-200 flex items-center gap-1.5">
                  <span>{link.label}</span>
                  <input
                    type="number"
                    value={link.pct}
                    onChange={(e) => updateLink(i, e.target.value)}
                    className="w-10 bg-transparent font-bold text-center outline-none border-b border-orange-300 text-orange-900"
                  />
                  <span>%</span>
                  <button
                    onClick={() => removeLink(i)}
                    className="ml-1 text-orange-300 hover:text-red-500 transition-colors"
                  >
                    <X size={12} />
                  </button>
                </div>
                <span className="text-gray-300 text-lg">→</span>
              </div>
            ))}

            {/* Beneficio */}
            <div className="bg-[#E8F5EE] text-[#1B5E4B] px-3 py-2 rounded-lg text-sm border border-green-200 flex items-center gap-1.5">
              <span>Beneficio</span>
              <input
                type="number"
                value={beneficio}
                onChange={(e) => setBeneficio(parseFloat(e.target.value) || 0)}
                className="w-10 bg-transparent font-bold text-center outline-none border-b border-green-300 text-green-900"
              />
              <span>%</span>
            </div>
            <span className="text-gray-300 text-lg">→</span>

            <div className="bg-[#2D8D68] text-white px-3 py-2 rounded-lg font-bold text-sm whitespace-nowrap">
              NETO TOTAL
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={addLink}
              className="text-xs text-[#2D8D68] font-medium hover:underline flex items-center gap-1"
            >
              <Plus size={12} /> Agregar eslabón
            </button>
            <span className="text-[10px] text-gray-400">Editá los % directamente · Click en × para quitar</span>
            <div className="ml-auto text-sm font-semibold text-gray-700">
              Total sobre directo: <span className="text-[#2D8D68]">{totalPct.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Editable table */}
        <div className="bg-white rounded-xl border p-5 mb-4">
          <h3 className="font-semibold text-gray-900 text-sm mb-3">Detalle de porcentajes</h3>
          <div className="space-y-2">
            {links.map((link, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-40 text-sm text-gray-700">{link.label}</div>
                <input
                  type="range"
                  min={0}
                  max={50}
                  value={link.pct}
                  onChange={(e) => updateLink(i, e.target.value)}
                  className="flex-1 accent-[#2D8D68]"
                />
                <div className="w-16 text-right font-bold text-[#2D8D68]">{link.pct}%</div>
              </div>
            ))}
            <div className="flex items-center gap-3">
              <div className="w-40 text-sm text-gray-700">Beneficio</div>
              <input
                type="range"
                min={0}
                max={50}
                value={beneficio}
                onChange={(e) => setBeneficio(parseFloat(e.target.value))}
                className="flex-1 accent-[#2D8D68]"
              />
              <div className="w-16 text-right font-bold text-[#2D8D68]">{beneficio}%</div>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <div className="text-xs text-gray-500">
              Total acumulado sobre costo directo:{' '}
              <strong className="text-gray-800">{totalPct.toFixed(1)}%</strong>
              {config && (
                <span className="ml-2 text-gray-400">
                  (original: {config.estructura_pct + config.jefatura_pct + config.logistica_pct + config.herramientas_pct + 10}%)
                </span>
              )}
            </div>
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-60 text-white font-semibold px-5 py-2 rounded-lg text-sm transition-colors flex items-center gap-2"
            >
              {saving && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {saved ? 'Guardado' : 'Guardar cambios'}
            </button>
          </div>
        </div>

        {/* USA example */}
        <div className="bg-gray-50 rounded-xl border p-4">
          <div className="text-xs font-medium text-gray-600 mb-2">Ejemplo de otro cliente (USA):</div>
          <div className="flex items-center gap-1 text-[10px] flex-wrap">
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Direct</span>
            {USA_EXAMPLE.map((u, i) => (
              <span key={i} className="flex items-center gap-1">
                <span className="text-gray-300">→</span>
                <span className={`px-2 py-1 rounded border ${u.green ? 'bg-green-50 text-green-800 border-green-200' : u.red ? 'bg-red-50 text-red-800 border-red-200' : 'bg-orange-50 text-orange-800 border-orange-200'}`}>
                  {u.label} {u.pct}%
                </span>
              </span>
            ))}
            <span className="text-gray-300">→</span>
            <span className="bg-gray-800 text-white px-2 py-1 rounded font-bold">NET</span>
          </div>
        </div>
      </div>
    </div>
  )
}
