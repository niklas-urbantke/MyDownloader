import { app, shell, BrowserWindow } from 'electron'
import { join } from 'node:path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import { registerIpc, queue } from './ipc'
import { startClipboardWatcher } from './clipboard'

function createWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1320,
    height: 880,
    minWidth: 1000,
    minHeight: 680,
    show: false,
    autoHideMenuBar: true,
    title: 'MyDownloader',
    backgroundColor: '#F2F5F9',
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  win.on('ready-to-show', () => win.show())

  // Smoke-Test-Hooks:
  //   MD_SCREENSHOT=<pfad.png>  Screenshot machen und beenden
  //   MD_SCREENSHOT_DELAY=<ms>  Wartezeit vor dem Screenshot (Default 2500)
  //   MD_E2E_URL=<url>          beim Start einen Download in die Queue legen
  const screenshotPath = process.env['MD_SCREENSHOT']
  if (screenshotPath) {
    const delay = Number.parseInt(process.env['MD_SCREENSHOT_DELAY'] ?? '2500', 10)
    win.webContents.once('did-finish-load', () => {
      const e2eUrl = process.env['MD_E2E_URL']
      if (e2eUrl) queue.add({ url: e2eUrl })
      setTimeout(async () => {
        const image = await win.webContents.capturePage()
        const { writeFileSync } = await import('node:fs')
        writeFileSync(screenshotPath, image.toPNG())
        app.quit()
      }, delay)
    })
  }

  win.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  const hash = process.env['MD_ROUTE']
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    win.loadURL(process.env['ELECTRON_RENDERER_URL'] + (hash ? `#${hash}` : ''))
  } else {
    win.loadFile(join(__dirname, '../renderer/index.html'), hash ? { hash } : undefined)
  }

  return win
}

const gotLock = app.requestSingleInstanceLock()
if (!gotLock) {
  app.quit()
} else {
  app.whenReady().then(() => {
    electronApp.setAppUserModelId('com.niklasurbantke.mydownloader')

    app.on('browser-window-created', (_, window) => {
      optimizer.watchWindowShortcuts(window)
    })

    registerIpc()
    startClipboardWatcher()
    createWindow()

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
  })

  app.on('second-instance', () => {
    const [win] = BrowserWindow.getAllWindows()
    if (win) {
      if (win.isMinimized()) win.restore()
      win.focus()
    }
  })

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })

  // Laufende yt-dlp-Prozesse beim Beenden sauber abräumen
  app.on('before-quit', () => {
    queue.cancelAll()
  })
}
