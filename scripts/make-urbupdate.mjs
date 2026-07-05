#!/usr/bin/env node
/**
 * Baut ein .urbupdate-Archiv (Issue #37) aus den Release-Artefakten.
 *
 * Verwendung (nach `npm run build:linux` / CI-Downloads in release/):
 *   node scripts/make-urbupdate.mjs [--dir release] [--out <datei>] [--platform linux|win32|darwin]
 *
 * Das Archiv ist ein ZIP mit manifest.json und den Installern.
 * Ohne --platform landen alle gefundenen Assets in EINER Datei (groß).
 * Mit --platform wird nur das passende Asset gepackt (klein, empfohlen).
 * In der App: Info → „Update aus Datei installieren“.
 */
import { createHash } from 'node:crypto'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import AdmZip from 'adm-zip'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const pkg = JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf-8'))

const args = process.argv.slice(2)
const get = (name, fallback) => {
  const i = args.indexOf(`--${name}`)
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback
}
const dir = join(ROOT, get('dir', 'release'))
const platformFilter = get('platform', null)
const defaultOut = platformFilter
  ? `MyDownloader-${pkg.version}-${platformFilter}.urbupdate`
  : `MyDownloader-${pkg.version}.urbupdate`
const out = join(ROOT, get('out', defaultOut))

/** Ordnet Release-Dateien Plattform/Typ zu */
function classify(file) {
  if (file.endsWith('.AppImage')) return { platform: 'linux', arch: 'x64', type: 'appimage' }
  if (/Setup.*\.exe$/.test(file)) return { platform: 'win32', arch: 'x64', type: 'nsis' }
  if (file.endsWith('-arm64.dmg')) return { platform: 'darwin', arch: 'arm64', type: 'dmg' }
  if (file.endsWith('.dmg')) return { platform: 'darwin', arch: 'x64', type: 'dmg' }
  return null
}

const zip = new AdmZip()
const assets = []

for (const file of readdirSync(dir)) {
  const meta = classify(file)
  if (!meta) continue
  if (platformFilter && meta.platform !== platformFilter) continue
  const path = join(dir, file)
  if (!statSync(path).isFile()) continue
  const data = readFileSync(path)
  const sha256 = createHash('sha256').update(data).digest('hex')
  zip.addFile(file, data)
  assets.push({ ...meta, file, sha256 })
  console.log(`  + ${file} (${(data.length / 1024 / 1024).toFixed(1)} MB, ${meta.platform}/${meta.arch})`)
}

if (assets.length === 0) {
  console.error(`Keine Release-Artefakte in ${dir} gefunden.`)
  process.exit(1)
}

const manifest = {
  name: 'mydownloader',
  version: pkg.version,
  createdAt: new Date().toISOString(),
  assets
}
zip.addFile('manifest.json', Buffer.from(JSON.stringify(manifest, null, 2), 'utf-8'))
zip.writeZip(out)
console.log(`\n✓ ${out}`)
