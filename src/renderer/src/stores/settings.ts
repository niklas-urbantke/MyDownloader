import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { AppSettings } from '@shared/types'
import { applyLocale } from '../i18n'

/**
 * Setzt das Erscheinungsbild und die Darstellungswahl am Wurzelelement.
 * Vier unabhaengige Achsen, genau wie in den Einstellungen sichtbar:
 *   data-theme   hell oder dunkel (system folgt dem Betriebssystem)
 *   data-style   classic (bisheriger Look) oder aero (urbDesign)
 *   data-accent  einer der sechs Markentoene, nur im Stil aero wirksam
 *   data-glass / data-vivid  die beiden Schalter, nur im Stil aero wirksam
 */
function applyAppearance(s: AppSettings): void {
  const root = document.documentElement
  const resolved =
    s.theme === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : s.theme
  root.dataset.theme = resolved
  root.dataset.style = s.style
  root.dataset.accent = s.accent
  root.dataset.glass = s.glass ? 'on' : 'off'
  root.dataset.vivid = s.vivid ? 'on' : 'off'
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings | null>(null)
  const loaded = ref(false)
  let saveTimer: ReturnType<typeof setTimeout> | null = null

  async function load(): Promise<void> {
    const firstLoad = !loaded.value
    settings.value = await window.api.settings.get()
    loaded.value = true
    applyAppearance(settings.value)
    applyLocale(settings.value.locale)
    if (!firstLoad) return

    // Änderungen automatisch (debounced) persistieren
    watch(
      settings,
      (val) => {
        if (!val) return
        applyAppearance(val)
        applyLocale(val.locale)
        if (saveTimer) clearTimeout(saveTimer)
        saveTimer = setTimeout(() => {
          saveTimer = null
          void window.api.settings.set({ ...val })
        }, 400)
      },
      { deep: true }
    )

    // Beim Schließen darf keine debounced Änderung verloren gehen (Issue #7):
    // ausstehende Saves sofort und ohne Antwort-Roundtrip rausschicken.
    window.addEventListener('pagehide', () => {
      if (saveTimer && settings.value) {
        clearTimeout(saveTimer)
        saveTimer = null
        window.api.settings.flush({ ...settings.value })
      }
    })

    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', () => settings.value && applyAppearance(settings.value))
  }

  async function pickDownloadFolder(): Promise<void> {
    const folder = await window.api.settings.pickFolder()
    if (folder && settings.value) settings.value.downloadFolder = folder
  }

  return { settings, loaded, load, pickDownloadFolder }
})
