import { useState } from 'react'
import { MoreVertical } from 'lucide-react'
import type { BudgetItem } from '../../types'
import { fmtCurrency, fmtNumber } from '../../lib/format'

interface Props {
  items: BudgetItem[]
  onEdit?: (item: BudgetItem, field: string, value: string) => void
}

export default function DataTable({ items, onEdit }: Props) {
  const [editing, setEditing] = useState<{ id: string; field: string } | null>(null)
  const [editValue, setEditValue] = useState('')

  const totals = items.reduce(
    (acc, item) => ({
      directo: acc.directo + item.directo_total,
      indirecto: acc.indirecto + item.indirecto_total,
      neto: acc.neto + item.neto_total,
    }),
    { directo: 0, indirecto: 0, neto: 0 },
  )

  function startEdit(item: BudgetItem, field: string, value: string) {
    setEditing({ id: item.id, field })
    setEditValue(value)
  }

  function commitEdit(item: BudgetItem) {
    if (!editing) return
    onEdit?.(item, editing.field, editValue)
    setEditing(null)
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead className="bg-gray-100 text-gray-600">
          <tr>
            <th className="px-2 py-2 text-left font-semibold">Código</th>
            <th className="px-2 py-2 text-left font-semibold">Descripción</th>
            <th className="px-2 py-2 text-left font-semibold">Unidad</th>
            <th className="px-2 py-2 text-right font-semibold">Cant.</th>
            <th className="px-2 py-2 text-right font-semibold">MAT Unit</th>
            <th className="px-2 py-2 text-right font-semibold">MO Unit</th>
            <th className="px-2 py-2 text-right font-semibold">Directo</th>
            <th className="px-2 py-2 text-right font-semibold">Indirecto</th>
            <th className="px-2 py-2 text-right font-semibold">Neto</th>
            <th className="px-2 py-2 w-6" />
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b hover:bg-gray-50">
              <td className="px-2 py-2 font-mono text-gray-400">{item.code}</td>
              <td className="px-2 py-2">
                {editing?.id === item.id && editing.field === 'description' ? (
                  <input
                    autoFocus
                    className="w-full border-b border-[#2D8D68] outline-none bg-transparent"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onBlur={() => commitEdit(item)}
                    onKeyDown={(e) => e.key === 'Enter' && commitEdit(item)}
                  />
                ) : (
                  <span
                    className="font-medium text-gray-800 editable cursor-text"
                    onClick={() => startEdit(item, 'description', item.description || '')}
                  >
                    {item.description}
                  </span>
                )}
              </td>
              <td className="px-2 py-2 text-gray-500">{item.unidad}</td>
              <td className="px-2 py-2 cost-cell">
                {editing?.id === item.id && editing.field === 'cantidad' ? (
                  <input
                    autoFocus
                    className="w-16 border-b border-[#2D8D68] outline-none bg-transparent text-right"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onBlur={() => commitEdit(item)}
                    onKeyDown={(e) => e.key === 'Enter' && commitEdit(item)}
                  />
                ) : (
                  <span
                    className="editable cursor-text"
                    onClick={() => startEdit(item, 'cantidad', String(item.cantidad ?? ''))}
                  >
                    {item.cantidad !== undefined ? fmtNumber(item.cantidad, 0) : '—'}
                  </span>
                )}
              </td>
              <td className="px-2 py-2 cost-cell">{fmtCurrency(item.mat_unitario)}</td>
              <td className="px-2 py-2 cost-cell">{fmtCurrency(item.mo_unitario)}</td>
              <td className="px-2 py-2 cost-cell font-medium text-blue-700">{fmtCurrency(item.directo_total)}</td>
              <td className="px-2 py-2 cost-cell text-gray-400">{fmtCurrency(item.indirecto_total)}</td>
              <td className="px-2 py-2 cost-cell font-bold text-[#2D8D68]">{fmtCurrency(item.neto_total)}</td>
              <td className="px-2 py-2 text-center text-gray-300 cursor-pointer hover:text-gray-500">
                <MoreVertical size={14} />
              </td>
            </tr>
          ))}
        </tbody>
        {items.length > 0 && (
          <tfoot className="bg-gray-50 font-semibold text-xs">
            <tr>
              <td colSpan={6} className="px-2 py-2 text-right text-gray-500">TOTAL</td>
              <td className="px-2 py-2 cost-cell text-blue-700">{fmtCurrency(totals.directo)}</td>
              <td className="px-2 py-2 cost-cell text-orange-600">{fmtCurrency(totals.indirecto)}</td>
              <td className="px-2 py-2 cost-cell text-[#2D8D68] font-bold">{fmtCurrency(totals.neto)}</td>
              <td />
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  )
}
