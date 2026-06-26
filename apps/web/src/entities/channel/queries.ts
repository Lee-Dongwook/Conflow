/**
 * TanStack Query hooks for Channel.
 *
 * Channel mutations (create/archive/join/leave) all invalidate the channel
 * root key so list views refresh. Message-stream invalidation lives in
 * `entities/message/queries.ts`.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { commsKeys } from 'app/shared/api'
import type {
  ChannelListFilter,
  ChannelListOutput,
} from 'app/shared/types/api'

import {
  archiveChannel,
  createChannel,
  joinChannel,
  leaveChannel,
  listChannels,
} from './api'

export function useChannels(
  workspaceUuid: string,
  filters: ChannelListFilter = { member_only: true },
) {
  return useQuery<ChannelListOutput>({
    queryKey: commsKeys.channelList(
      workspaceUuid,
      filters as Record<string, unknown>,
    ),
    queryFn: () => listChannels({ workspaceUuid, filters }),
  })
}

export function useCreateChannel(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Parameters<typeof createChannel>[0]['payload']) =>
      createChannel({ workspaceUuid, payload }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: commsKeys.channels(workspaceUuid) })
    },
  })
}

export function useArchiveChannel(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (channelUuid: string) =>
      archiveChannel({ workspaceUuid, channelUuid }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: commsKeys.channels(workspaceUuid) })
    },
  })
}

export function useJoinChannel(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (channelUuid: string) =>
      joinChannel({ workspaceUuid, channelUuid }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: commsKeys.channels(workspaceUuid) })
    },
  })
}

export function useLeaveChannel(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (channelUuid: string) =>
      leaveChannel({ workspaceUuid, channelUuid }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: commsKeys.channels(workspaceUuid) })
    },
  })
}
