/**
 * electron-builder-Hook: besorgt vor jedem Packvorgang die gebündelten Binaries
 * für genau die Plattform/Architektur, die gerade gebaut wird.
 *
 * Ohne diesen Hook holt ein lokaler `npm run build:mac` nur die Binaries der
 * eigenen Architektur, electron-builder packt aber beide Mac-Varianten — die
 * x64-DMG entstand dann kommentarlos ohne yt-dlp und FFmpeg (electron-builder
 * meldet das nur als beiläufiges „file source doesn't exist“ und baut weiter).
 * Der Hook zieht die Binaries je Ziel nach und bricht ab, wenn das misslingt,
 * damit kein unbrauchbares Paket veröffentlicht wird.
 */
const { execFileSync } = require('node:child_process')
const { existsSync } = require('node:fs')
const { join } = require('node:path')

// electron-builder Arch-Enum → Bezeichner von fetch-binaries.mjs
const ARCH_NAMES = { 0: 'ia32', 1: 'x64', 2: 'armv7l', 3: 'arm64', 4: 'universal' }

exports.default = async function beforePack(context) {
  const platform = context.electronPlatformName // 'darwin' | 'win32' | 'linux'
  const arch = ARCH_NAMES[context.arch] ?? String(context.arch)

  // Universal-Builds setzen sich aus den bereits gepackten Einzel-Archs zusammen
  if (arch === 'universal') return

  const root = join(__dirname, '..')
  console.log(`  • ensuring bundled binaries  platform=${platform} arch=${arch}`)
  try {
    execFileSync(
      process.execPath,
      [join(root, 'scripts', 'fetch-binaries.mjs'), '--platform', platform, '--arch', arch],
      { cwd: root, stdio: 'inherit' }
    )
  } catch (err) {
    throw new Error(
      `Binaries für ${platform}-${arch} konnten nicht bereitgestellt werden: ${err.message}`
    )
  }

  // Absicherung: lieber der Build scheitert als ein Paket ohne yt-dlp/FFmpeg
  const dir = join(root, 'resources', 'bin', `${platform}-${arch}`)
  const ext = platform === 'win32' ? '.exe' : ''
  for (const name of [`yt-dlp${ext}`, `ffmpeg${ext}`]) {
    if (!existsSync(join(dir, name))) {
      throw new Error(`${name} fehlt in ${dir} — Paket wäre ohne Downloader unbrauchbar`)
    }
  }
}
