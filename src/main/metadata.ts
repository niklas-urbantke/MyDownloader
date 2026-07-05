import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { existsSync, renameSync, unlinkSync } from 'node:fs'
import { extname } from 'node:path'
import type { MusicBrainzSuggestion, TrackTags } from '@shared/types'
import { getFfmpegPath } from './binaries'

const execFileP = promisify(execFile)

export function emptyTags(): TrackTags {
  return { title: '', artist: '', album: '', albumArtist: '', track: '', genre: '', date: '', comment: '' }
}

/**
 * Liest ID3-/Container-Tags über ffmpeg (ffprobe ist nicht gebündelt).
 * `ffmpeg -f ffmetadata` liefert die Tags als key=value-Zeilen.
 */
export async function readTags(file: string): Promise<TrackTags> {
  const tags = emptyTags()
  const ffmpeg = await getFfmpegPath()
  if (!ffmpeg || !existsSync(file)) return tags
  try {
    const { stdout } = await execFileP(
      ffmpeg,
      ['-hide_banner', '-i', file, '-f', 'ffmetadata', 'pipe:1'],
      { timeout: 60000, maxBuffer: 8 * 1024 * 1024 }
    )
    const map: Record<string, string> = {}
    for (const line of stdout.split(/\r?\n/)) {
      if (line.startsWith(';') || !line.includes('=')) continue
      const idx = line.indexOf('=')
      // ffmetadata escapet '=', ';', '#', '\' und Zeilenumbrüche mit '\'
      map[line.slice(0, idx).toLowerCase()] = line.slice(idx + 1).replace(/\\(.)/g, '$1')
    }
    tags.title = map['title'] ?? ''
    tags.artist = map['artist'] ?? ''
    tags.album = map['album'] ?? ''
    tags.albumArtist = map['album_artist'] ?? ''
    tags.track = map['track'] ?? ''
    tags.genre = map['genre'] ?? ''
    tags.date = map['date'] ?? map['year'] ?? ''
    tags.comment = map['comment'] ?? ''
  } catch {
    /* Datei ohne lesbare Tags */
  }
  return tags
}

/** Dauer in Sekunden aus dem ffmpeg-Banner ("Duration: 00:03:45.12") */
export async function readDurationSeconds(file: string): Promise<number | null> {
  const ffmpeg = await getFfmpegPath()
  if (!ffmpeg || !existsSync(file)) return null
  try {
    await execFileP(ffmpeg, ['-hide_banner', '-i', file, '-f', 'null', '-t', '0', '-'], {
      timeout: 60000
    })
  } catch (err) {
    const msg = err instanceof Error && 'stderr' in err ? String((err as { stderr: unknown }).stderr) : ''
    return parseDuration(msg)
  }
  return null
}

function parseDuration(stderr: string): number | null {
  const m = /Duration:\s*(\d+):(\d{2}):(\d{2})(?:\.(\d+))?/.exec(stderr)
  if (!m) return null
  return Number(m[1]) * 3600 + Number(m[2]) * 60 + Number(m[3])
}

/**
 * Schreibt Tags (und optional ein neues Cover) in die Datei (Issue #25).
 * Stream-Copy — kein Re-Encode, nur der Container wird neu geschrieben.
 */
export async function writeTags(
  file: string,
  tags: TrackTags,
  coverPath: string | null
): Promise<{ ok: boolean; message: string }> {
  const ffmpeg = await getFfmpegPath()
  if (!ffmpeg) return { ok: false, message: 'ffmpeg not found' }
  if (!existsSync(file)) return { ok: false, message: 'file not found' }
  const ext = extname(file)
  const tmp = `${file.slice(0, -ext.length)}.tmp-md${ext}`

  const args = ['-hide_banner', '-y', '-i', file]
  const withCover = coverPath && existsSync(coverPath) && ext.toLowerCase() !== '.wav'
  if (withCover) {
    args.push('-i', coverPath)
    // Audio aus der Originaldatei, Bild aus der zweiten Quelle
    args.push('-map', '0:a', '-map', '1:v')
    args.push('-c', 'copy', '-disposition:v:0', 'attached_pic')
    if (ext.toLowerCase() === '.mp3') args.push('-id3v2_version', '3')
    args.push('-metadata:s:v', 'title=Album cover', '-metadata:s:v', 'comment=Cover (front)')
  } else {
    args.push('-map', '0', '-c', 'copy')
    if (ext.toLowerCase() === '.mp3') args.push('-id3v2_version', '3')
  }

  const meta: Record<string, string> = {
    title: tags.title,
    artist: tags.artist,
    album: tags.album,
    album_artist: tags.albumArtist,
    track: tags.track,
    genre: tags.genre,
    date: tags.date,
    comment: tags.comment
  }
  for (const [key, value] of Object.entries(meta)) {
    args.push('-metadata', `${key}=${value}`)
  }
  args.push(tmp)

  try {
    await execFileP(ffmpeg, args, { timeout: 5 * 60 * 1000 })
    renameSync(tmp, file)
    return { ok: true, message: '' }
  } catch (err) {
    try {
      if (existsSync(tmp)) unlinkSync(tmp)
    } catch {
      /* ignorieren */
    }
    return { ok: false, message: err instanceof Error ? err.message : String(err) }
  }
}

interface MbArtistCredit {
  name?: string
}
interface MbRelease {
  title?: string
  date?: string
}
interface MbRecording {
  title?: string
  score?: number
  'artist-credit'?: MbArtistCredit[]
  releases?: MbRelease[]
  'first-release-date'?: string
}

/**
 * Sucht passende Aufnahmen bei MusicBrainz (Issue #25).
 * Kein API-Key nötig; ein aussagekräftiger User-Agent ist Pflicht.
 */
export async function searchMusicBrainz(
  artist: string,
  title: string
): Promise<MusicBrainzSuggestion[]> {
  const lucene = artist
    ? `recording:"${title}" AND artist:"${artist}"`
    : `recording:"${title}"`
  const url = `https://musicbrainz.org/ws/2/recording?query=${encodeURIComponent(lucene)}&fmt=json&limit=5`
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'MyDownloader/5.0 (https://github.com/niklas-urbantke/YouTube-Downloader)'
      },
      signal: AbortSignal.timeout(15000)
    })
    if (!res.ok) return []
    const data = (await res.json()) as { recordings?: MbRecording[] }
    return (data.recordings ?? []).map((r) => {
      const release = r.releases?.[0]
      const date = release?.date ?? r['first-release-date'] ?? null
      return {
        title: r.title ?? '',
        artist: (r['artist-credit'] ?? []).map((a) => a.name ?? '').filter(Boolean).join(', '),
        album: release?.title ?? null,
        date: date ? date.slice(0, 4) : null,
        score: r.score ?? 0
      }
    })
  } catch {
    return []
  }
}
