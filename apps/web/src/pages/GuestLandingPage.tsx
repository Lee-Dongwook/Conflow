/**
 * Guest landing — shown at `/` for unauthenticated visitors.
 *
 * The first page is always visible (no login wall). It previews the product
 * surface (domain sidebar + overview, demo data) and a banner invites the
 * visitor into the fully browsable demo at `/w/demo`. Every sidebar link and
 * overview action navigates into `/w/demo/...`, where they can explore all
 * domains; write actions there prompt login. Authenticated users never reach
 * here (LandingRedirectPage sends them to their real `/w/...`).
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { LoginModal } from 'app/pages/LoginPage'
import { DEMO_OVERVIEW, OverviewContent } from 'app/pages/WorkspaceOverviewPage'
import { DEMO_WORKSPACE_UUID } from 'app/shared/demo'
import { captureLaunchRef, trackLaunchEvent } from 'app/shared/lib'
import { ProductHuntBanner } from 'app/widgets/product-hunt-banner'
import { WorkspaceSidebar } from 'app/widgets/sidebar'

const DEMO_BASE = `/w/${DEMO_WORKSPACE_UUID}`

export const GuestLandingPage = () => {
  const navigate = useNavigate()
  const [loginOpen, setLoginOpen] = useState(false)

  useEffect(() => {
    captureLaunchRef()
  }, [])

  const enterDemo = (path?: string) => {
    trackLaunchEvent('guest_overlay_click')
    navigate(path ? `${DEMO_BASE}/${path}` : DEMO_BASE)
  }

  return (
    <>
      <ProductHuntBanner
        onLoginRequest={() => setLoginOpen(true)}
        productHuntUrl={import.meta.env.VITE_PRODUCT_HUNT_URL}
      />
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-teal-200 bg-teal-50 px-6 py-2.5 text-sm text-teal-900">
        <span>로그인 없이 데모로 모든 기능을 둘러볼 수 있어요.</span>
        <button
          type="button"
          onClick={() => enterDemo()}
          className="rounded-md bg-teal-600 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-teal-700"
        >
          데모 둘러보기 →
        </button>
      </div>
      <div className="flex min-h-screen bg-slate-50">
        <WorkspaceSidebar
          workspaceUuid={DEMO_WORKSPACE_UUID}
          onLoginRequest={() => setLoginOpen(true)}
        />
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-slate-200 bg-white px-6 py-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">workspace</p>
            <h1 className="mt-1 text-sm font-medium text-slate-700">데모 워크스페이스</h1>
          </header>
          <main className="flex-1 p-6">
            <OverviewContent data={DEMO_OVERVIEW} onNavigate={enterDemo} isDemo />
          </main>
        </div>
      </div>
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  )
}
