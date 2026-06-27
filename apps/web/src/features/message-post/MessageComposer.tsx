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
    <div className="space-y-1.5">
      <div className="flex items-end gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 shadow-sm transition focus-within:border-slate-500 focus-within:ring-2 focus-within:ring-slate-100">
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder ?? '메시지 보내기…'}
          rows={1}
          className="max-h-40 min-h-6 flex-1 resize-none border-0 bg-transparent text-sm leading-relaxed text-slate-800 placeholder:text-slate-400 focus:outline-none"
        />
        <button
          type="button"
          onClick={() => void send()}
          disabled={post.isPending || !body.trim()}
          className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white shadow-sm transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
          aria-label="전송"
        >
          {post.isPending ? (
            <span className="size-3.5 animate-spin rounded-full border-2 border-white/40 border-t-white" />
          ) : (
            <svg
              viewBox="0 0 20 20"
              fill="currentColor"
              className="size-4"
              aria-hidden="true"
            >
              <path d="M1.5 10.5 18 3l-4 14.5-4.5-5.5L15 6 7.5 11l-6-0.5Z" />
            </svg>
          )}
        </button>
      </div>
      <div className="flex items-center justify-between px-1">
        <span className="text-[11px] text-rose-600">{formError ?? ''}</span>
        <span className="text-[11px] text-slate-400">
          Enter 전송 · Shift+Enter 줄바꿈
        </span>
      </div>
    </div>
  )
}
