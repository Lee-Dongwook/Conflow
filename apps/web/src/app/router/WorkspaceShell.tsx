/**
 * Workspace shell — host for the new domain pages.
 *
 * Wraps `/w/:workspaceUuid/*` routes with `WorkspaceProvider` so nested
 * pages can call `useCurrentWorkspaceUuid()` instead of `useParams`.
 * Side-effect: WorkspaceProvider mirrors the uuid to localStorage so the
 * "last visited workspace" redirect (landing page) works.
 *
 * Also hosts the required-consent gate (relocated from the retired legacy
 * AppContent): an authenticated user with un-accepted required consents is
 * shown the ConsentForm before any domain page renders.
 */

import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import type { ReactNode } from 'react'

import { useCurrentWorkspaceUuid, WorkspaceProvider } from 'app/app/providers'
import { useSession } from 'app/entities/session'
import { consentApi, ConsentForm, type ConsentAccept } from 'app/features/consent'
import { WorkspaceSidebar } from 'app/widgets/sidebar'

const ConsentGate = ({ children }: { readonly children: ReactNode }) => {
  const session = useSession()
  const [pending, setPending] = useState(false)
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    if (session.status !== 'authenticated') {
      setChecked(false)
      setPending(false)
      return
    }

    const checkConsent = async () => {
      try {
        const status = await consentApi.getStatus()
        setPending(!status.allRequiredAccepted)
      } catch {
        setPending(false)
      }
      setChecked(true)
    }
    checkConsent()
  }, [session.status])

  const handleConsent = async (consents: Record<string, boolean>) => {
    const payload: readonly ConsentAccept[] = Object.entries(consents)
      .filter(([, accepted]) => accepted)
      .map(([type]) => ({ consentType: type as ConsentAccept['consentType'], version: '1.0' }))

    if (payload.length > 0) {
      await consentApi.accept(payload)
    }
    setPending(false)
  }

  if (session.status === 'authenticated' && checked && pending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-8">
        <ConsentForm onComplete={handleConsent} />
      </div>
    )
  }

  return <>{children}</>
}

const WorkspaceHeader = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">workspace</p>
      <h1 className="mt-1 font-mono text-sm text-slate-700">{workspaceUuid}</h1>
    </header>
  )
}

const WorkspaceLayout = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  return (
    <div className="flex min-h-screen bg-slate-50">
      <WorkspaceSidebar workspaceUuid={workspaceUuid} />
      <div className="flex min-w-0 flex-1 flex-col">
        <WorkspaceHeader />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export const WorkspaceShell = () => (
  <WorkspaceProvider>
    <ConsentGate>
      <WorkspaceLayout />
    </ConsentGate>
  </WorkspaceProvider>
)
