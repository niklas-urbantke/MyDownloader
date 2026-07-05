/**
 * Gemeinsame Typen zwischen Main-, Preload- und Renderer-Prozess.
 * Diese Datei ist die einzige Quelle der Wahrheit für die IPC-Verträge.
 */

// ---------------------------------------------------------------------------
// Einstellungen
// ---------------------------------------------------------------------------

export type AudioFormat = 'mp3' | 'm4a' | 'opus' | 'flac' | 'wav'
export type VideoContainer = 'mp4' | 'mkv' | 'webm'
export type VideoQuality = 'best' | '2160' | '1440' | '1080' | '720' | '480'
export type DownloadMode = 'audio' | 'video'
export type ThemeName = 'light' | 'dark' | 'system'
export type LocaleName = 'de' | 'en' | 'system'

export interface AppSettings {
  downloadFolder: string
  mode: DownloadMode
  audioFormat: AudioFormat
  /** yt-dlp Audioqualität: '0' (beste) bis '9' (kleinste) */
  audioQuality: '0' | '2' | '5' | '7' | '9'
  videoContainer: VideoContainer
  videoQuality: VideoQuality
  embedThumbnail: boolean
  embedMetadata: boolean
  writeSubtitles: boolean
  subtitleLanguages: string
  /** MB/s, leer = unbegrenzt */
  speedLimit: string
  /** Anzahl paralleler Downloads (1–5) */
  concurrency: number
  /** SponsorBlock-Segmente automatisch entfernen */
  sponsorBlock: boolean
  /** Zusätzliche yt-dlp-Argumente (Profi-Option) */
  extraArgs: string
  /** Playlist-Einträge in Unterordner mit Playlist-Namen */
  playlistSubfolder: boolean
  /** Dateinamen-Schema: 'title' | 'artist-title' | 'index-title' */
  filenameTemplate: 'title' | 'artist-title' | 'index-title'
  theme: ThemeName
  locale: LocaleName
  notifyOnComplete: boolean
  clipboardWatcher: boolean
  /** Seitenleiste beim Start eingeblendet lassen */
  sidebarOpen: boolean
}

// ---------------------------------------------------------------------------
// Medien-Infos (Vorschau)
// ---------------------------------------------------------------------------

export interface VideoInfo {
  id: string
  url: string
  title: string
  uploader: string
  durationSeconds: number | null
  thumbnailUrl: string | null
  viewCount: number | null
  isPlaylist: false
}

export interface PlaylistEntryInfo {
  id: string
  url: string
  title: string
  uploader: string | null
  durationSeconds: number | null
}

export interface PlaylistInfo {
  id: string
  url: string
  title: string
  uploader: string | null
  entryCount: number
  entries: PlaylistEntryInfo[]
  isPlaylist: true
}

export type MediaInfo = VideoInfo | PlaylistInfo

// ---------------------------------------------------------------------------
// Downloads / Queue
// ---------------------------------------------------------------------------

export type DownloadStatus =
  | 'queued'
  | 'fetching-info'
  | 'downloading'
  | 'converting'
  | 'completed'
  | 'error'
  | 'cancelled'
  | 'paused'

export interface DownloadRequest {
  url: string
  /** true = sofort starten; false/undefined = wartet, bis die Queue gestartet wird */
  startNow?: boolean
  /** Überschreibt die globalen Einstellungen für diesen Download (optional) */
  overrides?: Partial<
    Pick<
      AppSettings,
      | 'mode'
      | 'audioFormat'
      | 'audioQuality'
      | 'videoContainer'
      | 'videoQuality'
      | 'downloadFolder'
      | 'writeSubtitles'
    >
  >
  /** Anzeigetitel, falls schon bekannt (z. B. aus der Vorschau) */
  knownTitle?: string
}

export interface DownloadProgress {
  /** 0–100, -1 = unbekannt */
  percent: number
  downloadedBytes: number
  totalBytes: number | null
  /** Bytes pro Sekunde */
  speed: number | null
  /** Sekunden */
  eta: number | null
  /** Bei Playlists: aktueller Eintrag */
  playlistIndex: number | null
  playlistCount: number | null
}

export interface DownloadItem {
  id: string
  url: string
  title: string
  uploader: string | null
  thumbnailUrl: string | null
  status: DownloadStatus
  progress: DownloadProgress
  mode: DownloadMode
  format: string
  /** Zielordner */
  destination: string
  /** Fertige Datei(en) */
  outputFiles: string[]
  errorMessage: string | null
  /** Log-Zeilen des yt-dlp-Prozesses */
  addedAt: string
  startedAt: string | null
  finishedAt: string | null
  isPlaylist: boolean
}

// ---------------------------------------------------------------------------
// Vorlagen (Download-Presets)
// ---------------------------------------------------------------------------

export interface DownloadTemplate {
  id: string
  name: string
  /** 'both' lädt Video UND Audio (zwei Queue-Einträge) */
  mode: DownloadMode | 'both'
  audioFormat: AudioFormat
  audioQuality: AppSettings['audioQuality']
  videoContainer: VideoContainer
  videoQuality: VideoQuality
  writeSubtitles: boolean
  /** Zielordner (leer = globaler Download-Ordner); bei 'both' der Video-Ordner */
  folder: string
  /** Separater Audio-Ordner im 'both'-Modus (leer = folder) */
  audioFolder: string
}

// ---------------------------------------------------------------------------
// Verlauf
// ---------------------------------------------------------------------------

export interface HistoryEntry {
  id: string
  url: string
  title: string
  uploader: string | null
  /** ISO-Zeitstempel */
  timestamp: string
  mode: DownloadMode
  format: string
  destination: string
  outputFiles: string[]
  isPlaylist: boolean
  status: 'completed' | 'error' | 'cancelled'
}

// ---------------------------------------------------------------------------
// Binaries / System
// ---------------------------------------------------------------------------

export interface BinaryStatus {
  ytDlp: { available: boolean; path: string | null; version: string | null }
  ffmpeg: { available: boolean; path: string | null; version: string | null }
}

export interface AppInfo {
  version: string
  platform: NodeJS.Platform
  arch: string
  electronVersion: string
  userDataPath: string
}

// ---------------------------------------------------------------------------
// IPC-Kanäle
// ---------------------------------------------------------------------------

export const IPC = {
  // Settings
  settingsGet: 'settings:get',
  settingsSet: 'settings:set',
  /** Fire-and-forget-Variante für den Fensterschluss (kein Antwort-Roundtrip) */
  settingsFlush: 'settings:flush',
  settingsPickFolder: 'settings:pick-folder',
  // Media-Infos
  mediaProbe: 'media:probe',
  // Downloads
  downloadAdd: 'download:add',
  downloadAddMany: 'download:add-many',
  downloadCancel: 'download:cancel',
  downloadRetry: 'download:retry',
  downloadRemove: 'download:remove',
  downloadClearFinished: 'download:clear-finished',
  downloadList: 'download:list',
  downloadGetLog: 'download:get-log',
  downloadQueueStart: 'download:queue-start',
  downloadQueuePause: 'download:queue-pause',
  downloadQueueState: 'download:queue-state',
  downloadMove: 'download:move',
  // Events (Main -> Renderer)
  downloadChanged: 'download:changed',
  downloadLogLine: 'download:log-line',
  clipboardUrl: 'clipboard:url',
  // Vorlagen
  templatesList: 'templates:list',
  templatesSave: 'templates:save',
  templatesDelete: 'templates:delete',
  // Verlauf
  historyList: 'history:list',
  historyClear: 'history:clear',
  historyRemove: 'history:remove',
  // System
  binariesStatus: 'binaries:status',
  binariesUpdateYtDlp: 'binaries:update-ytdlp',
  importV3: 'import:v3',
  appInfo: 'app:info',
  openPath: 'shell:open-path',
  showInFolder: 'shell:show-in-folder',
  openExternal: 'shell:open-external'
} as const
