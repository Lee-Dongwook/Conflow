/**
 * WorkspaceProvider — URL-derived current workspace + localStorage hint.
 *
 * The current workspace_uuid lives in the URL (`/w/:workspaceUuid/...`)
 * — react-router is the source of truth. This provider exposes it via
 * context so pages don't have to call `useParams` (cleaner testing) and
 * mirrors the value to localStorage so a user landing on `/` can be
 * routed back to their last-visited workspace by the upcoming switcher.
 *
 * Used only inside the WorkspaceShell route; outside that tree the
 * `useCurrentWorkspaceUuid` hook returns `null`.
 */

import { createContext, useContext, useEffect, useMemo, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'

import { isDemoWorkspace } from 'app/shared/demo'

const LAST_VISITED_KEY = 'conflow.workspace.lastVisitedUuid'

interface WorkspaceContextValue {
  readonly workspaceUuid: string
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null)

interface WorkspaceProviderProps {
  readonly children: ReactNode
}

export const WorkspaceProvider = ({ children }: WorkspaceProviderProps) => {
  const { workspaceUuid } = useParams<{ workspaceUuid: string }>()

  // Persist on visit. Wrap in try/catch so private-browsing rejections
  // don't crash navigation. The demo sentinel is never persisted, so a
  // returning authenticated user is not redirected into `/w/demo`.
  useEffect(() => {
    if (!workspaceUuid || isDemoWorkspace(workspaceUuid)) return
    try {
      window.localStorage.setItem(LAST_VISITED_KEY, workspaceUuid)
    } catch {
      /* storage disabled — non-fatal */
    }
  }, [workspaceUuid])

  const value = useMemo<WorkspaceContextValue | null>(
    () => (workspaceUuid ? { workspaceUuid } : null),
    [workspaceUuid],
  )

  return (
    <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
  )
}

/**
 * Required-flavor hook. Throws when called outside a WorkspaceProvider —
 * use this in pages that *must* run inside a workspace context. The throw
 * is intentional: a missing workspace_uuid means the page is mounted at
 * the wrong route, not a state to render around.
 */
export function useCurrentWorkspaceUuid(): string {
  const ctx = useContext(WorkspaceContext)
  if (!ctx) {
    throw new Error(
      'useCurrentWorkspaceUuid must be used inside <WorkspaceProvider> — ' +
        'check that the route is nested under /w/:workspaceUuid/.',
    )
  }
  return ctx.workspaceUuid
}

/**
 * Optional-flavor hook. Returns the URL workspace_uuid if present, else
 * the last-visited one from localStorage, else null. Use this for the
 * landing-page redirect logic and the global sidebar.
 */
export function useLastVisitedWorkspaceUuid(): string | null {
  const ctx = useContext(WorkspaceContext)
  if (ctx) return ctx.workspaceUuid
  try {
    return window.localStorage.getItem(LAST_VISITED_KEY)
  } catch {
    return null
  }
}
