/**
 * In-memory demo message store.
 *
 * Browsing the demo is read-only for most domains, but the comms channel is
 * meant to *feel* alive: a visitor can type a message and see a teammate
 * "reply". This store keeps a mutable per-channel message list (seeded from
 * `DEMO_SEED_MESSAGES`), appends the visitor's message on post, and schedules
 * a canned auto-reply from a rotating demo member.
 *
 * State lives for the browser session only — a refresh resets to the seed.
 * Nothing here touches the network.
 */

import type {
  MessageListFilter,
  MessageListOutput,
  MessagePostInput,
  MessageRead,
} from 'app/shared/types/api'

import { DEMO_SEED_MESSAGES } from './fixtures'
import { DEMO_WORKSPACE_UUID } from './constants'

/** Synthetic author for messages the demo visitor sends. */
export const DEMO_VISITOR_UUID = 'demo-member-you'

const REPLY_AUTHORS: readonly string[] = [
  'demo-member-minseo',
  'demo-member-hyun',
  'demo-member-sora',
]

const REPLY_BODY = '테스트 대화 내용입니다 🙂'
const REPLY_DELAY_MS = 1100

type Listener = (channelUuid: string) => void

// Mutable copy of the seed, grouped by channel (newest-first, like the API).
let store: Record<string, MessageRead[]> | null = null
let seq = 0
const listeners = new Set<Listener>()

// Channel → member uuid currently "typing" a reply (for the typing indicator).
const typing: Record<string, string | undefined> = {}

/** The demo member currently composing a reply in this channel, if any. */
export const demoTypingAuthor = (channelUuid: string): string | undefined =>
  typing[channelUuid]

const ensureStore = (): Record<string, MessageRead[]> => {
  if (store) return store
  const grouped: Record<string, MessageRead[]> = {}
  for (const m of DEMO_SEED_MESSAGES) {
    ;(grouped[m.channel_uuid] ??= []).push(m)
  }
  store = grouped
  return store
}

const notify = (channelUuid: string): void => {
  for (const cb of listeners) cb(channelUuid)
}

const makeMessage = (
  channelUuid: string,
  author: string,
  body: string,
): MessageRead => {
  seq += 1
  return {
    uuid: `demo-msg-live-${seq}`,
    workspace_uuid: DEMO_WORKSPACE_UUID,
    channel_uuid: channelUuid,
    thread_root_uuid: null,
    author_member_uuid: author,
    body,
    attachments: [],
    mentions: [],
    created_at: new Date().toISOString(),
    edited_at: null,
  }
}

/** Read a channel's messages (newest-first), seeded lazily. */
export const demoMessageList = (filters: MessageListFilter): MessageListOutput => {
  const messages = ensureStore()[filters.channel_uuid] ?? []
  // Return a fresh array each read: the store is mutated in place on post, so
  // handing back the live reference would let React Query's previous snapshot
  // mutate underneath it — structural sharing then sees "no change" and skips
  // the re-render. Copying decouples the cached snapshot from the live store.
  return { messages: [...messages], has_more: false }
}

/**
 * Append the visitor's message, schedule a teammate auto-reply, and return
 * the created message so the post mutation resolves successfully.
 */
export const demoPostMessage = (payload: MessagePostInput): MessageRead => {
  const channels = ensureStore()
  const channelUuid = payload.channel_uuid
  const list = (channels[channelUuid] ??= [])

  const mine = makeMessage(channelUuid, DEMO_VISITOR_UUID, payload.body)
  list.unshift(mine)

  // Simulate a teammate replying a beat later, with a "typing…" indicator.
  const replyAuthor =
    REPLY_AUTHORS[seq % REPLY_AUTHORS.length] ?? REPLY_AUTHORS[0]!
  typing[channelUuid] = replyAuthor
  notify(channelUuid)
  setTimeout(() => {
    const reply = makeMessage(channelUuid, replyAuthor, REPLY_BODY)
    ;(channels[channelUuid] ??= []).unshift(reply)
    typing[channelUuid] = undefined
    notify(channelUuid)
  }, REPLY_DELAY_MS)

  return mine
}

/** Subscribe to store changes (auto-replies). Returns an unsubscribe fn. */
export const subscribeDemoMessages = (cb: Listener): (() => void) => {
  listeners.add(cb)
  return () => {
    listeners.delete(cb)
  }
}
