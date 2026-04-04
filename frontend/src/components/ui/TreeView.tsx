import { useState } from 'react'
import { ChevronRight, ChevronDown } from 'lucide-react'
import type { TreeNode } from '../../types'

interface Props {
  nodes: TreeNode[]
  selectedId?: string
  onSelect: (node: TreeNode) => void
  depth?: number
}

interface ItemProps {
  node: TreeNode
  selectedId?: string
  onSelect: (node: TreeNode) => void
  depth: number
}

function TreeItem({ node, selectedId, onSelect, depth }: ItemProps) {
  const children: TreeNode[] = (node.children ?? []) as TreeNode[]
  const hasChildren = children.length > 0
  const [open, setOpen] = useState(depth === 0)
  const isSelected = node.id === selectedId

  return (
    <div>
      <div
        onClick={() => {
          onSelect(node)
          if (hasChildren) setOpen(!open)
        }}
        className={`flex items-center gap-1 px-2 py-1.5 rounded cursor-pointer text-xs transition-colors ${
          isSelected
            ? 'bg-[#E8F5EE] text-[#143D34] font-semibold'
            : 'text-gray-600 hover:bg-gray-50'
        }`}
        style={{ paddingLeft: `${8 + depth * 12}px` }}
      >
        {hasChildren ? (
          <span className="text-gray-400 flex-shrink-0">
            {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </span>
        ) : (
          <span className="w-3 flex-shrink-0" />
        )}
        {depth > 0 && node.code && (
          <span className="font-mono text-[10px] text-gray-400 mr-1">{node.code}</span>
        )}
        <span className="truncate">{node.description ?? '(sin descripción)'}</span>
      </div>
      {hasChildren && open && (
        <div>
          {children.map((child) => (
            <TreeItem
              key={child.id}
              node={child}
              selectedId={selectedId}
              onSelect={onSelect}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function TreeView({ nodes, selectedId, onSelect, depth = 0 }: Props) {
  return (
    <div className="space-y-0.5 text-xs">
      {nodes.map((node) => (
        <TreeItem
          key={node.id}
          node={node}
          selectedId={selectedId}
          onSelect={onSelect}
          depth={depth}
        />
      ))}
    </div>
  )
}
