/**
 * Demo workspace sentinel.
 *
 * Logged-out visitors browse the product at `/w/demo`. Entity api wrappers
 * short-circuit to mock fixtures when the workspace uuid is this sentinel,
 * so every page/widget works without auth and without touching the network.
 */

export const DEMO_WORKSPACE_UUID = 'demo'

export const isDemoWorkspace = (workspaceUuid: string | null | undefined): boolean =>
  workspaceUuid === DEMO_WORKSPACE_UUID
