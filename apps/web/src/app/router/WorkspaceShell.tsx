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
 *
 * When the workspace is the demo sentinel (`/w/demo`), a DemoModeBar is
 * shown and the write guard is wired to open the login modal on any
 * mutation attempt (see `shared/demo`).
 */

import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import type { ReactNode } from 'react'

import { useCurrentWorkspaceUuid, WorkspaceProvider } from 'app/app/providers'
import { useSession } from 'app/entities/session'
import { consentApi, ConsentForm, type ConsentAccept } from 'app/features/consent'
import { LoginModal } from 'app/pages/LoginPage'
import { demoGuard, isDemoWorkspace } from 'app/shared/demo'
import { WorkspaceSidebar } from 'app/widgets/sidebar'

const DemoModeBar = () => {
  const [loginOpen, setLoginOpen] = useState(false)

  useEffect(() => {
    demoGuard.setOnWriteAttempt(() => setLoginOpen(true))
    return () => demoGuard.setOnWriteAttempt(null)
  }, [])

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200 bg-amber-50 px-6 py-2 text-sm text-amber-900">
        <span>🎭 데모 모드로 둘러보는 중입니다 — 변경 사항은 저장되지 않아요.</span>
        <button
          type="button"
          onClick={() => setLoginOpen(true)}
          className="rounded-md bg-amber-900 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-amber-800"
        >
          로그인하고 시작하기
        </button>
      </div>
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  )
}

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
  const demo = isDemoWorkspace(workspaceUuid)
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">workspace</p>
      <h1 className={demo ? 'mt-1 text-sm font-medium text-slate-700' : 'mt-1 font-mono text-sm text-slate-700'}>
        {demo ? '데모 워크스페이스' : workspaceUuid}
      </h1>
    </header>
  )
}

const WorkspaceLayout = () => {
  const workspaceUuid = useCurrentWorkspaceUuid()
  const demo = isDemoWorkspace(workspaceUuid)
  return (
    <div className="flex min-h-screen bg-slate-50">
      <WorkspaceSidebar workspaceUuid={workspaceUuid} />
      <div className="flex min-w-0 flex-1 flex-col">
        {demo ? <DemoModeBar /> : null}
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
