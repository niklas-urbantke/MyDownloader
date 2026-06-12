import { contextBridge } from 'electron'

// Die vollständige API-Bridge (Downloads, Settings, History …) folgt mit der
// Download-Engine. Der Scaffold stellt nur App-Metadaten bereit.
const api = {
  versions: {
    electron: process.versions.electron,
    chrome: process.versions.chrome,
    node: process.versions.node
  }
}

export type PreloadApi = typeof api

contextBridge.exposeInMainWorld('api', api)
