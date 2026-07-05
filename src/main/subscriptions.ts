import { randomUUID } from 'node:crypto'
import { Notification } from 'electron'
import type { DownloadRequest, Subscription } from '@shared/types'
import { JsonStore } from './store'
import { probeUrl } from './ytdlp'
import { getSettings } from './settings'
import { listTemplates } from './templates'
import type { DownloadQueue } from './queue'

/**
 * Playlist-Abos (Issue #21): abonnierte Playlists/Kanäle werden periodisch
 * geprüft; nur neue Videos landen automatisch in der Queue.
 */

let store: JsonStore<Subscription[]> | null = null
let cached: Subscription[] | null = null
let onChangedCb: ((subs: Subscription[]) => void) | null = null
let queueRef: DownloadQueue | null = null
const checking = new Set<string>()

function getStore(): JsonStore<Subscription[]> {
  if (!store) store = new JsonStore<Subscription[]>('subscriptions.json', [])
  return store
}

export function listSubscriptions(): Subscription[] {
  if (!cached) {
    const loaded = getStore().load()
    cached = Array.isArray(loaded) ? loaded : []
  }
  return cached
}

function persist(): void {
  getStore().save(listSubscriptions())
  onChangedCb?.(listSubscriptions())
}

/** Baut die Download-Requests für neue Abo-Videos (Vorlage oder Defaults) */
function requestsFor(sub: Subscription, videoUrl: string, title: string): DownloadRequest[] {
  const base: DownloadRequest = { url: videoUrl, knownTitle: title, startNow: true }
  const tpl = sub.templateId ? listTemplates().find((t) => t.id === sub.templateId) : undefined
  if (!tpl) {
    return [
      sub.folder ? { ...base, overrides: { downloadFolder: sub.folder } } : base
    ]
  }
  const folderOverride = sub.folder || tpl.folder
  const videoReq: DownloadRequest = {
    ...base,
    overrides: {
      mode: 'video',
      videoContainer: tpl.videoContainer,
      videoQuality: tpl.videoQuality,
      writeSubtitles: tpl.writeSubtitles,
      ...(folderOverride ? { downloadFolder: folderOverride } : {})
    }
  }
  const audioReq: DownloadRequest = {
    ...base,
    overrides: {
      mode: 'audio',
      audioFormat: tpl.audioFormat,
      audioQuality: tpl.audioQuality,
      writeSubtitles: tpl.writeSubtitles,
      ...(sub.folder || tpl.audioFolder || tpl.folder
        ? { downloadFolder: sub.folder || tpl.audioFolder || tpl.folder }
        : {})
    }
  }
  if (tpl.mode === 'video') return [videoReq]
  if (tpl.mode === 'audio') return [audioReq]
  return [videoReq, audioReq]
}

/** Prüft ein Abo auf neue Videos und lädt sie herunter. */
export async function checkSubscription(id: string): Promise<number> {
  const sub = listSubscriptions().find((s) => s.id === id)
  if (!sub || checking.has(id)) return 0
  checking.add(id)
  try {
    const info = await probeUrl(sub.url)
    if (!info.isPlaylist) return 0
    const known = new Set(sub.knownVideoIds)
    const fresh = info.entries.filter((e) => e.id && !known.has(e.id))
    for (const entry of fresh) {
      if (!entry.url) continue
      for (const request of requestsFor(sub, entry.url, entry.title)) {
        queueRef?.add(request)
      }
      sub.knownVideoIds.push(entry.id)
    }
    sub.title = info.title || sub.title
    sub.lastCheckedAt = new Date().toISOString()
    sub.lastNewCount = fresh.length
    persist()
    if (fresh.length > 0 && getSettings().notifyOnComplete && Notification.isSupported()) {
      new Notification({
        title: 'MyDownloader',
        body: `♪ ${sub.title}: ${fresh.length} neue${fresh.length === 1 ? 'r Titel' : ' Titel'}`
      }).show()
    }
    return fresh.length
  } catch {
    sub.lastCheckedAt = new Date().toISOString()
    persist()
    return 0
  } finally {
    checking.delete(id)
  }
}

/**
 * Legt ein Abo an. Der aktuelle Bestand wird als „bekannt“ markiert —
 * geladen wird nur, was NACH dem Abonnieren erscheint.
 */
export async function addSubscription(
  url: string,
  options: { folder?: string; templateId?: string; intervalMinutes?: number }
): Promise<Subscription> {
  const info = await probeUrl(url)
  const sub: Subscription = {
    id: randomUUID(),
    url,
    title: info.isPlaylist ? info.title : info.title,
    enabled: true,
    folder: options.folder ?? '',
    templateId: options.templateId ?? '',
    intervalMinutes: Math.max(15, options.intervalMinutes ?? 360),
    lastCheckedAt: new Date().toISOString(),
    knownVideoIds: info.isPlaylist ? info.entries.map((e) => e.id).filter(Boolean) : [],
    lastNewCount: 0
  }
  listSubscriptions().push(sub)
  persist()
  return sub
}

export function updateSubscription(patch: Partial<Subscription> & { id: string }): void {
  const sub = listSubscriptions().find((s) => s.id === patch.id)
  if (!sub) return
  Object.assign(sub, patch)
  if (sub.intervalMinutes < 15) sub.intervalMinutes = 15
  persist()
}

export function removeSubscription(id: string): void {
  const list = listSubscriptions()
  const idx = list.findIndex((s) => s.id === id)
  if (idx !== -1) {
    list.splice(idx, 1)
    persist()
  }
}

/** Startet den periodischen Prüf-Loop (App-Start + jede Minute fälligkeitsbasiert). */
export function startSubscriptionScheduler(
  queue: DownloadQueue,
  onChanged: (subs: Subscription[]) => void
): void {
  queueRef = queue
  onChangedCb = onChanged

  const checkDue = (): void => {
    const now = Date.now()
    for (const sub of listSubscriptions()) {
      if (!sub.enabled) continue
      const last = sub.lastCheckedAt ? Date.parse(sub.lastCheckedAt) : 0
      if (now - last >= sub.intervalMinutes * 60 * 1000) {
        void checkSubscription(sub.id)
      }
    }
  }

  // Beim Start kurz warten (App-UI zuerst), dann fälligkeitsbasiert prüfen
  setTimeout(checkDue, 15_000)
  setInterval(checkDue, 60_000)
}
