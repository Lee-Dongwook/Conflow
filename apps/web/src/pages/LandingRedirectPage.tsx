/**
 * `/` landing — auth-aware redirect to the right workspace shell.
 *
 *   loading        → spinner (Supabase getSession race)
 *   authenticated  → `/w/{lastVisited}` if remembered, else `/workspace/new`
 *   unauthenticated → render the `fallback` (GuestLandingPage)
 *
 * Keeping the guest fallback under `/` means logged-out visitors don't
 * see a redirect loop on the create-workspace page (which requires auth
 * to succeed but currently doesn't gate render).
 */

import { Navigate } from 'react-router-dom'
import type { ReactNode } from 'react'

import { useLastVisitedWorkspaceUuid } from 'app/app/providers'
import { useSession } from 'app/entities/session'

interface LandingRedirectPageProps {
  readonly fallback: ReactNode
}

export const LandingRedirectPage = ({ fallback }: LandingRedirectPageProps) => {
  const session = useSession()
  const lastUuid = useLastVisitedWorkspaceUuid()

  if (session.status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-sm text-slate-500">로딩 중…</div>
      </div>
    )
  }

  if (session.status === 'authenticated') {
    const dest = lastUuid ? `/w/${lastUuid}` : '/workspace/new'
    return <Navigate to={dest} replace />
  }

  return <>{fallback}</>
}
