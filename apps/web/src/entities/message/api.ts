/**
 * Comms Message HTTP wrappers. Mandatory Zod validation.
 */

import { apiClient, commsPaths } from 'app/shared/api'
import {
  MessageListFilter as MessageListFilterSchema,
  type MessageListFilter,
  MessageListOutput,
  type MessageListOutput as MessageListOutputType,
  MessagePostInput as MessagePostInputSchema,
  type MessagePostInput,
  MessageRead,
  type MessageRead as MessageReadType,
  MessageUpdateInput as MessageUpdateInputSchema,
  type MessageUpdateInput,
} from 'app/shared/types/api'

export async function listMessages(args: {
  readonly workspaceUuid: string
  readonly filters: MessageListFilter
}): Promise<MessageListOutputType> {
  const parsed = MessageListFilterSchema.parse(args.filters)
  const { data } = await apiClient.get(commsPaths.messages(args.workspaceUuid), {
    params: parsed,
  })
  return MessageListOutput.parse(data)
}

export async function postMessage(args: {
  readonly workspaceUuid: string
  readonly payload: MessagePostInput
}): Promise<MessageReadType> {
  const parsed = MessagePostInputSchema.parse(args.payload)
  const { data } = await apiClient.post(
    commsPaths.messages(args.workspaceUuid),
    parsed,
  )
  return MessageRead.parse(data)
}

export async function editMessage(args: {
  readonly workspaceUuid: string
  readonly messageUuid: string
  readonly payload: MessageUpdateInput
}): Promise<MessageReadType> {
  const parsed = MessageUpdateInputSchema.parse(args.payload)
  const { data } = await apiClient.patch(
    commsPaths.message(args.workspaceUuid, args.messageUuid),
    parsed,
  )
  return MessageRead.parse(data)
}

export async function deleteMessage(args: {
  readonly workspaceUuid: string
  readonly messageUuid: string
}): Promise<void> {
  await apiClient.delete(
    commsPaths.message(args.workspaceUuid, args.messageUuid),
  )
}
