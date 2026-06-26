/**
 * TanStack Query hooks for PM Issue.
 *
 * `useIssues` keys on the full filter object so distinct filter combos
 * cache independently. Mutations invalidate the workspace's issue root
 * (`pmKeys.issues`) so any open list view refetches.
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from '@tanstack/react-query'

import { pmKeys } from 'app/shared/api'
import type {
  IssueListFilter,
  IssueListOutput,
  IssueRead,
} from 'app/shared/types/api'

import {
  createIssue,
  getIssue,
  listIssues,
  transitionIssue,
} from './api'

export function useIssues(
  workspaceUuid: string,
  filters: IssueListFilter = {},
  options?: Omit<
    UseQueryOptions<IssueListOutput>,
    'queryKey' | 'queryFn'
  >,
) {
  return useQuery<IssueListOutput>({
    queryKey: pmKeys.issueList(workspaceUuid, filters as Record<string, unknown>),
    queryFn: () => listIssues({ workspaceUuid, filters }),
    ...options,
  })
}

export function useIssue(
  workspaceUuid: string,
  issueUuid: string | null | undefined,
) {
  return useQuery<IssueRead>({
    queryKey: pmKeys.issueDetail(workspaceUuid, issueUuid ?? ''),
    queryFn: () =>
      getIssue({ workspaceUuid, issueUuid: issueUuid as string }),
    enabled: Boolean(issueUuid),
  })
}

export function useCreateIssue(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Parameters<typeof createIssue>[0]['payload']) =>
      createIssue({ workspaceUuid, payload }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: pmKeys.issues(workspaceUuid) })
    },
  })
}

export function useTransitionIssue(workspaceUuid: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (args: {
      readonly issueUuid: string
      readonly payload: Parameters<typeof transitionIssue>[0]['payload']
    }) =>
      transitionIssue({
        workspaceUuid,
        issueUuid: args.issueUuid,
        payload: args.payload,
      }),
    onSuccess: (data) => {
      // Both the detail view and any list need updating.
      qc.invalidateQueries({ queryKey: pmKeys.issues(workspaceUuid) })
      qc.setQueryData(pmKeys.issueDetail(workspaceUuid, data.uuid), data)
    },
  })
}
