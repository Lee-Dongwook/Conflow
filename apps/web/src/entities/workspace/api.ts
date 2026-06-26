/**
 * Workspace + Member-acceptance HTTP wrappers.
 *
 * Every response is validated against the Zod schemas in `shared/types/api.ts`
 * (CLAUDE.md: mandatory Zod for external data). Path strings come from
 * `shared/api/paths.ts` — never inline a `/workspaces/...` string here.
 */

import { apiClient, memberPaths, workspacesRoot } from 'app/shared/api'
import {
  MemberRead,
  type MemberRead as MemberReadType,
  WorkspaceCreateInput as WorkspaceCreateInputSchema,
  type WorkspaceCreateInput,
  WorkspaceRead,
  type WorkspaceRead as WorkspaceReadType,
} from 'app/shared/types/api'

export async function createWorkspace(
  payload: WorkspaceCreateInput,
): Promise<WorkspaceReadType> {
  // Validate payload too — fail fast before the API round-trip.
  const parsed = WorkspaceCreateInputSchema.parse(payload)
  const { data } = await apiClient.post(workspacesRoot(), parsed)
  return WorkspaceRead.parse(data)
}

export async function acceptInvitation(args: {
  readonly workspaceUuid: string
  readonly invitedMemberUuid: string
}): Promise<MemberReadType> {
  const { data } = await apiClient.post(
    memberPaths.accept(args.workspaceUuid, args.invitedMemberUuid),
  )
  return MemberRead.parse(data)
}
