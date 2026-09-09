import { app } from 'electron'
import { join } from 'node:path'
import type { AppSettings } from '@shared/types'
import { JsonStore } from './store'

export function defaultSettings(): AppSettings {
  return {
    downloadFolder: join(app.getPath('downloads'), 'MyDownloader'),
    mode: 'audio',
    audioFormat: 'mp3',
    audioQuality: '0',
    videoContainer: 'mp4',
    videoQuality: 'best',
    embedThumbnail: true,
    embedMetadata: true,
    writeSubtitles: false,
    subtitleLanguages: 'de,en',
    speedLimit: '',
    concurrency: 2,
    scheduleEnabled: false,
    scheduleFrom: '02:00',
    scheduleTo: '06:00',
    sponsorBlock: false,
    extraArgs: '',
    playlistSubfolder: true,
    filenameTemplate: 'title',
    customFilenameTemplate: '{artist}/{album}/{track} - {title}',
    normalizeAudio: 'off',
    targetLufs: -14,
    fetchLyrics: false,
    theme: 'system',
    locale: 'system',
    notifyOnComplete: true,
    clipboardWatcher: false,
    sidebarOpen: true,
    onboardingDone: false,
    closeToTray: true,
    autoUpdate: 'notify',
    useAccountCookies: false,
    spotifyClientId: '',
    // Standard YouTube Music: die normale Suche liefert fast immer das
    // Musikvideo, eine Live- oder Lyric-Fassung statt der Albumversion
    musicSource: 'ytmusic'
  }
}

let store: JsonStore<AppSettings> | null = null
let cached: AppSettings | null = null

function getStore(): JsonStore<AppSettings> {
  if (!store) store = new JsonStore<AppSettings>('settings.json', defaultSettings())
  return store
}

export function getSettings(): AppSettings {
  if (!cached) cached = getStore().load()
  return cached
}

export function updateSettings(patch: Partial<AppSettings>): AppSettings {
  cached = { ...getSettings(), ...patch }
  getStore().save(cached)
  return cached
}
