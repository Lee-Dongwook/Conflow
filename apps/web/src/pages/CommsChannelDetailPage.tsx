/**
 * `/w/:workspaceUuid/comms/channels/:channelUuid` — message stream + composer.
 *
 * Chat-app shaped: a fixed channel header, a scrollable message stream that
 * fills the available height, and a composer card pinned to the bottom.
 * Channel metadata is fetched cheaply via `useChannels` + find — a dedicated
 * `useChannel(uuid)` lands once the backend exposes a single-channel GET.
 */

import { Link, useNavigate, useParams } from 'react-router-dom'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useChannels } from 'app/entities/channel'
import { MessageComposer } from 'app/features/message-post'
import { MessageStream } from 'app/widgets/message-stream'

export const CommsChannelDetailPage = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const navigate = useNavigate()
  const { channelUuid } = useParams<{ channelUuid: string }>()
  const channelsQuery = useChannels(workspaceUuid, { member_only: true })
  const channel = channelsQuery.data?.channels.find((c) => c.uuid === channelUuid)
  const isPrivate = channel?.type === 'private'

  if (!channelUuid) {
    return <div className="text-sm text-rose-700">channelUuid 가 없습니다.</div>
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      {/* Channel header */}
      <header className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3">
        <Link
          to={`/w/${workspaceUuid}/comms/channels`}
          onClick={(e) => {
            e.preventDefault()
            navigate(-1)
          }}
          className="flex size-8 items-center justify-center rounded-md text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          aria-label="채널 목록으로"
        >
          ←
        </Link>
        <div
          className={`flex size-9 shrink-0 items-center justify-center rounded-lg text-base ${
            isPrivate ? 'bg-amber-50 text-amber-600' : 'bg-emerald-50 text-emerald-600'
          }`}
        >
          {isPrivate ? '🔒' : '#'}
        </div>
        <div className="min-w-0 flex-1">
          {channel ? (
            <>
              <h1 className="truncate text-base font-semibold text-slate-900">
                {channel.name}
              </h1>
              <p className="truncate text-xs text-slate-500">
                {channel.topic || (isPrivate ? '비공개 채널' : '공개 채널')}
              </p>
            </>
          ) : (
            <h1 className="font-mono text-sm text-slate-500">{channelUuid}</h1>
          )}
        </div>
        {channel && (
          <span
            className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${
              isPrivate
                ? 'bg-amber-50 text-amber-700'
                : 'bg-emerald-50 text-emerald-700'
            }`}
          >
            {isPrivate ? '비공개' : '공개'}
          </span>
        )}
      </header>

      {/* Message stream */}
      <div className="flex-1 overflow-y-auto bg-slate-50/40 px-2">
        <MessageStream channelUuid={channelUuid} />
      </div>

      {/* Composer */}
      <div className="border-t border-slate-200 bg-white px-3 py-3">
        <MessageComposer channelUuid={channelUuid} />
      </div>
    </div>
  )
}
