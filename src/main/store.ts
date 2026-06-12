import { app } from 'electron'
import { readFileSync, writeFileSync, mkdirSync, existsSync, renameSync } from 'node:fs'
import { join, dirname } from 'node:path'

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
