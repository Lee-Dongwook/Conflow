import { useCallback, useEffect, useRef, useState } from 'react'

import { Button } from '@conflow/ui'

import { userApi } from 'app/entities/user'
import { consentApi, type ConsentAccept } from 'app/features/consent'
import { ConsentForm } from 'app/features/consent'
import { supabase } from 'app/shared'

type LoginModalProps = {
  readonly open: boolean
  readonly onClose: () => void
}

type Mode = 'login' | 'signup'
type Step = 'credentials' | 'consent'

type SignupData = {
  readonly supabaseUuid: string
  readonly name: string
  readonly email: string
}

export const LoginModal = ({ open, onClose }: LoginModalProps) => {
  const [mode, setMode] = useState<Mode>('login')
  const [step, setStep] = useState<Step>('credentials')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [signupData, setSignupData] = useState<SignupData | null>(null)
  const backdropRef = useRef<HTMLDivElement>(null)

  const resetState = useCallback(() => {
    setMode('login')
    setStep('credentials')
    setName('')
    setEmail('')
    setPassword('')
    setError(null)
    setLoading(false)
    setSignupData(null)
  }, [])

  useEffect(() => {
    if (!open) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && step === 'credentials') {
        resetState()
        onClose()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [open, onClose, step, resetState])

  if (!open) return null

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const { error: authError } = await supabase.auth.signInWithPassword({ email, password })

    if (authError) {
      setError(authError.message)
    } else {
      resetState()
      onClose()
    }
    setLoading(false)
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const { data, error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { name } },
    })

    if (authError) {
      setError(authError.message)
      setLoading(false)
      return
    }

    if (!data.session || !data.user) {
      setError('인증 이메일을 확인해 주세요. 이메일의 링크를 클릭한 후 로그인해 주세요.')
      setLoading(false)
      return
    }

    setSignupData({ supabaseUuid: data.user.id, name, email })
    setStep('consent')
    setLoading(false)
  }

  const handleConsentComplete = async (consents: Record<string, boolean>) => {
    if (!signupData) return
    setError(null)
    setLoading(true)

    try {
      await userApi.create({
        name: signupData.name,
        email: signupData.email,
        supabaseUuid: signupData.supabaseUuid,
      })

      const consentPayload: readonly ConsentAccept[] = Object.entries(consents)
        .filter(([, accepted]) => accepted)
        .map(([type]) => ({ consentType: type as ConsentAccept['consentType'], version: '1.0' }))

      if (consentPayload.length > 0) {
        await consentApi.accept(consentPayload)
      }

      resetState()
      onClose()
    } catch (err) {
      const message = err instanceof Error ? err.message : '회원가입 중 오류가 발생했습니다.'
      setError(message)
      setLoading(false)
    }
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === backdropRef.current && step === 'credentials') {
      resetState()
      onClose()
    }
  }

  const switchMode = () => {
    setMode((prev) => (prev === 'login' ? 'signup' : 'login'))
    setError(null)
  }

  return (
    <div
      ref={backdropRef}
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      {step === 'consent' ? (
        <div className="w-full max-w-lg">
          {error ? (
            <p className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-center text-sm text-red-600">
              {error}
            </p>
          ) : null}
          {loading ? (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-xl">
              <p className="text-sm text-slate-500">계정을 생성하는 중...</p>
            </div>
          ) : (
            <ConsentForm onComplete={handleConsentComplete} />
          )}
        </div>
      ) : (
        <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-xl">
          <div className="mb-5 text-center">
            <h2 className="text-lg font-semibold text-slate-900">
              {mode === 'login' ? '로그인' : '회원가입'}
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              {mode === 'login'
                ? '이메일로 로그인하세요'
                : '새 계정을 만들어 시작하세요'}
            </p>
          </div>
          <form
            onSubmit={mode === 'login' ? handleLogin : handleSignup}
            className="flex flex-col gap-4"
          >
            {mode === 'signup' ? (
              <div className="flex flex-col gap-1.5">
                <label htmlFor="auth-name" className="text-sm font-medium text-slate-700">
                  이름
                </label>
                <input
                  id="auth-name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                  placeholder="홍길동"
                  autoFocus
                />
              </div>
            ) : null}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="auth-email" className="text-sm font-medium text-slate-700">
                이메일
              </label>
              <input
                id="auth-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
                placeholder="admin@conflow.io"
                autoFocus={mode === 'login'}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="auth-password" className="text-sm font-medium text-slate-700">
                비밀번호
              </label>
              <input
                id="auth-password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              />
            </div>
            {error ? <p className="text-sm text-red-600">{error}</p> : null}
            <div className="flex gap-2">
              <Button
                type="button"
                variant="secondary"
                className="flex-1"
                onClick={() => {
                  resetState()
                  onClose()
                }}
              >
                취소
              </Button>
              <Button type="submit" disabled={loading} className="flex-1">
                {loading
                  ? (mode === 'login' ? '로그인 중...' : '가입 중...')
                  : (mode === 'login' ? '로그인' : '다음')}
              </Button>
            </div>
          </form>
          <p className="mt-4 text-center text-sm text-slate-500">
            {mode === 'login' ? '계정이 없으신가요? ' : '이미 계정이 있으신가요? '}
            <button
              type="button"
              onClick={switchMode}
              className="font-medium text-teal-600 hover:text-teal-800"
            >
              {mode === 'login' ? '회원가입' : '로그인'}
            </button>
          </p>
        </div>
      )}
    </div>
  )
}
