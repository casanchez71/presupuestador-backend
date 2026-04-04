import { fmtCurrency } from '../../lib/format'

interface MarkupLink {
  label: string
  pct: number
}

interface Props {
  directo: number
  neto: number
  links: MarkupLink[]
}

export default function MarkupChainDisplay({ directo, neto, links }: Props) {
  return (
    <div className="px-3 py-1.5 bg-gray-50 border-b flex items-center gap-1 text-[10px] flex-wrap">
      <span className="bg-[#FFF0EB] text-[#9A3412] text-[10px] px-1.5 py-0.5 rounded font-semibold border border-orange-200">
        CADENA
      </span>
      <span className="font-medium text-gray-700">{fmtCurrency(directo)}</span>
      {links.map((link) => (
        <span key={link.label} className="text-gray-400">
          → +{link.label} {link.pct}%
        </span>
      ))}
      <span className="text-gray-400">→</span>
      <span className="font-bold text-[#2D8D68]">{fmtCurrency(neto)}</span>
    </div>
  )
}
