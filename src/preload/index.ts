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
  type TrackTags
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
    probe: (url: string): Promise<MediaInfo> => ipcRenderer.invoke(IPC.mediaProbe, url)
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
