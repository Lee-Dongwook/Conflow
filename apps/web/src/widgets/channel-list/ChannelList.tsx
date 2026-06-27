/**
 * ChannelList widget — fetches & renders channels for the current workspace
 * as a scannable, chat-app-style list.
 *
 * Each row shows a type-colored icon chip, the channel name, its topic, and
 * the last-active time. Click handler is exposed for the host page to route
 * to the channel detail view. A "include archived" toggle filters the fetch.
 */

import { isAPIError } from '@conflow/core'
import { useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useChannels } from 'app/entities/channel'
import type { ChannelRead, ChannelType } from 'app/shared/types/api'

interface TypeStyle {
  readonly glyph: string
  readonly chip: string
  readonly label: string
}

const TYPE_STYLE: Record<ChannelType, TypeStyle> = {
  public: { glyph: '#', chip: 'bg-emerald-50 text-emerald-600', label: '공개' },
  private: { glyph: '🔒', chip: 'bg-amber-50 text-amber-600', label: '비공개' },
  dm: { glyph: '✉', chip: 'bg-sky-50 text-sky-600', label: 'DM' },
  external: { glyph: '🔗', chip: 'bg-violet-50 text-violet-600', label: '외부' },
}

const relativeTime = (iso: string): string => {
  try {
    const diffMs = Date.now() - new Date(iso).getTime()
    const min = Math.round(diffMs / 60000)
    if (min < 1) return '방금'
    if (min < 60) return `${min}분 전`
    const hr = Math.round(min / 60)
    if (hr < 24) return `${hr}시간 전`
    const day = Math.round(hr / 24)
    if (day < 7) return `${day}일 전`
    return new Intl.DateTimeFormat('ko-KR', { month: 'short', day: 'numeric' }).format(
      new Date(iso),
    )
  } catch {
    return ''
  }
}

interface ChannelListProps {
  readonly onChannelClick?: (channel: ChannelRead) => void
}

const ChannelRow = ({
  channel,
  onClick,
}: {
  readonly channel: ChannelRead
  readonly onClick: (() => void) | undefined
}) => {
  const style = TYPE_STYLE[channel.type]

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!onClick}
      className="group flex w-full items-center gap-3 rounded-lg border border-transparent px-3 py-2.5 text-left transition hover:border-slate-200 hover:bg-slate-50 disabled:cursor-default disabled:hover:border-transparent disabled:hover:bg-transparent"
    >
      <span
        className={`flex size-10 shrink-0 items-center justify-center rounded-lg text-base font-semibold ${
          channel.is_archived ? 'bg-slate-100 text-slate-400' : style.chip
        }`}
      >
        {style.glyph}
      </span>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span
            className={`truncate text-sm font-semibold ${
              channel.is_archived ? 'text-slate-400 line-through' : 'text-slate-900'
            }`}
          >
            {channel.name}
          </span>
          {channel.is_archived && (
            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-400">
              archived
            </span>
          )}
        </div>
        <p className="truncate text-xs text-slate-500">
          {channel.topic || '주제가 설정되지 않았습니다'}
        </p>
      </div>

      <div className="flex shrink-0 flex-col items-end gap-1">
        <span className="text-[11px] text-slate-400">
          {relativeTime(channel.updated_at)}
        </span>
        <span className="text-slate-300 opacity-0 transition group-hover:opacity-100">
          →
        </span>
      </div>
    </button>
  )
}

export const ChannelList = ({ onChannelClick }: ChannelListProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const [includeArchived, setIncludeArchived] = useState(false)
  const query = useChannels(workspaceUuid, {
    member_only: true,
    include_archived: includeArchived,
  })

  if (query.isPending) {
    return (
      <div className="space-y-2">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="flex items-center gap-3 rounded-lg px-3 py-2.5">
            <div className="size-10 shrink-0 animate-pulse rounded-lg bg-slate-200" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-28 animate-pulse rounded bg-slate-200" />
              <div className="h-2.5 w-44 animate-pulse rounded bg-slate-100" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : '채널 목록을 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <p className="text-xs font-medium text-slate-500">
          채널 {query.data.total}개
        </p>
        <label className="flex cursor-pointer items-center gap-1.5 text-xs text-slate-500">
          <input
            type="checkbox"
            checked={includeArchived}
            onChange={(e) => setIncludeArchived(e.target.checked)}
            className="size-3.5 rounded border-slate-300"
          />
          보관된 채널 포함
        </label>
      </div>

      {query.data.channels.length === 0 ? (
        <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center">
          <span className="text-3xl">💬</span>
          <p className="text-sm font-medium text-slate-700">아직 채널이 없습니다</p>
          <p className="text-xs text-slate-400">새 채널을 만들어 대화를 시작하세요.</p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white p-1.5 shadow-sm">
          {query.data.channels.map((channel) => (
            <ChannelRow
              key={channel.uuid}
              channel={channel}
              onClick={onChannelClick ? () => onChannelClick(channel) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  )
}
