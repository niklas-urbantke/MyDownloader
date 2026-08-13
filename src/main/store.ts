import { app } from 'electron'
import { readFileSync, writeFileSync, mkdirSync, existsSync, renameSync } from 'node:fs'
import { join, dirname } from 'node:path'

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/** Hat der geladene Wert dieselbe Grundform wie die Defaults? */
function sameShape(raw: unknown, defaults: unknown): boolean {
  if (Array.isArray(defaults)) return Array.isArray(raw)
  if (isPlainObject(defaults)) return isPlainObject(raw)
  // null als Default (z. B. spotify.json) lässt jeden gespeicherten Wert zu
  if (defaults === null) return true
  return typeof raw === typeof defaults
}

/**
 * Minimaler JSON-Datei-Store im userData-Verzeichnis.
 * Schreibt atomar (tmp + rename), damit ein Absturz keine Daten zerstört.
 */
export class JsonStore<T> {
  private readonly file: string

  constructor(
    name: string,
    private readonly defaults: T
  ) {
    this.file = join(app.getPath('userData'), name)
  }

  get path(): string {
    return this.file
  }

  load(): T {
    try {
      if (!existsSync(this.file)) return structuredClone(this.defaults)
      const raw = JSON.parse(readFileSync(this.file, 'utf-8'))
      // Nur Objekt-Stores (settings.json) werden mit den Defaults gemerged,
      // damit neu hinzugekommene Felder ihren Standardwert bekommen.
      // Listen-Stores dürfen NICHT gemerged werden: { ...[], ...[a, b] }
      // ergibt { "0": a, "1": b } — kein Array mehr, und die Aufrufer
      // verwerfen das per Array.isArray-Prüfung stillschweigend.
      if (!isPlainObject(this.defaults) || !isPlainObject(raw)) {
        return sameShape(raw, this.defaults) ? (raw as T) : structuredClone(this.defaults)
      }
      return { ...structuredClone(this.defaults), ...raw }
    } catch {
      return structuredClone(this.defaults)
    }
  }

  save(value: T): void {
    mkdirSync(dirname(this.file), { recursive: true })
    const tmp = `${this.file}.tmp`
    writeFileSync(tmp, JSON.stringify(value, null, 2), 'utf-8')
    renameSync(tmp, this.file)
  }
}
