/**
 * MessageStream widget — top-level messages of one channel.
 *
 * Alpha: top-level only (`thread_root_uuid IS NULL`), DESC by created_at
 * (mirrors the backend default). Thread replies UI lands when the detail
 * page can host a side-panel.
 */

import { isAPIError } from '@conflow/core'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useMessages } from 'app/entities/message'
import type { MessageRead } from 'app/shared/types/api'

const formatTime = (iso: string): string => {
  try {
    return new Intl.DateTimeFormat('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      month: 'short',
      day: 'numeric',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

const MessageRow = ({ msg }: { readonly msg: MessageRead }) => (
  <article className="rounded-md border border-slate-200 bg-white p-3 shadow-sm">
    <header className="flex items-baseline justify-between gap-2 text-xs">
      <span className="font-mono font-medium text-slate-700">
        @{msg.author_member_uuid.slice(0, 8)}
      </span>
      <span className="text-slate-400">
        {formatTime(msg.created_at)}
        {msg.edited_at && <span className="ml-1 italic">(edited)</span>}
      </span>
    </header>
    <p className="mt-1 whitespace-pre-wrap text-sm text-slate-800">{msg.body}</p>
    {msg.mentions.length > 0 && (
      <p className="mt-1 text-xs text-slate-500">
        멘션: {msg.mentions.map((m) => '@' + m.slice(0, 8)).join(', ')}
      </p>
    )}
  </article>
)

interface MessageStreamProps {
  readonly channelUuid: string
}

export const MessageStream = ({ channelUuid }: MessageStreamProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const query = useMessages(workspaceUuid, { channel_uuid: channelUuid, limit: 50 })

  if (query.isPending) {
    return <div className="py-12 text-center text-sm text-slate-500">로딩 중…</div>
  }

  if (query.isError) {
    const msg = isAPIError(query.error)
      ? query.error.message
      : '메시지를 불러올 수 없습니다.'
    return (
      <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {msg}
      </div>
    )
  }

  if (query.data.messages.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center text-sm text-slate-600">
        아직 메시지가 없습니다. 첫 메시지를 보내보세요.
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {query.data.messages.map((msg) => (
        <MessageRow key={msg.uuid} msg={msg} />
      ))}
      {query.data.has_more && (
        <p className="text-center text-xs text-slate-400">
          더 오래된 메시지가 있습니다 (페이지네이션은 다음 단위)
        </p>
      )}
    </div>
  )
}
