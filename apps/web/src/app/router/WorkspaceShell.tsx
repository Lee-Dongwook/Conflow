/**
 * Workspace shell — host for the new domain pages.
 *
 * Wraps `/w/:workspaceUuid/*` routes with `WorkspaceProvider` so nested
 * pages can call `useCurrentWorkspaceUuid()` instead of `useParams`.
 * Side-effect: WorkspaceProvider mirrors the uuid to localStorage so the
 * "last visited workspace" redirect (landing page) works.
 *
 * Legacy state-based pages stay under `/` (see App.tsx); this shell only
 * wraps the new tree.
 */

import { Outlet } from 'react-router-dom'

import { useCurrentWorkspaceUuid, WorkspaceProvider } from 'app/app/providers'

const WorkspaceHeader = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        workspace
      </p>
      <h1 className="mt-1 font-mono text-sm text-slate-700">{workspaceUuid}</h1>
    </header>
  )
}

export const WorkspaceShell = () => (
  <WorkspaceProvider>
    <div className="flex min-h-screen flex-col bg-slate-50">
      <WorkspaceHeader />
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  </WorkspaceProvider>
)
