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
    <div className="flex gap-1 p-1 rounded-xl bg-gray-100/80">
      {MODES.map(({ key, label, icon: Icon }) => {
        const active = mode === key
        return (
          <button
            key={key}
            onClick={() => onChange(key)}
            className={`flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-semibold rounded-lg transition-all duration-200 flex-1 justify-center ${
              active
                ? 'bg-white text-[#143D34] shadow-sm'
                : 'text-gray-400 hover:text-gray-600 hover:bg-white/50'
            }`}
          >
            <Icon size={12} className={active ? 'text-[#2D8D68]' : ''} />
            {label}
          </button>
        )
      })}
    </div>
  )
}
