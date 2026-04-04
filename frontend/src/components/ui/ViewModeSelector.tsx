import { Layers, Building2, Package, Wrench } from 'lucide-react'
import type { ViewMode } from '../../lib/viewModes'

interface Props {
  mode: ViewMode
  onChange: (mode: ViewMode) => void
}

const MODES: { key: ViewMode; label: string; icon: typeof Layers; tooltip: string }[] = [
  { key: 'rubro', label: 'Rubro', icon: Layers, tooltip: 'Agrupa items por seccion de obra (Estructura, Albanileria, Instalaciones...)' },
  { key: 'piso', label: 'Piso', icon: Building2, tooltip: 'Agrupa items por planta del edificio (Subsuelo, PB, Pisos, Azotea)' },
  { key: 'material', label: 'Material', icon: Package, tooltip: 'Agrupa items por tipo de material (Hormigon, Acero, Ladrillos...)' },
  { key: 'tipo', label: 'Tipo', icon: Wrench, tooltip: 'Agrupa items por tipo de trabajo (Electricidad, Plomeria, Pintura...)' },
]

export default function ViewModeSelector({ mode, onChange }: Props) {
  return (
    <div className="flex gap-1 p-1 rounded-xl bg-gray-100/80">
      {MODES.map(({ key, label, icon: Icon, tooltip }) => {
        const active = mode === key
        return (
          <div key={key} className="relative flex-1 group">
            <button
              onClick={() => onChange(key)}
              className={`flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-semibold rounded-lg transition-all duration-200 w-full justify-center ${
                active
                  ? 'bg-white text-[#143D34] shadow-sm'
                  : 'text-gray-400 hover:text-gray-600 hover:bg-white/50'
              }`}
            >
              <Icon size={12} className={active ? 'text-[#2D8D68]' : ''} />
              {label}
            </button>
            <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2.5 py-1.5 bg-gray-800 text-white text-[10px] leading-tight rounded-lg whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 z-50 shadow-lg max-w-[200px] whitespace-normal text-center">
              {tooltip}
              <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800" />
            </div>
          </div>
        )
      })}
    </div>
  )
}
