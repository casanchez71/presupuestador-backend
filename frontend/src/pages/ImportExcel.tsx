import { useState } from 'react'
import { Upload } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { budgetApi } from '../lib/api'
import FileUpload from '../components/ui/FileUpload'

interface DetectedFormat {
  format: string
  catalogs: number
  items: number
  detailSheets: number
  warnings: string[]
}

const DEMO_FORMAT: DetectedFormat = {
  format: 'Terrac — Cómputo y Presupuesto',
  catalogs: 5,
  items: 108,
  detailSheets: 44,
  warnings: ['12 códigos de ítem detectados como fechas por Excel. Corrección automática: 2024-01-01 → 1.1, 2024-02-01 → 1.2, etc.'],
}

export default function ImportExcel() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [detected, setDetected] = useState<DetectedFormat | null>(null)
  const [importing, setImporting] = useState(false)
  const [error, setError] = useState('')

  function handleFile(f: File) {
    setFile(f)
    setError('')
    // Simulate format detection
    setTimeout(() => setDetected(DEMO_FORMAT), 800)
  }

  async function handleImport() {
    if (!file) return
    setImporting(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)
    try {
      const budget = await budgetApi.importExcel(formData)
      navigate(`/app/budgets/${budget.id}/editor`)
    } catch (e) {
      setError('Error al importar. Verificá que el archivo sea un Excel válido en formato Terrac.')
      setImporting(false)
    }
  }

  return (
    <div className="p-6 fade-in">
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Upload size={14} /> IMPORTACIÓN
      </div>
      <div className="flex items-center gap-3 mb-2">
        <div className="w-1 h-7 bg-[#2D8D68] rounded-full" />
        <h1 className="text-xl font-extrabold text-gray-900">IMPORTAR EXCEL</h1>
      </div>
      <p className="text-gray-500 text-sm mb-6 ml-4">
        El sistema detecta el formato automáticamente y convierte hojas, ítems y catálogos.
      </p>

      <div className="max-w-3xl">
        <div className="mb-6">
          <FileUpload
            accept=".xlsx,.xls"
            label="Arrastrá tu Excel acá"
            hint=".xlsx o .xls"
            onFile={handleFile}
            icon={
              <svg className="mx-auto" width="48" height="48" fill="none" stroke="#9CA3AF" strokeWidth="1.5" viewBox="0 0 24 24">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
            }
          />
        </div>

        {/* Detected format panel */}
        {detected && (
          <div className="bg-white rounded-xl border p-5 fade-in">
            <h3 className="font-semibold text-gray-900 mb-3">
              Formato detectado:{' '}
              <span className="text-[#2D8D68]">{detected.format}</span>
            </h3>

            <div className="grid grid-cols-3 gap-3 text-sm mb-4">
              <div className="bg-[#E8F5EE] rounded-lg p-3 border border-green-200">
                <div className="text-[#1B5E4B] font-medium text-xs">{detected.catalogs} catálogos detectados</div>
                <div className="text-[10px] text-gray-500 mt-1">00_Mat, 00_MO, 00_Eq, 00_Sub, 00_JEF+ESTR</div>
              </div>
              <div className="bg-[#E8F5EE] rounded-lg p-3 border border-green-200">
                <div className="text-[#1B5E4B] font-medium text-xs">Hoja 01_C&P detectada</div>
                <div className="text-[10px] text-gray-500 mt-1">26 columnas · {detected.items} ítems · desglose MAT/MO/EQ/SUB</div>
              </div>
              <div className="bg-[#E8F5EE] rounded-lg p-3 border border-green-200">
                <div className="text-[#1B5E4B] font-medium text-xs">{detected.detailSheets} hojas detalle</div>
                <div className="text-[10px] text-gray-500 mt-1">78 filas c/u · 5 secciones: MAT, MO, EQ, SUB, Resumen</div>
              </div>
            </div>

            {detected.warnings.map((w, i) => (
              <div key={i} className="bg-amber-50 rounded-lg p-3 border border-amber-200 text-xs mb-4">
                <span className="text-amber-800 font-medium">{w}</span>
              </div>
            ))}

            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 text-xs px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleImport}
                disabled={importing}
                className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-60 text-white font-semibold px-5 py-2.5 rounded-lg text-sm transition-colors flex items-center gap-2"
              >
                {importing && (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                )}
                {importing ? 'Importando...' : 'Importar como presupuesto nuevo'}
              </button>
              <button className="bg-white border text-gray-600 px-5 py-2.5 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                Solo importar catálogos
              </button>
            </div>
          </div>
        )}

        {/* Info box */}
        <div className="mt-4 bg-[#E8F5EE] rounded-xl border border-green-200 p-4 text-xs text-[#143D34]">
          <p className="font-semibold mb-2">Formatos compatibles</p>
          <ul className="space-y-1 text-gray-600">
            <li>Catálogos → van a <strong>Catálogos de Precios</strong></li>
            <li>01_C&P → crea el <strong>árbol de ítems</strong></li>
            <li>Hojas detalle → crean los <strong>recursos por ítem</strong></li>
            <li>Códigos-fecha → se <strong>corrigen automáticamente</strong></li>
          </ul>
        </div>
      </div>
    </div>
  )
}
