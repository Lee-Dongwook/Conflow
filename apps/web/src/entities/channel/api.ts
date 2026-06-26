/**
 * Comms Channel HTTP wrappers. Mandatory Zod validation.
 */

import { apiClient, commsPaths } from 'app/shared/api'
import {
  ChannelCreateInput as ChannelCreateInputSchema,
  type ChannelCreateInput,
  ChannelListFilter as ChannelListFilterSchema,
  type ChannelListFilter,
  ChannelListOutput,
  type ChannelListOutput as ChannelListOutputType,
  ChannelRead,
  type ChannelRead as ChannelReadType,
} from 'app/shared/types/api'

export async function listChannels(args: {
  readonly workspaceUuid: string
  readonly filters: ChannelListFilter
}): Promise<ChannelListOutputType> {
  const parsed = ChannelListFilterSchema.parse(args.filters)
  const { data } = await apiClient.get(commsPaths.channels(args.workspaceUuid), {
    params: parsed,
  })
  return ChannelListOutput.parse(data)
}

export async function createChannel(args: {
  readonly workspaceUuid: string
  readonly payload: ChannelCreateInput
}): Promise<ChannelReadType> {
  const parsed = ChannelCreateInputSchema.parse(args.payload)
  const { data } = await apiClient.post(
    commsPaths.channels(args.workspaceUuid),
    parsed,
  )
  return ChannelRead.parse(data)
}

export async function archiveChannel(args: {
  readonly workspaceUuid: string
  readonly channelUuid: string
}): Promise<ChannelReadType> {
  const { data } = await apiClient.post(
    commsPaths.channelArchive(args.workspaceUuid, args.channelUuid),
  )
  return ChannelRead.parse(data)
}

export async function joinChannel(args: {
  readonly workspaceUuid: string
  readonly channelUuid: string
}): Promise<void> {
  await apiClient.post(
    commsPaths.channelJoin(args.workspaceUuid, args.channelUuid),
  )
}

export async function leaveChannel(args: {
  readonly workspaceUuid: string
  readonly channelUuid: string
}): Promise<void> {
  await apiClient.post(
    commsPaths.channelLeave(args.workspaceUuid, args.channelUuid),
  )
}
