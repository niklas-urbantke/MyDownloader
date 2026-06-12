import { clipboard, BrowserWindow } from 'electron'
import { IPC } from '@shared/types'
import { getSettings } from './settings'

/** Hosts, bei denen ein Clipboard-Hinweis sinnvoll ist */
const VIDEO_URL = /^https?:\/\/(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com|vimeo\.com|soundcloud\.com|twitch\.tv|dailymotion\.com)\//i

let lastText = ''
let timer: ReturnType<typeof setInterval> | null = null

/**
 * Beobachtet die Zwischenablage (nur wenn in den Einstellungen aktiviert)
 * und meldet neue Video-URLs an den Renderer.
 */
export function startClipboardWatcher(): void {
  if (timer) return
  lastText = clipboard.readText() // Bestand beim Start nicht melden
  timer = setInterval(() => {
    if (!getSettings().clipboardWatcher) return
    const text = clipboard.readText().trim()
    if (!text || text === lastText) return
    lastText = text
    const firstLine = text.split(/\r?\n/)[0] ?? ''
    if (VIDEO_URL.test(firstLine)) {
      for (const win of BrowserWindow.getAllWindows()) {
        win.webContents.send(IPC.clipboardUrl, firstLine)
      }
    }
  }, 1500)
}
