<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BinaryStatus } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxSelect from '../components/BxSelect.vue'
import BxToggle from '../components/BxToggle.vue'
import BxSegmented from '../components/BxSegmented.vue'
import BxChip from '../components/BxChip.vue'
import BxBanner from '../components/BxBanner.vue'
import { useSettingsStore } from '../stores/settings'
import { showToast } from '../composables/toast'

const { t } = useI18n()
const store = useSettingsStore()

const settings = computed(() => store.settings)

const binaries = ref<BinaryStatus | null>(null)
const updatingYtDlp = ref(false)

onMounted(async () => {
  binaries.value = await window.api.system.binaries()
})

async function updateYtDlp(): Promise<void> {
  updatingYtDlp.value = true
  try {
    const result = await window.api.system.updateYtDlp()
    if (result.ok) {
      showToast(t('settings.binaries.updated', { v: result.message }))
    } else {
      showToast(t('settings.binaries.updateFailed', { msg: result.message }), 'error')
    }
    binaries.value = await window.api.system.binaries()
  } finally {
    updatingYtDlp.value = false
  }
}

const audioFormatOptions = ['mp3', 'm4a', 'opus', 'flac', 'wav'].map((v) => ({
  value: v,
  label: v.toUpperCase()
}))
const audioQualityOptions = computed(() => [
  { value: '0', label: t('settings.fields.audioQualityBest') },
  { value: '2', label: '2' },
  { value: '5', label: '5' },
  { value: '7', label: '7' },
  { value: '9', label: t('settings.fields.audioQualitySmallest') }
])
const containerOptions = ['mp4', 'mkv', 'webm'].map((v) => ({ value: v, label: v.toUpperCase() }))
const videoQualityOptions = computed(() => [
  { value: 'best', label: t('settings.fields.videoQualityBest') },
  { value: '2160', label: '2160p (4K)' },
  { value: '1440', label: '1440p' },
  { value: '1080', label: '1080p' },
  { value: '720', label: '720p' },
  { value: '480', label: '480p' }
])
const filenameOptions = computed(() => [
  { value: 'title', label: t('settings.fields.filenameTitle') },
  { value: 'artist-title', label: t('settings.fields.filenameArtistTitle') },
  { value: 'index-title', label: t('settings.fields.filenameIndexTitle') }
])
const concurrencyOptions = ['1', '2', '3', '4', '5'].map((v) => ({ value: v, label: v }))
const themeOptions = computed(() => [
  { value: 'light', label: t('settings.fields.themeLight'), icon: 'sun' },
  { value: 'dark', label: t('settings.fields.themeDark'), icon: 'moon' },
  { value: 'system', label: t('settings.fields.themeSystem'), icon: 'sun-moon' }
])
const localeOptions = computed(() => [
  { value: 'de', label: 'Deutsch' },
  { value: 'en', label: 'English' },
  { value: 'system', label: t('settings.fields.localeSystem') }
])

const concurrencyProxy = computed({
  get: () => String(settings.value?.concurrency ?? 2),
  set: (v: string) => {
    if (settings.value) settings.value.concurrency = Number.parseInt(v, 10)
  }
})
</script>

<template>
  <PageHead :title="t('settings.title')" :sub="t('settings.subtitle')" />

  <div v-if="settings" class="stack stack--lg">
    <!-- Ausgabe -->
    <BxCard :title="t('settings.sections.output')">
      <div class="bx-form-grid">
        <div class="col-12">
          <BxField
            v-model="settings.downloadFolder"
            :label="t('settings.fields.downloadFolder')"
            icon="folder"
          >
            <template #append>
              <BxBtn
                size="sm"
                variant="outline"
                icon="manage-folder"
                :label="t('settings.fields.browse')"
                @click="store.pickDownloadFolder()"
              />
            </template>
          </BxField>
        </div>
        <div class="col-6">
          <div class="f">
            <div class="f-label">{{ t('settings.fields.mode') }}</div>
            <BxSegmented
              v-model="settings.mode"
              :options="[
                { value: 'audio', label: t('settings.fields.modeAudio'), icon: 'music' },
                { value: 'video', label: t('settings.fields.modeVideo'), icon: 'video-player' }
              ]"
            />
          </div>
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.filenameTemplate"
            :label="t('settings.fields.filenameTemplate')"
            icon="pencil-line"
            :options="filenameOptions"
          />
        </div>
        <div class="col-12">
          <BxToggle
            v-model="settings.playlistSubfolder"
            :label="t('settings.fields.playlistSubfolder')"
          />
        </div>
      </div>
    </BxCard>

    <!-- Audio -->
    <BxCard :title="t('settings.sections.audio')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxSelect
            v-model="settings.audioFormat"
            :label="t('settings.fields.audioFormat')"
            icon="music"
            :options="audioFormatOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.audioQuality"
            :label="t('settings.fields.audioQuality')"
            icon="setting-horizontal"
            :options="audioQualityOptions"
          />
        </div>
        <div class="col-6">
          <BxToggle v-model="settings.embedThumbnail" :label="t('settings.fields.embedThumbnail')" />
        </div>
        <div class="col-6">
          <BxToggle v-model="settings.embedMetadata" :label="t('settings.fields.embedMetadata')" />
        </div>
      </div>
    </BxCard>

    <!-- Video -->
    <BxCard :title="t('settings.sections.video')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxSelect
            v-model="settings.videoContainer"
            :label="t('settings.fields.videoContainer')"
            icon="video-player"
            :options="containerOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.videoQuality"
            :label="t('settings.fields.videoQuality')"
            icon="full-screen"
            :options="videoQualityOptions"
          />
        </div>
      </div>
    </BxCard>

    <!-- Untertitel -->
    <BxCard :title="t('settings.sections.subtitles')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxToggle v-model="settings.writeSubtitles" :label="t('settings.fields.writeSubtitles')" />
        </div>
        <div class="col-6">
          <BxField
            v-model="settings.subtitleLanguages"
            :label="t('settings.fields.subtitleLanguages')"
            icon="globe"
            placeholder="de,en"
            :disabled="!settings.writeSubtitles"
          />
        </div>
      </div>
    </BxCard>

    <!-- Netzwerk & Leistung -->
    <BxCard :title="t('settings.sections.network')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxField
            v-model="settings.speedLimit"
            :label="t('settings.fields.speedLimit')"
            icon="rocket"
            :hint="t('settings.fields.speedLimitHint')"
            placeholder="∞"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="concurrencyProxy"
            :label="t('settings.fields.concurrency')"
            icon="stop-start"
            :options="concurrencyOptions"
          />
        </div>
      </div>
    </BxCard>

    <!-- Erweitert -->
    <BxCard :title="t('settings.sections.advanced')">
      <div class="bx-form-grid">
        <div class="col-12">
          <BxToggle v-model="settings.sponsorBlock" :label="t('settings.fields.sponsorBlock')" />
        </div>
        <div class="col-12">
          <BxField
            v-model="settings.extraArgs"
            :label="t('settings.fields.extraArgs')"
            icon="setting-vertical"
            :hint="t('settings.fields.extraArgsHint')"
            placeholder="--cookies-from-browser firefox"
          />
        </div>
      </div>
    </BxCard>

    <!-- Darstellung -->
    <BxCard :title="t('settings.sections.appearance')">
      <div class="bx-form-grid">
        <div class="col-6">
          <div class="f">
            <div class="f-label">{{ t('settings.fields.theme') }}</div>
            <BxSegmented v-model="settings.theme" :options="themeOptions" />
          </div>
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.locale"
            :label="t('settings.fields.locale')"
            icon="globe"
            :options="localeOptions"
          />
        </div>
        <div class="col-6">
          <BxToggle
            v-model="settings.notifyOnComplete"
            :label="t('settings.fields.notifyOnComplete')"
          />
        </div>
        <div class="col-6">
          <BxToggle
            v-model="settings.clipboardWatcher"
            :label="t('settings.fields.clipboardWatcher')"
          />
        </div>
      </div>
    </BxCard>

    <!-- System & Wartung -->
    <BxCard :title="t('settings.binaries.title')">
      <div class="stack">
        <div class="row" style="gap: 12px; flex-wrap: wrap">
          <BxChip
            :variant="binaries?.ytDlp.available ? 'apple' : 'neg'"
            :icon="binaries?.ytDlp.available ? 'check-in-circle' : 'cancel-in-circle'"
          >
            {{ t('settings.binaries.ytdlp') }}
            {{
              binaries?.ytDlp.version
                ? t('settings.binaries.version', { v: binaries.ytDlp.version })
                : t('settings.binaries.missing')
            }}
          </BxChip>
          <BxChip
            :variant="binaries?.ffmpeg.available ? 'apple' : 'neg'"
            :icon="binaries?.ffmpeg.available ? 'check-in-circle' : 'cancel-in-circle'"
          >
            {{ t('settings.binaries.ffmpeg') }}
            {{
              binaries?.ffmpeg.version
                ? t('settings.binaries.version', { v: binaries.ffmpeg.version })
                : t('settings.binaries.missing')
            }}
          </BxChip>
          <span class="spacer" />
          <BxBtn
            icon="cloud-download"
            variant="outline"
            :label="t('settings.binaries.updateYtDlp')"
            :disabled="updatingYtDlp || !binaries?.ytDlp.available"
            @click="updateYtDlp"
          />
        </div>
        <BxBanner v-if="binaries && (!binaries.ytDlp.available || !binaries.ffmpeg.available)" variant="warn">
          {{ t('dashboard.badges.binariesMissing') }}
        </BxBanner>
      </div>
    </BxCard>
  </div>
</template>
