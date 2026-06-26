/**
 * Query key factories — one place to express the cache hierarchy.
 *
 * Convention: every key starts with the resource root, followed by
 * scoping params (workspace_uuid first when applicable). This lets
 * `queryClient.invalidateQueries({queryKey: pmKeys.issues(ws)})` blow
 * away an entire workspace's issue cache in one call.
 *
 * Add a factory when a new feature/page consumes that resource.
 */

export const workspaceKeys = {
  root: ['workspaces'] as const,
  list: () => [...workspaceKeys.root, 'list'] as const,
  detail: (workspaceUuid: string) =>
    [...workspaceKeys.root, 'detail', workspaceUuid] as const,
}

export const memberKeys = {
  root: ['members'] as const,
  list: (workspaceUuid: string) =>
    [...memberKeys.root, workspaceUuid, 'list'] as const,
  detail: (workspaceUuid: string, memberUuid: string) =>
    [...memberKeys.root, workspaceUuid, 'detail', memberUuid] as const,
}

export const pmKeys = {
  root: ['pm'] as const,
  issues: (workspaceUuid: string) =>
    [...pmKeys.root, workspaceUuid, 'issues'] as const,
  issueList: (workspaceUuid: string, filters: Record<string, unknown>) =>
    [...pmKeys.issues(workspaceUuid), 'list', filters] as const,
  issueDetail: (workspaceUuid: string, issueUuid: string) =>
    [...pmKeys.issues(workspaceUuid), 'detail', issueUuid] as const,
}

export const commsKeys = {
  root: ['comms'] as const,
  channels: (workspaceUuid: string) =>
    [...commsKeys.root, workspaceUuid, 'channels'] as const,
  channelList: (workspaceUuid: string, filters: Record<string, unknown>) =>
    [...commsKeys.channels(workspaceUuid), 'list', filters] as const,
  messages: (workspaceUuid: string, channelUuid: string) =>
    [...commsKeys.root, workspaceUuid, 'messages', channelUuid] as const,
}

export const hrKeys = {
  root: ['hr'] as const,
  profiles: (workspaceUuid: string) =>
    [...hrKeys.root, workspaceUuid, 'profiles'] as const,
  profileList: (workspaceUuid: string, filters: Record<string, unknown>) =>
    [...hrKeys.profiles(workspaceUuid), 'list', filters] as const,
  profileDetail: (workspaceUuid: string, profileUuid: string) =>
    [...hrKeys.profiles(workspaceUuid), 'detail', profileUuid] as const,
  onboardings: (workspaceUuid: string) =>
    [...hrKeys.root, workspaceUuid, 'onboardings'] as const,
}

export const documentsKeys = {
  root: ['documents'] as const,
  templates: (workspaceUuid: string) =>
    [...documentsKeys.root, workspaceUuid, 'templates'] as const,
  instances: (workspaceUuid: string) =>
    [...documentsKeys.root, workspaceUuid, 'instances'] as const,
  instanceList: (workspaceUuid: string, filters: Record<string, unknown>) =>
    [...documentsKeys.instances(workspaceUuid), 'list', filters] as const,
}

export const a2uiKeys = {
  root: ['a2ui'] as const,
  catalog: (workspaceUuid: string) =>
    [...a2uiKeys.root, workspaceUuid, 'catalog'] as const,
}
