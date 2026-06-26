/**
 * ChannelList widget — fetches & renders channels for the current workspace.
 *
 * Toggleable "include archived" filter. Type prefix mimics Slack
 * (#/🔒/✉/🔗) so users can scan visually. Click handler exposed for the
 * host page to route to the channel detail view.
 */

import { isAPIError } from '@conflow/core'
import { useState } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useChannels } from 'app/entities/channel'
import type { ChannelRead, ChannelType } from 'app/shared/types/api'

const TYPE_PREFIX: Record<ChannelType, string> = {
  public: '#',
  private: '🔒',
  dm: '✉',
  external: '🔗',
}

interface ChannelListProps {
  readonly onChannelClick?: (channel: ChannelRead) => void
}

export const ChannelList = ({ onChannelClick }: ChannelListProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const [includeArchived, setIncludeArchived] = useState(false)
  const query = useChannels(workspaceUuid, {
    member_only: true,
    include_archived: includeArchived,
  })

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
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
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-500">총 {query.data.total}개</p>
        <label className="flex cursor-pointer items-center gap-1 text-xs text-slate-600">
          <input
            type="checkbox"
            checked={includeArchived}
            onChange={(e) => setIncludeArchived(e.target.checked)}
          />
          archived 포함
        </label>
      </div>
      {query.data.channels.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center text-sm text-slate-600">
          아직 채널이 없습니다.
        </div>
      ) : (
        <ul className="space-y-1">
          {query.data.channels.map((channel) => (
            <li key={channel.uuid}>
              <button
                type="button"
                onClick={
                  onChannelClick ? () => onChannelClick(channel) : undefined
                }
                disabled={!onChannelClick}
                className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition hover:bg-slate-100 disabled:cursor-default disabled:hover:bg-transparent"
              >
                <span className="font-mono text-slate-400">
                  {TYPE_PREFIX[channel.type]}
                </span>
                <span
                  className={`flex-1 truncate font-medium ${
                    channel.is_archived
                      ? 'text-slate-400 line-through'
                      : 'text-slate-800'
                  }`}
                >
                  {channel.name}
                </span>
                {channel.is_archived && (
                  <span className="text-[10px] uppercase text-slate-400">
                    archived
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
