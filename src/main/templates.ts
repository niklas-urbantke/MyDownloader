import { randomUUID } from 'node:crypto'
import type { DownloadTemplate } from '@shared/types'
import { JsonStore } from './store'

let store: JsonStore<DownloadTemplate[]> | null = null
let cached: DownloadTemplate[] | null = null

function getStore(): JsonStore<DownloadTemplate[]> {
  if (!store) store = new JsonStore<DownloadTemplate[]>('templates.json', [])
  return store
}

export function listTemplates(): DownloadTemplate[] {
  if (!cached) {
    const loaded = getStore().load()
    cached = Array.isArray(loaded) ? loaded : []
  }
  return cached
}

/** Legt eine Vorlage an oder aktualisiert sie (Upsert über id). */
export function saveTemplate(template: DownloadTemplate): DownloadTemplate {
  const list = listTemplates()
  const saved: DownloadTemplate = { ...template, id: template.id || randomUUID() }
  const idx = list.findIndex((t) => t.id === saved.id)
  if (idx === -1) list.push(saved)
  else list[idx] = saved
  getStore().save(list)
  return saved
}

export function deleteTemplate(id: string): void {
  const list = listTemplates()
  const idx = list.findIndex((t) => t.id === id)
  if (idx !== -1) {
    list.splice(idx, 1)
    getStore().save(list)
  }
}
