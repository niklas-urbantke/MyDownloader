import { createI18n } from 'vue-i18n'
import de from './de.json'
import en from './en.json'

export type MessageSchema = typeof de

function systemLocale(): 'de' | 'en' {
  return navigator.language.toLowerCase().startsWith('de') ? 'de' : 'en'
}

export const i18n = createI18n({
  legacy: false,
  locale: systemLocale(),
  fallbackLocale: 'en',
  messages: { de, en }
})

/** Stellt die UI-Sprache um ('system' nutzt die OS-Sprache). */
export function applyLocale(locale: 'de' | 'en' | 'system'): void {
  i18n.global.locale.value = locale === 'system' ? systemLocale() : locale
}
