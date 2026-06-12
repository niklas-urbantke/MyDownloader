/** Formatierungs-Helfer für Bytes, Geschwindigkeit, Dauer und Datum. */

export function formatBytes(bytes: number | null): string {
  if (bytes === null || !Number.isFinite(bytes)) return '–'
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB', 'TB']
  let value = bytes
  let unit = ''
  for (const u of units) {
    value /= 1024
    unit = u
    if (value < 1024) break
  }
  return `${value.toFixed(value >= 100 ? 0 : 1)} ${unit}`
}

export function formatSpeed(bytesPerSecond: number | null): string {
  if (bytesPerSecond === null || !Number.isFinite(bytesPerSecond)) return '–'
  return `${formatBytes(bytesPerSecond)}/s`
}

export function formatEta(seconds: number | null): string {
  if (seconds === null || !Number.isFinite(seconds) || seconds < 0) return '–'
  const s = Math.round(seconds)
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}:${String(s % 60).padStart(2, '0')} min`
  return `${Math.floor(m / 60)}:${String(m % 60).padStart(2, '0')} h`
}

export function formatDuration(seconds: number | null): string {
  if (seconds === null || !Number.isFinite(seconds)) return '–'
  const s = Math.round(seconds)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${m}:${String(sec).padStart(2, '0')}`
}

export function formatDateTime(iso: string, locale: string): string {
  try {
    return new Intl.DateTimeFormat(locale, {
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export function formatCount(n: number | null, locale: string): string {
  if (n === null || !Number.isFinite(n)) return '–'
  return new Intl.NumberFormat(locale).format(n)
}

export function isHttpUrl(value: string): boolean {
  try {
    const u = new URL(value.trim())
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

export interface CombiUrl {
  /** Kanonische URL nur für das einzelne Video */
  videoUrl: string
  /** Kanonische URL für die gesamte Playlist */
  playlistUrl: string
}

/**
 * Erkennt YouTube-"Combi-Links" (watch?v=… UND list=…), bei denen unklar ist,
 * ob das einzelne Video oder die ganze Playlist gemeint ist (Issue #2).
 */
export function analyzeCombiUrl(value: string): CombiUrl | null {
  try {
    const u = new URL(value.trim())
    if (!/(^|\.)youtube\.com$/.test(u.hostname) && u.hostname !== 'youtu.be') return null
    const videoId =
      u.hostname === 'youtu.be' ? u.pathname.slice(1) : (u.searchParams.get('v') ?? '')
    const listId = u.searchParams.get('list') ?? ''
    if (!videoId || !listId) return null
    return {
      videoUrl: `https://www.youtube.com/watch?v=${videoId}`,
      playlistUrl: `https://www.youtube.com/playlist?list=${listId}`
    }
  } catch {
    return null
  }
}
