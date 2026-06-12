import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { HistoryEntry } from '@shared/types'

export const useHistoryStore = defineStore('history', () => {
  const entries = ref<HistoryEntry[]>([])
  const loaded = ref(false)

  async function load(): Promise<void> {
    entries.value = await window.api.history.list()
    loaded.value = true
  }

  async function remove(id: string): Promise<void> {
    await window.api.history.remove(id)
    entries.value = entries.value.filter((e) => e.id !== id)
  }

  async function clear(): Promise<void> {
    await window.api.history.clear()
    entries.value = []
  }

  return { entries, loaded, load, remove, clear }
})
