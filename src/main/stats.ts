import { existsSync, statSync } from 'node:fs'
import type { StatsSummary } from '@shared/types'
import { listHistory } from './history'

/**
 * Statistiken aus dem Download-Verlauf (Issue #36).
 * Rein lokal berechnet; Dateigrößen werden über die noch vorhandenen
 * Ausgabedateien ermittelt.
 */
export function computeStats(): StatsSummary {
  const history = listHistory()

  let totalBytes = 0
  const monthCounts = new Map<string, number>()
  const uploaderCounts = new Map<string, number>()
  const formatCounts = new Map<string, number>()
  let completed = 0
  let errors = 0

  // Zwölf Monate zurück vorbelegen, damit das Diagramm keine Lücken hat
  const now = new Date()
  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    monthCounts.set(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`, 0)
  }

  for (const entry of history) {
    if (entry.status === 'completed') completed++
    if (entry.status === 'error') errors++

    const month = entry.timestamp.slice(0, 7)
    if (monthCounts.has(month) && entry.status === 'completed') {
      monthCounts.set(month, (monthCounts.get(month) ?? 0) + 1)
    }

    if (entry.status === 'completed') {
      if (entry.uploader) {
        uploaderCounts.set(entry.uploader, (uploaderCounts.get(entry.uploader) ?? 0) + 1)
      }
      formatCounts.set(entry.format, (formatCounts.get(entry.format) ?? 0) + 1)
      for (const file of entry.outputFiles) {
        try {
          if (existsSync(file)) totalBytes += statSync(file).size
        } catch {
          /* Datei nicht lesbar */
        }
      }
    }
  }

  const top = (map: Map<string, number>, n: number): { name: string; count: number }[] =>
    [...map.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, n)
      .map(([name, count]) => ({ name, count }))

  return {
    totalDownloads: history.length,
    completed,
    errors,
    totalBytes,
    perMonth: [...monthCounts.entries()].map(([month, count]) => ({ month, count })),
    topUploaders: top(uploaderCounts, 8),
    formats: [...formatCounts.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([format, count]) => ({ format, count }))
  }
}
