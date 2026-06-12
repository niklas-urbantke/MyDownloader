<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { AppSettings, DownloadRequest, MediaInfo } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxSelect from '../components/BxSelect.vue'
import BxSegmented from '../components/BxSegmented.vue'
import BxToggle from '../components/BxToggle.vue'
import BxChip from '../components/BxChip.vue'
import AppIcon from '../components/AppIcon.vue'
import { useSettingsStore } from '../stores/settings'
import { useDownloadsStore } from '../stores/downloads'
import { showToast } from '../composables/toast'
import { formatDuration, formatCount, isHttpUrl } from '../utils/format'

const { t, locale } = useI18n()
const router = useRouter()
const settingsStore = useSettingsStore()
const downloads = useDownloadsStore()

const url = ref('')
const probing = ref(false)
const probeError = ref('')
const info = ref<MediaInfo | null>(null)

// Optionen für diesen Download (Abweichung von den globalen Einstellungen)
const useDefaults = ref(true)
const mode = ref<'audio' | 'video'>('audio')
const audioFormat = ref('mp3')
const videoQuality = ref('best')

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

function buildRequest(): DownloadRequest {
  const request: DownloadRequest = { url: url.value.trim() }
  if (info.value) request.knownTitle = info.value.title
  if (!useDefaults.value) {
    request.overrides = {
      mode: mode.value,
      audioFormat: audioFormat.value as AppSettings['audioFormat'],
      videoQuality: videoQuality.value as AppSettings['videoQuality']
    }
  }
  return request
}

async function probe(): Promise<void> {
  if (!urlValid.value) {
    probeError.value = t('download.errors.invalidUrl')
    return
  }
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
  await downloads.add(buildRequest())
  showToast(t('download.added'))
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

    <!-- Optionen für diesen Download -->
    <BxCard :title="t('download.options.title')">
      <div class="stack">
        <BxToggle v-model="useDefaults" :label="t('download.options.useDefaults')" />
        <div v-if="!useDefaults" class="bx-form-grid">
          <div class="col-4">
            <div class="f">
              <div class="f-label">{{ t('download.options.mode') }}</div>
              <BxSegmented
                v-model="mode"
                :options="[
                  { value: 'audio', label: t('download.options.audio'), icon: 'music' },
                  { value: 'video', label: t('download.options.video'), icon: 'video-player' }
                ]"
              />
            </div>
          </div>
          <div class="col-4">
            <BxSelect
              v-if="mode === 'audio'"
              v-model="audioFormat"
              icon="music"
              :label="t('download.options.format')"
              :options="audioFormatOptions"
            />
            <BxSelect
              v-else
              v-model="videoQuality"
              icon="video-player"
              :label="t('download.options.quality')"
              :options="videoQualityOptions"
            />
          </div>
          <div class="col-4">
            <BxField
              :label="t('download.options.folder')"
              icon="folder"
              :model-value="settingsStore.settings?.downloadFolder ?? ''"
              readonly
            />
          </div>
        </div>
      </div>
    </BxCard>
  </div>
</template>
