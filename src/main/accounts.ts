import { app, BrowserWindow, session } from 'electron'
import { existsSync, mkdirSync, writeFileSync, unlinkSync } from 'node:fs'
import { join } from 'node:path'
import type { AccountStatus } from '@shared/types'

/**
 * YouTube-/Google-Konto-Anbindung (Issue #13): Der Nutzer meldet sich in einem
 * echten Browserfenster an; die Cookies der Session werden im
 * Netscape-Format exportiert und an yt-dlp durchgereicht (--cookies).
 * Damit funktionieren altersbeschränkte und Mitglieder-Inhalte.
 */

const PARTITION = 'persist:account-youtube'

function cookieDir(): string {
  return join(app.getPath('userData'), 'cookies')
}

export function cookieFilePath(): string {
  return join(cookieDir(), 'youtube.txt')
}

/** Exportiert die Session-Cookies als Netscape cookies.txt */
export async function exportCookies(): Promise<boolean> {
  const ses = session.fromPartition(PARTITION)
  const cookies = await ses.cookies.get({})
  const relevant = cookies.filter((c) =>
    /(^|\.)((youtube|google|googlevideo)\.[a-z.]+)$/.test(c.domain ?? '')
  )
  if (relevant.length === 0) return false

  const lines = ['# Netscape HTTP Cookie File', '# Exportiert von MyDownloader', '']
  for (const c of relevant) {
    const domain = c.domain ?? ''
    const includeSubdomains = domain.startsWith('.') ? 'TRUE' : 'FALSE'
    const path = c.path ?? '/'
    const secure = c.secure ? 'TRUE' : 'FALSE'
    const expires = c.expirationDate ? Math.floor(c.expirationDate) : 0
    lines.push(
      [domain, includeSubdomains, path, secure, expires, c.name, c.value].join('\t')
    )
  }
  mkdirSync(cookieDir(), { recursive: true })
  writeFileSync(cookieFilePath(), lines.join('\n'), 'utf-8')
  return true
}

/** Ist ein Login vorhanden? (heuristisch über die Google-Session-Cookies) */
export async function accountStatus(): Promise<AccountStatus> {
  const ses = session.fromPartition(PARTITION)
  const cookies = await ses.cookies.get({ name: 'SAPISID' })
  const loggedIn = cookies.length > 0
  const file = cookieFilePath()
  return { loggedIn, cookieFile: loggedIn && existsSync(file) ? file : null }
}

/**
 * Öffnet das Login-Fenster. Auflösung, wenn der Nutzer das Fenster schließt —
 * danach werden die Cookies exportiert.
 */
export async function loginYouTube(parent?: BrowserWindow): Promise<AccountStatus> {
  await new Promise<void>((resolve) => {
    const win = new BrowserWindow({
      width: 520,
      height: 720,
      parent,
      title: 'YouTube-Konto anmelden',
      autoHideMenuBar: true,
      webPreferences: {
        partition: PARTITION,
        nodeIntegration: false,
        contextIsolation: true
      }
    })
    win.on('closed', () => resolve())
    void win.loadURL(
      'https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2F'
    )
    // Sobald der Login durch ist, landet man auf youtube.com — Fenster kann zu
    win.webContents.on('did-navigate', (_e, url) => {
      if (/^https:\/\/(www\.)?youtube\.com\/?$/.test(url)) {
        setTimeout(() => {
          if (!win.isDestroyed()) win.close()
        }, 1500)
      }
    })
  })
  await exportCookies()
  return accountStatus()
}

/** Meldet das Konto ab und entfernt die exportierten Cookies. */
export async function logoutYouTube(): Promise<AccountStatus> {
  const ses = session.fromPartition(PARTITION)
  await ses.clearStorageData()
  try {
    if (existsSync(cookieFilePath())) unlinkSync(cookieFilePath())
  } catch {
    /* ignorieren */
  }
  return accountStatus()
}

/** Liefert den Pfad zur cookies.txt, wenn Konto-Cookies genutzt werden sollen. */
export function activeCookieFile(useAccountCookies: boolean): string | null {
  if (!useAccountCookies) return null
  const file = cookieFilePath()
  return existsSync(file) ? file : null
}
