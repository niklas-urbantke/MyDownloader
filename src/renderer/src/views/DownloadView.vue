<script setup lang="ts">
import { computed, ref, watch } from 'vue'
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
import { formatDuration, formatCount, isHttpUrl, analyzeCombiUrl, type CombiUrl } from '../utils/format'

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
const { useDefaults, mode, audioFormat, videoQuality, folder, audioFolder, writeSubtitles, templateId } =
  storeToRefs(options)

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

/**
 * Baut die Download-Requests: normalerweise einer; im "Beides"-Modus
 * (manuell oder per Vorlage) zwei — Video und Audio mit eigenen Ordnern.
 */
function buildRequests(): DownloadRequest[] {
  const base: DownloadRequest = { url: url.value.trim() }
  if (info.value) base.knownTitle = info.value.title

  // Vorlage gewählt → Vorlage bestimmt alles
  const tpl = activeTemplate.value
  if (tpl) {
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
    if (tpl.mode === 'video') return [videoReq]
    if (tpl.mode === 'audio') return [audioReq]
    return [videoReq, audioReq]
  }

  if (useDefaults.value) return [base]

  const common = {
    audioFormat: audioFormat.value as AppSettings['audioFormat'],
    videoQuality: videoQuality.value as AppSettings['videoQuality'],
    writeSubtitles: writeSubtitles.value
  }
  if (mode.value === 'both') {
    return [
      {
        ...base,
        overrides: {
          ...common,
          mode: 'video',
          ...(folder.value ? { downloadFolder: folder.value } : {})
        }
      },
      {
        ...base,
        overrides: {
          ...common,
          mode: 'audio',
          ...(audioFolder.value || folder.value
            ? { downloadFolder: audioFolder.value || folder.value }
            : {})
        }
      }
    ]
  }
  return [
    {
      ...base,
      overrides: {
        ...common,
        mode: mode.value as AppSettings['mode'],
        ...(folder.value ? { downloadFolder: folder.value } : {})
      }
    }
  ]
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
    info.value = await window.api.media.probe(url.value.trim())
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
        <div class="row" style="flex-wrap: wrap">
          <BxBtn
            icon="search"
            variant="outline"
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
            icon="add"
            variant="outline"
            :label="t('download.addToQueue')"
            :disabled="!urlValid"
            @click="start(false)"
          />
          <BxBtn
            icon="download"
            variant="cta"
            :label="t('download.start')"
            :disabled="!urlValid"
            @click="start(true)"
          />
        </div>
      </div>
    </BxCard>

    <!-- Vorschau -->
    <BxCard :title="t('download.preview.title')" :padded="false">
      <div v-if="probing" class="bx-card-section" style="color: var(--fg2)">
        <AppIcon name="searching" /> {{ t('common.loading') }}
      </div>

      <div v-else-if="!info" class="bx-card-section" style="color: var(--fg2)">
        {{ t('download.preview.empty') }}
      </div>

      <!-- Einzelnes Video -->
      <div v-else-if="!info.isPlaylist" class="bx-card-section">
        <div class="row" style="align-items: flex-start; gap: 20px">
          <img
            v-if="info.thumbnailUrl"
            :src="info.thumbnailUrl"
            alt=""
            style="width: 220px; border-radius: 8px; border: 1px solid var(--marine-10)"
          />
          <div class="stack--sm stack" style="min-width: 0">
            <h3 class="t-display-3" style="margin: 0">{{ info.title }}</h3>
            <div class="row" style="flex-wrap: wrap; gap: 8px">
              <BxChip icon="male-user" variant="neutral">{{ info.uploader }}</BxChip>
              <BxChip v-if="info.durationSeconds" icon="time" variant="neutral">
                {{ formatDuration(info.durationSeconds) }}
              </BxChip>
              <BxChip v-if="info.viewCount" icon="line-chart" variant="neutral">
                {{ formatCount(info.viewCount, locale) }} {{ t('download.preview.views') }}
              </BxChip>
            </div>
          </div>
        </div>
      </div>

      <!-- Playlist -->
      <template v-else>
        <div class="bx-card-section">
          <div class="row" style="gap: 12px; flex-wrap: wrap">
            <BxChip icon="checklist" variant="marine">{{ t('download.preview.playlist') }}</BxChip>
            <h3 class="t-display-3" style="margin: 0">{{ info.title }}</h3>
            <BxChip variant="apple">{{
              t('download.preview.entries', { n: info.entryCount })
            }}</BxChip>
          </div>
        </div>
        <table class="bx-table">
          <tbody>
            <tr v-for="(entry, i) in playlistPreview" :key="entry.id" style="cursor: default">
              <td style="width: 40px; color: var(--fg2)">{{ i + 1 }}</td>
              <td>{{ entry.title }}</td>
              <td style="width: 90px; color: var(--fg2); text-align: right">
                {{ formatDuration(entry.durationSeconds) }}
              </td>
            </tr>
          </tbody>
        </table>
        <div
          v-if="info.entryCount > playlistPreview.length"
          class="bx-card-section"
          style="color: var(--fg2); font-size: 0.85rem"
        >
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
          variant="outline"
          icon="video-player"
          :label="t('download.combi.video')"
          @click="chooseCombi('video')"
        />
        <BxBtn
          variant="cta"
          icon="checklist"
          :label="t('download.combi.playlist')"
          @click="chooseCombi('playlist')"
        />
      </template>
    </BxDialog>

    <!-- Optionen für diesen Download -->
    <BxCard :title="t('download.options.title')">
      <div class="stack">
        <!-- Vorlagen-Auswahl -->
        <div class="row" style="gap: 16px; align-items: flex-end; flex-wrap: wrap">
          <div style="flex: 1; min-width: 240px">
            <BxSelect
              v-model="templateId"
              :label="t('templates.useTemplate')"
              icon="layout"
              :options="templateOptions"
            />
          </div>
          <BxBtn
            icon="pencil"
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
          <div v-if="!useDefaults" class="bx-form-grid">
            <div class="col-6">
              <div class="f">
                <div class="f-label">{{ t('download.options.mode') }}</div>
                <BxSegmented
                  v-model="mode"
                  :options="[
                    { value: 'audio', label: t('download.options.audio'), icon: 'music' },
                    { value: 'video', label: t('download.options.video'), icon: 'video-player' },
                    { value: 'both', label: t('templates.modeBoth'), icon: 'layout' }
                  ]"
                />
              </div>
            </div>
            <div class="col-6">
              <BxSelect
                v-if="mode === 'audio'"
                v-model="audioFormat"
                icon="music"
                :label="t('download.options.format')"
                :options="audioFormatOptions"
              />
              <BxSelect
                v-else-if="mode === 'video'"
                v-model="videoQuality"
                icon="video-player"
                :label="t('download.options.quality')"
                :options="videoQualityOptions"
              />
              <div v-else class="bx-form-grid" style="gap: 16px">
                <div class="col-6">
                  <BxSelect
                    v-model="audioFormat"
                    icon="music"
                    :label="t('download.options.format')"
                    :options="audioFormatOptions"
                  />
                </div>
                <div class="col-6">
                  <BxSelect
                    v-model="videoQuality"
                    icon="video-player"
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
                    variant="outline"
                    icon="manage-folder"
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
                    variant="outline"
                    icon="manage-folder"
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
          </div>
        </template>
      </div>
    </BxCard>
  </div>
</template>
