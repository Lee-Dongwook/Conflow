/**
 * MessageComposer (Phase 4.2).
 *
 * Slack-shaped: textarea with Enter-to-send, Shift+Enter for newline.
 * Body trimmed on send; empty submissions ignored. Mentions / attachments
 * are out of alpha scope — the composer just sends `body`.
 *
 * Dumb: receives `channelUuid` + `onPosted` callback. Host (ChannelPage)
 * is responsible for refetch (the mutation already invalidates, so the
 * host typically just keeps the focus).
 */

import { isAPIError } from '@conflow/core'
import { useState, type KeyboardEvent } from 'react'

import { useCurrentWorkspaceUuid } from 'app/app/providers'
import { usePostMessage } from 'app/entities/message'
import type { MessageRead } from 'app/shared/types/api'

interface MessageComposerProps {
  readonly channelUuid: string
  readonly threadRootUuid?: string
  readonly onPosted?: (message: MessageRead) => void
  readonly placeholder?: string
}

export const MessageComposer = ({
  channelUuid,
  threadRootUuid,
  onPosted,
  placeholder,
}: MessageComposerProps) => {
  const workspaceUuid = useCurrentWorkspaceUuid()  // noqa kept for symmetry
  void workspaceUuid
  const post = usePostMessage(useCurrentWorkspaceUuid())
  const [body, setBody] = useState('')

  const send = async () => {
    const trimmed = body.trim()
    if (!trimmed || post.isPending) return
    const msg = await post.mutateAsync({
      channel_uuid: channelUuid,
      body: trimmed,
      ...(threadRootUuid ? { thread_root_uuid: threadRootUuid } : {}),
    })
    setBody('')
    onPosted?.(msg)
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      void send()
    }
  }

  const formError = post.error
    ? isAPIError(post.error)
      ? post.error.message
      : '메시지 전송 실패'
    : null

  return (
    <div className="space-y-2">
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder={placeholder ?? '메시지 입력 (Enter 전송, Shift+Enter 줄바꿈)'}
        rows={2}
        className="w-full resize-y rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-slate-500 focus:outline-none"
      />
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs text-rose-700">{formError ?? ''}</span>
        <button
          type="button"
          onClick={() => void send()}
          disabled={post.isPending || !body.trim()}
          className="rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white shadow-sm transition disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {post.isPending ? '전송 중…' : '전송'}
        </button>
      </div>
    </div>
  )
}
