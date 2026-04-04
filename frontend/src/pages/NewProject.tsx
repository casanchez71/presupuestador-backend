import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Upload,
  Building2,
  Percent,
  CheckCircle,
  ChevronRight,
  ChevronLeft,
  Plus,
  Trash2,
  GripVertical,
  Image,
  FileJson,
  Sparkles,
  ArrowRight,
} from 'lucide-react'
import { budgetApi, catalogApi } from '../lib/api'
import type { Budget, PriceCatalog } from '../types'
import FileUpload from '../components/ui/FileUpload'

// ─── Types ─────────────────────────────────────────────────────────────────────

interface ProjectData {
  name: string
  description: string
  superficie: string
  duracion: string
}

interface SectionItem {
  id: string
  descripcion: string
  unidad: string
  cantidad: string
}

interface Section {
  id: string
  nombre: string
  items: SectionItem[]
}

interface IndirectCosts {
  estructura: number
  jefatura: number
  logistica: number
  herramientas: number
  beneficio: number
}

type PriceOption = 'csv' | 'catalog' | 'skip'
type StructureOption = 'plan' | 'manual' | 'json'

const STEPS = [
  { label: 'Datos', icon: FileText },
  { label: 'Precios', icon: Upload },
  { label: 'Estructura', icon: Building2 },
  { label: 'Indirectos', icon: Percent },
  { label: 'Resultado', icon: CheckCircle },
]

function uid() {
  return Math.random().toString(36).slice(2, 9)
}

// ─── Main Component ────────────────────────────────────────────────────────────

export default function NewProject() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  // Step 1
  const [project, setProject] = useState<ProjectData>({
    name: '',
    description: '',
    superficie: '',
    duracion: '',
  })

  // Step 2
  const [priceOption, setPriceOption] = useState<PriceOption>('skip')
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvPreview, setCsvPreview] = useState<string[][]>([])
  const [catalogs, setCatalogs] = useState<PriceCatalog[]>([])
  const [selectedCatalog, setSelectedCatalog] = useState('')
  const [catalogsLoaded, setCatalogsLoaded] = useState(false)

  // Step 3
  const [structureOption, setStructureOption] = useState<StructureOption>('manual')
  const [planFile, setPlanFile] = useState<File | null>(null)
  const [sections, setSections] = useState<Section[]>([
    { id: uid(), nombre: '', items: [] },
  ])
  const [jsonFile, setJsonFile] = useState<File | null>(null)
  const [jsonSections, setJsonSections] = useState<Section[]>([])

  // Step 4
  const [indirects, setIndirects] = useState<IndirectCosts>({
    estructura: 15,
    jefatura: 8,
    logistica: 5,
    herramientas: 3,
    beneficio: 10,
  })

  // Step 5
  const [result, setResult] = useState<{
    budgetId: string
    sectionsCount: number
    itemsCount: number
  } | null>(null)

  // ─── Step navigation ───────────────────────────────────────────────────────

  function canAdvance(): boolean {
    if (step === 0) return project.name.trim().length > 0
    return true
  }

  function next() {
    if (!canAdvance()) return
    if (step === 3) {
      handleCreate()
      return
    }
    setStep((s) => Math.min(s + 1, 4))
    setError('')
  }

  function prev() {
    setStep((s) => Math.max(s - 1, 0))
    setError('')
  }

  // ─── Load catalogs lazily ──────────────────────────────────────────────────

  const loadCatalogs = useCallback(() => {
    if (catalogsLoaded) return
    catalogApi.list()
      .then((list) => {
        setCatalogs(list)
        if (list.length > 0) setSelectedCatalog(list[0].id)
      })
      .catch(() => {/* ignore */})
      .finally(() => setCatalogsLoaded(true))
  }, [catalogsLoaded])

  // ─── CSV preview parsing ──────────────────────────────────────────────────

  function handleCsvFile(f: File) {
    setCsvFile(f)
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const lines = text.split('\n').filter((l) => l.trim())
      const rows = lines.slice(0, 11).map((l) => l.split(/[,;\t]/).map((c) => c.trim()))
      setCsvPreview(rows)
    }
    reader.readAsText(f)
  }

  // ─── JSON structure import ────────────────────────────────────────────────

  function handleJsonFile(f: File) {
    setJsonFile(f)
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string)
        if (Array.isArray(data)) {
          const imported: Section[] = data.map((s: { nombre?: string; items?: { descripcion?: string; unidad?: string; cantidad?: number }[] }) => ({
            id: uid(),
            nombre: s.nombre ?? '',
            items: (s.items ?? []).map((it: { descripcion?: string; unidad?: string; cantidad?: number }) => ({
              id: uid(),
              descripcion: it.descripcion ?? '',
              unidad: it.unidad ?? '',
              cantidad: String(it.cantidad ?? ''),
            })),
          }))
          setJsonSections(imported)
        }
      } catch {
        setError('El archivo JSON no tiene un formato valido.')
      }
    }
    reader.readAsText(f)
  }

  // ─── Section management ───────────────────────────────────────────────────

  function addSection() {
    setSections((prev) => [...prev, { id: uid(), nombre: '', items: [] }])
  }

  function removeSection(sectionId: string) {
    setSections((prev) => prev.filter((s) => s.id !== sectionId))
  }

  function updateSectionName(sectionId: string, name: string) {
    setSections((prev) =>
      prev.map((s) => (s.id === sectionId ? { ...s, nombre: name } : s))
    )
  }

  function addItem(sectionId: string) {
    setSections((prev) =>
      prev.map((s) =>
        s.id === sectionId
          ? { ...s, items: [...s.items, { id: uid(), descripcion: '', unidad: 'gl', cantidad: '1' }] }
          : s
      )
    )
  }

  function removeItem(sectionId: string, itemId: string) {
    setSections((prev) =>
      prev.map((s) =>
        s.id === sectionId
          ? { ...s, items: s.items.filter((it) => it.id !== itemId) }
          : s
      )
    )
  }

  function updateItem(sectionId: string, itemId: string, field: keyof SectionItem, value: string) {
    setSections((prev) =>
      prev.map((s) =>
        s.id === sectionId
          ? {
            ...s,
            items: s.items.map((it) =>
              it.id === itemId ? { ...it, [field]: value } : it
            ),
          }
          : s
      )
    )
  }

  function moveSectionUp(idx: number) {
    if (idx <= 0) return
    setSections((prev) => {
      const arr = [...prev]
      ;[arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]
      return arr
    })
  }

  function moveSectionDown(idx: number) {
    setSections((prev) => {
      if (idx >= prev.length - 1) return prev
      const arr = [...prev]
      ;[arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]
      return arr
    })
  }

  // ─── Create budget ────────────────────────────────────────────────────────

  async function handleCreate() {
    setCreating(true)
    setError('')
    try {
      // 1. Create budget
      const budget = await budgetApi.create({
        name: project.name,
        description: project.description || undefined,
        status: 'borrador',
      } as Partial<Budget>)

      const budgetId = budget.id

      // 2. Determine which sections/items to use
      const finalSections =
        structureOption === 'json' && jsonSections.length > 0
          ? jsonSections
          : structureOption === 'manual'
            ? sections.filter((s) => s.nombre.trim())
            : []

      // 3. Create items (sections as parent, then children)
      let totalItems = 0
      for (let si = 0; si < finalSections.length; si++) {
        const sec = finalSections[si]
        // Create parent/section item
        const parentItem = await budgetApi.createItem(budgetId, {
          description: sec.nombre,
          code: `${si + 1}`,
          sort_order: (si + 1) * 100,
          cantidad: 1,
          unidad: 'gl',
        })

        // Create child items
        for (let ii = 0; ii < sec.items.length; ii++) {
          const it = sec.items[ii]
          if (!it.descripcion.trim()) continue
          await budgetApi.createItem(budgetId, {
            parent_id: parentItem.id,
            description: it.descripcion,
            code: `${si + 1}.${ii + 1}`,
            unidad: it.unidad || 'gl',
            cantidad: parseFloat(it.cantidad) || 1,
            sort_order: (si + 1) * 100 + ii + 1,
          })
          totalItems++
        }
      }

      // 4. Set indirect costs
      try {
        await budgetApi.updateIndirects(budgetId, {
          estructura_pct: indirects.estructura,
          jefatura_pct: indirects.jefatura,
          logistica_pct: indirects.logistica,
          herramientas_pct: indirects.herramientas,
        })
      } catch {
        // Indirects endpoint may not exist yet - continue
      }

      // 5. Apply catalog if selected
      if (priceOption === 'catalog' && selectedCatalog) {
        try {
          await catalogApi.apply(budgetId, selectedCatalog)
        } catch {
          // Continue even if catalog fails
        }
      }

      setResult({
        budgetId,
        sectionsCount: finalSections.length,
        itemsCount: totalItems,
      })
      setStep(4)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Error desconocido'
      setError(`Error al crear el presupuesto: ${msg}`)
    } finally {
      setCreating(false)
    }
  }

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="p-6 fade-in">
      {/* Page header */}
      <div className="flex items-center gap-2 text-[#2D8D68] text-[11px] font-bold tracking-wider mb-1">
        <Plus size={14} /> NUEVO PRESUPUESTO
      </div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-1 h-8 bg-[#2D8D68] rounded-full" />
        <h1 className="text-2xl font-extrabold text-gray-900">CREAR PRESUPUESTO</h1>
      </div>

      {/* Stepper */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="flex items-center justify-between relative">
          {/* Connecting line */}
          <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 z-0" />
          <div
            className="absolute top-5 left-0 h-0.5 bg-[#2D8D68] z-0 transition-all duration-500"
            style={{ width: `${(step / (STEPS.length - 1)) * 100}%` }}
          />

          {STEPS.map((s, i) => {
            const Icon = s.icon
            const isActive = i === step
            const isDone = i < step
            return (
              <div key={i} className="flex flex-col items-center z-10">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isDone
                      ? 'bg-[#2D8D68] text-white'
                      : isActive
                        ? 'bg-[#2D8D68] text-white ring-4 ring-[#2D8D68]/20'
                        : 'bg-white border-2 border-gray-300 text-gray-400'
                  }`}
                >
                  {isDone ? (
                    <CheckCircle size={18} />
                  ) : (
                    <Icon size={18} />
                  )}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    isActive || isDone ? 'text-[#2D8D68]' : 'text-gray-400'
                  }`}
                >
                  {s.label}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Step content */}
      <div className="max-w-4xl mx-auto">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {step === 0 && (
          <StepDatos project={project} setProject={setProject} />
        )}
        {step === 1 && (
          <StepPrecios
            priceOption={priceOption}
            setPriceOption={setPriceOption}
            csvFile={csvFile}
            csvPreview={csvPreview}
            onCsvFile={handleCsvFile}
            catalogs={catalogs}
            selectedCatalog={selectedCatalog}
            setSelectedCatalog={setSelectedCatalog}
            loadCatalogs={loadCatalogs}
          />
        )}
        {step === 2 && (
          <StepEstructura
            structureOption={structureOption}
            setStructureOption={setStructureOption}
            planFile={planFile}
            setPlanFile={setPlanFile}
            sections={sections}
            addSection={addSection}
            removeSection={removeSection}
            updateSectionName={updateSectionName}
            addItem={addItem}
            removeItem={removeItem}
            updateItem={updateItem}
            moveSectionUp={moveSectionUp}
            moveSectionDown={moveSectionDown}
            jsonFile={jsonFile}
            jsonSections={jsonSections}
            onJsonFile={handleJsonFile}
          />
        )}
        {step === 3 && (
          <StepIndirectos indirects={indirects} setIndirects={setIndirects} />
        )}
        {step === 4 && result && (
          <StepResultado result={result} navigate={navigate} />
        )}

        {/* Navigation buttons */}
        {step < 4 && (
          <div className="flex items-center justify-between mt-8">
            <button
              onClick={prev}
              disabled={step === 0}
              className="flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={16} /> Anterior
            </button>
            <button
              onClick={next}
              disabled={!canAdvance() || creating}
              className="bg-[#2D8D68] hover:bg-[#1B5E4B] disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition-colors flex items-center gap-2"
            >
              {creating && (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              )}
              {step === 3
                ? creating
                  ? 'Creando...'
                  : 'Crear Presupuesto'
                : 'Siguiente'}
              {!creating && step < 3 && <ChevronRight size={16} />}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Step 1: Datos del Proyecto ─────────────────────────────────────────────

function StepDatos({
  project,
  setProject,
}: {
  project: ProjectData
  setProject: React.Dispatch<React.SetStateAction<ProjectData>>
}) {
  function update(field: keyof ProjectData, value: string) {
    setProject((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="bg-white rounded-xl border p-6 fade-in">
      <h2 className="text-lg font-bold text-gray-900 mb-1">Datos del Proyecto</h2>
      <p className="text-sm text-gray-500 mb-6">Informacion basica de la obra.</p>

      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre del proyecto <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={project.name}
            onChange={(e) => update('name', e.target.value)}
            placeholder="Ej: Casa Lugones, Edificio Norte..."
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] transition-all"
            autoFocus
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Descripcion</label>
          <textarea
            value={project.description}
            onChange={(e) => update('description', e.target.value)}
            placeholder="Descripcion breve de la obra..."
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] transition-all resize-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Superficie total (m2)
            </label>
            <input
              type="number"
              value={project.superficie}
              onChange={(e) => update('superficie', e.target.value)}
              placeholder="Ej: 250"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duracion estimada (meses)
            </label>
            <input
              type="number"
              value={project.duracion}
              onChange={(e) => update('duracion', e.target.value)}
              placeholder="Ej: 12"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] transition-all"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Step 2: Lista de Precios ───────────────────────────────────────────────

function StepPrecios({
  priceOption,
  setPriceOption,
  csvFile,
  csvPreview,
  onCsvFile,
  catalogs,
  selectedCatalog,
  setSelectedCatalog,
  loadCatalogs,
}: {
  priceOption: PriceOption
  setPriceOption: (v: PriceOption) => void
  csvFile: File | null
  csvPreview: string[][]
  onCsvFile: (f: File) => void
  catalogs: PriceCatalog[]
  selectedCatalog: string
  setSelectedCatalog: (v: string) => void
  loadCatalogs: () => void
}) {
  return (
    <div className="fade-in space-y-4">
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-1">Lista de Precios</h2>
        <p className="text-sm text-gray-500 mb-6">
          Podes cargar un catalogo de precios ahora o hacerlo despues.
        </p>

        <div className="grid grid-cols-3 gap-3 mb-6">
          <OptionCard
            active={priceOption === 'csv'}
            onClick={() => setPriceOption('csv')}
            icon={<Upload size={20} />}
            title="Subir CSV"
            description="Materiales, MO, equipos"
          />
          <OptionCard
            active={priceOption === 'catalog'}
            onClick={() => {
              setPriceOption('catalog')
              loadCatalogs()
            }}
            icon={<FileText size={20} />}
            title="Catalogo existente"
            description="Usar uno ya cargado"
          />
          <OptionCard
            active={priceOption === 'skip'}
            onClick={() => setPriceOption('skip')}
            icon={<ChevronRight size={20} />}
            title="Cargar despues"
            description="Saltear este paso"
          />
        </div>

        {priceOption === 'csv' && (
          <div className="fade-in">
            <FileUpload
              accept=".csv,.tsv,.txt"
              label="Arrastra tu archivo de precios"
              hint=".csv con columnas: tipo, codigo, descripcion, unidad, precio"
              onFile={onCsvFile}
            />
            {csvFile && csvPreview.length > 0 && (
              <div className="mt-4 overflow-x-auto">
                <div className="text-xs font-medium text-gray-500 mb-2">
                  Vista previa ({csvPreview.length > 10 ? '10 primeras filas' : `${csvPreview.length} filas`})
                </div>
                <table className="w-full text-xs border-collapse">
                  <tbody>
                    {csvPreview.slice(0, 11).map((row, ri) => (
                      <tr key={ri} className={ri === 0 ? 'bg-gray-100 font-semibold' : 'border-t border-gray-100'}>
                        {row.map((cell, ci) => (
                          <td key={ci} className="px-3 py-1.5 text-gray-600 truncate max-w-[150px]">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {priceOption === 'catalog' && (
          <div className="fade-in">
            {catalogs.length === 0 ? (
              <div className="text-sm text-gray-500 bg-gray-50 rounded-lg p-4 text-center">
                No hay catalogos cargados todavia. Podes subir uno desde la seccion Catalogos.
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Selecciona un catalogo
                </label>
                <select
                  value={selectedCatalog}
                  onChange={(e) => setSelectedCatalog(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] bg-white"
                >
                  {catalogs.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({new Date(c.created_at).toLocaleDateString('es-AR')})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        {priceOption === 'skip' && (
          <div className="fade-in bg-[#E8F5EE] rounded-lg p-4 border border-green-200 text-sm text-[#143D34]">
            Vas a poder cargar precios mas tarde desde el Editor o la seccion Catalogos.
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Step 3: Estructura de Obra ─────────────────────────────────────────────

function StepEstructura({
  structureOption,
  setStructureOption,
  planFile,
  setPlanFile,
  sections,
  addSection,
  removeSection,
  updateSectionName,
  addItem,
  removeItem,
  updateItem,
  moveSectionUp,
  moveSectionDown,
  jsonFile,
  jsonSections,
  onJsonFile,
}: {
  structureOption: StructureOption
  setStructureOption: (v: StructureOption) => void
  planFile: File | null
  setPlanFile: (f: File | null) => void
  sections: Section[]
  addSection: () => void
  removeSection: (id: string) => void
  updateSectionName: (id: string, name: string) => void
  addItem: (id: string) => void
  removeItem: (sectionId: string, itemId: string) => void
  updateItem: (sectionId: string, itemId: string, field: keyof SectionItem, value: string) => void
  moveSectionUp: (idx: number) => void
  moveSectionDown: (idx: number) => void
  jsonFile: File | null
  jsonSections: Section[]
  onJsonFile: (f: File) => void
}) {
  return (
    <div className="fade-in space-y-4">
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-1">Estructura de Obra</h2>
        <p className="text-sm text-gray-500 mb-6">
          Define las secciones e items de tu presupuesto.
        </p>

        <div className="grid grid-cols-3 gap-3 mb-6">
          <OptionCard
            active={structureOption === 'plan'}
            onClick={() => setStructureOption('plan')}
            icon={<Image size={20} />}
            title="Subir plano"
            description="IA analiza la imagen"
          />
          <OptionCard
            active={structureOption === 'manual'}
            onClick={() => setStructureOption('manual')}
            icon={<Building2 size={20} />}
            title="Definir manual"
            description="Armar secciones e items"
          />
          <OptionCard
            active={structureOption === 'json'}
            onClick={() => setStructureOption('json')}
            icon={<FileJson size={20} />}
            title="Importar JSON"
            description="Estructura desde archivo"
          />
        </div>

        {/* Plan upload */}
        {structureOption === 'plan' && (
          <div className="fade-in">
            <FileUpload
              accept=".jpg,.jpeg,.png,.pdf"
              label="Subi el plano de obra"
              hint="JPG, PNG o PDF"
              onFile={(f) => setPlanFile(f)}
              icon={<Image size={48} className="text-gray-300" />}
            />
            {planFile && (
              <div className="mt-4 bg-[#FEF9EE] rounded-lg p-4 border border-[#E0A33A]/30 flex items-start gap-3">
                <Sparkles size={20} className="text-[#E0A33A] flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-800">IA va a analizar este plano</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Una vez creado el presupuesto, vas a poder ir a la seccion IA para que analice
                    el plano y sugiera items automaticamente.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Manual structure */}
        {structureOption === 'manual' && (
          <div className="fade-in space-y-4">
            {sections.map((sec, si) => (
              <div
                key={sec.id}
                className="border border-gray-200 rounded-lg overflow-hidden"
              >
                {/* Section header */}
                <div className="bg-gray-50 px-4 py-3 flex items-center gap-3">
                  <div className="flex flex-col gap-0.5">
                    <button
                      onClick={() => moveSectionUp(si)}
                      disabled={si === 0}
                      className="text-gray-400 hover:text-gray-600 disabled:opacity-20 transition-colors"
                    >
                      <GripVertical size={14} />
                    </button>
                    <button
                      onClick={() => moveSectionDown(si)}
                      disabled={si === sections.length - 1}
                      className="text-gray-400 hover:text-gray-600 disabled:opacity-20 transition-colors"
                    >
                      <GripVertical size={14} />
                    </button>
                  </div>
                  <span className="text-xs font-bold text-[#2D8D68] w-6">{si + 1}.</span>
                  <input
                    type="text"
                    value={sec.nombre}
                    onChange={(e) => updateSectionName(sec.id, e.target.value)}
                    placeholder="Nombre de seccion (ej: Tareas Preliminares)"
                    className="flex-1 bg-transparent border-b border-gray-300 text-sm font-medium text-gray-800 focus:outline-none focus:border-[#2D8D68] px-1 py-0.5 transition-colors"
                  />
                  <button
                    onClick={() => removeSection(sec.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors p-1"
                    title="Eliminar seccion"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>

                {/* Items */}
                <div className="p-4 space-y-2">
                  {sec.items.map((it, ii) => (
                    <div key={it.id} className="flex items-center gap-2">
                      <span className="text-[10px] text-gray-400 w-8 text-right">
                        {si + 1}.{ii + 1}
                      </span>
                      <input
                        type="text"
                        value={it.descripcion}
                        onChange={(e) => updateItem(sec.id, it.id, 'descripcion', e.target.value)}
                        placeholder="Descripcion del item"
                        className="flex-1 border border-gray-200 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] transition-all"
                      />
                      <select
                        value={it.unidad}
                        onChange={(e) => updateItem(sec.id, it.id, 'unidad', e.target.value)}
                        className="w-20 border border-gray-200 rounded px-2 py-1.5 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-[#2D8D68]/30"
                      >
                        <option value="gl">gl</option>
                        <option value="m2">m2</option>
                        <option value="m3">m3</option>
                        <option value="ml">ml</option>
                        <option value="kg">kg</option>
                        <option value="un">un</option>
                        <option value="hs">hs</option>
                      </select>
                      <input
                        type="number"
                        value={it.cantidad}
                        onChange={(e) => updateItem(sec.id, it.id, 'cantidad', e.target.value)}
                        placeholder="Cant."
                        className="w-20 border border-gray-200 rounded px-2 py-1.5 text-sm text-right focus:outline-none focus:ring-1 focus:ring-[#2D8D68]/30 focus:border-[#2D8D68] transition-all"
                      />
                      <button
                        onClick={() => removeItem(sec.id, it.id)}
                        className="text-gray-400 hover:text-red-500 transition-colors p-1"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => addItem(sec.id)}
                    className="flex items-center gap-1 text-xs text-[#2D8D68] font-medium hover:text-[#1B5E4B] mt-2 transition-colors"
                  >
                    <Plus size={12} /> Agregar item
                  </button>
                </div>
              </div>
            ))}

            <button
              onClick={addSection}
              className="w-full border-2 border-dashed border-gray-300 rounded-lg py-3 text-sm font-medium text-gray-500 hover:border-[#2D8D68] hover:text-[#2D8D68] transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={16} /> Agregar seccion
            </button>
          </div>
        )}

        {/* JSON import */}
        {structureOption === 'json' && (
          <div className="fade-in">
            <FileUpload
              accept=".json"
              label="Subi un archivo JSON"
              hint='Formato: [{"nombre": "Seccion", "items": [{"descripcion": "...", "unidad": "m2", "cantidad": 10}]}]'
              onFile={onJsonFile}
              icon={<FileJson size={48} className="text-gray-300" />}
            />
            {jsonFile && jsonSections.length > 0 && (
              <div className="mt-4 bg-[#E8F5EE] rounded-lg p-4 border border-green-200">
                <div className="text-sm font-medium text-[#143D34] mb-2">
                  Estructura importada: {jsonSections.length} secciones,{' '}
                  {jsonSections.reduce((s, sec) => s + sec.items.length, 0)} items
                </div>
                <div className="space-y-1">
                  {jsonSections.map((sec, i) => (
                    <div key={sec.id} className="text-xs text-gray-600">
                      <span className="font-medium">{i + 1}. {sec.nombre}</span>
                      <span className="text-gray-400 ml-2">({sec.items.length} items)</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Step 4: Costos Indirectos ──────────────────────────────────────────────

function StepIndirectos({
  indirects,
  setIndirects,
}: {
  indirects: IndirectCosts
  setIndirects: React.Dispatch<React.SetStateAction<IndirectCosts>>
}) {
  function update(field: keyof IndirectCosts, value: number) {
    setIndirects((prev) => ({ ...prev, [field]: value }))
  }

  const chain = [
    { label: 'Estructura', key: 'estructura' as const, color: 'bg-orange-50 text-orange-800 border-orange-200' },
    { label: 'Jefatura', key: 'jefatura' as const, color: 'bg-orange-50 text-orange-800 border-orange-200' },
    { label: 'Logistica', key: 'logistica' as const, color: 'bg-orange-50 text-orange-800 border-orange-200' },
    { label: 'Herramientas', key: 'herramientas' as const, color: 'bg-orange-50 text-orange-800 border-orange-200' },
    { label: 'Beneficio', key: 'beneficio' as const, color: 'bg-[#E8F5EE] text-[#1B5E4B] border-green-200' },
  ]

  const totalPct = chain.reduce((s, c) => s + indirects[c.key], 0)

  return (
    <div className="fade-in space-y-4">
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-1">Costos Indirectos</h2>
        <p className="text-sm text-gray-500 mb-6">
          Configura los porcentajes que se aplican sobre el costo directo.
        </p>

        {/* Visual chain */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6 overflow-x-auto">
          <div className="flex items-center gap-2 min-w-max">
            <div className="bg-blue-100 text-blue-800 px-3 py-2 rounded-lg font-medium text-sm whitespace-nowrap">
              Directo
            </div>
            {chain.map((c) => (
              <div key={c.key} className="flex items-center gap-2">
                <ArrowRight size={14} className="text-gray-300 flex-shrink-0" />
                <div className={`px-3 py-2 rounded-lg text-sm border whitespace-nowrap ${c.color}`}>
                  +{indirects[c.key]}% {c.label}
                </div>
              </div>
            ))}
            <ArrowRight size={14} className="text-gray-300 flex-shrink-0" />
            <div className="bg-[#2D8D68] text-white px-3 py-2 rounded-lg font-bold text-sm whitespace-nowrap">
              NETO
            </div>
          </div>
        </div>

        {/* Sliders */}
        <div className="space-y-5">
          {chain.map((c) => (
            <div key={c.key}>
              <div className="flex items-center justify-between mb-1">
                <label className="text-sm font-medium text-gray-700">{c.label}</label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={0}
                    max={50}
                    value={indirects[c.key]}
                    onChange={(e) => update(c.key, parseFloat(e.target.value) || 0)}
                    className="w-16 border border-gray-300 rounded px-2 py-1 text-sm text-right font-bold text-[#2D8D68] focus:outline-none focus:ring-1 focus:ring-[#2D8D68]/30"
                  />
                  <span className="text-sm text-gray-500">%</span>
                </div>
              </div>
              <input
                type="range"
                min={0}
                max={50}
                step={0.5}
                value={indirects[c.key]}
                onChange={(e) => update(c.key, parseFloat(e.target.value))}
                className="w-full accent-[#2D8D68] h-2"
              />
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Total sobre costo directo
          </span>
          <span className="text-lg font-bold text-[#2D8D68]">{totalPct.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  )
}

// ─── Step 5: Resultado ──────────────────────────────────────────────────────

function StepResultado({
  result,
  navigate,
}: {
  result: { budgetId: string; sectionsCount: number; itemsCount: number }
  navigate: (path: string) => void
}) {
  return (
    <div className="fade-in">
      <div className="bg-white rounded-xl border p-8 text-center">
        {/* Success animation */}
        <div className="w-20 h-20 bg-[#E8F5EE] rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
          <CheckCircle size={40} className="text-[#2D8D68]" />
        </div>

        <h2 className="text-xl font-bold text-gray-900 mb-2">Presupuesto creado</h2>
        <p className="text-sm text-gray-500 mb-6">
          Tu presupuesto fue creado exitosamente y esta listo para editar.
        </p>

        <div className="flex justify-center gap-4 mb-8">
          <div className="bg-[#E8F5EE] rounded-lg px-6 py-4 text-center">
            <div className="text-2xl font-bold text-[#2D8D68]">{result.sectionsCount}</div>
            <div className="text-[10px] text-gray-500 font-medium">SECCIONES</div>
          </div>
          <div className="bg-[#E8F5EE] rounded-lg px-6 py-4 text-center">
            <div className="text-2xl font-bold text-[#2D8D68]">{result.itemsCount}</div>
            <div className="text-[10px] text-gray-500 font-medium">ITEMS</div>
          </div>
        </div>

        <div className="flex justify-center gap-3">
          <button
            onClick={() => navigate(`/app/budgets/${result.budgetId}/editor`)}
            className="bg-[#2D8D68] hover:bg-[#1B5E4B] text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition-colors"
          >
            Abrir en Editor
          </button>
          <button
            onClick={() => navigate('/app/dashboard')}
            className="bg-white border text-gray-600 px-6 py-2.5 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          >
            Volver al Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Shared: OptionCard ─────────────────────────────────────────────────────

function OptionCard({
  active,
  onClick,
  icon,
  title,
  description,
}: {
  active: boolean
  onClick: () => void
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-lg border-2 text-left transition-all ${
        active
          ? 'border-[#2D8D68] bg-[#E8F5EE]'
          : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
    >
      <div
        className={`mb-2 ${active ? 'text-[#2D8D68]' : 'text-gray-400'}`}
      >
        {icon}
      </div>
      <div className={`text-sm font-semibold ${active ? 'text-[#143D34]' : 'text-gray-700'}`}>
        {title}
      </div>
      <div className="text-xs text-gray-500 mt-0.5">{description}</div>
    </button>
  )
}
