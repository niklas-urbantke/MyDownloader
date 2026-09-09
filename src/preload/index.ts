import { contextBridge, ipcRenderer } from 'electron'
import {
  IPC,
  type AppInfo,
  type AppSettings,
  type BinaryStatus,
  type DownloadItem,
  type DownloadRequest,
  type DownloadTemplate,
  type HistoryEntry,
  type MediaInfo,
  type MusicBrainzSuggestion,
  type TrackTags,
  type Subscription,
  type SpotifyPlaylist,
  type SpotifyStatus,
  type StatsSummary,
  type AccountStatus,
  type UpdateEventPayload
} from '../shared/types'

/**
 * Typisierte IPC-Bridge für den Renderer (window.api).
 * Kein direkter Node-Zugriff im Renderer — alles läuft über diese Fassade.
 */
const api = {
  versions: {
    electron: process.versions.electron,
    chrome: process.versions.chrome,
    node: process.versions.node
  },

  settings: {
    get: (): Promise<AppSettings> => ipcRenderer.invoke(IPC.settingsGet),
    set: (patch: Partial<AppSettings>): Promise<AppSettings> =>
      ipcRenderer.invoke(IPC.settingsSet, patch),
    /** Synchron abschicken ohne auf Antwort zu warten (für beforeunload) */
    flush: (patch: Partial<AppSettings>): void => ipcRenderer.send(IPC.settingsFlush, patch),
    pickFolder: (defaultPath?: string): Promise<string | null> =>
      ipcRenderer.invoke(IPC.settingsPickFolder, defaultPath)
  },

  media: {
    probe: (url: string): Promise<MediaInfo> => ipcRenderer.invoke(IPC.mediaProbe, url),
    previewUrl: (url: string): Promise<string | null> =>
      ipcRenderer.invoke(IPC.mediaPreviewUrl, url)
  },

  subscriptions: {
    list: (): Promise<Subscription[]> => ipcRenderer.invoke(IPC.subsList),
    add: (
      url: string,
      options: { folder?: string; templateId?: string; intervalMinutes?: number }
    ): Promise<Subscription> => ipcRenderer.invoke(IPC.subsAdd, url, options),
    update: (patch: Partial<Subscription> & { id: string }): Promise<void> =>
      ipcRenderer.invoke(IPC.subsUpdate, patch),
    remove: (id: string): Promise<void> => ipcRenderer.invoke(IPC.subsRemove, id),
    checkNow: (id: string): Promise<number> => ipcRenderer.invoke(IPC.subsCheckNow, id),
    onChanged: (cb: (subs: Subscription[]) => void): (() => void) => {
      const listener = (_e: unknown, subs: Subscription[]): void => cb(subs)
      ipcRenderer.on(IPC.subsChanged, listener)
      return () => ipcRenderer.removeListener(IPC.subsChanged, listener)
    }
  },

  account: {
    status: (): Promise<AccountStatus> => ipcRenderer.invoke(IPC.accountStatus),
    login: (): Promise<AccountStatus> => ipcRenderer.invoke(IPC.accountLogin),
    logout: (): Promise<AccountStatus> => ipcRenderer.invoke(IPC.accountLogout)
  },

  spotify: {
    status: (): Promise<SpotifyStatus> => ipcRenderer.invoke(IPC.spotifyStatus),
    login: (): Promise<SpotifyStatus> => ipcRenderer.invoke(IPC.spotifyLogin),
    logout: (): Promise<SpotifyStatus> => ipcRenderer.invoke(IPC.spotifyLogout),
    getPlaylist: (url: string): Promise<SpotifyPlaylist | null> =>
      ipcRenderer.invoke(IPC.spotifyGetPlaylist, url)
  },

  stats: {
    compute: (): Promise<StatsSummary> => ipcRenderer.invoke(IPC.statsCompute)
  },

  updates: {
    check: (): Promise<void> => ipcRenderer.invoke(IPC.updateCheck),
    download: (): Promise<void> => ipcRenderer.invoke(IPC.updateDownload),
    install: (): Promise<void> => ipcRenderer.invoke(IPC.updateInstall),
    installUrbUpdate: (): Promise<{ ok: boolean; message: string }> =>
      ipcRenderer.invoke(IPC.urbupdateInstall),
    onEvent: (cb: (payload: UpdateEventPayload) => void): (() => void) => {
      const listener = (_e: unknown, payload: UpdateEventPayload): void => cb(payload)
      ipcRenderer.on(IPC.updateEvent, listener)
      return () => ipcRenderer.removeListener(IPC.updateEvent, listener)
    }
  },

  downloads: {
    add: (request: DownloadRequest): Promise<DownloadItem> =>
      ipcRenderer.invoke(IPC.downloadAdd, request),
    addMany: (requests: DownloadRequest[]): Promise<DownloadItem[]> =>
      ipcRenderer.invoke(IPC.downloadAddMany, requests),
    cancel: (id: string): Promise<void> => ipcRenderer.invoke(IPC.downloadCancel, id),
    pause: (id: string): Promise<void> => ipcRenderer.invoke(IPC.downloadPause, id),
    resume: (id: string): Promise<void> => ipcRenderer.invoke(IPC.downloadResume, id),
    retry: (id: string): Promise<void> => ipcRenderer.invoke(IPC.downloadRetry, id),
    remove: (id: string): Promise<void> => ipcRenderer.invoke(IPC.downloadRemove, id),
    clearFinished: (): Promise<string[]> => ipcRenderer.invoke(IPC.downloadClearFinished),
    list: (): Promise<DownloadItem[]> => ipcRenderer.invoke(IPC.downloadList),
    getLog: (id: string): Promise<string[]> => ipcRenderer.invoke(IPC.downloadGetLog, id),
    startQueue: (): Promise<void> => ipcRenderer.invoke(IPC.downloadQueueStart),
    pauseQueue: (): Promise<void> => ipcRenderer.invoke(IPC.downloadQueuePause),
    queueState: (): Promise<boolean> => ipcRenderer.invoke(IPC.downloadQueueState),
    move: (id: string, direction: 'up' | 'down'): Promise<void> =>
      ipcRenderer.invoke(IPC.downloadMove, id, direction),
    onQueueState: (cb: (processing: boolean) => void): (() => void) => {
      const listener = (_e: unknown, processing: boolean): void => cb(processing)
      ipcRenderer.on(IPC.downloadQueueState, listener)
      return () => ipcRenderer.removeListener(IPC.downloadQueueState, listener)
    },
    onChanged: (cb: (item: DownloadItem) => void): (() => void) => {
      const listener = (_e: unknown, item: DownloadItem): void => cb(item)
      ipcRenderer.on(IPC.downloadChanged, listener)
      return () => ipcRenderer.removeListener(IPC.downloadChanged, listener)
    },
    onLogLine: (cb: (payload: { id: string; line: string }) => void): (() => void) => {
      const listener = (_e: unknown, payload: { id: string; line: string }): void => cb(payload)
      ipcRenderer.on(IPC.downloadLogLine, listener)
      return () => ipcRenderer.removeListener(IPC.downloadLogLine, listener)
    }
  },

  templates: {
    list: (): Promise<DownloadTemplate[]> => ipcRenderer.invoke(IPC.templatesList),
    save: (template: DownloadTemplate): Promise<DownloadTemplate> =>
      ipcRenderer.invoke(IPC.templatesSave, template),
    remove: (id: string): Promise<void> => ipcRenderer.invoke(IPC.templatesDelete, id)
  },

  metadata: {
    read: (file: string): Promise<TrackTags> => ipcRenderer.invoke(IPC.metaReadTags, file),
    write: (
      file: string,
      tags: TrackTags,
      coverPath: string | null
    ): Promise<{ ok: boolean; message: string }> =>
      ipcRenderer.invoke(IPC.metaWriteTags, file, tags, coverPath),
    searchMusicBrainz: (artist: string, title: string): Promise<MusicBrainzSuggestion[]> =>
      ipcRenderer.invoke(IPC.metaSearchMusicBrainz, artist, title),
    pickImage: (): Promise<string | null> => ipcRenderer.invoke(IPC.metaPickImage)
  },

  history: {
    list: (): Promise<HistoryEntry[]> => ipcRenderer.invoke(IPC.historyList),
    remove: (id: string): Promise<void> => ipcRenderer.invoke(IPC.historyRemove, id),
    clear: (): Promise<void> => ipcRenderer.invoke(IPC.historyClear)
  },

  system: {
    binaries: (): Promise<BinaryStatus> => ipcRenderer.invoke(IPC.binariesStatus),
    updateYtDlp: (): Promise<{ ok: boolean; message: string }> =>
      ipcRenderer.invoke(IPC.binariesUpdateYtDlp),
    /** Meldet, wenn der Start-Check yt-dlp aktualisiert hat oder es veraltet ist */
    onYtDlpEvent: (
      cb: (info: { current: string | null; latest: string | null; updated: boolean }) => void
    ): (() => void) => {
      const listener = (
        _e: unknown,
        info: { current: string | null; latest: string | null; updated: boolean }
      ): void => cb(info)
      ipcRenderer.on(IPC.binariesYtDlpEvent, listener)
      return () => ipcRenderer.removeListener(IPC.binariesYtDlpEvent, listener)
    },
    appInfo: (): Promise<AppInfo> => ipcRenderer.invoke(IPC.appInfo),
    importV3: (): Promise<{ ok: boolean; settingsImported: number; historyImported: number }> =>
      ipcRenderer.invoke(IPC.importV3),
    openPath: (path: string): Promise<string> => ipcRenderer.invoke(IPC.openPath, path),
    showInFolder: (path: string): Promise<boolean> => ipcRenderer.invoke(IPC.showInFolder, path),
    openExternal: (url: string): Promise<void> => ipcRenderer.invoke(IPC.openExternal, url)
  },

  clipboard: {
    onUrlDetected: (cb: (url: string) => void): (() => void) => {
      const listener = (_e: unknown, url: string): void => cb(url)
      ipcRenderer.on(IPC.clipboardUrl, listener)
      return () => ipcRenderer.removeListener(IPC.clipboardUrl, listener)
    }
  }
}

export type PreloadApi = typeof api

contextBridge.exposeInMainWorld('api', api)
