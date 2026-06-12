import { app } from 'electron'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { existsSync, chmodSync } from 'node:fs'
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

async function resolveBinary(name: string): Promise<string | null> {
  const bundled = join(bundledDir(), exe(name))
  if (existsSync(bundled)) {
    if (process.platform !== 'win32') {
      try {
        chmodSync(bundled, 0o755)
      } catch {
        /* schreibgeschützt (z. B. AppImage) — Binary ist dann schon ausführbar */
      }
    }
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

export async function getBinaryStatus(): Promise<BinaryStatus> {
  const [yt, ff] = await Promise.all([getYtDlpPath(), getFfmpegPath()])
  const [ytV, ffVRaw] = await Promise.all([
    versionOf(yt, ['--version']),
    versionOf(ff, ['-version'])
  ])
  // "ffmpeg version 7.1 Copyright ..." → "7.1"
  const ffV = ffVRaw ? (ffVRaw.match(/ffmpeg version (\S+)/)?.[1] ?? ffVRaw) : null
  return {
    ytDlp: { available: !!yt, path: yt, version: ytV },
    ffmpeg: { available: !!ff, path: ff, version: ffV }
  }
}

/**
 * Aktualisiert das yt-dlp-Binary über den eingebauten Self-Updater.
 * Funktioniert nur für die offiziellen Standalone-Binaries.
 */
export async function updateYtDlp(): Promise<{ ok: boolean; message: string }> {
  const yt = await getYtDlpPath()
  if (!yt) return { ok: false, message: 'yt-dlp not found' }
  try {
    const { stdout, stderr } = await execFileP(yt, ['-U'], { timeout: 120000 })
    const out = `${stdout}\n${stderr}`.trim()
    const version = await versionOf(yt, ['--version'])
    return { ok: true, message: version ?? out }
  } catch (err) {
    return { ok: false, message: err instanceof Error ? err.message : String(err) }
  }
}
