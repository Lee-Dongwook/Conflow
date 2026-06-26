/**
 * TanStack Query hooks for Message.
 *
 * `useMessages` keys on (workspace, channel) — switching channels swaps
 * caches without cross-contamination. Mutations invalidate the channel's
 * message key.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { commsKeys } from 'app/shared/api'
import type {
  MessageListFilter,
  MessageListOutput,
  MessagePostInput,
} from 'app/shared/types/api'

import { deleteMessage, editMessage, listMessages, postMessage } from './api'

export function useMessages(
  workspaceUuid: string,
  filters: MessageListFilter,
) {
  return useQuery<MessageListOutput>({
    queryKey: [
      ...commsKeys.messages(workspaceUuid, filters.channel_uuid),
      filters,
    ],
    queryFn: () => listMessages({ workspaceUuid, filters }),
  })
}

export function usePostMessage(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: MessagePostInput) =>
      postMessage({ workspaceUuid, payload }),
    onSuccess: (data) => {
      qc.invalidateQueries({
        queryKey: commsKeys.messages(workspaceUuid, data.channel_uuid),
      })
    },
  })
}

export function useEditMessage(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (args: {
      readonly messageUuid: string
      readonly payload: Parameters<typeof editMessage>[0]['payload']
    }) =>
      editMessage({
        workspaceUuid,
        messageUuid: args.messageUuid,
        payload: args.payload,
      }),
    onSuccess: (data) => {
      qc.invalidateQueries({
        queryKey: commsKeys.messages(workspaceUuid, data.channel_uuid),
      })
    },
  })
}

export function useDeleteMessage(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (messageUuid: string) =>
      deleteMessage({ workspaceUuid, messageUuid }),
    onSuccess: () => {
      // Author-only delete: we don't know which channel without the row,
      // so invalidate the whole comms root and let pages refetch.
      qc.invalidateQueries({ queryKey: commsKeys.root })
    },
  })
}
