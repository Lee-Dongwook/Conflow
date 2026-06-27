/**
 * PM Issue HTTP wrappers.
 *
 * Responses validated through `shared/types/api.ts` schemas (mandatory).
 * Paths come from `shared/api/paths.ts`; never inline `/workspaces/...`.
 */

import { apiClient, pmPaths } from 'app/shared/api'
import {
  demoCreateIssue,
  demoIssue,
  demoIssueList,
  demoTransitionIssue,
  isDemoWorkspace,
} from 'app/shared/demo'
import {
  IssueCreateInput as IssueCreateInputSchema,
  type IssueCreateInput,
  IssueListFilter as IssueListFilterSchema,
  type IssueListFilter,
  IssueListOutput,
  type IssueListOutput as IssueListOutputType,
  IssueRead,
  type IssueRead as IssueReadType,
  IssueTransitionInput as IssueTransitionInputSchema,
  type IssueTransitionInput,
} from 'app/shared/types/api'

export async function listIssues(args: {
  readonly workspaceUuid: string
  readonly filters: IssueListFilter
}): Promise<IssueListOutputType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoIssueList(args.filters)
  const parsed = IssueListFilterSchema.parse(args.filters)
  const { data } = await apiClient.get(pmPaths.issues(args.workspaceUuid), {
    params: parsed,
  })
  return IssueListOutput.parse(data)
}

export async function getIssue(args: {
  readonly workspaceUuid: string
  readonly issueUuid: string
}): Promise<IssueReadType> {
  if (isDemoWorkspace(args.workspaceUuid)) return demoIssue(args.issueUuid)
  const { data } = await apiClient.get(
    pmPaths.issue(args.workspaceUuid, args.issueUuid),
  )
  return IssueRead.parse(data)
}

export async function createIssue(args: {
  readonly workspaceUuid: string
  readonly payload: IssueCreateInput
}): Promise<IssueReadType> {
  const parsed = IssueCreateInputSchema.parse(args.payload)
  if (isDemoWorkspace(args.workspaceUuid)) return demoCreateIssue(parsed)
  const { data } = await apiClient.post(
    pmPaths.issues(args.workspaceUuid),
    parsed,
  )
  return IssueRead.parse(data)
}

export async function transitionIssue(args: {
  readonly workspaceUuid: string
  readonly issueUuid: string
  readonly payload: IssueTransitionInput
}): Promise<IssueReadType> {
  const parsed = IssueTransitionInputSchema.parse(args.payload)
  if (isDemoWorkspace(args.workspaceUuid))
    return demoTransitionIssue(args.issueUuid, parsed)
  const { data } = await apiClient.post(
    pmPaths.issueTransition(args.workspaceUuid, args.issueUuid),
    parsed,
  )
  return IssueRead.parse(data)
}
