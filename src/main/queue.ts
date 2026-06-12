import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { mkdirSync } from 'node:fs'
import type {
  AppSettings,
  DownloadItem,
  DownloadProgress,
  DownloadRequest,
  DownloadStatus
} from '@shared/types'
import { getSettings } from './settings'
import { buildDownloadCommand, probeUrl, ytDlpEnv, PROGRESS_PREFIX, OUTPUT_PREFIX } from './ytdlp'

const MAX_LOG_LINES = 2000

export interface QueueEvents {
  onItemChanged: (item: DownloadItem) => void
  onLogLine: (id: string, line: string) => void
  onItemFinished: (item: DownloadItem) => void
  /** Meldet, ob die Warteschlange gerade aktiv abgearbeitet wird */
  onQueueState: (processing: boolean) => void
}

interface InternalItem {
  item: DownloadItem
  request: DownloadRequest
  proc: ChildProcessWithoutNullStreams | null
  log: string[]
  cancelled: boolean
}

function looksLikePlaylist(url: string): boolean {
  return /[?&]list=/.test(url) || /\/playlist\b/.test(url)
}

function emptyProgress(): DownloadProgress {
  return {
    percent: -1,
    downloadedBytes: 0,
    totalBytes: null,
    speed: null,
    eta: null,
    playlistIndex: null,
    playlistCount: null
  }
}

/**
 * Verwaltet die Download-Warteschlange: startet bis zu `concurrency`
 * yt-dlp-Prozesse parallel, parst deren Fortschritt und meldet jede
 * Änderung an den Renderer.
 */
export class DownloadQueue {
  private items = new Map<string, InternalItem>()
  private order: string[] = []
  /**
   * false = wartende Einträge bleiben liegen, bis der Nutzer die Queue
   * startet. Einträge mit request.startNow laufen immer sofort los.
   */
  private processing = false

  constructor(private events: QueueEvents) {}

  isProcessing(): boolean {
    return this.processing
  }

  startProcessing(): void {
    if (!this.processing) {
      this.processing = true
      this.events.onQueueState(true)
    }
    this.tick()
  }

  pauseProcessing(): void {
    if (this.processing) {
      this.processing = false
      this.events.onQueueState(false)
    }
  }

  /** Verschiebt einen wartenden Eintrag in der Reihenfolge nach oben/unten. */
  move(id: string, direction: 'up' | 'down'): void {
    const idx = this.order.indexOf(id)
    if (idx === -1) return
    const target = direction === 'up' ? idx - 1 : idx + 1
    if (target < 0 || target >= this.order.length) return
    ;[this.order[idx], this.order[target]] = [this.order[target], this.order[idx]]
    // Beide betroffenen Items neu melden, damit der Renderer die Reihenfolge übernimmt
    this.emit(this.order[idx])
    this.emit(this.order[target])
  }

  list(): DownloadItem[] {
    return this.order
      .map((id) => this.items.get(id)?.item)
      .filter((i): i is DownloadItem => !!i)
  }

  getLog(id: string): string[] {
    return this.items.get(id)?.log ?? []
  }

  add(request: DownloadRequest): DownloadItem {
    const settings = getSettings()
    const merged = { ...settings, ...request.overrides }
    const isPlaylist = looksLikePlaylist(request.url)
    const item: DownloadItem = {
      id: randomUUID(),
      url: request.url,
      title: request.knownTitle ?? request.url,
      uploader: null,
      thumbnailUrl: null,
      status: 'queued',
      progress: emptyProgress(),
      mode: merged.mode,
      format: merged.mode === 'audio' ? merged.audioFormat : merged.videoContainer,
      destination: merged.downloadFolder,
      outputFiles: [],
      errorMessage: null,
      addedAt: new Date().toISOString(),
      startedAt: null,
      finishedAt: null,
      isPlaylist
    }
    this.items.set(item.id, { item, request, proc: null, log: [], cancelled: false })
    this.order.push(item.id)
    this.emit(item.id)
    this.tick()
    return item
  }

  addMany(requests: DownloadRequest[]): DownloadItem[] {
    return requests.map((r) => this.add(r))
  }

  cancel(id: string): void {
    const entry = this.items.get(id)
    if (!entry) return
    if (entry.item.status === 'queued') {
      entry.item.status = 'cancelled'
      entry.item.finishedAt = new Date().toISOString()
      this.emit(id)
      this.events.onItemFinished(entry.item)
      return
    }
    if (entry.proc && this.isActive(entry.item.status)) {
      entry.cancelled = true
      this.killTree(entry.proc)
    }
  }

  retry(id: string): void {
    const entry = this.items.get(id)
    if (!entry) return
    if (entry.item.status !== 'error' && entry.item.status !== 'cancelled') return
    entry.cancelled = false
    entry.request.startNow = true // expliziter Nutzer-Klick → sofort loslegen
    entry.log.length = 0
    entry.item.status = 'queued'
    entry.item.progress = emptyProgress()
    entry.item.errorMessage = null
    entry.item.startedAt = null
    entry.item.finishedAt = null
    entry.item.outputFiles = []
    this.emit(id)
    this.tick()
  }

  remove(id: string): void {
    const entry = this.items.get(id)
    if (!entry) return
    if (this.isActive(entry.item.status)) this.cancel(id)
    this.items.delete(id)
    this.order = this.order.filter((x) => x !== id)
  }

  clearFinished(): string[] {
    const removed: string[] = []
    for (const id of [...this.order]) {
      const st = this.items.get(id)?.item.status
      if (st === 'completed' || st === 'cancelled' || st === 'error') {
        this.items.delete(id)
        this.order = this.order.filter((x) => x !== id)
        removed.push(id)
      }
    }
    return removed
  }

  cancelAll(): void {
    for (const id of this.order) {
      const st = this.items.get(id)?.item.status
      if (st && (st === 'queued' || this.isActive(st))) this.cancel(id)
    }
  }

  activeCount(): number {
    return this.list().filter((i) => this.isActive(i.status)).length
  }

  private isActive(status: DownloadStatus): boolean {
    return status === 'fetching-info' || status === 'downloading' || status === 'converting'
  }

  private emit(id: string): void {
    const entry = this.items.get(id)
    if (entry) this.events.onItemChanged({ ...entry.item, progress: { ...entry.item.progress } })
  }

  private log(id: string, line: string): void {
    const entry = this.items.get(id)
    if (!entry) return
    entry.log.push(line)
    if (entry.log.length > MAX_LOG_LINES) entry.log.splice(0, entry.log.length - MAX_LOG_LINES)
    this.events.onLogLine(id, line)
  }

  private tick(): void {
    const settings = getSettings()
    const max = Math.max(1, Math.min(5, settings.concurrency))
    let running = this.activeCount()
    for (const id of this.order) {
      if (running >= max) break
      const entry = this.items.get(id)
      if (!entry || entry.item.status !== 'queued') continue
      // Ohne gestartete Queue laufen nur explizit gestartete Downloads
      if (!this.processing && !entry.request.startNow) continue
      running++
      void this.run(entry, settings)
    }

    // Queue automatisch beenden, wenn nichts Wartendes mehr da ist
    if (this.processing) {
      const hasQueued = this.order.some((id) => this.items.get(id)?.item.status === 'queued')
      if (!hasQueued) {
        this.processing = false
        this.events.onQueueState(false)
      }
    }
  }

  private async run(entry: InternalItem, settings: AppSettings): Promise<void> {
    const { item } = entry
    item.status = 'fetching-info'
    item.startedAt = new Date().toISOString()
    this.emit(item.id)

    // Titel/Thumbnail besorgen, falls noch nicht bekannt
    if (!entry.request.knownTitle) {
      try {
        const info = await probeUrl(item.url)
        item.title = info.title
        item.isPlaylist = info.isPlaylist
        if (info.isPlaylist) {
          item.uploader = info.uploader
          item.progress.playlistCount = info.entryCount
        } else {
          item.uploader = info.uploader
          item.thumbnailUrl = info.thumbnailUrl
        }
      } catch (err) {
        // Vorschau-Fehler ist nicht fatal — yt-dlp meldet echte Fehler beim Download
        this.log(item.id, `[info] Vorschau fehlgeschlagen: ${String(err)}`)
      }
    }
    if (entry.cancelled) {
      this.finish(entry, 'cancelled')
      return
    }

    let cmd
    try {
      cmd = await buildDownloadCommand(entry.request, settings, item.isPlaylist)
      mkdirSync(item.destination, { recursive: true })
    } catch (err) {
      item.errorMessage = err instanceof Error ? err.message : String(err)
      this.finish(entry, 'error')
      return
    }

    item.status = 'downloading'
    this.emit(item.id)
    this.log(item.id, `$ yt-dlp ${cmd.args.join(' ')}`)

    const proc = spawn(cmd.bin, cmd.args, { windowsHide: true, env: ytDlpEnv() })
    entry.proc = proc

    let stdoutBuf = ''
    let stderrBuf = ''
    const errorLines: string[] = []

    proc.stdout.on('data', (chunk: Buffer) => {
      stdoutBuf += chunk.toString('utf-8')
      let nl: number
      while ((nl = stdoutBuf.indexOf('\n')) !== -1) {
        const line = stdoutBuf.slice(0, nl).replace(/\r$/, '')
        stdoutBuf = stdoutBuf.slice(nl + 1)
        this.handleStdoutLine(entry, line)
      }
    })
    proc.stderr.on('data', (chunk: Buffer) => {
      stderrBuf += chunk.toString('utf-8')
      let nl: number
      while ((nl = stderrBuf.indexOf('\n')) !== -1) {
        const line = stderrBuf.slice(0, nl).replace(/\r$/, '')
        stderrBuf = stderrBuf.slice(nl + 1)
        if (line.trim()) {
          this.log(item.id, line)
          if (/^ERROR/i.test(line.trim())) errorLines.push(line.trim())
        }
      }
    })

    proc.on('close', (code) => {
      entry.proc = null
      if (entry.cancelled) {
        this.finish(entry, 'cancelled')
      } else if (code === 0) {
        item.progress.percent = 100
        this.finish(entry, 'completed')
      } else {
        item.errorMessage = errorLines.at(-1) ?? `yt-dlp exited with code ${code}`
        this.finish(entry, 'error')
      }
    })

    proc.on('error', (err) => {
      entry.proc = null
      item.errorMessage = err.message
      this.finish(entry, 'error')
    })
  }

  private handleStdoutLine(entry: InternalItem, line: string): void {
    const { item } = entry
    if (line.startsWith(PROGRESS_PREFIX)) {
      const parts = line.slice(PROGRESS_PREFIX.length).split('|')
      const num = (s: string | undefined): number | null => {
        if (!s || s === 'NA' || s === 'None') return null
        const n = Number.parseFloat(s)
        return Number.isFinite(n) ? n : null
      }
      const downloaded = num(parts[0]) ?? 0
      const total = num(parts[1]) ?? num(parts[2])
      const speed = num(parts[3])
      const eta = num(parts[4])
      const plIndex = num(parts[5])
      const plCount = num(parts[6])
      item.progress = {
        percent: total ? Math.min(100, (downloaded / total) * 100) : -1,
        downloadedBytes: downloaded,
        totalBytes: total,
        speed,
        eta,
        playlistIndex: plIndex,
        playlistCount: plCount ?? item.progress.playlistCount
      }
      if (item.status !== 'downloading') item.status = 'downloading'
      this.emit(item.id)
      return
    }
    if (line.startsWith(OUTPUT_PREFIX)) {
      const file = line.slice(OUTPUT_PREFIX.length).trim()
      if (file) item.outputFiles.push(file)
      this.emit(item.id)
      return
    }
    if (line.trim()) {
      // Postprocessing-Phasen erkennen ([ExtractAudio], [Merger], [EmbedThumbnail] …)
      if (/^\[(ExtractAudio|Merger|EmbedThumbnail|Metadata|VideoConvertor|VideoRemuxer|SponsorBlock|ModifyChapters)\]/.test(line)) {
        if (item.status !== 'converting') {
          item.status = 'converting'
          this.emit(item.id)
        }
      }
      this.log(item.id, line)
    }
  }

  private finish(entry: InternalItem, status: 'completed' | 'error' | 'cancelled'): void {
    const { item } = entry
    item.status = status
    item.finishedAt = new Date().toISOString()
    this.emit(item.id)
    this.events.onItemFinished({ ...item })
    this.tick()
  }

  private killTree(proc: ChildProcessWithoutNullStreams): void {
    if (process.platform === 'win32' && proc.pid) {
      spawn('taskkill', ['/PID', String(proc.pid), '/T', '/F'], { windowsHide: true })
    } else {
      proc.kill('SIGTERM')
    }
  }
}
