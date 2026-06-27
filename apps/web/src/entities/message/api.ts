/**
 * Comms Message HTTP wrappers. Mandatory Zod validation.
 */

import { apiClient, commsPaths } from 'app/shared/api'
import {
  demoGuard,
  demoMessageList,
  demoPostMessage,
  isDemoWorkspace,
} from 'app/shared/demo'
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
  if (isDemoWorkspace(args.workspaceUuid)) return demoMessageList(args.filters)
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
  // Demo exception: comms is the one domain where visitors may "chat" — the
  // store appends the message locally and simulates a teammate reply.
  if (isDemoWorkspace(args.workspaceUuid)) {
    const parsed = MessagePostInputSchema.parse(args.payload)
    return demoPostMessage(parsed)
  }
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
  if (isDemoWorkspace(args.workspaceUuid)) return demoGuard.blockWrite()
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
  if (isDemoWorkspace(args.workspaceUuid)) return demoGuard.blockWrite()
  await apiClient.delete(
    commsPaths.message(args.workspaceUuid, args.messageUuid),
  )
}
