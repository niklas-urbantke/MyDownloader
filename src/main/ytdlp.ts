import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { dirname } from 'node:path'
import type { AppSettings, DownloadRequest, MediaInfo, PlaylistEntryInfo } from '@shared/types'
import { getYtDlpPath, getFfmpegPath } from './binaries'

const execFileP = promisify(execFile)

/** Maschinell parsebare Fortschritts-Zeilen (siehe queue.ts) */
export const PROGRESS_PREFIX = 'MDPROGRESS|'
export const OUTPUT_PREFIX = 'MDOUTPUT|'

/**
 * yt-dlp braucht für YouTube eine JavaScript-Runtime (Node >= 22).
 * Electron bringt Node mit: mit ELECTRON_RUN_AS_NODE=1 verhält sich die
 * eigene Executable wie ein normales Node — damit ist die App vollständig
 * self-contained, ohne Deno/Node-Extra-Download.
 */
export function jsRuntimeArgs(): string[] {
  return ['--js-runtimes', `node:${process.execPath}`]
}

export function ytDlpEnv(): NodeJS.ProcessEnv {
  return { ...process.env, ELECTRON_RUN_AS_NODE: '1' }
}

export class YtDlpMissingError extends Error {
  constructor() {
    super('yt-dlp binary not found')
  }
}

/** Zerlegt eine Argument-Zeile unter Beachtung von "..." und '...' */
export function splitArgs(line: string): string[] {
  const out: string[] = []
  const re = /"([^"]*)"|'([^']*)'|(\S+)/g
  let m: RegExpExecArray | null
  while ((m = re.exec(line)) !== null) {
    out.push(m[1] ?? m[2] ?? m[3] ?? '')
  }
  return out.filter((a) => a.length > 0)
}

function outputTemplate(settings: AppSettings, isPlaylist: boolean, suffix = ''): string {
  let name: string
  switch (settings.filenameTemplate) {
    case 'artist-title':
      name = '%(artist,creator,channel,uploader)s - %(title)s'
      break
    case 'index-title':
      name = '%(playlist_index&{} - |)s%(title)s'
      break
    default:
      name = '%(title)s'
  }
  name = `${name}${suffix}.%(ext)s`
  if (isPlaylist && settings.playlistSubfolder) {
    return `%(playlist_title,playlist_id)s/${name}`
  }
  return name
}

/** Akzeptiert "ss", "mm:ss" oder "hh:mm:ss" */
export function isValidTimestamp(value: string): boolean {
  return /^\d{1,3}(:[0-5]?\d){0,2}$/.test(value.trim())
}

export interface BuiltCommand {
  bin: string
  args: string[]
}

/**
 * Baut das komplette yt-dlp-Kommando für einen Download.
 * Fortschritt und fertige Dateipfade werden über eindeutige Präfixe
 * (MDPROGRESS|…, MDOUTPUT|…) auf stdout gemeldet.
 */
export async function buildDownloadCommand(
  request: DownloadRequest,
  settings: AppSettings,
  isPlaylist: boolean
): Promise<BuiltCommand> {
  const bin = await getYtDlpPath()
  if (!bin) throw new YtDlpMissingError()

  const merged: AppSettings = { ...settings, ...request.overrides }
  const args: string[] = []

  args.push(...jsRuntimeArgs())

  // Fortschritt maschinenlesbar, eine Zeile pro Update
  args.push(
    '--newline',
    '--progress-template',
    `download:${PROGRESS_PREFIX}%(progress.downloaded_bytes)s|%(progress.total_bytes)s|%(progress.total_bytes_estimate)s|%(progress.speed)s|%(progress.eta)s|%(info.playlist_index)s|%(info.n_entries)s`,
    '--print',
    `after_move:${OUTPUT_PREFIX}%(filepath)s`,
    '--no-quiet'
  )

  // Robustheit
  args.push('--retries', '10', '--fragment-retries', '10', '--no-overwrites')

  // FFmpeg-Pfad explizit setzen (gebündeltes Binary)
  const ffmpeg = await getFfmpegPath()
  if (ffmpeg) args.push('--ffmpeg-location', dirname(ffmpeg))

  // Ziel
  args.push('-P', merged.downloadFolder, '-o', outputTemplate(merged, isPlaylist, request.filenameSuffix ?? ''))
  args.push('--windows-filenames')

  // Nur einen Zeitbereich laden (Issue #24)
  if (request.sectionFrom || request.sectionTo) {
    const from = request.sectionFrom?.trim() || '0:00'
    const to = request.sectionTo?.trim() || 'inf'
    args.push('--download-sections', `*${from}-${to}`, '--force-keyframes-at-cuts')
  }

  // Video anhand der Kapitel aufteilen (Issue #23): Einzeldateien in einem
  // Unterordner mit dem Videotitel, nummeriert nach Kapitel-Reihenfolge
  if (request.splitChapters) {
    args.push(
      '--split-chapters',
      '-o',
      'chapter:%(title)s/%(section_number)02d - %(section_title)s.%(ext)s'
    )
  }

  if (merged.mode === 'audio') {
    args.push('-f', 'bestaudio/best', '-x', '--audio-format', merged.audioFormat)
    args.push('--audio-quality', merged.audioQuality)
    if (merged.embedThumbnail) args.push('--embed-thumbnail')
    if (merged.embedMetadata) args.push('--embed-metadata')
  } else {
    const h = merged.videoQuality
    if (h === 'best') {
      args.push('-f', 'bestvideo+bestaudio/best')
    } else {
      args.push('-f', `bestvideo[height<=${h}]+bestaudio/best[height<=${h}]/best`)
    }
    args.push('--merge-output-format', merged.videoContainer)
    if (merged.embedMetadata) args.push('--embed-metadata')
    if (merged.embedThumbnail) args.push('--embed-thumbnail')
  }

  if (merged.writeSubtitles) {
    const langs = merged.subtitleLanguages
      .split(',')
      .map((l) => l.trim())
      .filter(Boolean)
      .join(',')
    args.push('--write-subs', '--sub-langs', langs || 'de,en', '--convert-subs', 'srt')
  }

  if (merged.speedLimit.trim()) {
    const mbps = Number.parseFloat(merged.speedLimit.replace(',', '.'))
    if (Number.isFinite(mbps) && mbps > 0) args.push('-r', `${mbps}M`)
  }

  if (merged.sponsorBlock) {
    args.push('--sponsorblock-remove', 'sponsor,selfpromo')
  }

  if (merged.extraArgs.trim()) {
    args.push(...splitArgs(merged.extraArgs))
  }

  args.push('--', request.url)
  return { bin, args }
}

interface RawEntry {
  id?: string
  url?: string
  webpage_url?: string
  title?: string
  uploader?: string
  channel?: string
  duration?: number
}

interface RawInfo extends RawEntry {
  _type?: string
  entries?: RawEntry[]
  thumbnail?: string
  thumbnails?: { url: string }[]
  view_count?: number
  playlist_count?: number
  chapters?: unknown[] | null
}

/**
 * Holt Metadaten ohne Download (Vorschau).
 * Playlists werden flach extrahiert (schnell, keine Format-Auflösung je Video).
 */
export async function probeUrl(url: string): Promise<MediaInfo> {
  const bin = await getYtDlpPath()
  if (!bin) throw new YtDlpMissingError()

  const { stdout } = await execFileP(
    bin,
    [...jsRuntimeArgs(), '-J', '--flat-playlist', '--no-warnings', '--', url],
    { timeout: 60000, maxBuffer: 64 * 1024 * 1024, env: ytDlpEnv() }
  )
  const info = JSON.parse(stdout) as RawInfo

  if (info._type === 'playlist' && Array.isArray(info.entries)) {
    const entries: PlaylistEntryInfo[] = info.entries.map((e) => ({
      id: e.id ?? '',
      url: e.url ?? e.webpage_url ?? '',
      title: e.title ?? 'Unbekannt',
      uploader: e.uploader ?? e.channel ?? null,
      durationSeconds: typeof e.duration === 'number' ? e.duration : null
    }))
    return {
      id: info.id ?? '',
      url,
      title: info.title ?? 'Playlist',
      uploader: info.uploader ?? info.channel ?? null,
      entryCount: info.playlist_count ?? entries.length,
      entries,
      isPlaylist: true
    }
  }

  return {
    id: info.id ?? '',
    url,
    title: info.title ?? 'Unbekannt',
    uploader: info.uploader ?? info.channel ?? '',
    durationSeconds: typeof info.duration === 'number' ? info.duration : null,
    thumbnailUrl: info.thumbnail ?? info.thumbnails?.at(-1)?.url ?? null,
    viewCount: typeof info.view_count === 'number' ? info.view_count : null,
    chapterCount: Array.isArray(info.chapters) ? info.chapters.length : 0,
    isPlaylist: false
  }
}
