/**
 * DocumentInstance HTTP wrappers — list + state-machine actions.
 *
 * Draft creation lives in features/document-instance-draft (next slice);
 * this file owns the read + lifecycle-transition surface only.
 */

import { apiClient, documentsPaths } from 'app/shared/api'
import {
  demoDocument,
  demoDocumentList,
  demoTransitionDocument,
  demoVoidDocument,
  isDemoWorkspace,
} from 'app/shared/demo'
import {
  DocumentInstanceListFilter as DocumentInstanceListFilterSchema,
  type DocumentInstanceListFilter,
  DocumentInstanceListOutput,
  type DocumentInstanceListOutput as DocumentInstanceListOutputType,
  DocumentInstanceOutput,
  type DocumentInstanceOutput as DocumentInstanceOutputType,
  DocumentInstanceVoidInput as DocumentInstanceVoidInputSchema,
  type DocumentInstanceVoidInput,
} from 'app/shared/types/api'

const instanceAction = (
  workspaceUuid: string,
  instanceUuid: string,
  action: string,
): string => `${documentsPaths.instances(workspaceUuid)}/${instanceUuid}/${action}`

export async function listDocumentInstances(args: {
  readonly workspaceUuid: string
  readonly filters: DocumentInstanceListFilter
}): Promise<DocumentInstanceListOutputType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoDocumentList(args.filters)
  const parsed = DocumentInstanceListFilterSchema.parse(args.filters)
  const { data } = await apiClient.get(
    documentsPaths.instances(args.workspaceUuid),
    { params: parsed },
  )
  return DocumentInstanceListOutput.parse(data)
}

export async function getDocumentInstance(args: {
  readonly workspaceUuid: string
  readonly instanceUuid: string
}): Promise<DocumentInstanceOutputType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoDocument(args.instanceUuid)
  const { data } = await apiClient.get(
    `${documentsPaths.instances(args.workspaceUuid)}/${args.instanceUuid}`,
  )
  return DocumentInstanceOutput.parse(data)
}

const transition = async (
  workspaceUuid: string,
  instanceUuid: string,
  action: 'submit' | 'approve' | 'reject' | 'issue',
): Promise<DocumentInstanceOutputType> => {
  // Demo exception: run the lifecycle transition against the in-memory store
  // so visitors can drive documents through their state machine.
  if (isDemoWorkspace(workspaceUuid)) {
    return demoTransitionDocument(instanceUuid, action)
  }
  const { data } = await apiClient.post(
    instanceAction(workspaceUuid, instanceUuid, action),
  )
  return DocumentInstanceOutput.parse(data)
}

export const submitForReview = (
  workspaceUuid: string,
  instanceUuid: string,
) => transition(workspaceUuid, instanceUuid, 'submit')

export const approveInstance = (
  workspaceUuid: string,
  instanceUuid: string,
) => transition(workspaceUuid, instanceUuid, 'approve')

export const rejectInstance = (
  workspaceUuid: string,
  instanceUuid: string,
) => transition(workspaceUuid, instanceUuid, 'reject')

export const issueInstance = (
  workspaceUuid: string,
  instanceUuid: string,
) => transition(workspaceUuid, instanceUuid, 'issue')

export async function voidInstance(args: {
  readonly workspaceUuid: string
  readonly instanceUuid: string
  readonly payload: DocumentInstanceVoidInput
}): Promise<DocumentInstanceOutputType> {
  const parsed = DocumentInstanceVoidInputSchema.parse(args.payload)
  if (isDemoWorkspace(args.workspaceUuid)) {
    return demoVoidDocument(args.instanceUuid, parsed.void_reason)
  }
  const { data } = await apiClient.post(
    instanceAction(args.workspaceUuid, args.instanceUuid, 'void'),
    parsed,
  )
  return DocumentInstanceOutput.parse(data)
}
