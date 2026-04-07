import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Settings } from 'lucide-react'
import { budgetApi } from '../lib/api'
import type { IndirectConfig } from '../types'

const DEFAULT_CONFIG: IndirectConfig = {
  id: '',
  org_id: '',
  imprevistos_pct: 3,
  estructura_pct: 15,
  jefatura_pct: 8,
  logistica_pct: 5,
  herramientas_pct: 3,
  beneficio_pct: 25,
  ingresos_brutos_pct: 7,
  imp_cheque_pct: 1.2,
  iva_pct: 21,
}

interface FieldDef {
  key: keyof IndirectConfig
  label: string
  hint?: string
}

const INDIRECTO_FIELDS: FieldDef[] = [
  { key: 'imprevistos_pct', label: 'Imprevistos' },
  { key: 'estructura_pct', label: 'Estructura' },
  { key: 'jefatura_pct', label: 'Jefatura de Obra' },
  { key: 'logistica_pct', label: 'Logística' },
  { key: 'herramientas_pct', label: 'Herramientas' },
]

const IMPUESTO_FIELDS: FieldDef[] = [
  { key: 'ingresos_brutos_pct', label: 'Ingresos Brutos', hint: 'sobre Neto con Beneficio' },
  { key: 'imp_cheque_pct', label: 'Impuesto al Cheque', hint: 'sobre Neto con Beneficio' },
]

function PctInput({
  value,
  onChange,
}: {
  value: number
  onChange: (v: number) => void
}) {
  return (
    <div className="flex items-center gap-1">
      <input
        type="number"
        step="0.1"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="w-16 text-right px-2 py-1 text-sm font-semibold border border-gray-200 rounded-lg bg-white focus:outline-none focus:border-[#2D8D68] focus:ring-2 focus:ring-[#2D8D68]/20 tabular-nums"
      />
      <span className="text-sm text-gray-500 font-medium">%</span>
    </div>
  )
}

function SectionDivider({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 mt-5 mb-3">
      <div className="h-px flex-1 bg-gray-200" />
      <span className="text-[11px] font-bold tracking-widest text-gray-400 uppercase px-2">{label}</span>
      <div className="h-px flex-1 bg-gray-200" />
    </div>
  )
}

export default function MarkupChain() {
  const { id } = useParams<{ id: string }>()
  const [cfg, setCfg] = useState<IndirectConfig>(DEFAULT_CONFIG)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    budgetApi
      .getIndirects(id)
      .then((data) => {
        setCfg({
          ...DEFAULT_CONFIG,
          ...data,
          // ensure new fields have defaults if backend returns null/undefined
          imprevistos_pct: data.imprevistos_pct ?? DEFAULT_CONFIG.imprevistos_pct,
          beneficio_pct: data.beneficio_pct ?? DEFAULT_CONFIG.beneficio_pct,
          ingresos_brutos_pct: data.ingresos_brutos_pct ?? DEFAULT_CONFIG.ingresos_brutos_pct,
          imp_cheque_pct: data.imp_cheque_pct ?? DEFAULT_CONFIG.imp_cheque_pct,
          iva_pct: data.iva_pct ?? DEFAULT_CONFIG.iva_pct,
        })
      })
      .catch(() => {/* use defaults */})
      .finally(() => setLoading(false))
  }, [id])

  function set(key: keyof IndirectConfig, val: number) {
    setCfg((prev) => ({ ...prev, [key]: val }))
  }

  async function handleSave() {
    setSaving(true)
    try {
      if (id) {
        await budgetApi.updateIndirects(id, {
          imprevistos_pct: cfg.imprevistos_pct,
          estructura_pct: cfg.estructura_pct,
          jefatura_pct: cfg.jefatura_pct,
          logistica_pct: cfg.logistica_pct,
          herramientas_pct: cfg.herramientas_pct,
          beneficio_pct: cfg.beneficio_pct,
          ingresos_brutos_pct: cfg.ingresos_brutos_pct,
          imp_cheque_pct: cfg.imp_cheque_pct,
          iva_pct: cfg.iva_pct,
        })
      }
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      // ignore
    }
    setSaving(false)
  }

  const subtotalIndirectosPct = INDIRECTO_FIELDS.reduce(
    (s, f) => s + ((cfg[f.key] as number) ?? 0),
    0,
  )

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Settings size={14} /> CONFIGURACIÓN
      </div>
      <div className="flex items-center gap-3 mb-2">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">CADENA DE COSTOS INDIRECTOS</h1>
      </div>
      <p className="text-gray-500 text-sm mb-6 ml-4">
        Configurá los porcentajes que se aplican en cascada sobre el costo directo.
      </p>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          <div className="w-4 h-4 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
          Cargando...
        </div>
      )}

      <div className="max-w-lg">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          {/* Header */}
          <div className="bg-[#E8F5EE] px-6 py-4 border-b border-[#2D8D68]/20">
            <h2 className="text-[#143D34] font-bold text-base">Parámetros de costos</h2>
            <p className="text-[#2D8D68] text-xs mt-0.5">
              Directo → + Indirectos → + Beneficio → + Impuestos → + IVA = Total Final
            </p>
          </div>

          <div className="px-6 pb-6">
            {/* ── COSTOS INDIRECTOS ── */}
            <SectionDivider label="Costos Indirectos" />
            <div className="space-y-2">
              {INDIRECTO_FIELDS.map((f) => (
                <div key={f.key} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{f.label}</span>
                  <PctInput
                    value={(cfg[f.key] as number) ?? 0}
                    onChange={(v) => set(f.key, v)}
                  />
                </div>
              ))}
            </div>
            {/* Subtotal indirectos */}
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-dashed border-gray-200">
              <span className="text-sm font-semibold text-gray-600">Subtotal Indirectos:</span>
              <span className="text-sm font-bold text-[#E8663C]">{subtotalIndirectosPct.toFixed(1)} %</span>
            </div>

            {/* ── BENEFICIO ── */}
            <SectionDivider label="Beneficio" />
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-700">Beneficio</span>
                <span className="ml-2 text-[11px] text-gray-400">(sobre Subt. con Indirectos)</span>
              </div>
              <PctInput
                value={cfg.beneficio_pct ?? 25}
                onChange={(v) => set('beneficio_pct', v)}
              />
            </div>

            {/* ── IMPUESTOS ── */}
            <SectionDivider label="Impuestos" />
            <div className="space-y-2">
              {IMPUESTO_FIELDS.map((f) => (
                <div key={f.key} className="flex items-center justify-between">
                  <div>
                    <span className="text-sm text-gray-700">{f.label}</span>
                    {f.hint && (
                      <span className="ml-2 text-[11px] text-gray-400">({f.hint})</span>
                    )}
                  </div>
                  <PctInput
                    value={(cfg[f.key] as number) ?? 0}
                    onChange={(v) => set(f.key, v)}
                  />
                </div>
              ))}
            </div>

            {/* ── IVA ── */}
            <SectionDivider label="IVA" />
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-700">IVA</span>
                <span className="ml-2 text-[11px] text-gray-400">(sobre Neto)</span>
              </div>
              <PctInput
                value={cfg.iva_pct ?? 21}
                onChange={(v) => set('iva_pct', v)}
              />
            </div>

            {/* Save */}
            <div className="mt-6 flex justify-end">
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-60 text-white font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors flex items-center gap-2 shadow-sm"
              >
                {saving && (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                )}
                {saved ? 'Guardado' : 'Guardar cambios'}
              </button>
            </div>
          </div>
        </div>

        {/* Visual cascade summary */}
        <div className="mt-4 bg-gray-50 rounded-xl border border-gray-100 shadow-sm p-4">
          <div className="text-[11px] font-bold text-gray-500 tracking-wider mb-3">CASCADA DE CÁLCULO</div>
          <div className="space-y-1.5 text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0" />
              <span>Costo Directo (MAT + MO)</span>
            </div>
            <div className="flex items-center gap-2 ml-3">
              <span className="text-gray-300">+</span>
              <span className="text-[#E8663C] font-medium">Indirectos ({subtotalIndirectosPct.toFixed(1)}%)</span>
              <span className="text-gray-400">= Subtotal 02</span>
            </div>
            <div className="flex items-center gap-2 ml-3">
              <span className="text-gray-300">+</span>
              <span className="text-amber-600 font-medium">Beneficio ({(cfg.beneficio_pct ?? 25).toFixed(1)}%)</span>
              <span className="text-gray-400">= Subtotal 03</span>
            </div>
            <div className="flex items-center gap-2 ml-3">
              <span className="text-gray-300">+</span>
              <span className="text-rose-600 font-medium">
                Impuestos ({((cfg.ingresos_brutos_pct ?? 7) + (cfg.imp_cheque_pct ?? 1.2)).toFixed(1)}%)
              </span>
              <span className="text-gray-400">= Neto</span>
            </div>
            <div className="flex items-center gap-2 ml-3">
              <span className="text-gray-300">+</span>
              <span className="text-[#143D34] font-medium">IVA ({(cfg.iva_pct ?? 21).toFixed(1)}%)</span>
              <span className="text-gray-400">= Total Final</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
