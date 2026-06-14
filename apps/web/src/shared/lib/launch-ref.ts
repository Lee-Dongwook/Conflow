const STORAGE_KEY = 'conflow-launch-ref-v1'

export type LaunchRef = {
  readonly ref: string | null
  readonly source: string | null
  readonly medium: string | null
  readonly campaign: string | null
  readonly capturedAt: string
}

const readFromUrl = (): Partial<LaunchRef> | null => {
  if (typeof window === 'undefined') return null
  const params = new URLSearchParams(window.location.search)
  const ref = params.get('ref')
  const source = params.get('utm_source')
  const medium = params.get('utm_medium')
  const campaign = params.get('utm_campaign')
  if (!ref && !source && !medium && !campaign) return null
  return { ref, source, medium, campaign }
}

const persist = (data: LaunchRef): void => {
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch {
    // sessionStorage unavailable — silently ignore
  }
}

const readPersisted = (): LaunchRef | null => {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as LaunchRef
  } catch {
    return null
  }
}

export const captureLaunchRef = (): LaunchRef | null => {
  const fromUrl = readFromUrl()
  if (fromUrl) {
    const data: LaunchRef = {
      ref: fromUrl.ref ?? null,
      source: fromUrl.source ?? null,
      medium: fromUrl.medium ?? null,
      campaign: fromUrl.campaign ?? null,
      capturedAt: new Date().toISOString(),
    }
    persist(data)
    return data
  }
  return readPersisted()
}

export const getLaunchRef = (): LaunchRef | null => readPersisted()

export const isProductHuntRef = (): boolean => {
  const data = readPersisted()
  if (!data) return false
  return data.ref === 'producthunt' || data.source === 'producthunt'
}

export type LaunchEvent =
  | 'guest_overlay_click'
  | 'ph_banner_cta_primary'
  | 'ph_banner_cta_secondary'
  | 'ph_banner_dismiss'

export const trackLaunchEvent = (
  event: LaunchEvent,
  extra: Record<string, unknown> = {},
): void => {
  if (typeof window === 'undefined') return
  const ref = readPersisted()
  const payload = { event, ref, ...extra, ts: new Date().toISOString() }
  if (import.meta.env.DEV) {
    // eslint-disable-next-line no-console
    console.debug('[launch]', payload)
  }
  window.dispatchEvent(new CustomEvent('conflow:launch', { detail: payload }))
}
