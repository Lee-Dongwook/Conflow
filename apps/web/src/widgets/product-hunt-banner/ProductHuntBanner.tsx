import { useCallback, useEffect, useState } from 'react'

import { useTranslation } from 'app/shared/i18n'
import { trackLaunchEvent } from 'app/shared/lib'

const DISMISS_KEY = 'ph-banner-dismissed-v1'

const readDismissed = (): boolean => {
  if (typeof window === 'undefined') return false
  try {
    return window.localStorage.getItem(DISMISS_KEY) === '1'
  } catch {
    return false
  }
}

const persistDismissed = (): void => {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(DISMISS_KEY, '1')
  } catch {
    // storage unavailable — silently ignore
  }
}

export type ProductHuntBannerProps = {
  readonly onLoginRequest: () => void
  readonly productHuntUrl?: string
}

export const ProductHuntBanner = ({ onLoginRequest, productHuntUrl }: ProductHuntBannerProps) => {
  const { t } = useTranslation()
  const [dismissed, setDismissed] = useState<boolean>(() => readDismissed())

  const dismiss = useCallback(() => {
    trackLaunchEvent('ph_banner_dismiss')
    persistDismissed()
    setDismissed(true)
  }, [])

  const handlePrimary = useCallback(() => {
    trackLaunchEvent('ph_banner_cta_primary')
    onLoginRequest()
  }, [onLoginRequest])

  const handleSecondary = useCallback(() => {
    trackLaunchEvent('ph_banner_cta_secondary')
  }, [])

  useEffect(() => {
    if (dismissed) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') dismiss()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [dismissed, dismiss])

  if (dismissed) return null

  const hasSecondary = typeof productHuntUrl === 'string' && productHuntUrl.length > 0

  return (
    <div
      role="banner"
      aria-label="Product Hunt launch"
      className="sticky top-0 z-50 w-full border-b border-orange-200 bg-linear-to-r from-orange-50 via-rose-50 to-amber-50"
    >
      <div className="mx-auto flex max-w-6xl flex-col items-start gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between md:gap-6 md:py-2.5">
        <div className="flex min-w-0 items-start gap-3 md:items-center">
          <span
            aria-hidden="true"
            className="mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-orange-500 text-xs font-bold text-white shadow-sm md:mt-0"
          >
            P
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-900">{t('marketing.banner.title')}</p>
            <p className="text-xs leading-snug text-slate-600 md:text-[13px]">
              {t('marketing.banner.subtitle')}
            </p>
          </div>
        </div>

        <div className="flex w-full flex-wrap items-center gap-2 md:w-auto md:flex-nowrap">
          <button
            type="button"
            onClick={handlePrimary}
            className="inline-flex h-9 items-center justify-center rounded-md bg-orange-500 px-3.5 text-xs font-semibold text-white shadow-sm transition-colors hover:bg-orange-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-400 focus-visible:ring-offset-1"
          >
            {t('marketing.banner.ctaPrimary')}
          </button>
          {hasSecondary ? (
            <a
              href={productHuntUrl}
              target="_blank"
              rel="noopener noreferrer"
              onClick={handleSecondary}
              className="inline-flex h-9 items-center justify-center rounded-md border border-orange-300 bg-white px-3.5 text-xs font-semibold text-orange-700 transition-colors hover:bg-orange-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-400 focus-visible:ring-offset-1"
            >
              {t('marketing.banner.ctaSecondary')} ↗
            </a>
          ) : null}
          <button
            type="button"
            onClick={dismiss}
            aria-label={t('marketing.banner.dismissLabel')}
            className="ml-auto inline-flex h-9 w-9 items-center justify-center rounded-md text-slate-500 transition-colors hover:bg-orange-100 hover:text-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-400 md:ml-0"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-4 w-4"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M4.28 4.22a.75.75 0 011.06 0L10 8.94l4.66-4.72a.75.75 0 111.07 1.05L11.06 10l4.67 4.73a.75.75 0 11-1.07 1.05L10 11.06l-4.66 4.72a.75.75 0 11-1.07-1.05L8.94 10 4.28 5.27a.75.75 0 010-1.05z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
