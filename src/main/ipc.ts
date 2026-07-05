import { app, dialog, ipcMain, shell, Notification, BrowserWindow } from 'electron'
import { existsSync } from 'node:fs'
import { IPC, type AppSettings, type DownloadRequest, type DownloadTemplate } from '@shared/types'
import { listTemplates, saveTemplate, deleteTemplate } from './templates'
import { readTags, writeTags, searchMusicBrainz } from './metadata'
import type { TrackTags } from '@shared/types'
import { getSettings, updateSettings } from './settings'
import { listHistory, addHistoryEntry, removeHistoryEntry, clearHistory } from './history'
import { getBinaryStatus, updateYtDlp } from './binaries'
import { probeUrl, previewStreamUrl } from './ytdlp'
import { DownloadQueue } from './queue'
import { importV3Data } from './importV3'
import { accountStatus, exportCookies, loginYouTube, logoutYouTube } from './accounts'
import {
  addSubscription,
  checkSubscription,
  listSubscriptions,
  removeSubscription,
  startSubscriptionScheduler,
  updateSubscription
} from './subscriptions'
import { getSpotifyPlaylist, spotifyLogin, spotifyLogout, spotifyStatus } from './spotify'
import { computeStats } from './stats'
import type { Subscription } from '@shared/types'

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
  onQueueState: (processing) => broadcast(IPC.downloadQueueState, processing),
  onItemFinished: (item) => {
    addHistoryEntry(item)
    const settings = getSettings()
    if (settings.notifyOnComplete && Notification.isSupported()) {
      if (item.status === 'completed') {
        const count =
          item.isPlaylist && item.outputFiles.length > 1 ? ` (${item.outputFiles.length})` : ''
        const n = new Notification({ title: 'MyDownloader', body: `✓ ${item.title}${count}` })
        // Klick öffnet die fertige Datei im Dateimanager (bzw. den Zielordner)
        n.on('click', () => {
          const file = item.outputFiles.at(-1)
          if (file && existsSync(file)) shell.showItemInFolder(file)
          else void shell.openPath(item.destination)
        })
        n.show()
      } else if (item.status === 'error') {
        new Notification({ title: 'MyDownloader', body: `✗ ${item.title}` }).show()
      }
    }
  }
})

export function registerIpc(): void {
  // Queue des letzten Laufs wiederherstellen (Issue #19)
  queue.restore()

  // --- Settings -------------------------------------------------------------
  ipcMain.handle(IPC.settingsGet, () => getSettings())
  ipcMain.handle(IPC.settingsSet, (_e, patch: Partial<AppSettings>) => updateSettings(patch))
  // Fire-and-forget beim Schließen: der Renderer kann nicht mehr auf eine
  // Antwort warten, die Änderung darf aber nicht verloren gehen (Issue #7)
  ipcMain.on(IPC.settingsFlush, (_e, patch: Partial<AppSettings>) => {
    updateSettings(patch)
  })
  ipcMain.handle(IPC.settingsPickFolder, async (_e, defaultPath?: string) => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'createDirectory'],
      defaultPath: defaultPath || getSettings().downloadFolder
    })
    return result.canceled ? null : (result.filePaths[0] ?? null)
  })

  // --- Medien-Infos ----------------------------------------------------------
  ipcMain.handle(IPC.mediaProbe, async (_e, url: string) => probeUrl(url))
  ipcMain.handle(IPC.mediaPreviewUrl, async (_e, url: string) => previewStreamUrl(url))

  // --- Downloads --------------------------------------------------------------
  ipcMain.handle(IPC.downloadAdd, (_e, request: DownloadRequest) => queue.add(request))
  ipcMain.handle(IPC.downloadAddMany, (_e, requests: DownloadRequest[]) =>
    queue.addMany(requests)
  )
  ipcMain.handle(IPC.downloadCancel, (_e, id: string) => queue.cancel(id))
  ipcMain.handle(IPC.downloadPause, (_e, id: string) => queue.pause(id))
  ipcMain.handle(IPC.downloadResume, (_e, id: string) => queue.resume(id))
  ipcMain.handle(IPC.downloadRetry, (_e, id: string) => queue.retry(id))
  ipcMain.handle(IPC.downloadRemove, (_e, id: string) => queue.remove(id))
  ipcMain.handle(IPC.downloadClearFinished, () => queue.clearFinished())
  ipcMain.handle(IPC.downloadList, () => queue.list())
  ipcMain.handle(IPC.downloadGetLog, (_e, id: string) => queue.getLog(id))
  ipcMain.handle(IPC.downloadQueueStart, () => queue.startProcessing())
  ipcMain.handle(IPC.downloadQueuePause, () => queue.pauseProcessing())
  ipcMain.handle(IPC.downloadQueueState, () => queue.isProcessing())
  ipcMain.handle(IPC.downloadMove, (_e, id: string, direction: 'up' | 'down') =>
    queue.move(id, direction)
  )

  // --- Vorlagen -----------------------------------------------------------------
  ipcMain.handle(IPC.templatesList, () => listTemplates())
  ipcMain.handle(IPC.templatesSave, (_e, template: DownloadTemplate) => saveTemplate(template))
  ipcMain.handle(IPC.templatesDelete, (_e, id: string) => deleteTemplate(id))

  // --- Metadaten (Issue #25) ----------------------------------------------------
  ipcMain.handle(IPC.metaReadTags, (_e, file: string) => readTags(file))
  ipcMain.handle(IPC.metaWriteTags, (_e, file: string, tags: TrackTags, cover: string | null) =>
    writeTags(file, tags, cover)
  )
  ipcMain.handle(IPC.metaSearchMusicBrainz, (_e, artist: string, title: string) =>
    searchMusicBrainz(artist, title)
  )
  ipcMain.handle(IPC.metaPickImage, async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: [{ name: 'Bilder', extensions: ['jpg', 'jpeg', 'png', 'webp'] }]
    })
    return result.canceled ? null : (result.filePaths[0] ?? null)
  })

  // --- Verlauf ----------------------------------------------------------------
  ipcMain.handle(IPC.historyList, () => listHistory())
  ipcMain.handle(IPC.historyRemove, (_e, id: string) => removeHistoryEntry(id))
  ipcMain.handle(IPC.historyClear, () => clearHistory())

  // --- Playlist-Abos (Issue #21) -------------------------------------------------
  startSubscriptionScheduler(queue, (subs) => broadcast(IPC.subsChanged, subs))
  ipcMain.handle(IPC.subsList, () => listSubscriptions())
  ipcMain.handle(
    IPC.subsAdd,
    (_e, url: string, options: { folder?: string; templateId?: string; intervalMinutes?: number }) =>
      addSubscription(url, options)
  )
  ipcMain.handle(IPC.subsUpdate, (_e, patch: Partial<Subscription> & { id: string }) =>
    updateSubscription(patch)
  )
  ipcMain.handle(IPC.subsRemove, (_e, id: string) => removeSubscription(id))
  ipcMain.handle(IPC.subsCheckNow, (_e, id: string) => checkSubscription(id))

  // --- Konto (Issue #13) ----------------------------------------------------------
  ipcMain.handle(IPC.accountStatus, () => accountStatus())
  ipcMain.handle(IPC.accountLogin, async () => {
    const status = await loginYouTube(BrowserWindow.getAllWindows()[0])
    return status
  })
  ipcMain.handle(IPC.accountLogout, () => logoutYouTube())
  // Beim Start einmal frisch exportieren, falls angemeldet
  void accountStatus().then((s) => {
    if (s.loggedIn) void exportCookies()
  })

  // --- Spotify (Issue #35) ---------------------------------------------------------
  ipcMain.handle(IPC.spotifyStatus, () => spotifyStatus())
  ipcMain.handle(IPC.spotifyLogin, () => spotifyLogin())
  ipcMain.handle(IPC.spotifyLogout, () => spotifyLogout())
  ipcMain.handle(IPC.spotifyGetPlaylist, (_e, url: string) => getSpotifyPlaylist(url))

  // --- Statistiken (Issue #36) ------------------------------------------------------
  ipcMain.handle(IPC.statsCompute, () => computeStats())

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
