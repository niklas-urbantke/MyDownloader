import { reactive } from 'vue'

export interface ToastEntry {
  id: number
  message: string
  variant: 'success' | 'error' | 'info'
  /** Optionale Aktion (z. B. „Herunterladen“ beim Clipboard-Hinweis) */
  actionLabel?: string
  onAction?: () => void
}

let nextId = 1

const state = reactive<{ toasts: ToastEntry[] }>({ toasts: [] })

export function useToasts(): { toasts: ToastEntry[] } {
  return state
}

export function showToast(
  message: string,
  variant: ToastEntry['variant'] = 'success',
  opts?: { actionLabel?: string; onAction?: () => void; durationMs?: number }
): void {
  const entry: ToastEntry = {
    id: nextId++,
    message,
    variant,
    actionLabel: opts?.actionLabel,
    onAction: opts?.onAction
  }
  state.toasts.push(entry)
  const duration = opts?.durationMs ?? (opts?.actionLabel ? 8000 : 4000)
  setTimeout(() => dismissToast(entry.id), duration)
}

export function dismissToast(id: number): void {
  const idx = state.toasts.findIndex((t) => t.id === id)
  if (idx !== -1) state.toasts.splice(idx, 1)
}
