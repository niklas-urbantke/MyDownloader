import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { AppSettings } from '@shared/types'
import { applyLocale } from '../i18n'

function applyTheme(theme: AppSettings['theme']): void {
  const resolved =
    theme === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : theme
  document.documentElement.dataset.theme = resolved
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings | null>(null)
  const loaded = ref(false)
  let saveTimer: ReturnType<typeof setTimeout> | null = null

  async function load(): Promise<void> {
    settings.value = await window.api.settings.get()
    loaded.value = true
    applyTheme(settings.value.theme)
    applyLocale(settings.value.locale)

    // Änderungen automatisch (debounced) persistieren
    watch(
      settings,
      (val) => {
        if (!val) return
        applyTheme(val.theme)
        applyLocale(val.locale)
        if (saveTimer) clearTimeout(saveTimer)
        saveTimer = setTimeout(() => {
          void window.api.settings.set({ ...val })
        }, 400)
      },
      { deep: true }
    )

    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', () => settings.value && applyTheme(settings.value.theme))
  }

  async function pickDownloadFolder(): Promise<void> {
    const folder = await window.api.settings.pickFolder()
    if (folder && settings.value) settings.value.downloadFolder = folder
  }

  return { settings, loaded, load, pickDownloadFolder }
})
