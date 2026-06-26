/**
 * `/w/:workspaceUuid/comms/channels/:channelUuid` — message stream + composer.
 *
 * Composer pinned to the bottom (sticky). Stream lives in the scrollable
 * region above it. Channel header (name / topic) is fetched cheaply via
 * `useChannels` + find — a dedicated `useChannel(uuid)` lands once the
 * backend exposes a single-channel GET.
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

  if (!channelUuid) {
    return <div className="text-sm text-rose-700">channelUuid 가 없습니다.</div>
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col space-y-4">
      <header className="space-y-1 border-b border-slate-200 pb-3">
        <Link
          to={`/w/${workspaceUuid}/comms/channels`}
          onClick={(e) => {
            e.preventDefault()
            navigate(-1)
          }}
          className="text-xs text-slate-500 hover:text-slate-900"
        >
          ← 채널 목록
        </Link>
        {channel ? (
          <>
            <h1 className="text-lg font-semibold text-slate-900">
              {channel.type === 'public' ? '#' : '🔒'} {channel.name}
            </h1>
            {channel.topic && (
              <p className="text-xs text-slate-600">{channel.topic}</p>
            )}
          </>
        ) : (
          <h1 className="font-mono text-sm text-slate-500">{channelUuid}</h1>
        )}
      </header>

      <div className="flex-1 overflow-y-auto pr-1">
        <MessageStream channelUuid={channelUuid} />
      </div>

      <div className="sticky bottom-0 border-t border-slate-200 bg-slate-50 pt-3">
        <MessageComposer channelUuid={channelUuid} />
      </div>
    </div>
  )
}
