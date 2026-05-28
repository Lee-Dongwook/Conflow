import { useCallback, useEffect, useSyncExternalStore } from 'react'

export type ThemeChoice = 'light' | 'system' | 'dark'

const STORAGE_KEY = 'conflow-theme'

const getSnapshot = (): ThemeChoice => {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark' || stored === 'system') return stored
  return 'system'
}

const getServerSnapshot = (): ThemeChoice => 'system'

const listeners = new Set<() => void>()

const subscribe = (cb: () => void) => {
  listeners.add(cb)
  return () => {
    listeners.delete(cb)
  }
}

const applyTheme = (choice: ThemeChoice) => {
  const isDark =
    choice === 'dark' ||
    (choice === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  document.documentElement.classList.toggle('dark', isDark)
}

export const useTheme = () => {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)

  const setTheme = useCallback((next: ThemeChoice) => {
    localStorage.setItem(STORAGE_KEY, next)
    applyTheme(next)
    for (const cb of listeners) cb()
  }, [])

  useEffect(() => {
    applyTheme(theme)

    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const onChange = () => {
      if (getSnapshot() === 'system') applyTheme('system')
    }
    mql.addEventListener('change', onChange)
    return () => {
      mql.removeEventListener('change', onChange)
    }
  }, [theme])

  return { theme, setTheme } as const
}
