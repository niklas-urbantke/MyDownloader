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
  /** Downloads nur innerhalb eines täglichen Zeitfensters ausführen (Issue #22) */
  scheduleEnabled: boolean
  /** Fenster-Beginn "HH:MM" */
  scheduleFrom: string
  /** Fenster-Ende "HH:MM" (kleiner als Beginn = über Mitternacht) */
  scheduleTo: string
  /** SponsorBlock-Segmente automatisch entfernen */
  sponsorBlock: boolean
  /** Zusätzliche yt-dlp-Argumente (Profi-Option) */
  extraArgs: string
  /** Playlist-Einträge in Unterordner mit Playlist-Namen */
  playlistSubfolder: boolean
  /** Dateinamen-Schema: 'custom' nutzt customFilenameTemplate (Issue #28) */
  filenameTemplate: 'title' | 'artist-title' | 'index-title' | 'custom'
  /** Eigenes Schema mit Platzhaltern {artist} {album} {title} {track} {year} {playlist} */
  customFilenameTemplate: string
  /** Lautstärke-Normalisierung nach Audio-Downloads (Issue #26) */
  normalizeAudio: 'off' | 'replaygain' | 'loudnorm'
  /** Ziel-Lautheit in LUFS (Standard -14) */
  targetLufs: number
  /** Songtexte automatisch suchen und einbetten (Issue #27) */
  fetchLyrics: boolean
  theme: ThemeName
  locale: LocaleName
  notifyOnComplete: boolean
  clipboardWatcher: boolean
  /** Seitenleiste beim Start eingeblendet lassen */
  sidebarOpen: boolean
  /** Einrichtungsassistent wurde abgeschlossen (Issue #31) */
  onboardingDone: boolean
  /** Angemeldete Konto-Cookies an yt-dlp durchreichen (Issue #13) */
  useAccountCookies: boolean
  /** Spotify-API Client-ID des Nutzers (Issue #35) */
  spotifyClientId: string
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
  /** Anzahl der Kapitel (0 = keine) — Basis für das Kapitel-Splitting (Issue #23) */
  chapterCount: number
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
  /** Nur diesen Zeitbereich laden, Format "hh:mm:ss" (Issue #24) */
  sectionFrom?: string
  sectionTo?: string
  /** Video anhand seiner Kapitel in Einzeldateien aufteilen (Issue #23) */
  splitChapters?: boolean
  /** Dateinamen-Zusatz, z. B. " [1080p]" bei Multi-Qualitäts-Downloads (Issue #10) */
  filenameSuffix?: string
  /** Geplanter Startzeitpunkt (ISO 8601) — vorher bleibt der Download liegen (Issue #22) */
  scheduledAt?: string
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
  /** Geplanter Startzeitpunkt (ISO), null = sofort verfügbar */
  scheduledAt: string | null
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
  /**
   * Zusätzliche Qualitätsstufen, die parallel geladen werden (Issue #10).
   * Jede weitere Stufe erzeugt einen eigenen Queue-Eintrag mit Suffix im Dateinamen.
   */
  extraVideoQualities?: VideoQuality[]
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
// Playlist-Abos (Issue #21)
// ---------------------------------------------------------------------------

export interface Subscription {
  id: string
  url: string
  title: string
  enabled: boolean
  /** Zielordner (leer = globaler Download-Ordner) */
  folder: string
  /** Vorlage für neue Downloads ('' = globale Einstellungen) */
  templateId: string
  /** Prüfintervall in Minuten */
  intervalMinutes: number
  lastCheckedAt: string | null
  /** Bereits bekannte Video-IDs — nur Neues wird geladen */
  knownVideoIds: string[]
  /** Zuletzt gefundene neue Titel (Anzeige) */
  lastNewCount: number
}

// ---------------------------------------------------------------------------
// Spotify-Import (Issue #35)
// ---------------------------------------------------------------------------

export interface SpotifyStatus {
  configured: boolean
  loggedIn: boolean
  displayName: string | null
}

export interface SpotifyTrack {
  artist: string
  title: string
  album: string | null
  durationSeconds: number | null
}

export interface SpotifyPlaylist {
  title: string
  owner: string | null
  tracks: SpotifyTrack[]
}

// ---------------------------------------------------------------------------
// Statistiken (Issue #36)
// ---------------------------------------------------------------------------

export interface StatsSummary {
  totalDownloads: number
  completed: number
  errors: number
  /** Gesamtgröße aller noch vorhandenen Dateien in Bytes */
  totalBytes: number
  /** Anzahl pro Monat, älteste zuerst — [{ month: '2026-01', count }] */
  perMonth: { month: string; count: number }[]
  topUploaders: { name: string; count: number }[]
  formats: { format: string; count: number }[]
}

// ---------------------------------------------------------------------------
// Konto (Issue #13)
// ---------------------------------------------------------------------------

export interface AccountStatus {
  loggedIn: boolean
  cookieFile: string | null
}

// ---------------------------------------------------------------------------
// Metadaten (Tag-Editor, Issue #25)
// ---------------------------------------------------------------------------

export interface TrackTags {
  title: string
  artist: string
  album: string
  albumArtist: string
  track: string
  genre: string
  date: string
  comment: string
}

export interface MusicBrainzSuggestion {
  title: string
  artist: string
  album: string | null
  date: string | null
  score: number
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
  /** Direkte Stream-URL für die Hörprobe (Issue #29) */
  mediaPreviewUrl: 'media:preview-url',
  // Downloads
  downloadAdd: 'download:add',
  downloadAddMany: 'download:add-many',
  downloadCancel: 'download:cancel',
  downloadPause: 'download:pause',
  downloadResume: 'download:resume',
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
  // Metadaten (Issue #25)
  metaReadTags: 'meta:read-tags',
  metaWriteTags: 'meta:write-tags',
  metaSearchMusicBrainz: 'meta:search-musicbrainz',
  metaPickImage: 'meta:pick-image',
  // Verlauf
  historyList: 'history:list',
  historyClear: 'history:clear',
  historyRemove: 'history:remove',
  // Playlist-Abos (Issue #21)
  subsList: 'subs:list',
  subsAdd: 'subs:add',
  subsUpdate: 'subs:update',
  subsRemove: 'subs:remove',
  subsCheckNow: 'subs:check-now',
  subsChanged: 'subs:changed',
  // Konto (Issue #13)
  accountStatus: 'account:status',
  accountLogin: 'account:login',
  accountLogout: 'account:logout',
  // Spotify (Issue #35)
  spotifyStatus: 'spotify:status',
  spotifyLogin: 'spotify:login',
  spotifyLogout: 'spotify:logout',
  spotifyGetPlaylist: 'spotify:get-playlist',
  // Statistiken (Issue #36)
  statsCompute: 'stats:compute',
  // System
  binariesStatus: 'binaries:status',
  binariesUpdateYtDlp: 'binaries:update-ytdlp',
  importV3: 'import:v3',
  appInfo: 'app:info',
  openPath: 'shell:open-path',
  showInFolder: 'shell:show-in-folder',
  openExternal: 'shell:open-external'
} as const
