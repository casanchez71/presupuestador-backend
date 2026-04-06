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
    <div className="grid grid-cols-5 gap-3 p-4 border-b bg-gradient-to-b from-white to-gray-50/50">
      {/* Materiales */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-blue-100 bg-gradient-to-br from-blue-50 to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-blue-400 to-blue-200" />
        <div className="text-[10px] font-semibold text-blue-500 uppercase tracking-wider mb-1">Materiales</div>
        <div className="font-bold text-lg text-blue-800 tabular-nums">{fmtCurrency(mat)}</div>
      </div>

      {/* Mano de Obra */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-purple-100 bg-gradient-to-br from-purple-50 to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-purple-400 to-purple-200" />
        <div className="text-[10px] font-semibold text-purple-500 uppercase tracking-wider mb-1">Mano de Obra</div>
        <div className="font-bold text-lg text-purple-800 tabular-nums">{fmtCurrency(mo)}</div>
      </div>

      {/* Directo */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-[#2D8D68]/20 bg-gradient-to-br from-[#E8F5EE] to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#2D8D68] to-[#2D8D68]/40" />
        <div className="text-[10px] font-semibold text-[#2D8D68] uppercase tracking-wider mb-1">Directo</div>
        <div className="font-bold text-lg text-[#143D34] tabular-nums">{fmtCurrency(directo)}</div>
      </div>

      {/* Indirecto */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-[#E8663C]/20 bg-gradient-to-br from-orange-50 to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#E8663C] to-[#E8663C]/40" />
        <div className="text-[10px] font-semibold text-[#E8663C] uppercase tracking-wider mb-1 flex items-center justify-center gap-1">
          Indirecto
          {indirectoPct ? (
            <span className="bg-[#E8663C]/10 text-[#E8663C] text-[9px] px-1.5 py-0 rounded-full font-bold">
              {indirectoPct}%
            </span>
          ) : null}
        </div>
        <div className="font-bold text-lg text-[#E8663C] tabular-nums">{fmtCurrency(indirecto)}</div>
      </div>

      {/* Neto — hero card */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-md border border-[#E0A33A]/30 bg-gradient-to-br from-[#FDF6E3] via-[#FEF9EE] to-white">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[#E0A33A] to-[#E0A33A]/50" />
        <div className="text-[10px] font-bold text-[#9D7A32] uppercase tracking-wider mb-1">Neto</div>
        <div className="font-extrabold text-xl text-[#9D7A32] tabular-nums">{fmtCurrency(neto)}</div>
      </div>
    </div>
  )
}
