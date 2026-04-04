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
    <div className="grid grid-cols-5 gap-2 p-3 border-b bg-gray-50">
      <div className="bg-white rounded-lg p-2 border text-center">
        <div className="text-[10px] text-gray-400">Materiales</div>
        <div className="font-bold text-sm text-gray-800">{fmtCurrency(mat)}</div>
      </div>
      <div className="bg-white rounded-lg p-2 border text-center">
        <div className="text-[10px] text-gray-400">Mano de Obra</div>
        <div className="font-bold text-sm text-gray-800">{fmtCurrency(mo)}</div>
      </div>
      <div className="bg-white rounded-lg p-2 border text-center">
        <div className="text-[10px] text-blue-600">Directo</div>
        <div className="font-bold text-sm text-blue-700">{fmtCurrency(directo)}</div>
      </div>
      <div className="bg-white rounded-lg p-2 border text-center">
        <div className="text-[10px] text-orange-500">
          Indirecto{indirectoPct ? ` (${indirectoPct}%)` : ''}
        </div>
        <div className="font-bold text-sm text-orange-600">{fmtCurrency(indirecto)}</div>
      </div>
      <div className="bg-[#E8F5EE] rounded-lg p-2 border border-[#2D8D68] text-center">
        <div className="text-[10px] text-[#1B5E4B]">Neto</div>
        <div className="font-bold text-sm text-[#2D8D68]">{fmtCurrency(neto)}</div>
      </div>
    </div>
  )
}
