import { useState, useRef, useEffect, useCallback } from 'react'
import { MoreVertical, Pencil, Loader2 } from 'lucide-react'
import type { BudgetItem } from '../../types'
import { fmtCurrency, fmtNumber } from '../../lib/format'

interface Props {
  items: BudgetItem[]
  onEditItem?: (itemId: string, field: string, oldValue: number, newValue: number) => Promise<void>
}

type EditableField = 'cantidad' | 'mat_unitario' | 'mo_unitario'

const EDITABLE_FIELDS: EditableField[] = ['cantidad', 'mat_unitario', 'mo_unitario']

interface CellState {
  saving: boolean
  justSaved: boolean
  error: string | null
  hasAudit: boolean
}

export default function DataTable({ items, onEditItem }: Props) {
  // Detect if any item has the extended columns populated
  const hasImpuestos = items.some((i) => (i.impuestos_total ?? 0) > 0)
  const hasIva = items.some((i) => (i.iva_total ?? 0) > 0)
  const hasTotalFinal = items.some((i) => (i.total_final ?? 0) > 0)
  const [editing, setEditing] = useState<{ id: string; field: EditableField } | null>(null)
  const [editValue, setEditValue] = useState('')
  const [cellStates, setCellStates] = useState<Record<string, CellState>>({})
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus input when editing starts
  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [editing])

  const cellKey = (itemId: string, field: string) => `${itemId}:${field}`

  const getCellState = (itemId: string, field: string): CellState =>
    cellStates[cellKey(itemId, field)] ?? { saving: false, justSaved: false, error: null, hasAudit: false }

  const updateCellState = useCallback((itemId: string, field: string, partial: Partial<CellState>) => {
    setCellStates((prev) => ({
      ...prev,
      [cellKey(itemId, field)]: { ...getCellState(itemId, field), ...partial },
    }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cellStates])

  function startEdit(item: BudgetItem, field: EditableField) {
    if (!onEditItem) return
    const value = item[field]
    setEditing({ id: item.id, field })
    setEditValue(value !== undefined && value !== null ? String(value) : '')
  }

  function cancelEdit() {
    setEditing(null)
    setEditValue('')
  }

  async function commitEdit(item: BudgetItem) {
    if (!editing || !onEditItem) return

    const { field } = editing
    const newValue = parseFloat(editValue)
    const oldValue = item[field] ?? 0

    // Cancel if same value or invalid
    if (isNaN(newValue) || newValue === oldValue) {
      cancelEdit()
      return
    }

    const key = { id: item.id, field }
    setEditing(null)
    setEditValue('')
    updateCellState(item.id, field, { saving: true, error: null })

    try {
      await onEditItem(item.id, field, oldValue, newValue)
      updateCellState(item.id, field, { saving: false, justSaved: true, hasAudit: true })
      // Clear the green flash after 1.5 seconds
      setTimeout(() => {
        updateCellState(item.id, field, { justSaved: false })
      }, 1500)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al guardar'
      updateCellState(key.id, key.field, { saving: false, error: message })
      // Clear error after 4 seconds
      setTimeout(() => {
        updateCellState(key.id, key.field, { error: null })
      }, 4000)
    }
  }

  const totals = items.reduce(
    (acc, item) => ({
      directo: acc.directo + item.directo_total,
      indirecto: acc.indirecto + item.indirecto_total,
      beneficio: acc.beneficio + (item.beneficio_total ?? 0),
      neto: acc.neto + item.neto_total,
      impuestos: acc.impuestos + (item.impuestos_total ?? 0),
      iva: acc.iva + (item.iva_total ?? 0),
      totalFinal: acc.totalFinal + (item.total_final ?? 0),
    }),
    { directo: 0, indirecto: 0, beneficio: 0, neto: 0, impuestos: 0, iva: 0, totalFinal: 0 },
  )

  function renderEditableCell(item: BudgetItem, field: EditableField, format: (v: number) => string) {
    const isEditing = editing?.id === item.id && editing?.field === field
    const state = getCellState(item.id, field)
    const value = item[field]

    if (isEditing) {
      return (
        <td className="px-3 py-2">
          <input
            ref={inputRef}
            type="number"
            step="any"
            className="w-full max-w-[100px] ml-auto block border-2 border-[#2D8D68] rounded-lg px-2 py-1 text-right text-xs bg-white outline-none shadow-sm [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onBlur={() => commitEdit(item)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') commitEdit(item)
              if (e.key === 'Escape') cancelEdit()
            }}
          />
        </td>
      )
    }

    // Determine cell visual state
    let cellClass = 'px-3 py-2.5 cost-cell relative group'
    let borderStyle = ''

    if (state.error) {
      borderStyle = 'border border-red-400 rounded-lg'
    } else if (state.justSaved) {
      cellClass += ' animate-save-flash'
    }

    if (onEditItem) {
      cellClass += ' cursor-pointer'
    }

    return (
      <td
        className={cellClass}
        onClick={() => startEdit(item, field)}
        title={state.error ?? undefined}
      >
        <span className={`inline-flex items-center gap-1 ${borderStyle} ${onEditItem ? 'editable-cell' : ''}`}>
          {state.saving ? (
            <Loader2 size={10} className="animate-spin text-[#2D8D68]" />
          ) : null}
          {value !== undefined && value !== null ? format(value) : '--'}
          {onEditItem && !state.saving ? (
            <Pencil size={9} className="text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity" />
          ) : null}
        </span>
        {state.hasAudit && !state.justSaved ? (
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-blue-500" title="Editado manualmente" />
        ) : null}
      </td>
    )
  }

  return (
    <div className="overflow-auto max-h-full">
      {/* Save flash animation */}
      <style>{`
        @keyframes saveFlash {
          0% { background-color: transparent; }
          20% { background-color: rgb(187 247 208); }
          100% { background-color: transparent; }
        }
        .animate-save-flash {
          animation: saveFlash 1.5s ease-out;
        }
      `}</style>
      <table className="w-full text-xs">
        <thead className="sticky top-0 z-10">
          <tr className="bg-[#E8F5EE] text-[#143D34]">
            <th className="px-3 py-2.5 text-left font-semibold text-[11px] tracking-wide">Codigo</th>
            <th className="px-3 py-2.5 text-left font-semibold text-[11px] tracking-wide">Descripcion</th>
            <th className="px-3 py-2.5 text-left font-semibold text-[11px] tracking-wide">Unidad</th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide">
              Cant.
              {onEditItem ? <Pencil size={8} className="inline ml-1 text-[#143D34]/40" /> : null}
            </th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide">
              MAT Unit
              {onEditItem ? <Pencil size={8} className="inline ml-1 text-[#143D34]/40" /> : null}
            </th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide">
              MO Unit
              {onEditItem ? <Pencil size={8} className="inline ml-1 text-[#143D34]/40" /> : null}
            </th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">Directo</th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">Indirecto</th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">Beneficio</th>
            <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">Neto</th>
            {hasImpuestos && <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">Impuestos</th>}
            {hasIva && <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">IVA</th>}
            {hasTotalFinal && <th className="px-3 py-2.5 text-right font-semibold text-[11px] tracking-wide text-[#143D34]/70">Total Final</th>}
            <th className="px-3 py-2.5 w-6" />
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr
              key={item.id}
              className={`border-b border-gray-100 hover:bg-[#E8F5EE]/30 transition-colors duration-150 ${
                idx % 2 === 1 ? 'bg-gray-50/50' : 'bg-white'
              }`}
            >
              <td className="px-3 py-2.5 font-mono text-[10px] text-gray-400">{item.code}</td>
              <td className="px-3 py-2.5">
                <span className="font-medium text-gray-800">{item.description}</span>
              </td>
              <td className="px-3 py-2.5 text-gray-400 text-[10px] uppercase">{item.unidad}</td>
              {renderEditableCell(item, 'cantidad', (v) => fmtNumber(v, 0))}
              {renderEditableCell(item, 'mat_unitario', fmtCurrency)}
              {renderEditableCell(item, 'mo_unitario', fmtCurrency)}
              {/* Calculated columns — read-only */}
              <td className="px-3 py-2.5 cost-cell font-semibold text-blue-700/80">
                {fmtCurrency(item.directo_total)}
              </td>
              <td className="px-3 py-2.5 cost-cell text-gray-400">
                {fmtCurrency(item.indirecto_total)}
              </td>
              <td className="px-3 py-2.5 cost-cell text-amber-600">
                {fmtCurrency(item.beneficio_total ?? 0)}
              </td>
              <td className="px-3 py-2.5 cost-cell font-bold text-[#143D34]">
                {fmtCurrency(item.neto_total)}
              </td>
              {hasImpuestos && (
                <td className="px-3 py-2.5 cost-cell text-orange-600">
                  {fmtCurrency(item.impuestos_total ?? 0)}
                </td>
              )}
              {hasIva && (
                <td className="px-3 py-2.5 cost-cell text-blue-600">
                  {fmtCurrency(item.iva_total ?? 0)}
                </td>
              )}
              {hasTotalFinal && (
                <td className="px-3 py-2.5 cost-cell font-extrabold text-[#143D34]">
                  {fmtCurrency(item.total_final ?? 0)}
                </td>
              )}
              <td className="px-3 py-2.5 text-center text-gray-300 cursor-pointer hover:text-gray-500 transition-colors">
                <MoreVertical size={14} />
              </td>
            </tr>
          ))}
        </tbody>
        {items.length > 0 && (
          <tfoot className="sticky bottom-0 z-10">
            <tr className="bg-[#E8F5EE] font-semibold text-xs border-t border-[#2D8D68]/20">
              <td colSpan={6} className="px-3 py-3 text-right text-gray-400 uppercase text-[10px] tracking-wider">Total seccion</td>
              <td className="px-3 py-3 cost-cell text-blue-700 font-bold">{fmtCurrency(totals.directo)}</td>
              <td className="px-3 py-3 cost-cell text-[#E8663C] font-bold">{fmtCurrency(totals.indirecto)}</td>
              <td className="px-3 py-3 cost-cell text-amber-600 font-bold">{fmtCurrency(totals.beneficio)}</td>
              <td className="px-3 py-3 cost-cell text-[#143D34] font-extrabold text-sm">{fmtCurrency(totals.neto)}</td>
              {hasImpuestos && <td className="px-3 py-3 cost-cell text-orange-600 font-bold">{fmtCurrency(totals.impuestos)}</td>}
              {hasIva && <td className="px-3 py-3 cost-cell text-blue-600 font-bold">{fmtCurrency(totals.iva)}</td>}
              {hasTotalFinal && <td className="px-3 py-3 cost-cell text-[#143D34] font-extrabold text-sm">{fmtCurrency(totals.totalFinal)}</td>}
              <td />
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  )
}
