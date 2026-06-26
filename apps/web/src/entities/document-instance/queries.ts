/**
 * TanStack Query hooks for DocumentInstance.
 *
 * All five state-action mutations invalidate the instance list root so
 * the visible page refetches automatically. Action handler signatures
 * stay uniform — `(instanceUuid: string)` — so a generic `<ActionButton />`
 * can call any of them.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { documentsKeys } from 'app/shared/api'
import type {
  DocumentInstanceListFilter,
  DocumentInstanceListOutput,
  DocumentInstanceOutput,
  DocumentInstanceVoidInput,
} from 'app/shared/types/api'

import {
  approveInstance,
  getDocumentInstance,
  issueInstance,
  listDocumentInstances,
  rejectInstance,
  submitForReview,
  voidInstance,
} from './api'

export function useDocumentInstances(
  workspaceUuid: string,
  filters: DocumentInstanceListFilter = {},
) {
  return useQuery<DocumentInstanceListOutput>({
    queryKey: documentsKeys.instanceList(
      workspaceUuid,
      filters as Record<string, unknown>,
    ),
    queryFn: () => listDocumentInstances({ workspaceUuid, filters }),
  })
}

export function useDocumentInstance(
  workspaceUuid: string,
  instanceUuid: string | null | undefined,
) {
  return useQuery<DocumentInstanceOutput>({
    queryKey: [...documentsKeys.instances(workspaceUuid), 'detail', instanceUuid ?? ''],
    queryFn: () =>
      getDocumentInstance({
        workspaceUuid,
        instanceUuid: instanceUuid as string,
      }),
    enabled: Boolean(instanceUuid),
  })
}

function useInstanceAction<TArg>(
  workspaceUuid: string,
  action: (workspaceUuid: string, instanceUuid: string, arg?: TArg) => Promise<DocumentInstanceOutput>,
) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ instanceUuid, arg }: { readonly instanceUuid: string; readonly arg?: TArg }) =>
      action(workspaceUuid, instanceUuid, arg),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentsKeys.instances(workspaceUuid) })
    },
  })
}

export const useSubmitInstanceForReview = (workspaceUuid: string) =>
  useInstanceAction(workspaceUuid, (ws, id) => submitForReview(ws, id))

export const useApproveInstance = (workspaceUuid: string) =>
  useInstanceAction(workspaceUuid, (ws, id) => approveInstance(ws, id))

export const useRejectInstance = (workspaceUuid: string) =>
  useInstanceAction(workspaceUuid, (ws, id) => rejectInstance(ws, id))

export const useIssueInstance = (workspaceUuid: string) =>
  useInstanceAction(workspaceUuid, (ws, id) => issueInstance(ws, id))

export function useVoidInstance(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (args: {
      readonly instanceUuid: string
      readonly payload: DocumentInstanceVoidInput
    }) =>
      voidInstance({
        workspaceUuid,
        instanceUuid: args.instanceUuid,
        payload: args.payload,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentsKeys.instances(workspaceUuid) })
    },
  })
}
