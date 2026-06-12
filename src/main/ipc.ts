import { app, dialog, ipcMain, shell, Notification, BrowserWindow } from 'electron'
import { existsSync } from 'node:fs'
import { IPC, type AppSettings, type DownloadRequest } from '@shared/types'
import { getSettings, updateSettings } from './settings'
import { listHistory, addHistoryEntry, removeHistoryEntry, clearHistory } from './history'
import { getBinaryStatus, updateYtDlp } from './binaries'
import { probeUrl } from './ytdlp'
import { DownloadQueue } from './queue'
import { importV3Data } from './importV3'

function broadcast(channel: string, ...args: unknown[]): void {
  for (const win of BrowserWindow.getAllWindows()) {
    win.webContents.send(channel, ...args)
  }
}

/** Gesamtfortschritt aller aktiven Downloads in Dock/Taskbar anzeigen */
function updateDockProgress(): void {
  const active = queue
    .list()
    .filter((i) => i.status === 'downloading' || i.status === 'converting')
  const win = BrowserWindow.getAllWindows()[0]
  if (!win) return
  if (active.length === 0) {
    win.setProgressBar(-1)
    return
  }
  const known = active.filter((i) => i.progress.percent >= 0)
  if (known.length === 0) {
    win.setProgressBar(2) // unbestimmt
    return
  }
  const avg = known.reduce((sum, i) => sum + i.progress.percent, 0) / known.length / 100
  win.setProgressBar(Math.min(0.99, Math.max(0, avg)))
}

export const queue = new DownloadQueue({
  onItemChanged: (item) => {
    broadcast(IPC.downloadChanged, item)
    updateDockProgress()
  },
  onLogLine: (id, line) => broadcast(IPC.downloadLogLine, { id, line }),
  onItemFinished: (item) => {
    addHistoryEntry(item)
    const settings = getSettings()
    if (settings.notifyOnComplete && Notification.isSupported()) {
      if (item.status === 'completed') {
        new Notification({ title: 'MyDownloader', body: `✓ ${item.title}` }).show()
      } else if (item.status === 'error') {
        new Notification({ title: 'MyDownloader', body: `✗ ${item.title}` }).show()
      }
    }
  }
})

export function registerIpc(): void {
  // --- Settings -------------------------------------------------------------
  ipcMain.handle(IPC.settingsGet, () => getSettings())
  ipcMain.handle(IPC.settingsSet, (_e, patch: Partial<AppSettings>) => updateSettings(patch))
  ipcMain.handle(IPC.settingsPickFolder, async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'createDirectory'],
      defaultPath: getSettings().downloadFolder
    })
    return result.canceled ? null : (result.filePaths[0] ?? null)
  })

  // --- Medien-Infos ----------------------------------------------------------
  ipcMain.handle(IPC.mediaProbe, async (_e, url: string) => probeUrl(url))

  // --- Downloads --------------------------------------------------------------
  ipcMain.handle(IPC.downloadAdd, (_e, request: DownloadRequest) => queue.add(request))
  ipcMain.handle(IPC.downloadAddMany, (_e, requests: DownloadRequest[]) =>
    queue.addMany(requests)
  )
  ipcMain.handle(IPC.downloadCancel, (_e, id: string) => queue.cancel(id))
  ipcMain.handle(IPC.downloadRetry, (_e, id: string) => queue.retry(id))
  ipcMain.handle(IPC.downloadRemove, (_e, id: string) => queue.remove(id))
  ipcMain.handle(IPC.downloadClearFinished, () => queue.clearFinished())
  ipcMain.handle(IPC.downloadList, () => queue.list())
  ipcMain.handle(IPC.downloadGetLog, (_e, id: string) => queue.getLog(id))

  // --- Verlauf ----------------------------------------------------------------
  ipcMain.handle(IPC.historyList, () => listHistory())
  ipcMain.handle(IPC.historyRemove, (_e, id: string) => removeHistoryEntry(id))
  ipcMain.handle(IPC.historyClear, () => clearHistory())

  // --- System -----------------------------------------------------------------
  ipcMain.handle(IPC.binariesStatus, () => getBinaryStatus())
  ipcMain.handle(IPC.binariesUpdateYtDlp, () => updateYtDlp())
  ipcMain.handle(IPC.importV3, () => importV3Data())
  ipcMain.handle(IPC.appInfo, () => ({
    version: app.getVersion(),
    platform: process.platform,
    arch: process.arch,
    electronVersion: process.versions.electron,
    userDataPath: app.getPath('userData')
  }))
  ipcMain.handle(IPC.openPath, (_e, path: string) => shell.openPath(path))
  ipcMain.handle(IPC.showInFolder, (_e, path: string) => {
    if (existsSync(path)) {
      shell.showItemInFolder(path)
      return true
    }
    return false
  })
  ipcMain.handle(IPC.openExternal, (_e, url: string) => {
    if (/^https?:\/\//.test(url)) shell.openExternal(url)
  })
}
