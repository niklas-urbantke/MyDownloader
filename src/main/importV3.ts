import { dialog } from 'electron'
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { randomUUID } from 'node:crypto'
import type { AppSettings, HistoryEntry } from '@shared/types'
import { updateSettings } from './settings'
import { importHistoryEntries } from './history'

interface V3Settings {
  download_folder?: string
  audio_format?: string
  audio_quality?: string
  download_subtitles?: boolean
  subtitle_language?: string
  speed_limit?: string
  theme?: string
  embed_thumbnail?: boolean
  embed_metadata?: boolean
}

interface V3HistoryEntry {
  url?: string
  title?: string
  timestamp?: string
}

const AUDIO_FORMATS = new Set(['mp3', 'm4a', 'opus', 'flac', 'wav'])

/**
 * Importiert settings.json und download_history.json aus MyDownloader v3.
 * Der Nutzer wählt den Ordner, in dem die v3-Dateien liegen.
 */
export async function importV3Data(): Promise<{
  ok: boolean
  settingsImported: number
  historyImported: number
}> {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory'],
    title: 'MyDownloader v3 Ordner wählen'
  })
  if (result.canceled || !result.filePaths[0]) {
    return { ok: false, settingsImported: 0, historyImported: 0 }
  }
  const dir = result.filePaths[0]

  let settingsImported = 0
  const settingsFile = join(dir, 'settings.json')
  if (existsSync(settingsFile)) {
    try {
      const v3 = JSON.parse(readFileSync(settingsFile, 'utf-8')) as V3Settings
      const patch: Partial<AppSettings> = {}
      if (v3.download_folder) patch.downloadFolder = v3.download_folder
      if (v3.audio_format === 'none') {
        patch.mode = 'video'
      } else if (v3.audio_format && AUDIO_FORMATS.has(v3.audio_format)) {
        patch.mode = 'audio'
        patch.audioFormat = v3.audio_format as AppSettings['audioFormat']
      }
      if (v3.audio_quality && ['0', '2', '5', '7', '9'].includes(v3.audio_quality)) {
        patch.audioQuality = v3.audio_quality as AppSettings['audioQuality']
      }
      if (typeof v3.download_subtitles === 'boolean') patch.writeSubtitles = v3.download_subtitles
      if (v3.subtitle_language) patch.subtitleLanguages = v3.subtitle_language
      if (typeof v3.speed_limit === 'string') patch.speedLimit = v3.speed_limit
      if (v3.theme === 'dark' || v3.theme === 'light') patch.theme = v3.theme
      if (typeof v3.embed_thumbnail === 'boolean') patch.embedThumbnail = v3.embed_thumbnail
      if (typeof v3.embed_metadata === 'boolean') patch.embedMetadata = v3.embed_metadata
      settingsImported = Object.keys(patch).length
      if (settingsImported > 0) updateSettings(patch)
    } catch {
      /* defekte settings.json überspringen */
    }
  }

  let historyImported = 0
  const historyFile = join(dir, 'download_history.json')
  if (existsSync(historyFile)) {
    try {
      const v3 = JSON.parse(readFileSync(historyFile, 'utf-8')) as V3HistoryEntry[]
      if (Array.isArray(v3)) {
        const entries: HistoryEntry[] = v3
          .filter((e) => e.url && e.title)
          .map((e) => ({
            id: randomUUID(),
            url: e.url!,
            title: e.title!,
            uploader: null,
            // v3-Format "YYYY-MM-DD HH:MM:SS" → ISO
            timestamp: e.timestamp
              ? new Date(e.timestamp.replace(' ', 'T')).toISOString()
              : new Date().toISOString(),
            mode: 'audio',
            format: 'mp3',
            destination: '',
            outputFiles: [],
            isPlaylist: /[?&]list=/.test(e.url!),
            status: 'completed'
          }))
        historyImported = importHistoryEntries(entries)
      }
    } catch {
      /* defekte download_history.json überspringen */
    }
  }

  return { ok: true, settingsImported, historyImported }
}
