/**
 * URL path helpers — keep route shapes in one place.
 *
 * Backend prefixes every workspace-scoped route with
 * `/workspaces/{workspace_uuid}/...`. Components should never concatenate
 * that string themselves; use these helpers so renaming or versioning is
 * a one-file change.
 *
 * The `/api` prefix is already baked into `apiClient.baseURL`, so paths
 * here are relative to `/api`.
 */

const WORKSPACES = 'workspaces'

export function workspacesRoot(): string {
  return `/${WORKSPACES}`
}

export function workspacePath(
  workspaceUuid: string,
  ...segments: readonly string[]
): string {
  if (!workspaceUuid) {
    throw new Error('workspacePath: workspace_uuid is required')
  }
  const tail = segments
    .map((s) => s.replace(/^\/+|\/+$/g, ''))
    .filter(Boolean)
    .join('/')
  const suffix = tail ? `/${tail}` : ''
  return `/${WORKSPACES}/${workspaceUuid}${suffix}`
}

// Convenience namespaces — call site reads like a sentence.

export const pmPaths = {
  issues: (workspaceUuid: string) => workspacePath(workspaceUuid, 'issues'),
  issue: (workspaceUuid: string, issueUuid: string) =>
    workspacePath(workspaceUuid, 'issues', issueUuid),
  issueTransition: (workspaceUuid: string, issueUuid: string) =>
    workspacePath(workspaceUuid, 'issues', issueUuid, 'transition'),
}

export const commsPaths = {
  channels: (workspaceUuid: string) => workspacePath(workspaceUuid, 'channels'),
  channelArchive: (workspaceUuid: string, channelUuid: string) =>
    workspacePath(workspaceUuid, 'channels', channelUuid, 'archive'),
  channelJoin: (workspaceUuid: string, channelUuid: string) =>
    workspacePath(workspaceUuid, 'channels', channelUuid, 'join'),
  channelLeave: (workspaceUuid: string, channelUuid: string) =>
    workspacePath(workspaceUuid, 'channels', channelUuid, 'leave'),
  messages: (workspaceUuid: string) => workspacePath(workspaceUuid, 'messages'),
  message: (workspaceUuid: string, messageUuid: string) =>
    workspacePath(workspaceUuid, 'messages', messageUuid),
}

export const hrPaths = {
  profiles: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'hr', 'profiles'),
  profile: (workspaceUuid: string, profileUuid: string) =>
    workspacePath(workspaceUuid, 'hr', 'profiles', profileUuid),
  onboardings: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'hr', 'onboardings'),
  oneOnOnes: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'hr', 'one-on-ones'),
  leaves: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'hr', 'leaves'),
}

export const documentsPaths = {
  templates: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'documents', 'templates'),
  instances: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'documents', 'instances'),
}

export const a2uiPaths = {
  tools: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'a2ui', 'tools'),
  invoke: (workspaceUuid: string, toolId: string) =>
    workspacePath(workspaceUuid, 'a2ui', 'tools', toolId, 'invoke'),
}

export const memberPaths = {
  invite: (workspaceUuid: string) =>
    workspacePath(workspaceUuid, 'members', 'invite'),
  accept: (workspaceUuid: string, invitedMemberUuid: string) =>
    workspacePath(workspaceUuid, 'members', invitedMemberUuid, 'accept'),
}
