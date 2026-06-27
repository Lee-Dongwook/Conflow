/**
 * In-memory demo document store.
 *
 * The documents domain has a real state machine (draft → pending_review →
 * approved → issued, plus void). Browsing the demo should let a visitor run
 * those lifecycle actions and watch the card move through states, instead of
 * hitting the write guard. This store holds a mutable copy of the seed and
 * applies transitions locally.
 *
 * State lives for the browser session only — a refresh resets to the seed.
 * Nothing here touches the network.
 */

import type {
  DocumentInstanceListFilter,
  DocumentInstanceListOutput,
  DocumentInstanceOutput,
  DocumentInstanceState,
} from 'app/shared/types/api'

import { DEMO_SEED_DOCUMENTS } from './fixtures'

const ACTION_DELAY_MS = 450

export type DocumentAction = 'submit' | 'approve' | 'reject' | 'issue'

// Lazy mutable copy of the seed.
let store: DocumentInstanceOutput[] | null = null

const ensureStore = (): DocumentInstanceOutput[] => {
  if (!store) store = DEMO_SEED_DOCUMENTS.map((d) => ({ ...d }))
  return store
}

// Resulting state for each action (mirrors backend transitions).
const NEXT_STATE: Record<DocumentAction, DocumentInstanceState> = {
  submit: 'pending_review',
  approve: 'approved',
  reject: 'draft',
  issue: 'issued',
}

const nowIso = (): string => new Date().toISOString()

const delay = <T>(value: T): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), ACTION_DELAY_MS))

const findIndex = (uuid: string): number =>
  ensureStore().findIndex((d) => d.uuid === uuid)

/** List instances (optionally state-filtered) from the mutable store. */
export const demoDocumentList = (
  filters: DocumentInstanceListFilter = {},
): DocumentInstanceListOutput => {
  const filtered = ensureStore().filter((d) => {
    if (filters.state && d.state !== filters.state) return false
    return true
  })
  return { instances: filtered, total: filtered.length }
}

/** Read one instance from the mutable store. */
export const demoDocument = (instanceUuid: string): DocumentInstanceOutput => {
  const docs = ensureStore()
  return docs.find((d) => d.uuid === instanceUuid) ?? docs[0]!
}

/** Apply a lifecycle transition and return the updated instance. */
export const demoTransitionDocument = (
  instanceUuid: string,
  action: DocumentAction,
): Promise<DocumentInstanceOutput> => {
  const docs = ensureStore()
  const i = findIndex(instanceUuid)
  if (i === -1) return delay(demoDocument(instanceUuid))

  const current = docs[i]!
  const nextState = NEXT_STATE[action]
  const issuing = action === 'issue'

  const updated: DocumentInstanceOutput = {
    ...current,
    state: nextState,
    updated_at: nowIso(),
    ...(issuing
      ? {
          issued_at: nowIso(),
          rendered_pdf_uri:
            current.rendered_pdf_uri ??
            `https://demo.conflow.app/documents/${instanceUuid}.pdf`,
        }
      : {}),
  }
  docs[i] = updated
  return delay(updated)
}

/** Void an instance with a reason and return the updated instance. */
export const demoVoidDocument = (
  instanceUuid: string,
  reason: string,
): Promise<DocumentInstanceOutput> => {
  const docs = ensureStore()
  const i = findIndex(instanceUuid)
  if (i === -1) return delay(demoDocument(instanceUuid))

  const updated: DocumentInstanceOutput = {
    ...docs[i]!,
    state: 'void',
    void_reason: reason,
    updated_at: nowIso(),
  }
  docs[i] = updated
  return delay(updated)
}
