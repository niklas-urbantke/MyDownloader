import { app, BrowserWindow, Menu, Tray, nativeImage } from 'electron'
import icon from '../../build/icon.png?asset'
import type { DownloadQueue } from './queue'

/**
 * System-Tray-Integration (Issue #14): Icon mit Kontextmenü und
 * Fortschritts-Tooltip; optional Schließen-in-den-Tray.
 */

let tray: Tray | null = null
let quitting = false

export function isQuitting(): boolean {
  return quitting
}

export function setupTray(queue: DownloadQueue, getWindow: () => BrowserWindow | null): void {
  const image = nativeImage.createFromPath(icon).resize({ width: 22, height: 22 })
  tray = new Tray(image)
  tray.setToolTip('MyDownloader')

  const showWindow = (): void => {
    const win = getWindow()
    if (!win) return
    if (win.isMinimized()) win.restore()
    win.show()
    win.focus()
  }

  const rebuildMenu = (): void => {
    if (!tray) return
    const processing = queue.isProcessing()
    tray.setContextMenu(
      Menu.buildFromTemplate([
        { label: 'MyDownloader öffnen', click: showWindow },
        { type: 'separator' },
        processing
          ? { label: 'Warteschlange pausieren', click: () => queue.pauseProcessing() }
          : { label: 'Warteschlange starten', click: () => queue.startProcessing() },
        { type: 'separator' },
        {
          label: 'Beenden',
          click: () => {
            quitting = true
            app.quit()
          }
        }
      ])
    )
  }
  rebuildMenu()

  tray.on('click', showWindow)

  // Tooltip mit Live-Fortschritt versorgen
  updateTrayProgress(queue)
  setInterval(() => {
    updateTrayProgress(queue)
    rebuildMenu()
  }, 3000)

  app.on('before-quit', () => {
    quitting = true
  })
}

export function updateTrayProgress(queue: DownloadQueue): void {
  if (!tray) return
  const items = queue.list()
  const active = items.filter((i) => i.status === 'downloading' || i.status === 'converting')
  if (active.length === 0) {
    const queued = items.filter((i) => i.status === 'queued').length
    tray.setToolTip(queued > 0 ? `MyDownloader — ${queued} wartend` : 'MyDownloader')
    return
  }
  const known = active.filter((i) => i.progress.percent >= 0)
  const avg =
    known.length > 0
      ? Math.round(known.reduce((s, i) => s + i.progress.percent, 0) / known.length)
      : null
  tray.setToolTip(
    `MyDownloader — ${active.length} aktiv${avg !== null ? `, ${avg} %` : ''}`
  )
}
