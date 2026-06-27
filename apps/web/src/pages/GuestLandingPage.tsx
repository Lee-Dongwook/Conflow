/**
 * Guest landing — shown at `/` for unauthenticated visitors.
 *
 * Replaces the retired legacy `AppContent` marketing surface. Keeps the
 * Product Hunt banner and the login/signup modal entry; authenticated
 * users never reach here (LandingRedirectPage sends them to `/w/...`).
 */

import { useEffect, useState } from 'react'

import { Button } from '@conflow/ui'

import { LoginModal } from 'app/pages/LoginPage'
import { captureLaunchRef, trackLaunchEvent } from 'app/shared/lib'
import { ProductHuntBanner } from 'app/widgets/product-hunt-banner'

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
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-6 text-center">
        <span className="text-3xl font-semibold tracking-tight text-slate-900">Conflow</span>
        <p className="mt-3 max-w-md text-sm text-slate-600">
          팀플·스터디 팀을 위한 협업 워크스페이스. 회의 요약, 블로커 감지, 스프린트 관리를 한곳에서.
        </p>
        <Button type="button" className="mt-6" onClick={openLogin}>
          로그인 / 시작하기
        </Button>
      </div>
      <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
    </>
  )
}
