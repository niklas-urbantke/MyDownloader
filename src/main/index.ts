import { app, shell, BrowserWindow, nativeImage } from 'electron'
import { join } from 'node:path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import appIcon from '../../build/icons/512x512.png?asset'
import { registerIpc, queue } from './ipc'
import { startClipboardWatcher } from './clipboard'
import { getSettings } from './settings'
import { setupTray, isQuitting } from './tray'
import { setupAutoUpdater } from './updater'

/**
 * Deep-Links (Issue #34): mydownloader://download?url=<encoded>
 * Fügt die übergebene URL der Warteschlange hinzu und holt das Fenster nach vorn.
 */
function handleDeepLink(link: string): void {
  try {
    const parsed = new URL(link)
    if (parsed.protocol !== 'mydownloader:') return
    const target = parsed.searchParams.get('url')
    if (target && /^https?:\/\//.test(target)) {
      queue.add({ url: target })
    }
    const [win] = BrowserWindow.getAllWindows()
    if (win) {
      if (win.isMinimized()) win.restore()
      win.show()
      win.focus()
    }
  } catch {
    /* ungültiger Link — ignorieren */
  }
}

function deepLinkFromArgv(argv: string[]): string | null {
  return argv.find((a) => a.startsWith('mydownloader://')) ?? null
}

function createWindow(): BrowserWindow {
  // Test-Hook: größere Fensterhöhe für Ganzseiten-Screenshots (MD_WIN_HEIGHT)
  const testHeight = Number.parseInt(process.env['MD_WIN_HEIGHT'] ?? '', 10)
  const win = new BrowserWindow({
    width: 1320,
    height: Number.isFinite(testHeight) && testHeight > 0 ? testHeight : 880,
    minWidth: 1000,
    minHeight: 680,
    show: false,
    autoHideMenuBar: true,
    title: 'MyDownloader',
    // Fenster-/Taskbar-Icon zur Laufzeit (v. a. Linux/X11, wo es sonst fehlt)
    icon: nativeImage.createFromPath(appIcon),
    backgroundColor: '#F2F5F9',
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  win.on('ready-to-show', () => win.show())

  // Schließen minimiert in den Tray, wenn aktiviert (Issue #14)
  win.on('close', (event) => {
    if (getSettings().closeToTray && !isQuitting()) {
      event.preventDefault()
      win.hide()
    }
  })

  // Smoke-Test-Hooks:
  //   MD_SCREENSHOT=<pfad.png>  Screenshot machen und beenden
  //   MD_SCREENSHOT_DELAY=<ms>  Wartezeit vor dem Screenshot (Default 2500)
  //   MD_E2E_URL=<url>          beim Start einen Download in die Queue legen
  const screenshotPath = process.env['MD_SCREENSHOT']
  if (screenshotPath) {
    const delay = Number.parseInt(process.env['MD_SCREENSHOT_DELAY'] ?? '2500', 10)
    win.webContents.once('did-finish-load', () => {
      const e2eUrl = process.env['MD_E2E_URL']
      if (e2eUrl) queue.add({ url: e2eUrl, startNow: true })
      setTimeout(async () => {
        // Optional die CTA-Schaltfläche eines Dialogs mehrfach klicken
        // (z. B. Onboarding „Weiter“) — MD_CLICK_CTA=<anzahl>
        const clicks = Number.parseInt(process.env['MD_CLICK_CTA'] ?? '', 10)
        if (Number.isFinite(clicks) && clicks > 0) {
          for (let i = 0; i < clicks; i++) {
            await win.webContents
              .executeJavaScript(
                'document.querySelector(".bx-dialog-actions .btn--cta")?.click()'
              )
              .catch(() => undefined)
            await new Promise((r) => setTimeout(r, 500))
          }
        }
        // Optional den Inhaltsbereich scrollen (MD_SCROLL=<px>|'bottom')
        const scroll = process.env['MD_SCROLL']
        if (scroll) {
          const y = scroll === 'bottom' ? 100000 : Number.parseInt(scroll, 10) || 0
          await win.webContents
            .executeJavaScript(`document.querySelector(".bx-page")?.scrollTo(0, ${y})`)
            .catch(() => undefined)
          await new Promise((r) => setTimeout(r, 400))
        }
        // Optional herauszoomen, damit lange Seiten komplett passen (MD_ZOOM=0.6)
        const zoom = Number.parseFloat(process.env['MD_ZOOM'] ?? '')
        if (Number.isFinite(zoom) && zoom > 0) {
          win.webContents.setZoomFactor(zoom)
          await new Promise((r) => setTimeout(r, 500))
        }
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
  // Protokoll-Handler registrieren (Issue #34)
  app.setAsDefaultProtocolClient('mydownloader')

  app.whenReady().then(() => {
    electronApp.setAppUserModelId('com.niklasurbantke.mydownloader')

    app.on('browser-window-created', (_, window) => {
      optimizer.watchWindowShortcuts(window)
    })

    registerIpc()
    startClipboardWatcher()
    const win = createWindow()
    setupTray(queue, () => BrowserWindow.getAllWindows()[0] ?? null)
    setupAutoUpdater()

    // Deep-Link aus dem Erststart-Aufruf (Windows/Linux)
    const initialLink = deepLinkFromArgv(process.argv)
    if (initialLink) {
      win.webContents.once('did-finish-load', () => handleDeepLink(initialLink))
    }

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
  })

  // Zweite Instanz: Deep-Link übernehmen und Fenster fokussieren
  app.on('second-instance', (_event, argv) => {
    const link = deepLinkFromArgv(argv)
    if (link) {
      handleDeepLink(link)
      return
    }
    const [win] = BrowserWindow.getAllWindows()
    if (win) {
      if (win.isMinimized()) win.restore()
      win.show()
      win.focus()
    }
  })

  // macOS liefert Deep-Links über open-url
  app.on('open-url', (_event, url) => handleDeepLink(url))

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
  })

  // Zustand sichern und laufende yt-dlp-Prozesse sauber beenden — nach dem
  // nächsten Start stehen unterbrochene Downloads als „Pausiert“ bereit
  app.on('before-quit', () => {
    queue.shutdown()
  })
}
