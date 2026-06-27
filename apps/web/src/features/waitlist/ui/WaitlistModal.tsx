import { useCallback, useEffect, useRef, useState } from 'react'

import { Button } from '@conflow/ui'

import { getLaunchRef, trackLaunchEvent } from 'app/shared/lib'

/**
 * Waitlist modal — temporary stand-in for the login/signup flow while the
 * backend is offline (traffic-only deploy). Collects an email (and optional
 * name), fires a `waitlist_submit` launch event for attribution, and posts to
 * an external collector when `VITE_WAITLIST_ENDPOINT` is configured.
 *
 * Drop-in compatible with `LoginModal` props (`open` / `onClose`) so call sites
 * can swap back to real auth once the backend is live again.
 */

type WaitlistModalProps = {
  readonly open: boolean
  readonly onClose: () => void
}

const STORAGE_KEY = 'conflow-waitlist-v1'

type WaitlistEntry = {
  readonly email: string
  readonly name: string
  readonly ref: ReturnType<typeof getLaunchRef>
  readonly submittedAt: string
}

const persistLocally = (entry: WaitlistEntry): void => {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    const existing = raw ? (JSON.parse(raw) as readonly WaitlistEntry[]) : []
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...existing, entry]))
  } catch {
    // storage unavailable — silently ignore
  }
}

const postToEndpoint = async (entry: WaitlistEntry): Promise<void> => {
  const endpoint = import.meta.env.VITE_WAITLIST_ENDPOINT as string | undefined
  if (!endpoint) return
  await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  })
}

export const WaitlistModal = ({ open, onClose }: WaitlistModalProps) => {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const backdropRef = useRef<HTMLDivElement>(null)

  const reset = useCallback(() => {
    setEmail('')
    setName('')
    setLoading(false)
    setDone(false)
    setError(null)
  }, [])

  const close = useCallback(() => {
    reset()
    onClose()
  }, [reset, onClose])

  useEffect(() => {
    if (open) trackLaunchEvent('waitlist_open')
  }, [open])

  useEffect(() => {
    if (!open) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [open, close])

  if (!open) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const entry: WaitlistEntry = {
      email: email.trim(),
      name: name.trim(),
      ref: getLaunchRef(),
      submittedAt: new Date().toISOString(),
    }

    persistLocally(entry)
    trackLaunchEvent('waitlist_submit', { email: entry.email })

    try {
      await postToEndpoint(entry)
      setDone(true)
    } catch {
      // The email is already persisted locally and tracked — treat a failed
      // network post as success so the visitor still sees confirmation.
      setDone(true)
    }
    setLoading(false)
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === backdropRef.current) close()
  }

  return (
    <div
      ref={backdropRef}
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
    >
      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-xl">
        {done ? (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-teal-100 text-2xl">
              ✓
            </div>
            <h2 className="text-lg font-semibold text-slate-900">등록 완료!</h2>
            <p className="mt-2 text-sm text-slate-500">
              정식 출시되면 가장 먼저 알려드릴게요. 관심 가져주셔서 감사합니다.
            </p>
            <Button type="button" className="mt-5 w-full" onClick={close}>
              데모 계속 둘러보기
            </Button>
          </div>
        ) : (
          <>
            <div className="mb-5 text-center">
              <h2 className="text-lg font-semibold text-slate-900">출시 알림 받기</h2>
              <p className="mt-1 text-sm text-slate-500">
                이메일을 남겨주시면 정식 출시 소식을 보내드려요.
              </p>
            </div>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="waitlist-name" className="text-sm font-medium text-slate-700">
                  이름 <span className="font-normal text-slate-400">(선택)</span>
                </label>
                <input
                  id="waitlist-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                  placeholder="홍길동"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label htmlFor="waitlist-email" className="text-sm font-medium text-slate-700">
                  이메일
                </label>
                <input
                  id="waitlist-email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                  placeholder="you@company.com"
                  autoFocus
                />
              </div>
              {error ? <p className="text-sm text-red-600">{error}</p> : null}
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  className="flex-1"
                  onClick={close}
                >
                  닫기
                </Button>
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? '등록 중...' : '알림 신청'}
                </Button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
