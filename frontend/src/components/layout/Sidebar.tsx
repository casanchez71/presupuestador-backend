import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutGrid, Clock, Edit3, ClipboardList, BarChart2, Layers,
  Download, Upload, Settings, BookOpen, RefreshCw, LogOut,
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

const SOLE_LOGO = (
  <svg width="28" height="28" viewBox="0 0 512 512" fill="none">
    <path
      d="M256 72C170.947 72 102 140.947 102 226C102 311.053 170.947 380 256 380C316.134 380 368.215 345.533 393.832 295.282"
      stroke="#E0A33A" strokeWidth="28" strokeLinecap="round"
    />
    <circle cx="390" cy="179" r="28" fill="#E0A33A" />
    <path
      d="M251 334V250C251 221.768 273.768 199 302 199H319"
      stroke="#143D34" strokeWidth="24" strokeLinecap="round" strokeLinejoin="round"
    />
    <path
      d="M251 280C216.14 280 188 251.86 188 217V206C222.86 206 251 234.14 251 269V280Z"
      fill="#2D8D68"
    />
    <path
      d="M257 248C257 209.34 288.34 178 327 178H338C338 216.66 306.66 248 268 248H257Z"
      fill="#2D8D68"
    />
  </svg>
)

function NavItem({
  to, icon, label, end,
}: {
  to: string
  icon: React.ReactNode
  label: string
  end?: boolean
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-center gap-2.5 px-3 py-2 rounded text-[13px] transition-all border-l-[3px] ${
          isActive
            ? 'bg-[#E8F5EE] border-l-[#2D8D68] text-[#143D34] font-semibold'
            : 'border-l-transparent text-gray-500 hover:bg-[#F0FAF5]'
        }`
      }
    >
      {icon}
      {label}
    </NavLink>
  )
}

export default function Sidebar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  const orgName = (user?.user_metadata?.org_name as string) || 'YOPACTO SAS'
  const initials = orgName.slice(0, 1).toUpperCase()

  return (
    <aside className="w-56 bg-white border-r flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="px-4 py-3 flex items-center gap-2 border-b">
        {SOLE_LOGO}
        <div>
          <div className="text-[#143D34] font-extrabold text-xs tracking-wide leading-tight">SOLE</div>
          <div className="text-[#9D7A32] text-[8px] tracking-[0.2em] font-bold">IN THE GROW</div>
        </div>
      </div>

      {/* Operación Semanal */}
      <div className="px-3 pt-3 pb-1">
        <div className="text-[10px] font-bold text-gray-400 tracking-wider mb-1.5">OPERACIÓN SEMANAL</div>
      </div>
      <nav className="px-2 space-y-0.5">
        <NavItem to="#" icon={<LayoutGrid size={15} />} label="Iniciar" />
        <NavItem to="#" icon={<Clock size={15} />} label="SOLE HQ" />
      </nav>

      {/* Presupuestador PRO */}
      <div className="px-3 pt-4 pb-1">
        <div className="text-[10px] font-bold text-[#2D8D68] tracking-wider mb-1.5 flex items-center gap-1">
          <span className="w-1.5 h-1.5 bg-[#2D8D68] rounded-full" />
          PRESUPUESTADOR PRO
        </div>
      </div>
      <nav className="px-2 space-y-0.5 text-[13px] flex-1 overflow-y-auto">
        <NavItem to="/app/dashboard" end icon={<LayoutGrid size={15} />} label="Mis Presupuestos" />
        <NavItem to="/app/budgets/1/editor" icon={<Edit3 size={15} />} label="Editor de Obra" />
        <NavItem to="/app/budgets/1/item/1" icon={<ClipboardList size={15} />} label="Detalle de Ítem" />
        <NavItem to="/app/budgets/1/analysis" icon={<BarChart2 size={15} />} label="Análisis" />
        <NavItem to="/app/budgets/1/ai" icon={<Layers size={15} />} label="IA + Planos" />
        <NavItem to="/app/import" icon={<Upload size={15} />} label="Importar Excel" />
        <NavItem to="/app/budgets/1/export" icon={<Download size={15} />} label="Exportar" />

        <div className="border-t my-2 mx-1" />
        <div className="text-[10px] font-bold text-gray-400 tracking-wider mb-1 px-1">CONFIGURACIÓN</div>
        <NavItem to="/app/settings/markups" icon={<Settings size={15} />} label="Cadena de Markups" />
        <NavItem to="/app/catalogs" icon={<BookOpen size={15} />} label="Catálogos" />
        <NavItem to="/app/budgets/1/versions" icon={<RefreshCw size={15} />} label="Versiones" />
      </nav>

      {/* User */}
      <div className="p-3 border-t flex items-center gap-2">
        <div className="w-8 h-8 bg-[#2D8D68] rounded-full flex items-center justify-center font-bold text-white text-[10px]">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-gray-800 truncate">{orgName}</div>
          <div className="text-[10px] text-[#2D8D68] font-medium">ADMIN</div>
        </div>
      </div>
      <button
        onClick={handleSignOut}
        className="px-4 py-2 text-[11px] text-gray-400 hover:text-gray-600 flex items-center gap-1.5 border-t transition-colors"
      >
        <LogOut size={13} />
        CERRAR SESIÓN
      </button>
    </aside>
  )
}
