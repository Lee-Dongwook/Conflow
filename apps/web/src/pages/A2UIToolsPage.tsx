/**
 * `/w/:workspaceUuid/a2ui/tools` — Tool catalog + invoke surface.
 *
 * Two-pane layout: catalog (left) + selected Tool's invoke form (right).
 * When nothing is selected, the right pane shows guidance. Mobile
 * stacks vertically.
 */

import { useState } from 'react'

import { ToolInvokeForm } from 'app/features/a2ui-tool-invoke'
import type { ToolCatalogEntry } from 'app/shared/types/api'
import { ToolCatalog } from 'app/widgets/a2ui-tool-catalog'

export const A2UIToolsPage = () => {
  const [selected, setSelected] = useState<ToolCatalogEntry | null>(null)

  return (
    <div className="space-y-2">
      <header>
        <h1 className="text-xl font-semibold text-slate-900">A2UI Tools</h1>
        <p className="mt-1 text-xs text-slate-500">
          추후에 개발될 기능으로, 사용자가 원하는 형태로 글을 작성하면 AI가 분석하여
          결과에 맞는 문서를 생성합니다.
        </p>
      </header>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-[20rem_1fr]">
        <ToolCatalog
          onSelect={(tool) => setSelected(tool)}
          selectedId={selected?.id ?? null}
        />
        <div>
          {selected ? (
            <ToolInvokeForm tool={selected} />
          ) : (
            <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center text-sm text-slate-600">
              왼쪽에서 Tool 을 선택하면 호출 폼이 나타납니다.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
