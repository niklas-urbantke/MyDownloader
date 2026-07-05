import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DownloadTemplate } from '@shared/types'

export function emptyTemplate(): DownloadTemplate {
  return {
    id: '',
    name: '',
    mode: 'audio',
    audioFormat: 'mp3',
    audioQuality: '0',
    videoContainer: 'mp4',
    videoQuality: 'best',
    extraVideoQualities: [],
    writeSubtitles: false,
    folder: '',
    audioFolder: ''
  }
}

export const useTemplatesStore = defineStore('templates', () => {
  const entries = ref<DownloadTemplate[]>([])
  const loaded = ref(false)

  async function load(): Promise<void> {
    entries.value = await window.api.templates.list()
    loaded.value = true
  }

  async function save(template: DownloadTemplate): Promise<DownloadTemplate> {
    const saved = await window.api.templates.save({ ...template })
    const idx = entries.value.findIndex((t) => t.id === saved.id)
    if (idx === -1) entries.value.push(saved)
    else entries.value[idx] = saved
    return saved
  }

  async function remove(id: string): Promise<void> {
    await window.api.templates.remove(id)
    entries.value = entries.value.filter((t) => t.id !== id)
  }

  function byId(id: string): DownloadTemplate | undefined {
    return entries.value.find((t) => t.id === id)
  }

  return { entries, loaded, load, save, remove, byId }
})
