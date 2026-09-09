#!/usr/bin/env node
/**
 * Lädt yt-dlp und FFmpeg als statische Binaries für eine Zielplattform
 * nach resources/bin/<platform>-<arch>/.
 *
 * Verwendung:
 *   node scripts/fetch-binaries.mjs                       # aktuelle Plattform
 *   node scripts/fetch-binaries.mjs --platform win32 --arch x64
 *   node scripts/fetch-binaries.mjs --ytdlp-version 2026.08.19   # Version festnageln
 *   node scripts/fetch-binaries.mjs --offline              # nur vorhandenen Stand melden
 *
 * yt-dlp wird gegen die neueste Veröffentlichung abgeglichen, nicht nur auf
 * Vorhandensein geprüft: ein Release mit veraltetem yt-dlp fällt sonst erst
 * beim Nutzer auf, wenn YouTube den benutzten Player-Client sperrt und jeder
 * Download mitten im Vorgang mit „HTTP Error 403“ abbricht. Der geladene Stand
 * wird in <ziel>/yt-dlp.version notiert, damit der Abgleich auch bei Builds für
 * fremde Plattformen funktioniert (dort lässt sich das Binary nicht ausführen).
 *
 * Quellen:
 *   yt-dlp  — offizielle GitHub-Releases (yt-dlp/yt-dlp)
 *   ffmpeg  — statische Builds aus eugeneware/ffmpeg-static (GitHub-Releases)
 */
import { mkdir, chmod, writeFile, readFile, access, rm } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import process from 'node:process'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')

const FFMPEG_STATIC_RELEASE = 'b6.0'

const YTDLP_ASSETS = {
  'win32-x64': 'yt-dlp.exe',
  'win32-arm64': 'yt-dlp.exe',
  'darwin-x64': 'yt-dlp_macos',
  'darwin-arm64': 'yt-dlp_macos',
  'linux-x64': 'yt-dlp_linux',
  'linux-arm64': 'yt-dlp_linux_aarch64'
}

const FFMPEG_ASSETS = {
  'win32-x64': 'ffmpeg-win32-x64',
  'darwin-x64': 'ffmpeg-darwin-x64',
  'darwin-arm64': 'ffmpeg-darwin-arm64',
  'linux-x64': 'ffmpeg-linux-x64',
  'linux-arm64': 'ffmpeg-linux-arm64'
}

function parseArgs() {
  const args = process.argv.slice(2)
  const get = (name, fallback) => {
    const i = args.indexOf(`--${name}`)
    return i !== -1 && args[i + 1] ? args[i + 1] : fallback
  }
  return {
    platform: get('platform', process.platform),
    arch: get('arch', process.arch),
    ytdlpVersion: get('ytdlp-version', null),
    force: args.includes('--force'),
    offline: args.includes('--offline')
  }
}

async function exists(path) {
  try {
    await access(path)
    return true
  } catch {
    return false
  }
}

async function download(url, dest) {
  process.stdout.write(`  ↓ ${url}\n    → ${dest} … `)
  const res = await fetch(url, { redirect: 'follow' })
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`)
  const buf = Buffer.from(await res.arrayBuffer())
  await writeFile(dest, buf)
  process.stdout.write(`${(buf.length / 1024 / 1024).toFixed(1)} MB ✓\n`)
}

/**
 * Neueste veröffentlichte yt-dlp-Version (null = nicht ermittelbar).
 *
 * Zuerst über die Weiterleitung von /releases/latest auf /releases/tag/<version>:
 * das ist kein API-Aufruf und kennt deshalb keine Ratenbegrenzung. Der API-Weg
 * bleibt als Rückfall, ist auf CI-Runnern aber unzuverlässig, weil
 * unauthentifizierte Abfragen je IP begrenzt sind und Runner sich IPs teilen.
 * Genau daran scheiterte der macOS-Job in v5.2.0 und protokollierte „latest“
 * statt der Versionsnummer.
 */
async function latestYtDlpTag() {
  try {
    const res = await fetch('https://github.com/yt-dlp/yt-dlp/releases/latest', {
      redirect: 'manual',
      signal: AbortSignal.timeout(20000)
    })
    const location = res.headers.get('location')
    const tag = location && /\/releases\/tag\/([^/?#]+)/.exec(location)?.[1]
    if (tag) return decodeURIComponent(tag).trim()
  } catch {
    /* weiter mit der API */
  }
  try {
    const headers = { Accept: 'application/vnd.github+json' }
    // Im CI hebt das Token die Ratenbegrenzung deutlich an
    const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN
    if (token) headers.Authorization = `Bearer ${token}`
    const res = await fetch('https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest', {
      headers,
      signal: AbortSignal.timeout(20000)
    })
    if (!res.ok) return null
    const data = await res.json()
    return typeof data.tag_name === 'string' ? data.tag_name.trim() : null
  } catch {
    return null
  }
}

async function readStamp(path) {
  try {
    return (await readFile(path, 'utf-8')).trim() || null
  } catch {
    return null
  }
}

async function main() {
  const { platform, arch, force, offline, ytdlpVersion } = parseArgs()
  const key = `${platform}-${arch}`
  const ytAsset = YTDLP_ASSETS[key]
  const ffAsset = FFMPEG_ASSETS[key]
  if (!ytAsset || !ffAsset) {
    console.error(`Unsupported target: ${key}`)
    process.exit(1)
  }

  const dir = join(ROOT, 'resources', 'bin', key)
  await mkdir(dir, { recursive: true })
  console.log(`Fetching binaries for ${key} into ${dir}`)

  const ext = platform === 'win32' ? '.exe' : ''
  const ytDest = join(dir, `yt-dlp${ext}`)
  const ffDest = join(dir, `ffmpeg${ext}`)
  const ytStamp = join(dir, 'yt-dlp.version')

  const havePresent = await exists(ytDest)
  const haveVersion = await readStamp(ytStamp)

  // Gewünschter Stand: festgenagelt, sonst die neueste Veröffentlichung
  let wanted = ytdlpVersion
  if (!wanted && !offline) {
    wanted = await latestYtDlpTag()
    if (!wanted) {
      console.warn('  ! yt-dlp-Version konnte nicht ermittelt werden (kein Netz?)')
    }
  }

  const outdated = !!wanted && haveVersion !== wanted
  const needYt = force || !havePresent || outdated

  if (needYt && (wanted || !offline)) {
    if (havePresent && outdated) {
      console.log(`  yt-dlp veraltet: ${haveVersion ?? 'unbekannt'} → ${wanted}`)
    }
    const url = wanted
      ? `https://github.com/yt-dlp/yt-dlp/releases/download/${wanted}/${ytAsset}`
      : `https://github.com/yt-dlp/yt-dlp/releases/latest/download/${ytAsset}`
    await download(url, ytDest)
    if (wanted) {
      await writeFile(ytStamp, `${wanted}\n`, 'utf-8')
    } else {
      // Ohne bekannte Version keinen Stempel hinterlassen: „latest“ wäre beim
      // nächsten Abgleich wertlos und im Build-Log irreführend
      await rm(ytStamp, { force: true })
      console.warn('  ! Version unbekannt — kein Stempel geschrieben')
    }
  } else if (havePresent) {
    console.log(`  yt-dlp aktuell (${haveVersion ?? 'Version unbekannt'})`)
  } else {
    console.error('  ! yt-dlp fehlt und kann offline nicht geladen werden')
    process.exit(1)
  }

  if (force || !(await exists(ffDest))) {
    // Hinweis: die ffmpeg-static-Assets haben auch für Windows KEINE .exe-Endung
    await download(
      `https://github.com/eugeneware/ffmpeg-static/releases/download/${FFMPEG_STATIC_RELEASE}/${ffAsset}`,
      ffDest
    )
  } else {
    console.log(`  ffmpeg already present (use --force to refresh)`)
  }

  if (platform !== 'win32') {
    await chmod(ytDest, 0o755)
    await chmod(ffDest, 0o755)
  }

  // Im CI-Log nachvollziehbar machen, was tatsächlich ins Release wandert
  console.log(`Bundled yt-dlp version: ${(await readStamp(ytStamp)) ?? 'unbekannt'}`)
  console.log('Done.')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
