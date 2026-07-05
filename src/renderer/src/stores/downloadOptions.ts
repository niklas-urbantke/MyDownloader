import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Optionen der Download-Seite ("Optionen für diesen Download").
 * Bewusst NICHT auf Platte persistiert: Sie gelten für die laufende Sitzung
 * und werden erst beim App-Neustart oder manuell zurückgesetzt (Issue #3).
 */
export const useDownloadOptionsStore = defineStore('downloadOptions', () => {
  const useDefaults = ref(true)
  /** 'both' = Video und Audio nacheinander laden (zwei Queue-Einträge) */
  const mode = ref<'audio' | 'video' | 'both'>('audio')
  const audioFormat = ref('mp3')
  const videoQuality = ref('best')
  /** leer = globaler Download-Ordner */
  const folder = ref('')
  /** separater Ordner für den Audio-Teil im "Beides"-Modus (leer = folder) */
  const audioFolder = ref('')
  const writeSubtitles = ref(false)
  /** ID der gewählten Vorlage ('' = manuell) */
  const templateId = ref('')
  /** Weitere Qualitätsstufen, die zusätzlich geladen werden (Issue #10) */
  const extraQualities = ref<string[]>([])
  /** Video anhand seiner Kapitel aufteilen (Issue #23) */
  const splitChapters = ref(false)
  /** Nur Zeitbereich laden (Issue #24), leer = komplett */
  const sectionFrom = ref('')
  const sectionTo = ref('')
  /** Geplanter Start (Wert eines datetime-local-Inputs, Issue #22) */
  const scheduledAt = ref('')

  function reset(): void {
    useDefaults.value = true
    mode.value = 'audio'
    audioFormat.value = 'mp3'
    videoQuality.value = 'best'
    folder.value = ''
    audioFolder.value = ''
    writeSubtitles.value = false
    templateId.value = ''
    extraQualities.value = []
    splitChapters.value = false
    sectionFrom.value = ''
    sectionTo.value = ''
    scheduledAt.value = ''
  }

  return {
    useDefaults,
    mode,
    audioFormat,
    videoQuality,
    folder,
    audioFolder,
    writeSubtitles,
    templateId,
    extraQualities,
    splitChapters,
    sectionFrom,
    sectionTo,
    scheduledAt,
    reset
  }
})
