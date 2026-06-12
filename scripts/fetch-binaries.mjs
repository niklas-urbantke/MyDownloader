#!/usr/bin/env node
/**
 * Lädt yt-dlp und FFmpeg als statische Binaries für eine Zielplattform
 * nach resources/bin/<platform>-<arch>/.
 *
 * Verwendung:
 *   node scripts/fetch-binaries.mjs                       # aktuelle Plattform
 *   node scripts/fetch-binaries.mjs --platform win32 --arch x64
 *
 * Quellen:
 *   yt-dlp  — offizielle GitHub-Releases (yt-dlp/yt-dlp)
 *   ffmpeg  — statische Builds aus eugeneware/ffmpeg-static (GitHub-Releases)
 */
import { mkdir, chmod, writeFile, access } from 'node:fs/promises'
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
    force: args.includes('--force')
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

async function main() {
  const { platform, arch, force } = parseArgs()
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

  if (force || !(await exists(ytDest))) {
    await download(
      `https://github.com/yt-dlp/yt-dlp/releases/latest/download/${ytAsset}`,
      ytDest
    )
  } else {
    console.log(`  yt-dlp already present (use --force to refresh)`)
  }

  if (force || !(await exists(ffDest))) {
    await download(
      `https://github.com/eugeneware/ffmpeg-static/releases/download/${FFMPEG_STATIC_RELEASE}/${ffAsset}${platform === 'win32' ? '.exe' : ''}`,
      ffDest
    )
  } else {
    console.log(`  ffmpeg already present (use --force to refresh)`)
  }

  if (platform !== 'win32') {
    await chmod(ytDest, 0o755)
    await chmod(ffDest, 0o755)
  }
  console.log('Done.')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
