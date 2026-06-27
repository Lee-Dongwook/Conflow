/**
 * Guest landing — shown at `/` for unauthenticated visitors.
 *
 * Showcases the real product surface (domain sidebar + workspace overview)
 * with demo mock data, so logged-out visitors see what Conflow does before
 * signing in. The whole surface is read-only: a transparent overlay catches
 * any click and opens the login modal. Authenticated users never reach here
 * (LandingRedirectPage sends them to their real `/w/...`).
 */

import { useEffect, useState } from 'react'

import { LoginModal } from 'app/pages/LoginPage'
import { DEMO_OVERVIEW, OverviewContent } from 'app/pages/WorkspaceOverviewPage'
import { captureLaunchRef, trackLaunchEvent } from 'app/shared/lib'
import { ProductHuntBanner } from 'app/widgets/product-hunt-banner'
import { WorkspaceSidebar } from 'app/widgets/sidebar'

const noop = () => {}

export const GuestLandingPage = () => {
  const [loginOpen, setLoginOpen] = useState(false)

  useEffect(() => {
    captureLaunchRef()
  }, [])

  const openLogin = () => {
    trackLaunchEvent('guest_overlay_click')
    setLoginOpen(true)
  }

  return (
    <>
      <ProductHuntBanner
        onLoginRequest={() => setLoginOpen(true)}
        productHuntUrl={import.meta.env.VITE_PRODUCT_HUNT_URL}
      />
      <div className="relative flex min-h-screen bg-slate-50">
        {/* Demo is read-only — any interaction prompts login. */}
        <div className="absolute inset-0 z-40 cursor-pointer" onClick={openLogin} aria-hidden="true" />
        <WorkspaceSidebar workspaceUuid="demo" onLoginRequest={() => setLoginOpen(true)} />
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-slate-200 bg-white px-6 py-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">workspace</p>
            <h1 className="mt-1 text-sm font-medium text-slate-700">데모 워크스페이스</h1>
          </header>
          <main className="flex-1 p-6">
            <OverviewContent data={DEMO_OVERVIEW} onNavigate={noop} isDemo />
          </main>
        </div>
      </div>
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  )
}
