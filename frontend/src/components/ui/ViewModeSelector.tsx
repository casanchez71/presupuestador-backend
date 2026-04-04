import { Layers, Building2, Package, Wrench } from 'lucide-react'
import type { ViewMode } from '../../lib/viewModes'

interface Props {
  mode: ViewMode
  onChange: (mode: ViewMode) => void
}

const MODES: { key: ViewMode; label: string; icon: typeof Layers }[] = [
  { key: 'rubro', label: 'Rubro', icon: Layers },
  { key: 'piso', label: 'Piso', icon: Building2 },
  { key: 'material', label: 'Material', icon: Package },
  { key: 'tipo', label: 'Tipo', icon: Wrench },
]

export default function ViewModeSelector({ mode, onChange }: Props) {
  return (
    <div className="flex rounded-lg border border-gray-200 overflow-hidden bg-white">
      {MODES.map(({ key, label, icon: Icon }) => {
        const active = mode === key
        return (
          <button
            key={key}
            onClick={() => onChange(key)}
            className={`flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-semibold transition-colors ${
              active
                ? 'bg-[#2D8D68] text-white'
                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
            } ${key !== 'rubro' ? 'border-l border-gray-200' : ''}`}
          >
            <Icon size={12} />
            {label}
          </button>
        )
      })}
    </div>
  )
}
