import { useNavigate } from 'react-router-dom'
import type { Budget } from '../../types'
import { fmtCurrency } from '../../lib/format'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Borrador', borrador: 'Borrador',
  active: 'Activo', activo: 'Activo',
  approved: 'Aprobado', aprobado: 'Aprobado',
  sent: 'Enviado', presentado: 'Enviado',
  review: 'En Revisión',
  archivado: 'Archivado',
}

const STATUS_STYLES: Record<string, string> = {
  activo: 'bg-[#E8F5EE] text-[#1B5E4B]', active: 'bg-[#E8F5EE] text-[#1B5E4B]',
  borrador: 'bg-amber-50 text-amber-700', draft: 'bg-amber-50 text-amber-700',
  presentado: 'bg-blue-50 text-blue-700', sent: 'bg-blue-50 text-blue-700',
  archivado: 'bg-gray-100 text-gray-500',
  approved: 'bg-green-50 text-green-700', aprobado: 'bg-green-50 text-green-700',
  review: 'bg-yellow-50 text-yellow-700',
}

const BAR_COLORS: Record<string, string> = {
  activo: 'bg-[#2D8D68]', active: 'bg-[#2D8D68]',
  borrador: 'bg-[#E0A33A]', draft: 'bg-[#E0A33A]',
  presentado: 'bg-blue-500', sent: 'bg-blue-500',
  archivado: 'bg-gray-300',
  approved: 'bg-green-500', aprobado: 'bg-green-500',
  review: 'bg-yellow-500',
}

interface Props {
  budget: Budget
  directTotal?: number
  netoTotal?: number
  subtitle?: string
  tags?: string[]
}

export default function BudgetCard({ budget, directTotal, netoTotal, subtitle, tags }: Props) {
  const navigate = useNavigate()
  const status = budget.status?.toLowerCase() || 'borrador'

  return (
    <div
      onClick={() => navigate(`/app/budgets/${budget.id}/editor`)}
      className="bg-white rounded-xl border hover:shadow-md transition cursor-pointer overflow-hidden"
    >
      <div className={`h-1 ${BAR_COLORS[status] ?? 'bg-gray-300'}`} />
      <div className="p-5">
        <div className="flex justify-between items-start mb-2">
          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${STATUS_STYLES[status] ?? 'bg-gray-100 text-gray-500'}`}>
            {STATUS_LABELS[status] || budget.status || 'Borrador'}
          </span>
          <span className="text-[10px] text-gray-400">
            {budget.source_file ? '✓ Excel' : 'Manual'}
          </span>
        </div>
        <h3 className="font-bold text-gray-900">{budget.name}</h3>
        {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
        {tags && tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5 text-[10px]">
            {tags.map((t) => (
              <span key={t} className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{t}</span>
            ))}
          </div>
        )}
        <div className="mt-4 pt-3 border-t flex justify-between items-end">
          <div>
            <div className="text-[10px] text-gray-400">Directo</div>
            <div className="font-semibold text-gray-800 text-sm">
              {directTotal !== undefined ? fmtCurrency(directTotal) : '—'}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-gray-400">Neto Total</div>
            <div className="font-bold text-[#2D8D68] text-lg">
              {netoTotal !== undefined ? fmtCurrency(netoTotal) : '—'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
