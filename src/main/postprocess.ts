import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { existsSync, renameSync, unlinkSync, writeFileSync } from 'node:fs'
import { extname } from 'node:path'
import type { AppSettings } from '@shared/types'
import { getFfmpegPath } from './binaries'
import { readTags, readDurationSeconds } from './metadata'

const execFileP = promisify(execFile)

export const AUDIO_EXTENSIONS = new Set(['.mp3', '.m4a', '.opus', '.flac', '.wav'])

export function isAudioFile(file: string): boolean {
  return AUDIO_EXTENSIONS.has(extname(file).toLowerCase())
}

/** Encoder je Container für den loudnorm-Re-Encode */
function encoderFor(file: string): string[] {
  switch (extname(file).toLowerCase()) {
    case '.mp3':
      return ['-c:a', 'libmp3lame', '-q:a', '0']
    case '.m4a':
      return ['-c:a', 'aac', '-b:a', '256k']
    case '.opus':
      return ['-c:a', 'libopus', '-b:a', '160k']
    case '.flac':
      return ['-c:a', 'flac']
    default:
      return []
  }
}

interface LoudnessMeasurement {
  input_i: string
  input_tp: string
  input_lra: string
  input_thresh: string
  target_offset: string
}

/** Erster loudnorm-Pass: Ist-Lautheit messen (EBU R128) */
async function measureLoudness(
  ffmpeg: string,
  file: string,
  targetLufs: number
): Promise<LoudnessMeasurement | null> {
  try {
    const { stderr } = await execFileP(
      ffmpeg,
      [
        '-hide_banner',
        '-i',
        file,
        '-af',
        `loudnorm=I=${targetLufs}:TP=-1.5:LRA=11:print_format=json`,
        '-f',
        'null',
        '-'
      ],
      { timeout: 10 * 60 * 1000, maxBuffer: 16 * 1024 * 1024 }
    )
    // Das JSON steht am Ende von stderr
    const start = stderr.lastIndexOf('{')
    const end = stderr.lastIndexOf('}')
    if (start === -1 || end === -1 || end < start) return null
    return JSON.parse(stderr.slice(start, end + 1)) as LoudnessMeasurement
  } catch {
    return null
  }
}

/**
 * Lautstärke-Normalisierung (Issue #26).
 *  - 'replaygain': nicht-destruktiv, schreibt REPLAYGAIN_TRACK_GAIN-Tag
 *  - 'loudnorm':   Zwei-Pass EBU-R128-Re-Encode auf die Ziel-LUFS
 */
export async function normalizeAudio(
  file: string,
  mode: 'replaygain' | 'loudnorm',
  targetLufs: number,
  log: (line: string) => void
): Promise<void> {
  const ffmpeg = await getFfmpegPath()
  if (!ffmpeg || !existsSync(file)) return

  const measured = await measureLoudness(ffmpeg, file, targetLufs)
  if (!measured) {
    log(`[normalize] Messung fehlgeschlagen — ${file} bleibt unverändert`)
    return
  }

  if (mode === 'replaygain') {
    const gain = targetLufs - Number.parseFloat(measured.input_i)
    if (!Number.isFinite(gain)) return
    const tmp = replacementPath(file)
    try {
      await execFileP(
        ffmpeg,
        [
          '-hide_banner',
          '-y',
          '-i',
          file,
          '-map',
          '0',
          '-c',
          'copy',
          '-metadata',
          `REPLAYGAIN_TRACK_GAIN=${gain.toFixed(2)} dB`,
          '-metadata',
          `REPLAYGAIN_TRACK_PEAK=${Math.min(1, 10 ** (Number.parseFloat(measured.input_tp) / 20)).toFixed(6)}`,
          tmp
        ],
        { timeout: 5 * 60 * 1000 }
      )
      renameSync(tmp, file)
      log(`[normalize] ReplayGain ${gain.toFixed(2)} dB gesetzt`)
    } catch (err) {
      cleanupTmp(tmp)
      log(`[normalize] ReplayGain fehlgeschlagen: ${String(err)}`)
    }
    return
  }

  // Zweiter Pass: linear auf Ziel-LUFS bringen, Encoder passend zum Container
  const enc = encoderFor(file)
  if (enc.length === 0) {
    log('[normalize] Container unterstützt keinen Re-Encode — übersprungen')
    return
  }
  const filter =
    `loudnorm=I=${targetLufs}:TP=-1.5:LRA=11:linear=true` +
    `:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}` +
    `:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}` +
    `:offset=${measured.target_offset}`
  const tmp = replacementPath(file)
  try {
    await execFileP(
      ffmpeg,
      ['-hide_banner', '-y', '-i', file, '-map', '0', '-map_metadata', '0', '-af', filter, ...enc, tmp],
      { timeout: 15 * 60 * 1000 }
    )
    renameSync(tmp, file)
    log(`[normalize] loudnorm auf ${targetLufs} LUFS angewendet`)
  } catch (err) {
    cleanupTmp(tmp)
    log(`[normalize] loudnorm fehlgeschlagen: ${String(err)}`)
  }
}

/** Temporärer Zieldateiname mit gleicher Endung (ffmpeg leitet Format daraus ab) */
function replacementPath(file: string): string {
  const ext = extname(file)
  return `${file.slice(0, -ext.length)}.tmp-md${ext}`
}

function cleanupTmp(tmp: string): void {
  try {
    if (existsSync(tmp)) unlinkSync(tmp)
  } catch {
    /* ignorieren */
  }
}

interface LrcLibResponse {
  syncedLyrics?: string | null
  plainLyrics?: string | null
}

/**
 * Songtexte über LRCLIB suchen und einbetten (Issue #27).
 * Synchronisierte Lyrics werden zusätzlich als .lrc-Datei abgelegt.
 */
export async function fetchAndEmbedLyrics(
  file: string,
  fallbackTitle: string,
  fallbackArtist: string | null,
  log: (line: string) => void
): Promise<void> {
  if (!existsSync(file)) return
  const tags = await readTags(file)
  const artist = tags.artist || fallbackArtist || ''
  const title = tags.title || fallbackTitle
  if (!title) return
  const duration = await readDurationSeconds(file)

  const params = new URLSearchParams({ track_name: title, artist_name: artist })
  if (duration) params.set('duration', String(Math.round(duration)))
  let lyrics: LrcLibResponse | null = null
  try {
    const res = await fetch(`https://lrclib.net/api/get?${params.toString()}`, {
      headers: { 'User-Agent': 'MyDownloader (https://github.com/niklas-urbantke/YouTube-Downloader)' },
      signal: AbortSignal.timeout(15000)
    })
    if (res.ok) lyrics = (await res.json()) as LrcLibResponse
  } catch {
    /* Netzwerkfehler: Download bleibt trotzdem erfolgreich */
  }
  if (!lyrics || (!lyrics.syncedLyrics && !lyrics.plainLyrics)) {
    log('[lyrics] Keine Songtexte gefunden')
    return
  }

  // Synchronisierte Lyrics als .lrc neben die Datei legen
  if (lyrics.syncedLyrics) {
    const ext = extname(file)
    const lrcPath = `${file.slice(0, -ext.length)}.lrc`
    try {
      writeFileSync(lrcPath, lyrics.syncedLyrics, 'utf-8')
      log('[lyrics] .lrc-Datei gespeichert')
    } catch {
      /* Schreibfehler ignorieren */
    }
  }

  // Unsynchronisierten Text als Tag einbetten (breit unterstützt)
  const text = lyrics.plainLyrics ?? lyrics.syncedLyrics ?? ''
  if (!text) return
  const ffmpeg = await getFfmpegPath()
  if (!ffmpeg) return
  const tmp = replacementPath(file)
  try {
    await execFileP(
      ffmpeg,
      ['-hide_banner', '-y', '-i', file, '-map', '0', '-c', 'copy', '-metadata', `lyrics=${text}`, tmp],
      { timeout: 5 * 60 * 1000 }
    )
    renameSync(tmp, file)
    log('[lyrics] Songtext eingebettet')
  } catch (err) {
    cleanupTmp(tmp)
    log(`[lyrics] Einbetten fehlgeschlagen: ${String(err)}`)
  }
}

/** Führt alle aktivierten Audio-Nachbearbeitungsschritte für eine Datei aus. */
export async function postprocessAudioFile(
  file: string,
  settings: AppSettings,
  meta: { title: string; artist: string | null },
  log: (line: string) => void
): Promise<void> {
  if (!isAudioFile(file)) return
  if (settings.normalizeAudio !== 'off') {
    await normalizeAudio(file, settings.normalizeAudio, settings.targetLufs, log)
  }
  if (settings.fetchLyrics) {
    await fetchAndEmbedLyrics(file, meta.title, meta.artist, log)
  }
}
