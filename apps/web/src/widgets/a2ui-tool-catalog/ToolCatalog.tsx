/**
 * ToolCatalog widget — Tool cards filterable by domain.
 *
 * Each card shows: id (mono), description, tier/permission badges, and
 * a "cross-domain" pill for the composition Tools. Clicking a card
 * raises `onSelect` so the host page can open the invoke form.
 */

import { isAPIError } from '@conflow/core'
import { useMemo, useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useToolCatalog } from 'app/entities/a2ui'
import type { ToolCatalogEntry } from 'app/shared/types/api'

interface ToolCatalogProps {
  readonly onSelect?: (tool: ToolCatalogEntry) => void
  readonly selectedId?: string | null
}

const TIER_PILL: Record<string, string> = {
  free: 'bg-slate-100 text-slate-700',
  team: 'bg-blue-100 text-blue-800',
  business: 'bg-indigo-100 text-indigo-800',
  enterprise: 'bg-purple-100 text-purple-800',
}

const PERMISSION_PILL: Record<string, string> = {
  member: 'bg-slate-100 text-slate-700',
  writer: 'bg-amber-100 text-amber-800',
  admin: 'bg-rose-100 text-rose-800',
}

export const ToolCatalog = ({ onSelect, selectedId }: ToolCatalogProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const query = useToolCatalog(workspaceUuid)
  const [domainFilter, setDomainFilter] = useState<string>('')

  const domains = useMemo(() => {
    const set = new Set<string>()
    query.data?.tools.forEach((t) => set.add(t.domain))
    return Array.from(set).sort()
  }, [query.data])

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
  }
  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : 'Tool 카탈로그를 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }

  const filtered = domainFilter
    ? query.data.tools.filter((t) => t.domain === domainFilter)
    : query.data.tools

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-500">현재 워크스페이스 tier 에서 가능한 Tool</span>
        <span className="font-mono text-slate-700">
          ({query.data.tools.length}개)
        </span>
        <select
          value={domainFilter}
          onChange={(e) => setDomainFilter(e.target.value)}
          className="ml-auto rounded-md border border-slate-300 px-2 py-1 shadow-sm focus:border-slate-500 focus:outline-none"
        >
          <option value="">전체 도메인</option>
          {domains.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>
      {filtered.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center text-sm text-slate-600">
          조건에 맞는 Tool 이 없습니다.
        </div>
      ) : (
        <ul className="space-y-2">
          {filtered.map((tool) => {
            const selected = selectedId === tool.id
            return (
              <li key={tool.id}>
                <button
                  type="button"
                  onClick={onSelect ? () => onSelect(tool) : undefined}
                  disabled={!onSelect}
                  className={`block w-full rounded-lg border p-4 text-left shadow-sm transition disabled:cursor-default ${
                    selected
                      ? 'border-slate-900 bg-slate-50'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="font-mono text-sm font-semibold text-slate-900">
                      {tool.id}
                    </h3>
                    {tool.cross_domain && (
                      <span className="shrink-0 rounded-full bg-fuchsia-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-fuchsia-800">
                        cross-domain
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-slate-600">{tool.description}</p>
                  <div className="mt-2 flex flex-wrap gap-1 text-[10px]">
                    <span
                      className={`rounded px-1.5 py-0.5 font-semibold uppercase tracking-wide ${TIER_PILL[tool.min_tier] ?? TIER_PILL.free}`}
                    >
                      tier ≥ {tool.min_tier}
                    </span>
                    <span
                      className={`rounded px-1.5 py-0.5 font-semibold uppercase tracking-wide ${PERMISSION_PILL[tool.permission_required] ?? PERMISSION_PILL.member}`}
                    >
                      {tool.permission_required}
                    </span>
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 font-semibold uppercase tracking-wide text-slate-600">
                      phase {tool.phase}
                    </span>
                  </div>
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
