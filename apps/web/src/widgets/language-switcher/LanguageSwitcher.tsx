import { cn } from '@conflow/ui'

import { useLanguage } from 'app/shared/i18n'

const LABELS: Record<'ko' | 'en', string> = {
  ko: '한국어',
  en: 'English',
}

const SHORT: Record<'ko' | 'en', string> = {
  ko: 'KO',
  en: 'EN',
}

export type LanguageSwitcherProps = {
  readonly variant?: 'segmented' | 'compact'
  readonly className?: string
}

export const LanguageSwitcher = ({ variant = 'segmented', className }: LanguageSwitcherProps) => {
  const { current, change, supported } = useLanguage()

  if (variant === 'compact') {
    return (
      <div className={cn('inline-flex items-center gap-1 text-[11px]', className)}>
        {supported.map((lng) => (
          <button
            key={lng}
            type="button"
            onClick={() => {
              void change(lng)
            }}
            className={cn(
              'rounded px-1.5 py-0.5 transition-colors',
              current === lng ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-800',
            )}
            aria-pressed={current === lng}
          >
            {SHORT[lng]}
          </button>
        ))}
      </div>
    )
  }

  return (
    <div
      className={cn('flex rounded-lg bg-slate-100 p-0.5 text-[11px] font-medium', className)}
      role="group"
      aria-label="Language"
    >
      {supported.map((lng) => (
        <button
          key={lng}
          type="button"
          onClick={() => {
            void change(lng)
          }}
          className={cn(
            'flex-1 rounded-md px-1.5 py-1.5 transition-colors',
            current === lng
              ? 'bg-white text-teal-800 shadow-sm'
              : 'text-slate-500 hover:text-slate-800',
          )}
          aria-pressed={current === lng}
        >
          {LABELS[lng]}
        </button>
      ))}
    </div>
  )
}
