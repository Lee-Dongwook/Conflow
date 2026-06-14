import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'

import en from './locales/en.json'
import ko from './locales/ko.json'

export const SUPPORTED_LANGUAGES = ['ko', 'en'] as const
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]

export const DEFAULT_NS = 'translation' as const

export const resources = {
  ko: { translation: ko },
  en: { translation: en },
} as const

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ko',
    supportedLngs: SUPPORTED_LANGUAGES,
    defaultNS: DEFAULT_NS,
    ns: [DEFAULT_NS],
    returnNull: false,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'conflow.lang',
    },
  })

const syncHtmlLang = (lng: string) => {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lng
  }
}

syncHtmlLang(i18n.resolvedLanguage ?? i18n.language)
i18n.on('languageChanged', syncHtmlLang)

export default i18n
