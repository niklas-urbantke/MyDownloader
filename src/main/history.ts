import { randomUUID } from 'node:crypto'
import type { DownloadItem, HistoryEntry } from '@shared/types'
import { JsonStore } from './store'

const MAX_ENTRIES = 1000

let store: JsonStore<HistoryEntry[]> | null = null
let cached: HistoryEntry[] | null = null

function getStore(): JsonStore<HistoryEntry[]> {
  if (!store) store = new JsonStore<HistoryEntry[]>('history.json', [])
  return store
}

export function listHistory(): HistoryEntry[] {
  if (!cached) {
    const loaded = getStore().load()
    cached = Array.isArray(loaded) ? loaded : []
  }
  return cached
}

export function addHistoryEntry(item: DownloadItem): HistoryEntry | null {
  if (item.status !== 'completed' && item.status !== 'error' && item.status !== 'cancelled') {
    return null
  }
  const entry: HistoryEntry = {
    id: randomUUID(),
    url: item.url,
    title: item.title,
    uploader: item.uploader,
    timestamp: item.finishedAt ?? new Date().toISOString(),
    mode: item.mode,
    format: item.format,
    destination: item.destination,
    outputFiles: item.outputFiles,
    isPlaylist: item.isPlaylist,
    status: item.status
  }
  const list = listHistory()
  list.unshift(entry)
  if (list.length > MAX_ENTRIES) list.length = MAX_ENTRIES
  getStore().save(list)
  return entry
}

export function importHistoryEntries(entries: HistoryEntry[]): number {
  const list = listHistory()
  const existingUrls = new Set(list.map((e) => `${e.url}@${e.timestamp}`))
  let added = 0
  for (const entry of entries) {
    if (existingUrls.has(`${entry.url}@${entry.timestamp}`)) continue
    list.push(entry)
    added++
  }
  list.sort((a, b) => b.timestamp.localeCompare(a.timestamp))
  if (list.length > MAX_ENTRIES) list.length = MAX_ENTRIES
  getStore().save(list)
  return added
}

export function removeHistoryEntry(id: string): void {
  const list = listHistory()
  const idx = list.findIndex((e) => e.id === id)
  if (idx !== -1) {
    list.splice(idx, 1)
    getStore().save(list)
  }
}

export function clearHistory(): void {
  cached = []
  getStore().save([])
}
