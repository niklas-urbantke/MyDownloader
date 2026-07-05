import { app, BrowserWindow } from 'electron'
import electronUpdater from 'electron-updater'
import { IPC, type UpdateEventPayload } from '@shared/types'
import { getSettings } from './settings'

const { autoUpdater } = electronUpdater

/**
 * Auto-Updater über GitHub Releases (Issue #33).
 * electron-builder legt die nötigen Update-Metadaten (latest*.yml) bei jedem
 * Release an; electron-updater vergleicht dagegen und lädt bei Bedarf.
 */

function broadcast(payload: UpdateEventPayload): void {
  for (const win of BrowserWindow.getAllWindows()) {
    win.webContents.send(IPC.updateEvent, payload)
  }
}

let initialized = false

export function setupAutoUpdater(): void {
  if (initialized || !app.isPackaged) return
  initialized = true

  autoUpdater.autoDownload = false
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.on('checking-for-update', () => broadcast({ status: 'checking' }))
  autoUpdater.on('update-available', (info) => {
    broadcast({
      status: 'available',
      version: info.version,
      notes: typeof info.releaseNotes === 'string' ? info.releaseNotes : undefined
    })
    if (getSettings().autoUpdate === 'auto') {
      void autoUpdater.downloadUpdate()
    }
  })
  autoUpdater.on('update-not-available', () => broadcast({ status: 'not-available' }))
  autoUpdater.on('download-progress', (p) =>
    broadcast({ status: 'downloading', percent: p.percent })
  )
  autoUpdater.on('update-downloaded', (info) =>
    broadcast({ status: 'downloaded', version: info.version })
  )
  autoUpdater.on('error', (err) => broadcast({ status: 'error', message: err.message }))

  // Beim Start prüfen (außer deaktiviert), leicht verzögert
  if (getSettings().autoUpdate !== 'off') {
    setTimeout(() => {
      void autoUpdater.checkForUpdates().catch(() => undefined)
    }, 10_000)
  }
}

export async function checkForUpdates(): Promise<void> {
  if (!app.isPackaged) {
    broadcast({ status: 'error', message: 'Updates nur in der installierten App verfügbar' })
    return
  }
  setupAutoUpdater()
  await autoUpdater.checkForUpdates().catch((err) => {
    broadcast({ status: 'error', message: err instanceof Error ? err.message : String(err) })
  })
}

export async function downloadUpdate(): Promise<void> {
  await autoUpdater.downloadUpdate().catch((err) => {
    broadcast({ status: 'error', message: err instanceof Error ? err.message : String(err) })
  })
}

export function installUpdate(): void {
  autoUpdater.quitAndInstall()
}
