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
    <div className="px-4 py-3 bg-gradient-to-r from-gray-50 to-white border-b">
      <div className="flex items-center gap-1 text-[10px] uppercase tracking-wider text-gray-400 font-semibold mb-2">
        Cadena de Markups
      </div>
      <div className="flex items-center gap-0 flex-wrap">
        {/* Directo pill */}
        <div className="flex items-center gap-0">
          <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold bg-[#E8F5EE] text-[#143D34] border border-[#2D8D68]/20 shadow-sm">
            {fmtCurrency(directo)}
          </span>
        </div>

        {/* Markup links */}
        {links.map((link) => (
          <div key={link.label} className="flex items-center gap-0">
            {/* Arrow connector */}
            <svg width="24" height="12" viewBox="0 0 24 12" className="text-gray-300 flex-shrink-0">
              <line x1="0" y1="6" x2="18" y2="6" stroke="currentColor" strokeWidth="1.5" />
              <polygon points="16,2 22,6 16,10" fill="currentColor" />
            </svg>
            <span className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full text-[11px] font-semibold bg-white text-gray-600 border border-gray-200 shadow-sm hover:shadow transition-shadow">
              <span className="text-gray-400">+</span>
              {link.label}
              <span className="text-[10px] font-bold text-[#E8663C] bg-[#E8663C]/8 px-1.5 py-0 rounded-full">{link.pct}%</span>
            </span>
          </div>
        ))}

        {/* Final arrow to Neto */}
        <svg width="24" height="12" viewBox="0 0 24 12" className="text-[#E0A33A] flex-shrink-0">
          <line x1="0" y1="6" x2="18" y2="6" stroke="currentColor" strokeWidth="1.5" />
          <polygon points="16,2 22,6 16,10" fill="currentColor" />
        </svg>

        {/* Neto pill — hero */}
        <span className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-extrabold bg-gradient-to-r from-[#FDF6E3] to-[#FEF9EE] text-[#9D7A32] border border-[#E0A33A]/30 shadow-md">
          NETO {fmtCurrency(neto)}
        </span>
      </div>
    </div>
  )
}
