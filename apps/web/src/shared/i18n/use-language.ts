import { useCallback } from 'react'
import { useTranslation } from 'react-i18next'

import { SUPPORTED_LANGUAGES, type SupportedLanguage } from './i18n'

const isSupported = (value: string): value is SupportedLanguage =>
  (SUPPORTED_LANGUAGES as readonly string[]).includes(value)

export const useLanguage = () => {
  const { i18n } = useTranslation()
  const current: SupportedLanguage = isSupported(i18n.resolvedLanguage ?? i18n.language)
    ? ((i18n.resolvedLanguage ?? i18n.language) as SupportedLanguage)
    : 'ko'

  const change = useCallback(
    async (lang: SupportedLanguage) => {
      await i18n.changeLanguage(lang)
    },
    [i18n],
  )

  return { current, change, supported: SUPPORTED_LANGUAGES }
}
