import { track } from '@vercel/analytics'
import { Analytics } from '@vercel/analytics/react'
import { useEffect } from 'react'

/**
 * Vercel Web Analytics for the traffic-test deploy.
 *
 * `<Analytics />` captures page views automatically. The effect bridges the
 * app's existing `conflow:launch` CustomEvents (fired by `trackLaunchEvent`)
 * into Vercel custom events so funnel steps — demo entry, waitlist open/submit,
 * banner CTAs — are measurable alongside attribution (utm/ref).
 *
 * PII note: the bridge forwards only the event name and campaign attribution.
 * It deliberately drops `extra` fields (e.g. the submitted email) so no
 * personal data leaves for analytics.
 */

type LaunchDetail = {
  readonly event: string
  readonly ref: {
    readonly source?: string | null
    readonly medium?: string | null
    readonly campaign?: string | null
    readonly ref?: string | null
  } | null
}

export const AppAnalytics = () => {
  useEffect(() => {
    const onLaunch = (e: Event) => {
      const { event, ref } = (e as CustomEvent<LaunchDetail>).detail
      track(event, {
        ref: ref?.ref ?? null,
        source: ref?.source ?? null,
        medium: ref?.medium ?? null,
        campaign: ref?.campaign ?? null,
      })
    }
    window.addEventListener('conflow:launch', onLaunch)
    return () => window.removeEventListener('conflow:launch', onLaunch)
  }, [])

  return <Analytics />
}
