import { createServer, type Server } from 'node:http'
import { createHash, randomBytes } from 'node:crypto'
import { shell } from 'electron'
import type { SpotifyPlaylist, SpotifyStatus, SpotifyTrack } from '@shared/types'
import { JsonStore } from './store'
import { getSettings } from './settings'

/**
 * Spotify-Anbindung (Issue #35).
 *
 * Zwei Wege liegen hier nebeneinander:
 *
 *  1. Ein einzelner Song ohne jede Registrierung (siehe unten). Das ist der
 *     Weg, den die Oberfläche anbietet.
 *  2. Ganze Playlists und Alben über die Web-API, dafür braucht es OAuth 2.0
 *     mit PKCE und die Client-ID einer eigenen (kostenlosen) Developer-App.
 *     Der Code bleibt erhalten, wird derzeit aber nicht angeboten.
 */

// ---------------------------------------------------------------------------
// Einzelner Song, ganz ohne Anmeldung
// ---------------------------------------------------------------------------

/** open.spotify.com/track/<id>, auch mit /intl-xx/ davor, und spotify:track:<id> */
const TRACK_LINK = /(?:open\.spotify\.com\/(?:intl-[a-z-]+\/)?track\/|spotify:track:)([A-Za-z0-9]+)/

/**
 * Der User-Agent entscheidet, was Spotify ausliefert.
 *
 * Ein voller Desktop-Browser bekommt nur das Gerüst des Web-Players, das seine
 * Inhalte per JavaScript nachlädt: darin steht keine einzige og-Angabe. Ein
 * mobiler oder schlichter User-Agent bekommt dagegen die fertig gebaute Seite
 * mit Titel und Künstler. Deshalb steht hier ein Mobil-Browser vorn, und ein
 * schlichter Kennzeichner als Rückfallebene, falls Spotify das später anders
 * verteilt.
 */
const PAGE_USER_AGENTS = [
  'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 MyDownloader'
]

/** Ist das ein Link auf einen einzelnen Song? */
export function isSpotifyTrackLink(url: string): boolean {
  return TRACK_LINK.test(url.trim())
}

/** Die wenigen Entities, die in og-Angaben tatsächlich vorkommen. */
function decodeEntities(text: string): string {
  return text
    .replace(/&#(\d+);/g, (_m, d: string) => String.fromCodePoint(Number(d)))
    .replace(/&#x([0-9a-f]+);/gi, (_m, h: string) => String.fromCodePoint(Number.parseInt(h, 16)))
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
}

/** Inhalt einer og-Auszeichnung, in beiden möglichen Attribut-Reihenfolgen. */
function metaContent(html: string, property: string): string | null {
  const first = new RegExp(
    `<meta[^>]+property=["']${property}["'][^>]+content=["']([^"']*)["']`,
    'i'
  ).exec(html)
  if (first) return decodeEntities(first[1])
  const second = new RegExp(
    `<meta[^>]+content=["']([^"']*)["'][^>]+property=["']${property}["']`,
    'i'
  ).exec(html)
  return second ? decodeEntities(second[1]) : null
}

/**
 * Liest Künstler und Titel eines Songs aus der ganz normalen Songseite.
 *
 * Bewusst OHNE Web-API: die Seite trägt die Angaben in ihren
 * OpenGraph-Auszeichnungen, und die sind ohne Client-ID, ohne Secret und ohne
 * Anmeldung lesbar.
 *
 *   og:title       "Yellow"
 *   og:description "Coldplay · Parachutes · Song · 2000"
 *
 * Aus dem ersten Feld der Beschreibung kommt der Künstler.
 *
 * @returns "Künstler - Titel", nur den Titel, wenn kein Künstler zu ermitteln
 *          ist, oder null, wenn die Seite nicht lesbar war.
 */
export async function resolveSpotifyTrackQuery(url: string): Promise<string | null> {
  const match = TRACK_LINK.exec(url.trim())
  if (!match) return null
  for (const userAgent of PAGE_USER_AGENTS) {
    try {
      const res = await fetch(`https://open.spotify.com/track/${match[1]}`, {
        headers: {
          'User-Agent': userAgent,
          'Accept-Language': 'de,en;q=0.8'
        },
        signal: AbortSignal.timeout(15000)
      })
      if (!res.ok) continue
      const html = await res.text()
      const title = (metaContent(html, 'og:title') ?? '').trim()
      // Leer heißt: die Sparfassung ohne og-Angaben, also den nächsten
      // User-Agent versuchen
      if (!title) continue
      const artist = (metaContent(html, 'og:description') ?? '').split('·')[0].trim()
      if (!artist || artist.toLowerCase() === title.toLowerCase()) return title
      return `${artist} - ${title}`
    } catch {
      // Zeitüberschreitung oder Netzfehler: nächsten Versuch zulassen
    }
  }
  return null
}

// ---------------------------------------------------------------------------
// Playlists und Alben über die Web-API (PKCE, derzeit nicht in der Oberfläche)
// ---------------------------------------------------------------------------

export const SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8988/callback'
const CALLBACK_PORT = 8988
const SCOPES = 'playlist-read-private playlist-read-collaborative user-library-read'

interface SpotifyTokens {
  accessToken: string
  refreshToken: string
  /** Unix-Millisekunden */
  expiresAt: number
  clientId: string
}

let store: JsonStore<SpotifyTokens | null> | null = null
let cached: SpotifyTokens | null | undefined

function getStore(): JsonStore<SpotifyTokens | null> {
  if (!store) store = new JsonStore<SpotifyTokens | null>('spotify.json', null)
  return store
}

function getTokens(): SpotifyTokens | null {
  if (cached === undefined) {
    const loaded = getStore().load()
    cached = loaded && typeof loaded === 'object' && 'accessToken' in loaded ? loaded : null
  }
  return cached
}

function saveTokens(tokens: SpotifyTokens | null): void {
  cached = tokens
  getStore().save(tokens)
}

interface TokenResponse {
  access_token?: string
  refresh_token?: string
  expires_in?: number
  error?: string
  error_description?: string
}

async function tokenRequest(params: Record<string, string>): Promise<TokenResponse> {
  const res = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(params).toString(),
    signal: AbortSignal.timeout(20000)
  })
  return (await res.json()) as TokenResponse
}

/** Gültiges Access-Token besorgen (bei Bedarf per Refresh-Token erneuern) */
async function accessToken(): Promise<string | null> {
  const tokens = getTokens()
  if (!tokens) return null
  if (Date.now() < tokens.expiresAt - 30_000) return tokens.accessToken
  const refreshed = await tokenRequest({
    grant_type: 'refresh_token',
    refresh_token: tokens.refreshToken,
    client_id: tokens.clientId
  })
  if (!refreshed.access_token) {
    saveTokens(null)
    return null
  }
  saveTokens({
    ...tokens,
    accessToken: refreshed.access_token,
    refreshToken: refreshed.refresh_token ?? tokens.refreshToken,
    expiresAt: Date.now() + (refreshed.expires_in ?? 3600) * 1000
  })
  return refreshed.access_token
}

async function api<T>(path: string): Promise<T | null> {
  const token = await accessToken()
  if (!token) return null
  const res = await fetch(`https://api.spotify.com/v1${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    signal: AbortSignal.timeout(20000)
  })
  if (!res.ok) return null
  return (await res.json()) as T
}

export async function spotifyStatus(): Promise<SpotifyStatus> {
  const configured = getSettings().spotifyClientId.trim().length > 0
  const tokens = getTokens()
  if (!configured || !tokens) return { configured, loggedIn: false, displayName: null }
  const me = await api<{ display_name?: string }>('/me')
  return {
    configured,
    loggedIn: !!me,
    displayName: me?.display_name ?? null
  }
}

let pendingServer: Server | null = null

/**
 * Startet den PKCE-Login: lokaler Callback-Server + System-Browser.
 * Auflösung, sobald Spotify zurückleitet und der Token-Tausch geklappt hat.
 */
export async function spotifyLogin(): Promise<SpotifyStatus> {
  const clientId = getSettings().spotifyClientId.trim()
  if (!clientId) return { configured: false, loggedIn: false, displayName: null }

  // Alten hängenden Login-Versuch abräumen
  if (pendingServer) {
    pendingServer.close()
    pendingServer = null
  }

  const verifier = randomBytes(48).toString('base64url')
  const challenge = createHash('sha256').update(verifier).digest('base64url')

  const code = await new Promise<string | null>((resolve) => {
    const server = createServer((req, res) => {
      const url = new URL(req.url ?? '/', SPOTIFY_REDIRECT_URI)
      if (url.pathname !== '/callback') {
        res.writeHead(404).end()
        return
      }
      const authCode = url.searchParams.get('code')
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' })
      res.end(
        '<html><body style="font-family:sans-serif;text-align:center;padding-top:80px">' +
          (authCode
            ? '<h2>✓ Anmeldung erfolgreich</h2><p>Du kannst dieses Fenster schließen und zu MyDownloader zurückkehren.</p>'
            : '<h2>Anmeldung abgebrochen</h2>') +
          '</body></html>'
      )
      server.close()
      pendingServer = null
      resolve(authCode)
    })
    pendingServer = server
    server.on('error', () => resolve(null))
    server.listen(CALLBACK_PORT, '127.0.0.1', () => {
      const authUrl = new URL('https://accounts.spotify.com/authorize')
      authUrl.searchParams.set('client_id', clientId)
      authUrl.searchParams.set('response_type', 'code')
      authUrl.searchParams.set('redirect_uri', SPOTIFY_REDIRECT_URI)
      authUrl.searchParams.set('code_challenge_method', 'S256')
      authUrl.searchParams.set('code_challenge', challenge)
      authUrl.searchParams.set('scope', SCOPES)
      void shell.openExternal(authUrl.toString())
    })
    // Nach 5 Minuten aufgeben
    setTimeout(() => {
      server.close()
      pendingServer = null
      resolve(null)
    }, 5 * 60 * 1000)
  })

  if (!code) return spotifyStatus()

  const tokens = await tokenRequest({
    grant_type: 'authorization_code',
    code,
    redirect_uri: SPOTIFY_REDIRECT_URI,
    client_id: clientId,
    code_verifier: verifier
  })
  if (tokens.access_token && tokens.refresh_token) {
    saveTokens({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      expiresAt: Date.now() + (tokens.expires_in ?? 3600) * 1000,
      clientId
    })
  }
  return spotifyStatus()
}

export function spotifyLogout(): SpotifyStatus {
  saveTokens(null)
  return { configured: getSettings().spotifyClientId.trim().length > 0, loggedIn: false, displayName: null }
}

/** Extrahiert Typ und ID aus einer Spotify-URL oder -URI */
function parseSpotifyUrl(input: string): { type: 'playlist' | 'album' | 'track'; id: string } | null {
  const urlMatch = /open\.spotify\.com\/(?:intl-[a-z]+\/)?(playlist|album|track)\/([A-Za-z0-9]+)/.exec(input)
  if (urlMatch) return { type: urlMatch[1] as 'playlist' | 'album' | 'track', id: urlMatch[2] }
  const uriMatch = /^spotify:(playlist|album|track):([A-Za-z0-9]+)$/.exec(input.trim())
  if (uriMatch) return { type: uriMatch[1] as 'playlist' | 'album' | 'track', id: uriMatch[2] }
  return null
}

interface SpotifyApiTrack {
  name?: string
  artists?: { name?: string }[]
  album?: { name?: string }
  duration_ms?: number
}

function toTrack(t: SpotifyApiTrack, albumName?: string): SpotifyTrack {
  return {
    artist: (t.artists ?? []).map((a) => a.name ?? '').filter(Boolean).join(', '),
    title: t.name ?? '',
    album: t.album?.name ?? albumName ?? null,
    durationSeconds: t.duration_ms ? Math.round(t.duration_ms / 1000) : null
  }
}

/** Lädt alle Titel einer Playlist / eines Albums / eines einzelnen Tracks. */
export async function getSpotifyPlaylist(input: string): Promise<SpotifyPlaylist | null> {
  const parsed = parseSpotifyUrl(input)
  if (!parsed) return null

  if (parsed.type === 'track') {
    const t = await api<SpotifyApiTrack>(`/tracks/${parsed.id}`)
    if (!t) return null
    return { title: t.name ?? 'Track', owner: null, tracks: [toTrack(t)] }
  }

  if (parsed.type === 'album') {
    const album = await api<{
      name?: string
      artists?: { name?: string }[]
      tracks?: { items?: SpotifyApiTrack[]; next?: string | null }
    }>(`/albums/${parsed.id}`)
    if (!album) return null
    const tracks = (album.tracks?.items ?? []).map((t) => toTrack(t, album.name))
    return {
      title: album.name ?? 'Album',
      owner: (album.artists ?? []).map((a) => a.name ?? '').join(', ') || null,
      tracks
    }
  }

  const playlist = await api<{ name?: string; owner?: { display_name?: string } }>(
    `/playlists/${parsed.id}?fields=name,owner.display_name`
  )
  if (!playlist) return null
  const tracks: SpotifyTrack[] = []
  let offset = 0
  for (;;) {
    const page = await api<{ items?: { track?: SpotifyApiTrack | null }[]; next?: string | null }>(
      `/playlists/${parsed.id}/tracks?limit=100&offset=${offset}&fields=items(track(name,duration_ms,artists(name),album(name))),next`
    )
    if (!page) break
    for (const item of page.items ?? []) {
      if (item.track?.name) tracks.push(toTrack(item.track))
    }
    if (!page.next) break
    offset += 100
    if (offset > 2000) break // Sicherheitsgrenze
  }
  return {
    title: playlist.name ?? 'Playlist',
    owner: playlist.owner?.display_name ?? null,
    tracks
  }
}
