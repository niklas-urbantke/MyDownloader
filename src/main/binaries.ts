import { app } from 'electron'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { existsSync, chmodSync, mkdirSync, copyFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'
import { is } from '@electron-toolkit/utils'
import type { BinaryStatus } from '@shared/types'

const execFileP = promisify(execFile)

const exe = (name: string): string => (process.platform === 'win32' ? `${name}.exe` : name)

/**
 * Gebündelte Binaries liegen:
 *  - im Dev-Modus unter <projektRoot>/resources/bin/<platform>-<arch>/
 *  - im Build unter <resourcesPath>/bin/ (electron-builder extraResources)
 */
function bundledDir(): string {
  if (is.dev) {
    return join(app.getAppPath(), 'resources', 'bin', `${process.platform}-${process.arch}`)
  }
  return join(process.resourcesPath, 'bin')
}

/**
 * Ort für ein selbst aktualisiertes yt-dlp. Der Programmordner ist auf den
 * meisten Installationen schreibgeschützt (Linux-AppImage ist ein read-only
 * Mount, Windows-Installationen nach „Program Files“ gehören dem Administrator),
 * dort scheitert „yt-dlp -U“ mit „Unable to write to …“. userData gehört immer
 * dem angemeldeten Nutzer und übersteht auch App-Updates.
 */
function managedDir(): string {
  return join(app.getPath('userData'), 'bin')
}

function managedYtDlp(): string {
  return join(managedDir(), exe('yt-dlp'))
}

async function fromPath(name: string): Promise<string | null> {
  const cmd = process.platform === 'win32' ? 'where' : 'which'
  try {
    const { stdout } = await execFileP(cmd, [name])
    const first = stdout.split(/\r?\n/).find((l) => l.trim().length > 0)
    return first?.trim() ?? null
  } catch {
    return null
  }
}

function makeExecutable(path: string): void {
  if (process.platform === 'win32') return
  try {
    chmodSync(path, 0o755)
  } catch {
    /* schreibgeschützt (z. B. AppImage) — Binary ist dann schon ausführbar */
  }
}

async function resolveBinary(name: string): Promise<string | null> {
  // Selbst aktualisiertes yt-dlp hat Vorrang vor dem eingebackenen Stand
  if (name === 'yt-dlp' && existsSync(managedYtDlp())) {
    const managed = managedYtDlp()
    makeExecutable(managed)
    return managed
  }
  const bundled = join(bundledDir(), exe(name))
  if (existsSync(bundled)) {
    makeExecutable(bundled)
    return bundled
  }
  return fromPath(name)
}

let ytDlpPath: string | null = null
let ffmpegPath: string | null = null

export async function getYtDlpPath(): Promise<string | null> {
  if (!ytDlpPath) ytDlpPath = await resolveBinary('yt-dlp')
  return ytDlpPath
}

export async function getFfmpegPath(): Promise<string | null> {
  if (!ffmpegPath) ffmpegPath = await resolveBinary('ffmpeg')
  return ffmpegPath
}

async function versionOf(path: string | null, args: string[]): Promise<string | null> {
  if (!path) return null
  try {
    const { stdout } = await execFileP(path, args, { timeout: 15000 })
    return stdout.split(/\r?\n/)[0]?.trim() ?? null
  } catch {
    return null
  }
}

/**
 * Vergleicht yt-dlp-Versionen ("2026.08.19", gelegentlich mit vierter Stelle).
 * Liefert > 0, wenn a neuer als b ist.
 */
export function compareYtDlpVersions(a: string, b: string): number {
  const parts = (v: string): number[] =>
    v
      .trim()
      .split('.')
      .map((p) => Number.parseInt(p, 10))
      .map((n) => (Number.isFinite(n) ? n : 0))
  const pa = parts(a)
  const pb = parts(b)
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const diff = (pa[i] ?? 0) - (pb[i] ?? 0)
    if (diff !== 0) return diff
  }
  return 0
}

/**
 * Verwirft ein selbst aktualisiertes yt-dlp, das älter ist als das mit der App
 * ausgelieferte. Sonst würde eine frisch installierte App-Version dauerhaft mit
 * einem veralteten Binary aus einer früheren Installation laufen.
 */
export async function reconcileManagedYtDlp(): Promise<void> {
  const managed = managedYtDlp()
  if (!existsSync(managed)) return
  const bundled = join(bundledDir(), exe('yt-dlp'))
  if (!existsSync(bundled)) return
  const [managedV, bundledV] = await Promise.all([
    versionOf(managed, ['--version']),
    versionOf(bundled, ['--version'])
  ])
  // Unlesbares (z. B. abgebrochen kopiertes) Binary ebenfalls verwerfen
  if (!managedV || (bundledV && compareYtDlpVersions(bundledV, managedV) > 0)) {
    try {
      rmSync(managed, { force: true })
      ytDlpPath = null
    } catch {
      /* nicht schlimm — beim nächsten Update wird ohnehin überschrieben */
    }
  }
}

/**
 * Neueste offiziell veröffentlichte yt-dlp-Version (null = nicht ermittelbar).
 *
 * Zuerst über die Weiterleitung von /releases/latest auf /releases/tag/<version>,
 * weil das kein API-Aufruf ist und deshalb keiner Ratenbegrenzung unterliegt.
 * Die API bleibt als Rückfall; sie zählt unauthentifizierte Abfragen je IP und
 * schlägt hinter geteilten Adressen (Firmennetz, CI-Runner) schnell fehl.
 */
export async function latestYtDlpVersion(): Promise<string | null> {
  try {
    const res = await fetch('https://github.com/yt-dlp/yt-dlp/releases/latest', {
      redirect: 'manual',
      signal: AbortSignal.timeout(15000)
    })
    const location = res.headers.get('location')
    const tag = location ? /\/releases\/tag\/([^/?#]+)/.exec(location)?.[1] : null
    if (tag) return decodeURIComponent(tag).trim()
  } catch {
    /* weiter mit der API */
  }
  try {
    const res = await fetch('https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest', {
      headers: { Accept: 'application/vnd.github+json' },
      signal: AbortSignal.timeout(15000)
    })
    if (!res.ok) return null
    const data = (await res.json()) as { tag_name?: string }
    return data.tag_name?.trim() ?? null
  } catch {
    return null
  }
}

export async function getBinaryStatus(): Promise<BinaryStatus> {
  const [yt, ff] = await Promise.all([getYtDlpPath(), getFfmpegPath()])
  const [ytV, ffVRaw, latest] = await Promise.all([
    versionOf(yt, ['--version']),
    versionOf(ff, ['-version']),
    latestYtDlpVersion()
  ])
  // "ffmpeg version 7.1 Copyright ..." → "7.1"
  const ffV = ffVRaw ? (ffVRaw.match(/ffmpeg version (\S+)/)?.[1] ?? ffVRaw) : null
  return {
    ytDlp: {
      available: !!yt,
      path: yt,
      version: ytV,
      latestVersion: latest,
      updateAvailable: !!ytV && !!latest && compareYtDlpVersions(latest, ytV) > 0,
      managed: !!yt && yt === managedYtDlp()
    },
    ffmpeg: { available: !!ff, path: ff, version: ffV }
  }
}

/**
 * Aktualisiert yt-dlp über den eingebauten Self-Updater.
 *
 * Läuft grundsätzlich auf einer Kopie in userData: das ausgelieferte Binary
 * liegt je nach Installationsart schreibgeschützt (AppImage, „Program Files“),
 * dort bricht „-U“ ab. Die Kopie wird ab dem nächsten Aufruf bevorzugt geladen.
 */
export async function updateYtDlp(): Promise<{ ok: boolean; message: string }> {
  const managed = managedYtDlp()

  if (!existsSync(managed)) {
    const bundled = join(bundledDir(), exe('yt-dlp'))
    const source = existsSync(bundled) ? bundled : await fromPath('yt-dlp')
    if (!source) return { ok: false, message: 'yt-dlp not found' }
    try {
      mkdirSync(managedDir(), { recursive: true })
      copyFileSync(source, managed)
      makeExecutable(managed)
    } catch (err) {
      return {
        ok: false,
        message: `yt-dlp konnte nicht nach ${managedDir()} kopiert werden: ${
          err instanceof Error ? err.message : String(err)
        }`
      }
    }
  }

  try {
    const { stdout, stderr } = await execFileP(managed, ['-U'], { timeout: 300000 })
    const out = `${stdout}\n${stderr}`.trim()
    // yt-dlp meldet Schreibfehler auf stdout und beendet sich trotzdem mit 0
    if (/Unable to write to|try running as administrator/i.test(out)) {
      return { ok: false, message: out }
    }
    ytDlpPath = null // Pfad neu auflösen, damit die Kopie greift
    const version = await versionOf(managed, ['--version'])
    return { ok: true, message: version ?? out }
  } catch (err) {
    return { ok: false, message: err instanceof Error ? err.message : String(err) }
  }
}

/**
 * Prüft beim Start, ob das aktive yt-dlp veraltet ist, und aktualisiert es je
 * nach Einstellung selbsttätig. Ohne das altert das eingebackene Binary still
 * vor sich hin, bis YouTube den benutzten Client sperrt und jeder Download mit
 * „HTTP Error 403“ mitten im Vorgang abbricht.
 */
export async function checkYtDlpUpToDate(
  mode: 'auto' | 'notify' | 'off'
): Promise<{ current: string | null; latest: string | null; updated: boolean }> {
  if (mode === 'off') return { current: null, latest: null, updated: false }

  const yt = await getYtDlpPath()
  const [current, latest] = await Promise.all([versionOf(yt, ['--version']), latestYtDlpVersion()])
  if (!current || !latest || compareYtDlpVersions(latest, current) <= 0) {
    return { current, latest, updated: false }
  }
  if (mode !== 'auto') return { current, latest, updated: false }

  const result = await updateYtDlp()
  return {
    current: result.ok ? result.message : current,
    latest,
    updated: result.ok
  }
}
