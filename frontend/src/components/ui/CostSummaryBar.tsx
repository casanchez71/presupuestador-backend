import { fmtCurrency } from '../../lib/format'

interface Props {
  mat: number
  mo: number
  directo: number
  indirecto: number
  beneficio?: number
  impuestos?: number
  neto: number
  iva?: number
  totalFinal?: number
  indirectoPct?: number
}

export default function CostSummaryBar({
  mat,
  mo,
  directo,
  indirecto,
  beneficio = 0,
  impuestos = 0,
  neto,
  iva = 0,
  totalFinal,
  indirectoPct,
}: Props) {
  const showExtended = totalFinal != null && totalFinal > 0

  return (
    <div
      className={`grid gap-2 p-4 border-b bg-gradient-to-b from-white to-gray-50/50 ${
        showExtended ? 'grid-cols-7' : 'grid-cols-5'
      }`}
    >
      {/* Materiales */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-blue-100 bg-gradient-to-br from-blue-50 to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-blue-400 to-blue-200" />
        <div className="text-[10px] font-semibold text-blue-500 uppercase tracking-wider mb-1">Materiales</div>
        <div className="font-bold text-sm text-blue-800 tabular-nums">{fmtCurrency(mat)}</div>
      </div>

      {/* Mano de Obra */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-purple-100 bg-gradient-to-br from-purple-50 to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-purple-400 to-purple-200" />
        <div className="text-[10px] font-semibold text-purple-500 uppercase tracking-wider mb-1">Mano de Obra</div>
        <div className="font-bold text-sm text-purple-800 tabular-nums">{fmtCurrency(mo)}</div>
      </div>

      {/* Directo */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-[#2D8D68]/20 bg-gradient-to-br from-[#E8F5EE] to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#2D8D68] to-[#2D8D68]/40" />
        <div className="text-[10px] font-semibold text-[#2D8D68] uppercase tracking-wider mb-1">Directo</div>
        <div className="font-bold text-sm text-[#143D34] tabular-nums">{fmtCurrency(directo)}</div>
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
        <div className="font-bold text-sm text-[#E8663C] tabular-nums">{fmtCurrency(indirecto)}</div>
      </div>

      {/* Beneficio — only in extended mode; otherwise Neto takes its place */}
      {showExtended && (
        <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-sm border border-amber-200 bg-gradient-to-br from-amber-50 to-white">
          <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-amber-400 to-amber-200" />
          <div className="text-[10px] font-semibold text-amber-600 uppercase tracking-wider mb-1">Beneficio</div>
          <div className="font-bold text-sm text-amber-800 tabular-nums">{fmtCurrency(beneficio)}</div>
        </div>
      )}

      {/* Neto */}
      <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-md border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white">
        <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-emerald-500 to-emerald-300" />
        <div className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider mb-1">Neto</div>
        <div className="font-extrabold text-sm text-emerald-900 tabular-nums">{fmtCurrency(neto)}</div>
      </div>

      {/* Total Final — only in extended mode */}
      {showExtended && (
        <div className="relative overflow-hidden rounded-xl p-3 text-center shadow-md border border-[#143D34]/30 bg-gradient-to-br from-[#143D34] to-[#2D8D68]">
          <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#E0A33A] to-[#E0A33A]/60" />
          <div className="text-[10px] font-bold text-[#E0A33A] uppercase tracking-wider mb-1">Total c/IVA</div>
          <div className="font-extrabold text-sm text-white tabular-nums">{fmtCurrency(totalFinal ?? 0)}</div>
        </div>
      )}
    </div>
  )
}
