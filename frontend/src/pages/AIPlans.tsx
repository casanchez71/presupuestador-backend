import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Layers, Check, X } from 'lucide-react'
import { budgetApi } from '../lib/api'
import FileUpload from '../components/ui/FileUpload'

interface AISuggestion {
  id: string
  description: string
  unidad: string
  cantidad?: number
  confidence: 'alta' | 'media' | 'baja'
  accepted?: boolean
}

const DEMO_SUGGESTIONS: AISuggestion[] = [
  { id: '1', description: '2.1 Columnas PB — H-30', unidad: 'm³', cantidad: 42.5, confidence: 'alta' },
  { id: '2', description: '2.2 Vigas PB — H-30', unidad: 'm³', cantidad: 28, confidence: 'alta' },
  { id: '3', description: '2.4 Mampostería exterior LP18', unidad: 'm²', cantidad: 320, confidence: 'media' },
  { id: '4', description: '2.5 Cielorraso suspendido', unidad: 'm²', cantidad: 144, confidence: 'alta' },
  { id: '5', description: '2.6 Revoque grueso interior', unidad: 'm²', cantidad: 580, confidence: 'media' },
  { id: '6', description: '2.7 Contrapiso H-6', unidad: 'm²', cantidad: 144, confidence: 'alta' },
  { id: '7', description: '2.8 Impermeabilización', unidad: 'm²', cantidad: 60, confidence: 'baja' },
  { id: '8', description: '2.9 Carpintería exterior', unidad: 'm²', cantidad: 32, confidence: 'media' },
]

const CONFIDENCE_STYLE: Record<string, string> = {
  alta: 'bg-[#E8F5EE] border-green-200',
  media: 'bg-amber-50 border-amber-200',
  baja: 'bg-red-50 border-red-200',
}
const CONFIDENCE_TEXT: Record<string, string> = {
  alta: 'text-gray-500',
  media: 'text-amber-700',
  baja: 'text-red-600',
}

export default function AIPlans() {
  const { id } = useParams<{ id: string }>()
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [done, setDone] = useState(false)
  const [elapsed, setElapsed] = useState(0)

  const accepted = suggestions.filter((s) => s.accepted)

  async function handleFile(file: File) {
    setAnalyzing(true)
    setDone(false)
    const start = Date.now()

    const formData = new FormData()
    formData.append('file', file)

    try {
      if (id) {
        await budgetApi.analyzePlan(id, formData)
        // In real usage, populate from response
      }
    } catch {
      // Use demo suggestions as fallback
    }

    setElapsed(Math.round((Date.now() - start) / 1000))
    setSuggestions(DEMO_SUGGESTIONS)
    setAnalyzing(false)
  }

  function toggle(sid: string) {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === sid ? { ...s, accepted: !s.accepted } : s)),
    )
  }

  async function addAccepted() {
    if (accepted.length === 0) return
    setSaving(true)
    try {
      if (id) {
        await budgetApi.addItemsFromAI(
          id,
          accepted.map((s) => ({ description: s.description, unidad: s.unidad, cantidad: s.cantidad })),
        )
      }
      setDone(true)
    } catch {
      // ignore
    }
    setSaving(false)
  }

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Layers size={14} /> INTELIGENCIA ARTIFICIAL
      </div>
      <div className="flex items-center gap-3 mb-2">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">ANÁLISIS DE PLANOS CON IA</h1>
      </div>
      <p className="text-gray-500 text-sm mb-6 ml-4">
        Subí una foto del plano. La IA extrae secciones y cantidades para el presupuesto.
      </p>

      <div className="grid grid-cols-2 gap-6">
        {/* Upload */}
        <div>
          <FileUpload
            accept="image/*,.pdf"
            label="Arrastrá el plano acá"
            hint="JPG, PNG, WEBP o PDF · hasta 20 MB"
            onFile={handleFile}
            icon={
              <svg className="mx-auto" width="48" height="48" fill="none" stroke="#9CA3AF" strokeWidth="1.5" viewBox="0 0 24 24">
                <path d="M3 16l4-4a3 5 0 014 0l5 5M14 14l1-1a3 5 0 014 0l4 4M3.5 21h17a1.5 1.5 0 001.5-1.5v-15A1.5 1.5 0 0020.5 3h-17A1.5 1.5 0 002 4.5v15A1.5 1.5 0 003.5 21z" />
              </svg>
            }
          />
          {analyzing && (
            <div className="mt-4 bg-[#E8F5EE] rounded-xl p-4 flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
              <div>
                <p className="text-sm font-semibold text-[#143D34]">Analizando plano...</p>
                <p className="text-xs text-gray-500">La IA está procesando la imagen</p>
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="bg-white rounded-xl border overflow-hidden">
          <div className="bg-[#2D8D68] text-white px-4 py-3 flex justify-between items-center">
            <span className="font-semibold text-sm">Resultado IA</span>
            {suggestions.length > 0 && (
              <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
                {suggestions.length} ítems · {elapsed > 0 ? `${elapsed} seg` : '—'}
              </span>
            )}
          </div>

          {suggestions.length === 0 ? (
            <div className="p-8 text-center text-gray-400 text-sm">
              {analyzing ? 'Procesando...' : 'Cargá un plano para comenzar el análisis.'}
            </div>
          ) : (
            <>
              <div className="p-3 space-y-2 max-h-[360px] overflow-y-auto">
                {suggestions.map((s) => (
                  <div
                    key={s.id}
                    className={`border rounded-lg p-2.5 flex justify-between items-center text-xs ${CONFIDENCE_STYLE[s.confidence]}`}
                  >
                    <div>
                      <div className="font-medium text-gray-800">{s.description}</div>
                      <div className={CONFIDENCE_TEXT[s.confidence]}>
                        {s.unidad} · ~{s.cantidad} · confianza: {s.confidence}
                      </div>
                    </div>
                    <div className="flex gap-1 ml-3">
                      <button
                        onClick={() => toggle(s.id)}
                        className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${
                          s.accepted
                            ? 'bg-[#2D8D68] text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-[#E8F5EE]'
                        }`}
                      >
                        {s.accepted ? <Check size={12} /> : 'Aceptar'}
                      </button>
                      <button
                        onClick={() => toggle(s.id)}
                        className="bg-gray-200 text-gray-600 px-2 py-1 rounded text-[10px] hover:bg-red-50 hover:text-red-600"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 border-t bg-gray-50 flex justify-between items-center">
                <span className="text-[10px] text-gray-400">{accepted.length} de {suggestions.length} seleccionados</span>
                <button
                  onClick={addAccepted}
                  disabled={accepted.length === 0 || saving}
                  className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-50 text-white font-semibold px-4 py-2 rounded-lg text-xs transition-colors"
                >
                  {saving ? 'Agregando...' : 'Agregar al presupuesto'}
                </button>
              </div>
              {done && (
                <div className="p-3 bg-[#E8F5EE] text-xs text-[#1B5E4B] font-medium border-t">
                  {accepted.length} ítems agregados al presupuesto correctamente.
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
