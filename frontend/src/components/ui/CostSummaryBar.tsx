import { fmtCurrency } from '../../lib/format'

interface Props {
  mat: number
  mo: number
  directo: number
  indirecto: number
  neto: number
  indirectoPct?: number
}

export default function CostSummaryBar({ mat, mo, directo, indirecto, neto, indirectoPct }: Props) {
  return (
    <div className="border-b bg-white">
      <div className="flex divide-x divide-gray-100">
        <div className="flex-1 px-4 py-2.5">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Materiales</div>
          <div className="text-sm font-bold text-gray-800 tabular-nums">{fmtCurrency(mat)}</div>
        </div>
        <div className="flex-1 px-4 py-2.5">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Mano de Obra</div>
          <div className="text-sm font-bold text-gray-800 tabular-nums">{fmtCurrency(mo)}</div>
        </div>
        <div className="flex-1 px-4 py-2.5 bg-blue-50/30">
          <div className="text-[10px] text-blue-500 uppercase tracking-wider">Directo</div>
          <div className="text-sm font-bold text-blue-700 tabular-nums">{fmtCurrency(directo)}</div>
        </div>
        <div className="flex-1 px-4 py-2.5 bg-orange-50/30">
          <div className="text-[10px] text-[#E8663C] uppercase tracking-wider flex items-center gap-1">
            Indirecto
            {indirectoPct ? (
              <span className="text-[9px] font-bold">{indirectoPct}%</span>
            ) : null}
          </div>
          <div className="text-sm font-bold text-[#E8663C] tabular-nums">{fmtCurrency(indirecto)}</div>
        </div>
        <div className="px-5 py-2.5 bg-[#2D8D68] text-white min-w-[120px]">
          <div className="text-[10px] text-[#E0A33A] uppercase tracking-wider">Neto</div>
          <div className="text-base font-bold tabular-nums">{fmtCurrency(neto)}</div>
        </div>
      </div>
    </div>
  )
}
