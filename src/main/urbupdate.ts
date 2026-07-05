import { app, dialog, shell } from 'electron'
import { spawn } from 'node:child_process'
import { createHash } from 'node:crypto'
import { chmodSync, mkdirSync, renameSync, writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import AdmZip from 'adm-zip'

/**
 * .urbupdate-Format (Issue #37): ein ZIP-Archiv mit manifest.json und den
 * Plattform-Assets. Erstellt wird es mit `node scripts/make-urbupdate.mjs`
 * nach einem Release-Build.
 *
 * manifest.json:
 * {
 *   "name": "mydownloader",
 *   "version": "5.0.0",
 *   "assets": [
 *     { "platform": "linux",  "arch": "x64", "type": "appimage", "file": "MyDownloader-5.0.0-x86_64.AppImage", "sha256": "…" },
 *     { "platform": "win32",  "arch": "x64", "type": "nsis",     "file": "MyDownloader-Setup-5.0.0.exe",       "sha256": "…" },
 *     { "platform": "darwin", "arch": "arm64", "type": "dmg",    "file": "MyDownloader-5.0.0-arm64.dmg",       "sha256": "…" }
 *   ]
 * }
 */

interface UrbAsset {
  platform: string
  arch?: string
  type: string
  file: string
  sha256: string
}

interface UrbManifest {
  name?: string
  version?: string
  assets?: UrbAsset[]
}

function compareVersions(a: string, b: string): number {
  const pa = a.split('.').map((n) => Number.parseInt(n, 10) || 0)
  const pb = b.split('.').map((n) => Number.parseInt(n, 10) || 0)
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const diff = (pa[i] ?? 0) - (pb[i] ?? 0)
    if (diff !== 0) return diff
  }
  return 0
}

/** Öffnet den Dateidialog und installiert das gewählte .urbupdate-Archiv. */
export async function installUrbUpdate(): Promise<{ ok: boolean; message: string }> {
  const picked = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [{ name: 'MyDownloader Update', extensions: ['urbupdate'] }]
  })
  if (picked.canceled || !picked.filePaths[0]) return { ok: false, message: 'cancelled' }

  try {
    const zip = new AdmZip(picked.filePaths[0])
    const manifestEntry = zip.getEntry('manifest.json')
    if (!manifestEntry) return { ok: false, message: 'manifest.json fehlt im Archiv' }
    const manifest = JSON.parse(manifestEntry.getData().toString('utf-8')) as UrbManifest

    if (manifest.name !== 'mydownloader') {
      return { ok: false, message: 'Das Archiv ist kein MyDownloader-Update' }
    }
    const version = manifest.version ?? '0.0.0'
    if (compareVersions(version, app.getVersion()) <= 0) {
      return {
        ok: false,
        message: `Enthaltene Version ${version} ist nicht neuer als ${app.getVersion()}`
      }
    }

    // Passendes Asset für Plattform/Architektur suchen
    const asset = (manifest.assets ?? []).find(
      (a) => a.platform === process.platform && (!a.arch || a.arch === process.arch)
    )
    if (!asset) {
      return { ok: false, message: `Kein Update-Asset für ${process.platform}/${process.arch}` }
    }
    const entry = zip.getEntry(asset.file)
    if (!entry) return { ok: false, message: `Asset ${asset.file} fehlt im Archiv` }

    const data = entry.getData()
    const hash = createHash('sha256').update(data).digest('hex')
    if (hash !== asset.sha256) {
      return { ok: false, message: 'Prüfsumme stimmt nicht — Archiv beschädigt?' }
    }

    // --- Linux AppImage ---
    if (process.platform === 'linux' && asset.type === 'appimage') {
      // Direkt gestartete AppImage: sich selbst ersetzen und neu starten.
      const current = process.env['APPIMAGE']
      if (current) {
        try {
          const tmp = `${current}.update`
          writeFileSync(tmp, data)
          chmodSync(tmp, 0o755)
          renameSync(tmp, current)
          app.relaunch({ execPath: current })
          app.quit()
          return { ok: true, message: 'Update installiert — App startet neu' }
        } catch {
          // z. B. schreibgeschützter Ort — unten auf „in Ordner ablegen“ zurückfallen
        }
      }

      // Kein APPIMAGE (App läuft extrahiert/integriert, z. B. über GearLever):
      // Es gibt keine AppImage-Datei zum Ersetzen. Neue Version ablegen und
      // den Ordner öffnen, damit sie über den AppImage-Manager übernommen wird.
      const downloads = app.getPath('downloads')
      mkdirSync(downloads, { recursive: true })
      const target = join(downloads, asset.file)
      writeFileSync(target, data)
      chmodSync(target, 0o755)
      void shell.openPath(downloads)
      return {
        ok: true,
        message:
          `Neue Version nach „${target}“ gespeichert. Die App läuft nicht direkt als ` +
          `AppImage (z. B. über GearLever integriert) — bitte diese Datei über deinen ` +
          `AppImage-Manager aktualisieren oder die integrierte AppImage damit ersetzen.`
      }
    }

    // --- Windows: Installer entpacken und starten ---
    if (process.platform === 'win32') {
      const dir = join(app.getPath('temp'), 'mydownloader-update')
      mkdirSync(dir, { recursive: true })
      const target = join(dir, asset.file)
      writeFileSync(target, data)
      spawn(target, [], { detached: true, stdio: 'ignore' }).unref()
      app.quit()
      return { ok: true, message: 'Installer gestartet' }
    }

    // --- macOS: DMG/ZIP in Downloads legen und öffnen ---
    const downloads = app.getPath('downloads')
    mkdirSync(downloads, { recursive: true })
    const target = join(downloads, asset.file)
    writeFileSync(target, data)
    void shell.openPath(dirname(target))
    return {
      ok: true,
      message: `Update nach ${target} entpackt — bitte manuell installieren`
    }
  } catch (err) {
    return { ok: false, message: err instanceof Error ? err.message : String(err) }
  }
}
