interface IMarkdownRendererProps {
  readonly content: string
}

export const MarkdownRenderer = ({ content }: IMarkdownRendererProps) => {
  const lines = content.split('\n')
  const elements: React.ReactNode[] = []
  let inTable = false
  let tableRows: string[][] = []

  const flushTable = () => {
    if (tableRows.length === 0) return
    elements.push(
      <div key={`table-${elements.length}`} className="my-4 overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-slate-200 bg-slate-50">
              {tableRows[0]?.map((cell, i) => (
                <th key={i} className="px-3 py-2 text-left font-semibold text-slate-700">
                  {cell}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tableRows.slice(1).map((row, ri) => (
              <tr key={ri} className="border-b border-slate-100">
                {row.map((cell, ci) => (
                  <td key={ci} className="px-3 py-2 text-slate-600">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>,
    )
    tableRows = []
  }

  const renderInline = (text: string): React.ReactNode => {
    const parts = text.split(/(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\)|`[^`]+`)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        )
      }
      const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/)
      if (linkMatch) {
        return (
          <a
            key={i}
            href={linkMatch[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-teal-700 underline hover:text-teal-900"
          >
            {linkMatch[1]}
          </a>
        )
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="rounded bg-slate-100 px-1.5 py-0.5 text-sm text-slate-800">
            {part.slice(1, -1)}
          </code>
        )
      }
      return part
    })
  }

  for (const line of lines) {
    const trimmed = line.trim()

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      const cells = trimmed
        .slice(1, -1)
        .split('|')
        .map((c) => c.trim())
      if (cells.every((c) => /^[-:]+$/.test(c))) {
        inTable = true
        continue
      }
      tableRows.push(cells)
      inTable = true
      continue
    }

    if (inTable) {
      flushTable()
      inTable = false
    }

    if (trimmed === '' || trimmed === '---') {
      if (trimmed === '---') {
        elements.push(<hr key={elements.length} className="my-6 border-slate-200" />)
      }
      continue
    }

    if (trimmed.startsWith('# ')) {
      elements.push(
        <h1
          key={elements.length}
          className="mb-4 mt-8 text-2xl font-bold text-slate-900 first:mt-0"
        >
          {renderInline(trimmed.slice(2))}
        </h1>,
      )
    } else if (trimmed.startsWith('## ')) {
      elements.push(
        <h2 key={elements.length} className="mb-3 mt-6 text-xl font-semibold text-slate-900">
          {renderInline(trimmed.slice(3))}
        </h2>,
      )
    } else if (trimmed.startsWith('### ')) {
      elements.push(
        <h3 key={elements.length} className="mb-2 mt-4 text-lg font-semibold text-slate-800">
          {renderInline(trimmed.slice(4))}
        </h3>,
      )
    } else if (/^\d+\.\s/.test(trimmed)) {
      const text = trimmed.replace(/^\d+\.\s/, '')
      elements.push(
        <div
          key={elements.length}
          className="my-1 flex gap-2 pl-4 text-sm leading-relaxed text-slate-700"
        >
          <span className="shrink-0 text-slate-400">{trimmed.match(/^\d+/)?.[0]}.</span>
          <span>{renderInline(text)}</span>
        </div>,
      )
    } else if (trimmed.startsWith('- ')) {
      elements.push(
        <div
          key={elements.length}
          className="my-1 flex gap-2 pl-6 text-sm leading-relaxed text-slate-700"
        >
          <span className="shrink-0 text-slate-400">•</span>
          <span>{renderInline(trimmed.slice(2))}</span>
        </div>,
      )
    } else if (trimmed.startsWith('※')) {
      elements.push(
        <p key={elements.length} className="my-2 text-sm italic text-slate-500">
          {renderInline(trimmed)}
        </p>,
      )
    } else {
      elements.push(
        <p key={elements.length} className="my-2 text-sm leading-relaxed text-slate-700">
          {renderInline(trimmed)}
        </p>,
      )
    }
  }

  if (inTable) {
    flushTable()
  }

  return <div className="space-y-0">{elements}</div>
}
