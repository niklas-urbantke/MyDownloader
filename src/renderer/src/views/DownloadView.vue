<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { AppSettings, DownloadRequest, DownloadTemplate, MediaInfo } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxSelect from '../components/BxSelect.vue'
import BxSegmented from '../components/BxSegmented.vue'
import BxToggle from '../components/BxToggle.vue'
import BxChip from '../components/BxChip.vue'
import AppIcon from '../components/AppIcon.vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '../stores/settings'
import { useDownloadsStore } from '../stores/downloads'
import { useDownloadOptionsStore } from '../stores/downloadOptions'
import { useTemplatesStore } from '../stores/templates'
import BxDialog from '../components/BxDialog.vue'
import BxBanner from '../components/BxBanner.vue'
import { showToast } from '../composables/toast'
import {
  formatDuration,
  formatCount,
  isHttpUrl,
  analyzeCombiUrl,
  analyzeChannelUrl,
  type CombiUrl
} from '../utils/format'

const { t, locale } = useI18n()
const router = useRouter()
const settingsStore = useSettingsStore()
const downloads = useDownloadsStore()

const url = ref('')
const probing = ref(false)
const probeError = ref('')
const info = ref<MediaInfo | null>(null)

// Optionen für diesen Download — leben im Store und überdauern Downloads
// und Seitenwechsel (Issue #3); Reset nur per Toggle oder App-Neustart.
const options = useDownloadOptionsStore()
const {
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
  scheduledAt
} = storeToRefs(options)

const templates = useTemplatesStore()
const activeTemplate = computed<DownloadTemplate | null>(
  () => (templateId.value ? (templates.byId(templateId.value) ?? null) : null)
)
const templateOptions = computed(() => [
  { value: '', label: t('templates.manual') },
  ...templates.entries.map((tp) => ({ value: tp.id, label: tp.name }))
])

// Vorschau automatisch, sobald eine gültige URL eingegeben/eingefügt wurde
let probeTimer: ReturnType<typeof setTimeout> | null = null
watch(url, (value, old) => {
  if (value === old) return
  probeError.value = ''
  if (probeTimer) clearTimeout(probeTimer)
  if (!isHttpUrl(value)) return
  probeTimer = setTimeout(() => {
    if (!probing.value && isHttpUrl(url.value)) void probe()
  }, 600)
})

async function pickFolder(): Promise<void> {
  const picked = await window.api.settings.pickFolder(
    folder.value || settingsStore.settings?.downloadFolder
  )
  if (picked) folder.value = picked
}

async function pickAudioFolder(): Promise<void> {
  const picked = await window.api.settings.pickFolder(
    audioFolder.value || folder.value || settingsStore.settings?.downloadFolder
  )
  if (picked) audioFolder.value = picked
}

const audioFormatOptions = ['mp3', 'm4a', 'opus', 'flac', 'wav'].map((v) => ({
  value: v,
  label: v.toUpperCase()
}))
const videoQualityOptions = computed(() => [
  { value: 'best', label: t('settings.fields.videoQualityBest') },
  { value: '2160', label: '2160p (4K)' },
  { value: '1440', label: '1440p' },
  { value: '1080', label: '1080p' },
  { value: '720', label: '720p' },
  { value: '480', label: '480p' }
])

const urlValid = computed(() => isHttpUrl(url.value))

// --- Kanal-Downloads (Issue #9): Tab wählen (Videos/Shorts/Livestreams) ---
const channel = computed(() => analyzeChannelUrl(url.value))
const channelTab = ref<'videos' | 'shorts' | 'streams' | 'all'>('videos')
const channelTabOptions = computed(() => [
  { value: 'videos', label: t('download.channel.videos'), icon: 'image' },
  { value: 'shorts', label: t('download.channel.shorts'), icon: 'play' },
  { value: 'streams', label: t('download.channel.streams'), icon: 'circle' },
  { value: 'all', label: t('download.channel.all'), icon: 'list' }
])

/** Effektive Ziel-URL: bei Kanälen mit gewähltem Tab */
function targetUrl(): string {
  const ch = channel.value
  if (!ch) return url.value.trim()
  return channelTab.value === 'all' ? ch.base : `${ch.base}/${channelTab.value}`
}

// --- Hörprobe (Issue #29) ---
const previewingUrl = ref('')
const previewLoadingUrl = ref('')
let audioEl: HTMLAudioElement | null = null

function stopPreview(): void {
  audioEl?.pause()
  audioEl = null
  previewingUrl.value = ''
}

async function togglePreview(target: string): Promise<void> {
  if (previewingUrl.value === target) {
    stopPreview()
    return
  }
  stopPreview()
  previewLoadingUrl.value = target
  try {
    const stream = await window.api.media.previewUrl(target)
    if (!stream) {
      showToast(t('download.preview.previewFailed'), 'error')
      return
    }
    audioEl = new Audio(stream)
    previewingUrl.value = target
    // Hörprobe: nach 30 Sekunden automatisch stoppen
    audioEl.addEventListener('timeupdate', () => {
      if (audioEl && audioEl.currentTime > 30) stopPreview()
    })
    audioEl.addEventListener('ended', stopPreview)
    audioEl.addEventListener('error', stopPreview)
    void audioEl.play()
  } finally {
    previewLoadingUrl.value = ''
  }
}

onUnmounted(stopPreview)

// --- Combi-Link (Video + Playlist in einer URL): Nutzer entscheiden lassen ---
const combi = ref<CombiUrl | null>(null)
let afterCombiChoice: (() => void | Promise<void>) | null = null

/** true = Dialog geöffnet, Aktion wird nach der Wahl fortgesetzt */
function interceptCombi(continueWith: () => void | Promise<void>): boolean {
  const found = analyzeCombiUrl(url.value)
  if (!found) return false
  combi.value = found
  afterCombiChoice = continueWith
  return true
}

async function chooseCombi(which: 'video' | 'playlist'): Promise<void> {
  if (!combi.value) return
  url.value = which === 'video' ? combi.value.videoUrl : combi.value.playlistUrl
  combi.value = null
  const next = afterCombiChoice
  afterCombiChoice = null
  await next?.()
}

const qualityLabel = (q: string): string => (q === 'best' ? 'max' : `${q}p`)

/** Pro-Download-Extras: Kapitel-Splitting, Zeitbereich, geplanter Start */
function applyExtras(req: DownloadRequest): DownloadRequest {
  const out = { ...req }
  if (splitChapters.value) out.splitChapters = true
  if (sectionFrom.value.trim()) out.sectionFrom = sectionFrom.value.trim()
  if (sectionTo.value.trim()) out.sectionTo = sectionTo.value.trim()
  if (scheduledAt.value) {
    const ts = new Date(scheduledAt.value)
    if (!Number.isNaN(ts.getTime()) && ts.getTime() > Date.now()) {
      out.scheduledAt = ts.toISOString()
    }
  }
  return out
}

/**
 * Erzeugt für jede zusätzliche Qualitätsstufe einen weiteren Video-Request
 * mit Qualitäts-Suffix im Dateinamen (Issue #10).
 */
function expandQualities(
  videoReq: DownloadRequest,
  primary: string,
  extras: string[]
): DownloadRequest[] {
  const unique = [...new Set(extras)].filter((q) => q !== primary)
  if (unique.length === 0) return [videoReq]
  return [
    { ...videoReq, filenameSuffix: ` [${qualityLabel(primary)}]` },
    ...unique.map((q) => ({
      ...videoReq,
      overrides: { ...videoReq.overrides, videoQuality: q as AppSettings['videoQuality'] },
      filenameSuffix: ` [${qualityLabel(q)}]`
    }))
  ]
}

/**
 * Baut die Download-Requests: normalerweise einer; im "Beides"-Modus oder
 * mit zusätzlichen Qualitätsstufen entsprechend mehr.
 */
function buildRequests(): DownloadRequest[] {
  const base: DownloadRequest = { url: targetUrl() }
  if (info.value) base.knownTitle = info.value.title

  let requests: DownloadRequest[]
  const tpl = activeTemplate.value
  if (tpl) {
    // Vorlage gewählt → Vorlage bestimmt alles
    const videoReq: DownloadRequest = {
      ...base,
      overrides: {
        mode: 'video',
        videoContainer: tpl.videoContainer,
        videoQuality: tpl.videoQuality,
        writeSubtitles: tpl.writeSubtitles,
        ...(tpl.folder ? { downloadFolder: tpl.folder } : {})
      }
    }
    const audioReq: DownloadRequest = {
      ...base,
      overrides: {
        mode: 'audio',
        audioFormat: tpl.audioFormat,
        audioQuality: tpl.audioQuality,
        writeSubtitles: tpl.writeSubtitles,
        ...(tpl.audioFolder || tpl.folder
          ? { downloadFolder: tpl.audioFolder || tpl.folder }
          : {})
      }
    }
    const videoReqs = expandQualities(videoReq, tpl.videoQuality, tpl.extraVideoQualities ?? [])
    requests =
      tpl.mode === 'video' ? videoReqs : tpl.mode === 'audio' ? [audioReq] : [...videoReqs, audioReq]
  } else if (useDefaults.value) {
    requests = [base]
  } else {
    const common = {
      audioFormat: audioFormat.value as AppSettings['audioFormat'],
      videoQuality: videoQuality.value as AppSettings['videoQuality'],
      writeSubtitles: writeSubtitles.value
    }
    const videoReq: DownloadRequest = {
      ...base,
      overrides: {
        ...common,
        mode: 'video',
        ...(folder.value ? { downloadFolder: folder.value } : {})
      }
    }
    const audioReq: DownloadRequest = {
      ...base,
      overrides: {
        ...common,
        mode: 'audio',
        ...((mode.value === 'both' ? audioFolder.value || folder.value : folder.value)
          ? {
              downloadFolder:
                mode.value === 'both' ? audioFolder.value || folder.value : folder.value
            }
          : {})
      }
    }
    const videoReqs = expandQualities(videoReq, videoQuality.value, extraQualities.value)
    requests =
      mode.value === 'video'
        ? videoReqs
        : mode.value === 'audio'
          ? [audioReq]
          : [...videoReqs, audioReq]
  }
  return requests.map(applyExtras)
}

function toggleExtraQuality(q: string): void {
  const idx = extraQualities.value.indexOf(q)
  if (idx === -1) extraQualities.value.push(q)
  else extraQualities.value.splice(idx, 1)
}

async function probe(): Promise<void> {
  if (!urlValid.value) {
    probeError.value = t('download.errors.invalidUrl')
    return
  }
  if (interceptCombi(probe)) return
  probing.value = true
  probeError.value = ''
  info.value = null
  try {
    info.value = await window.api.media.probe(targetUrl())
  } catch (err) {
    probeError.value = t('download.errors.probeFailed', {
      msg: err instanceof Error ? err.message.split('\n')[0] : String(err)
    })
  } finally {
    probing.value = false
  }
}

async function start(goToQueue: boolean): Promise<void> {
  if (!urlValid.value) {
    probeError.value = t('download.errors.invalidUrl')
    return
  }
  if (interceptCombi(() => start(goToQueue))) return
  // "Download starten" legt sofort los; "Zur Warteschlange" wartet auf Queue-Start
  const requests = buildRequests().map((r) => ({ ...r, startNow: goToQueue }))
  await downloads.addMany(requests)
  showToast(
    requests.length > 1 ? t('download.addedMany', { n: requests.length }) : t('download.added')
  )
  url.value = ''
  info.value = null
  if (goToQueue) router.push({ name: 'queue' })
}

async function pasteFromClipboard(): Promise<void> {
  try {
    const text = await navigator.clipboard.readText()
    if (text.trim()) {
      url.value = text.trim().split(/\r?\n/)[0] ?? ''
      if (urlValid.value) await probe()
    }
  } catch {
    /* Zwischenablage nicht lesbar — Eingabe bleibt manuell */
  }
}

const playlistPreview = computed(() => {
  if (!info.value || !info.value.isPlaylist) return []
  return info.value.entries.slice(0, 10)
})
</script>

<template>
  <PageHead :title="t('download.title')" :sub="t('download.subtitle')" />

  <div class="stack">
    <!-- URL-Eingabe -->
    <BxCard>
      <div class="stack">
        <BxField
          v-model="url"
          icon="link"
          :placeholder="t('download.urlPlaceholder')"
          :error="probeError || undefined"
          @enter="probe"
        />
        <!-- Kanal erkannt: Tab wählen (Issue #9) -->
        <div v-if="channel" class="cluster">
          <BxChip icon="user" variant="accent">{{ t('download.channel.detected') }}</BxChip>
          <BxSegmented v-model="channelTab" :options="channelTabOptions" />
        </div>
        <div class="cluster">
          <BxBtn
            icon="search"
            variant="secondary"
            :label="t('download.probe')"
            :disabled="!urlValid || probing"
            @click="probe"
          />
          <BxBtn
            icon="clipboard"
            variant="ghost"
            :label="t('download.pasteFromClipboard')"
            @click="pasteFromClipboard"
          />
          <span class="spacer" />
          <BxBtn
            icon="plus"
            variant="secondary"
            :label="t('download.addToQueue')"
            :disabled="!urlValid"
            @click="start(false)"
          />
          <BxBtn
            icon="download"
            variant="primary"
            :label="t('download.start')"
            :disabled="!urlValid"
            @click="start(true)"
          />
        </div>
      </div>
    </BxCard>

    <!-- Vorschau -->
    <BxCard :title="t('download.preview.title')" :padded="false">
      <div v-if="probing" class="card__body cluster text-secondary">
        <AppIcon name="search" class="icon--sm" /> {{ t('common.loading') }}
      </div>

      <div v-else-if="!info" class="card__body text-secondary">
        {{ t('download.preview.empty') }}
      </div>

      <!-- Einzelnes Video -->
      <div v-else-if="!info.isPlaylist" class="card__body">
        <div class="cluster" style="align-items: flex-start; --cluster-gap: var(--space-5)">
          <img
            v-if="info.thumbnailUrl"
            :src="info.thumbnailUrl"
            alt=""
            style="
              width: 13.75rem;
              border-radius: var(--radius-lg);
              border: var(--border-thin) solid var(--color-border);
            "
          />
          <div class="stack stack--sm" style="flex: 1; min-width: 0">
            <h3>{{ info.title }}</h3>
            <div class="cluster" style="--cluster-gap: var(--space-2)">
              <BxChip icon="user" variant="slate">{{ info.uploader }}</BxChip>
              <BxChip v-if="info.durationSeconds" icon="clock" variant="slate">
                {{ formatDuration(info.durationSeconds) }}
              </BxChip>
              <BxChip v-if="info.viewCount" icon="activity" variant="slate">
                {{ formatCount(info.viewCount, locale) }} {{ t('download.preview.views') }}
              </BxChip>
              <BxChip v-if="info.chapterCount > 0" icon="list" variant="slate">
                {{ t('download.extras.chaptersFound', { n: info.chapterCount }) }}
              </BxChip>
            </div>
            <!-- Hörprobe (Issue #29) -->
            <div class="cluster">
              <BxBtn
                :icon="previewingUrl === info.url ? 'stop' : 'play'"
                variant="secondary"
                size="sm"
                :label="previewingUrl === info.url ? t('download.preview.stopListen') : t('download.preview.listen')"
                :disabled="previewLoadingUrl === info.url"
                @click="togglePreview(info.url)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Playlist -->
      <template v-else>
        <div class="card__body">
          <div class="cluster">
            <BxChip icon="list" variant="accent">{{ t('download.preview.playlist') }}</BxChip>
            <h3>{{ info.title }}</h3>
            <BxChip variant="success">{{
              t('download.preview.entries', { n: info.entryCount })
            }}</BxChip>
          </div>
        </div>
        <table class="table table--plain">
          <tbody>
            <tr v-for="(entry, i) in playlistPreview" :key="entry.id">
              <td class="text-muted" style="width: 2.5rem">{{ i + 1 }}</td>
              <td>{{ entry.title }}</td>
              <td style="width: 3.125rem">
                <BxBtn
                  v-if="entry.url"
                  :icon="previewingUrl === entry.url ? 'stop' : 'play'"
                  variant="ghost"
                  size="sm"
                  :title="t('download.preview.listen')"
                  :disabled="previewLoadingUrl === entry.url"
                  @click="togglePreview(entry.url)"
                />
              </td>
              <td class="text-muted" style="width: 5.625rem; text-align: right">
                {{ formatDuration(entry.durationSeconds) }}
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="info.entryCount > playlistPreview.length" class="card__body help">
          {{ t('download.preview.showingFirst', { n: playlistPreview.length }) }}
        </div>
      </template>
    </BxCard>

    <!-- Combi-Link: Video oder ganze Playlist? -->
    <BxDialog :open="!!combi" :title="t('download.combi.title')" @close="combi = null">
      {{ t('download.combi.question') }}
      <template #actions>
        <BxBtn variant="ghost" :label="t('common.cancel')" @click="combi = null" />
        <BxBtn
          variant="secondary"
          icon="image"
          :label="t('download.combi.video')"
          @click="chooseCombi('video')"
        />
        <BxBtn
          variant="primary"
          icon="list"
          :label="t('download.combi.playlist')"
          @click="chooseCombi('playlist')"
        />
      </template>
    </BxDialog>

    <!-- Optionen für diesen Download -->
    <BxCard :title="t('download.options.title')">
      <div class="stack">
        <!-- Vorlagen-Auswahl -->
        <div class="cluster" style="align-items: flex-end">
          <div style="flex: 1; min-width: 15rem">
            <BxSelect
              v-model="templateId"
              :label="t('templates.useTemplate')"
              icon="layout"
              :options="templateOptions"
            />
          </div>
          <BxBtn
            icon="edit"
            variant="ghost"
            :label="t('templates.manage')"
            @click="router.push({ name: 'templates' })"
          />
        </div>

        <!-- Aktive Vorlage: Zusammenfassung statt manueller Felder -->
        <BxBanner v-if="activeTemplate" variant="info" icon="layout">
          <strong>{{ activeTemplate.name }}</strong> —
          <template v-if="activeTemplate.mode === 'both'">{{ t('templates.modeBoth') }},
            {{ activeTemplate.videoContainer.toUpperCase() }} + {{ activeTemplate.audioFormat.toUpperCase() }}</template>
          <template v-else-if="activeTemplate.mode === 'audio'">{{ t('download.options.audio') }},
            {{ activeTemplate.audioFormat.toUpperCase() }}</template>
          <template v-else>{{ t('download.options.video') }},
            {{ activeTemplate.videoContainer.toUpperCase() }}</template>
          <template v-if="activeTemplate.folder"> → {{ activeTemplate.folder }}</template>
        </BxBanner>

        <template v-else>
          <BxToggle v-model="useDefaults" :label="t('download.options.useDefaults')" />
          <div v-if="!useDefaults" class="form-grid">
            <div class="col-6">
              <div class="field">
                <span class="label">{{ t('download.options.mode') }}</span>
                <BxSegmented
                  v-model="mode"
                  :options="[
                    { value: 'audio', label: t('download.options.audio'), icon: 'activity' },
                    { value: 'video', label: t('download.options.video'), icon: 'image' },
                    { value: 'both', label: t('templates.modeBoth'), icon: 'layout' }
                  ]"
                />
              </div>
            </div>
            <div class="col-6">
              <BxSelect
                v-if="mode === 'audio'"
                v-model="audioFormat"
                icon="activity"
                :label="t('download.options.format')"
                :options="audioFormatOptions"
              />
              <BxSelect
                v-else-if="mode === 'video'"
                v-model="videoQuality"
                icon="image"
                :label="t('download.options.quality')"
                :options="videoQualityOptions"
              />
              <div v-else class="form-grid">
                <div class="col-6">
                  <BxSelect
                    v-model="audioFormat"
                    icon="activity"
                    :label="t('download.options.format')"
                    :options="audioFormatOptions"
                  />
                </div>
                <div class="col-6">
                  <BxSelect
                    v-model="videoQuality"
                    icon="image"
                    :label="t('download.options.quality')"
                    :options="videoQualityOptions"
                  />
                </div>
              </div>
            </div>
            <div :class="mode === 'both' ? 'col-6' : 'col-8'">
              <BxField
                v-model="folder"
                :label="mode === 'both' ? t('templates.fields.videoFolder') : t('download.options.folder')"
                icon="folder"
                :placeholder="settingsStore.settings?.downloadFolder ?? ''"
              >
                <template #append>
                  <BxBtn
                    size="sm"
                    variant="secondary"
                    icon="folder"
                    :label="t('settings.fields.browse')"
                    @click="pickFolder"
                  />
                </template>
              </BxField>
            </div>
            <div v-if="mode === 'both'" class="col-6">
              <BxField
                v-model="audioFolder"
                :label="t('templates.fields.audioFolder')"
                icon="folder"
                :placeholder="folder || (settingsStore.settings?.downloadFolder ?? '')"
              >
                <template #append>
                  <BxBtn
                    size="sm"
                    variant="secondary"
                    icon="folder"
                    :label="t('settings.fields.browse')"
                    @click="pickAudioFolder"
                  />
                </template>
              </BxField>
            </div>
            <div class="col-12">
              <BxToggle
                v-model="writeSubtitles"
                :label="t('settings.fields.writeSubtitles')"
              />
            </div>
            <!-- Zusätzliche Qualitätsstufen parallel laden (Issue #10) -->
            <div v-if="mode !== 'audio'" class="col-12">
              <div class="field">
                <span class="label">{{ t('download.options.extraQualities') }}</span>
                <div class="cluster" style="--cluster-gap: var(--space-2)">
                  <BxChip
                    v-for="q in videoQualityOptions"
                    :key="q.value"
                    :variant="extraQualities.includes(q.value) ? 'accent' : 'slate'"
                    style="cursor: pointer"
                    @click="toggleExtraQuality(q.value)"
                  >
                    {{ q.label }}
                  </BxChip>
                </div>
                <span class="help">{{ t('download.options.extraQualitiesHint') }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </BxCard>

    <!-- Extras für diesen Download: Zeitbereich, Kapitel, geplanter Start -->
    <BxCard :title="t('download.extras.title')">
      <div class="form-grid">
        <div class="col-6">
          <BxField
            v-model="sectionFrom"
            :label="t('download.extras.sectionFrom')"
            icon="clock"
            placeholder="0:00"
            :hint="t('download.extras.sectionHint')"
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="sectionTo"
            :label="t('download.extras.sectionTo')"
            icon="clock"
            placeholder="1:23:45"
          />
        </div>
        <div class="col-6" style="align-self: center">
          <BxToggle
            v-model="splitChapters"
            :label="t('download.extras.splitChapters')"
            :hint="
              info && !info.isPlaylist && info.chapterCount > 0
                ? t('download.extras.chaptersFound', { n: info.chapterCount })
                : t('download.extras.splitChaptersHint')
            "
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="scheduledAt"
            type="datetime-local"
            :label="t('download.extras.scheduledAt')"
            icon="clock"
            :hint="t('download.extras.scheduledAtHint')"
          />
        </div>
      </div>
    </BxCard>
  </div>
</template>
