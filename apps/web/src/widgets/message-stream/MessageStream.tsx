/**
 * MessageStream widget — top-level messages of one channel, rendered as a
 * Slack-style threaded conversation.
 *
 * Alpha: top-level only (`thread_root_uuid IS NULL`). Backend returns DESC
 * by created_at; we render ascending (oldest → newest) so the newest sits
 * just above the composer. Consecutive messages from the same author inside
 * a 5-minute window are grouped under a single avatar/name header, and day
 * boundaries get a divider.
 */

import { isAPIError } from '@conflow/core'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { useMessages } from 'app/entities/message'
import { commsKeys } from 'app/shared/api'
import {
  demoTypingAuthor,
  isDemoWorkspace,
  subscribeDemoMessages,
} from 'app/shared/demo'
import { memberInitials, resolveMember } from 'app/shared/lib'
import type { MessageRead } from 'app/shared/types/api'

const GROUP_WINDOW_MS = 5 * 60 * 1000

const timeFmt = new Intl.DateTimeFormat('ko-KR', {
  hour: '2-digit',
  minute: '2-digit',
})

const dayFmt = new Intl.DateTimeFormat('ko-KR', {
  month: 'long',
  day: 'numeric',
  weekday: 'short',
})

const formatTime = (iso: string): string => {
  try {
    return timeFmt.format(new Date(iso))
  } catch {
    return iso
  }
}

const formatDay = (iso: string): string => {
  try {
    return dayFmt.format(new Date(iso))
  } catch {
    return iso
  }
}

const sameDay = (a: string, b: string): boolean =>
  new Date(a).toDateString() === new Date(b).toDateString()

const DateDivider = ({ iso }: { readonly iso: string }) => (
  <div className="my-4 flex items-center gap-3">
    <div className="h-px flex-1 bg-slate-200" />
    <span className="rounded-full border border-slate-200 bg-white px-3 py-0.5 text-xs font-medium text-slate-500">
      {formatDay(iso)}
    </span>
    <div className="h-px flex-1 bg-slate-200" />
  </div>
)

interface RowProps {
  readonly msg: MessageRead
  /** When true this message continues a group → hide the avatar/name header. */
  readonly grouped: boolean
}

const MessageRow = ({ msg, grouped }: RowProps) => {
  const member = resolveMember(msg.author_member_uuid)

  return (
    <div className="group flex gap-3 rounded-md px-2 py-0.5 transition hover:bg-slate-50">
      {grouped ? (
        <div className="w-9 shrink-0 pt-1 text-right">
          <span className="text-[10px] text-slate-300 opacity-0 group-hover:opacity-100">
            {formatTime(msg.created_at)}
          </span>
        </div>
      ) : (
        <div
          className={`mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-md text-xs font-semibold ${member.avatar}`}
        >
          {memberInitials(member.name)}
        </div>
      )}

      <div className="min-w-0 flex-1">
        {!grouped && (
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-semibold text-slate-900">{member.name}</span>
            <span className="text-[11px] text-slate-400">{member.role}</span>
            <span className="text-[11px] text-slate-400">{formatTime(msg.created_at)}</span>
            {msg.edited_at && (
              <span className="text-[11px] italic text-slate-300">(수정됨)</span>
            )}
          </div>
        )}
        <p className="whitespace-pre-wrap wrap-break-word text-sm leading-relaxed text-slate-700">
          {msg.body}
        </p>
        {msg.mentions.length > 0 && (
          <p className="mt-1 flex flex-wrap gap-1">
            {msg.mentions.map((m) => (
              <span
                key={m}
                className="rounded bg-sky-50 px-1.5 py-0.5 text-[11px] font-medium text-sky-700"
              >
                @{resolveMember(m).name.replace(/^@/, '')}
              </span>
            ))}
          </p>
        )}
      </div>
    </div>
  )
}

const TypingIndicator = ({ authorUuid }: { readonly authorUuid: string }) => {
  const member = resolveMember(authorUuid)
  return (
    <div className="flex gap-3 px-2 py-1">
      <div
        className={`flex size-9 shrink-0 items-center justify-center rounded-md text-xs font-semibold ${member.avatar}`}
      >
        {memberInitials(member.name)}
      </div>
      <div className="flex flex-col justify-center">
        <span className="text-[11px] text-slate-400">{member.name} 님이 입력 중…</span>
        <span className="mt-1 flex gap-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="size-1.5 animate-bounce rounded-full bg-slate-300"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </span>
      </div>
    </div>
  )
}

interface MessageStreamProps {
  readonly channelUuid: string
}

export const MessageStream = ({ channelUuid }: MessageStreamProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const query = useMessages(workspaceUuid, { channel_uuid: channelUuid, limit: 50 })
  const qc = useQueryClient()

  // Demo: refetch when the in-memory store emits an auto-reply / typing change.
  useEffect(() => {
    if (!isDemoWorkspace(workspaceUuid)) return
    return subscribeDemoMessages((ch) => {
      if (ch !== channelUuid) return
      qc.invalidateQueries({
        queryKey: commsKeys.messages(workspaceUuid, channelUuid),
      })
    })
  }, [workspaceUuid, channelUuid, qc])

  const typingAuthor = isDemoWorkspace(workspaceUuid)
    ? demoTypingAuthor(channelUuid)
    : undefined

  if (query.isPending) {
    return (
      <div className="space-y-4 py-4">
        {[0, 1, 2].map((i) => (
          <div key={i} className="flex gap-3 px-2">
            <div className="size-9 shrink-0 animate-pulse rounded-md bg-slate-200" />
            <div className="flex-1 space-y-2">
              <div className="h-3 w-24 animate-pulse rounded bg-slate-200" />
              <div className="h-3 w-2/3 animate-pulse rounded bg-slate-100" />
            </div>
          </div>
        ))}
      </div>
    )
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
      <div className="flex h-full flex-col items-center justify-center gap-2 py-16 text-center">
        <div className="flex size-12 items-center justify-center rounded-full bg-slate-100 text-2xl">
          💬
        </div>
        <p className="text-sm font-medium text-slate-700">아직 메시지가 없습니다</p>
        <p className="text-xs text-slate-400">첫 메시지를 보내 대화를 시작해 보세요.</p>
      </div>
    )
  }

  // Backend gives newest-first; flip to chronological for a chat reading order.
  const ordered = [...query.data.messages].reverse()

  return (
    <div className="space-y-0.5 py-2">
      {query.data.has_more && (
        <p className="pb-2 text-center text-xs text-slate-400">
          더 오래된 메시지가 있습니다
        </p>
      )}
      {ordered.map((msg, i) => {
        const prev = i > 0 ? ordered[i - 1] : undefined
        const showDivider = !prev || !sameDay(prev.created_at, msg.created_at)
        const grouped =
          !showDivider &&
          !!prev &&
          prev.author_member_uuid === msg.author_member_uuid &&
          new Date(msg.created_at).getTime() - new Date(prev.created_at).getTime() <
            GROUP_WINDOW_MS

        return (
          <div key={msg.uuid}>
            {showDivider && <DateDivider iso={msg.created_at} />}
            <MessageRow msg={msg} grouped={grouped} />
          </div>
        )
      })}
      {typingAuthor && <TypingIndicator authorUuid={typingAuthor} />}
    </div>
  )
}
