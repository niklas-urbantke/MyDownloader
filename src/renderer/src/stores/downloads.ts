import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { DownloadItem, DownloadRequest } from '@shared/types'

export const useDownloadsStore = defineStore('downloads', () => {
  const items = ref<DownloadItem[]>([])
  const logs = ref<Record<string, string[]>>({})
  /** true = Warteschlange wird gerade abgearbeitet */
  const processing = ref(false)

  async function load(): Promise<void> {
    items.value = await window.api.downloads.list()
    processing.value = await window.api.downloads.queueState()
    window.api.downloads.onQueueState((p) => {
      processing.value = p
    })
    window.api.downloads.onChanged((item) => {
      const idx = items.value.findIndex((i) => i.id === item.id)
      if (idx === -1) items.value.push(item)
      else items.value[idx] = item
    })
    window.api.downloads.onLogLine(({ id, line }) => {
      const log = logs.value[id] ?? (logs.value[id] = [])
      log.push(line)
      if (log.length > 2000) log.splice(0, log.length - 2000)
    })
  }

  async function add(request: DownloadRequest): Promise<DownloadItem> {
    return window.api.downloads.add(request)
  }

  async function addMany(requests: DownloadRequest[]): Promise<DownloadItem[]> {
    return window.api.downloads.addMany(requests)
  }

  async function cancel(id: string): Promise<void> {
    await window.api.downloads.cancel(id)
  }

  async function pause(id: string): Promise<void> {
    await window.api.downloads.pause(id)
  }

  async function resume(id: string): Promise<void> {
    await window.api.downloads.resume(id)
  }

  async function retry(id: string): Promise<void> {
    await window.api.downloads.retry(id)
  }

  async function remove(id: string): Promise<void> {
    await window.api.downloads.remove(id)
    items.value = items.value.filter((i) => i.id !== id)
    delete logs.value[id]
  }

  async function clearFinished(): Promise<void> {
    const removed = await window.api.downloads.clearFinished()
    items.value = items.value.filter((i) => !removed.includes(i.id))
    for (const id of removed) delete logs.value[id]
  }

  async function fetchLog(id: string): Promise<string[]> {
    const log = await window.api.downloads.getLog(id)
    logs.value[id] = log
    return log
  }

  async function startQueue(): Promise<void> {
    await window.api.downloads.startQueue()
  }

  async function pauseQueue(): Promise<void> {
    await window.api.downloads.pauseQueue()
  }

  async function move(id: string, direction: 'up' | 'down'): Promise<void> {
    await window.api.downloads.move(id, direction)
    // Reihenfolge kommt aus dem Main-Process — Liste neu übernehmen
    items.value = await window.api.downloads.list()
  }

  const activeItems = computed(() =>
    items.value.filter(
      (i) =>
        i.status === 'downloading' || i.status === 'converting' || i.status === 'fetching-info'
    )
  )
  const queuedItems = computed(() => items.value.filter((i) => i.status === 'queued'))
  const pausedItems = computed(() => items.value.filter((i) => i.status === 'paused'))
  const errorItems = computed(() => items.value.filter((i) => i.status === 'error'))
  const completedToday = computed(() => {
    const today = new Date().toDateString()
    return items.value.filter(
      (i) => i.status === 'completed' && i.finishedAt && new Date(i.finishedAt).toDateString() === today
    )
  })

  return {
    items,
    logs,
    processing,
    load,
    add,
    addMany,
    cancel,
    pause,
    resume,
    retry,
    remove,
    clearFinished,
    fetchLog,
    startQueue,
    pauseQueue,
    move,
    activeItems,
    queuedItems,
    pausedItems,
    errorItems,
    completedToday
  }
})
