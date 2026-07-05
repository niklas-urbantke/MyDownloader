<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BinaryStatus } from '@shared/types'
import BxDialog from './BxDialog.vue'
import BxBtn from './BxBtn.vue'
import BxField from './BxField.vue'
import BxSelect from './BxSelect.vue'
import BxSegmented from './BxSegmented.vue'
import BxChip from './BxChip.vue'
import AppLogo from './AppLogo.vue'
import { useSettingsStore } from '../stores/settings'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const { t } = useI18n()
const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)

const step = ref(0)
const stepCount = 4
const binaries = ref<BinaryStatus | null>(null)

onMounted(async () => {
  binaries.value = await window.api.system.binaries()
})

const audioFormatOptions = ['mp3', 'm4a', 'opus', 'flac', 'wav'].map((v) => ({
  value: v,
  label: v.toUpperCase()
}))
const videoQualityOptions = computed(() => [
  { value: 'best', label: t('settings.fields.videoQualityBest') },
  { value: '2160', label: '2160p (4K)' },
  { value: '1080', label: '1080p' },
  { value: '720', label: '720p' }
])
const themeOptions = computed(() => [
  { value: 'light', label: t('settings.fields.themeLight'), icon: 'sun' },
  { value: 'dark', label: t('settings.fields.themeDark'), icon: 'moon' },
  { value: 'colorful', label: t('settings.fields.themeColorful'), icon: 'color-palette' },
  { value: 'system', label: t('settings.fields.themeSystem'), icon: 'sun-moon' }
])
const localeOptions = computed(() => [
  { value: 'de', label: 'Deutsch' },
  { value: 'en', label: 'English' },
  { value: 'system', label: t('settings.fields.localeSystem') }
])

async function pickFolder(): Promise<void> {
  await settingsStore.pickDownloadFolder()
}

function finish(): void {
  if (settings.value) settings.value.onboardingDone = true
  emit('close')
}

function next(): void {
  if (step.value < stepCount - 1) step.value++
  else finish()
}

void props
</script>

<template>
  <BxDialog :open="open" :title="t('onboarding.title')" @close="finish">
    <div v-if="settings" class="stack stack--lg" style="min-width: 520px; min-height: 300px">
      <!-- Schritt 1: Willkommen + Komponenten-Check -->
      <template v-if="step === 0">
        <div class="row" style="gap: 16px; align-items: center">
          <AppLogo :size="52" />
          <div>
            <h3 class="t-display-3" style="margin: 0 0 4px">{{ t('onboarding.welcome') }}</h3>
            <p class="t-body2" style="margin: 0; color: var(--fg2)">
              {{ t('onboarding.welcomeText') }}
            </p>
          </div>
        </div>
        <div class="row" style="gap: 10px; flex-wrap: wrap">
          <BxChip
            :variant="binaries?.ytDlp.available ? 'apple' : 'neg'"
            :icon="binaries?.ytDlp.available ? 'check-in-circle' : 'cancel-in-circle'"
          >
            yt-dlp {{ binaries?.ytDlp.available ? t('settings.binaries.available') : t('settings.binaries.missing') }}
          </BxChip>
          <BxChip
            :variant="binaries?.ffmpeg.available ? 'apple' : 'neg'"
            :icon="binaries?.ffmpeg.available ? 'check-in-circle' : 'cancel-in-circle'"
          >
            FFmpeg {{ binaries?.ffmpeg.available ? t('settings.binaries.available') : t('settings.binaries.missing') }}
          </BxChip>
        </div>
      </template>

      <!-- Schritt 2: Zielordner -->
      <template v-else-if="step === 1">
        <h3 class="t-display-3" style="margin: 0">{{ t('onboarding.folderTitle') }}</h3>
        <BxField v-model="settings.downloadFolder" icon="folder" :label="t('settings.fields.downloadFolder')">
          <template #append>
            <BxBtn size="sm" variant="outline" icon="manage-folder"
              :label="t('settings.fields.browse')" @click="pickFolder" />
          </template>
        </BxField>
      </template>

      <!-- Schritt 3: Format & Qualität -->
      <template v-else-if="step === 2">
        <h3 class="t-display-3" style="margin: 0">{{ t('onboarding.formatTitle') }}</h3>
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
        <div class="bx-form-grid">
          <div class="col-6">
            <BxSelect
              v-if="settings.mode === 'audio'"
              v-model="settings.audioFormat"
              icon="music"
              :label="t('settings.fields.audioFormat')"
              :options="audioFormatOptions"
            />
            <BxSelect
              v-else
              v-model="settings.videoQuality"
              icon="video-player"
              :label="t('settings.fields.videoQuality')"
              :options="videoQualityOptions"
            />
          </div>
        </div>
      </template>

      <!-- Schritt 4: Darstellung -->
      <template v-else>
        <h3 class="t-display-3" style="margin: 0">{{ t('onboarding.appearanceTitle') }}</h3>
        <div class="f">
          <div class="f-label">{{ t('settings.fields.theme') }}</div>
          <BxSegmented v-model="settings.theme" :options="themeOptions" />
        </div>
        <BxSelect
          v-model="settings.locale"
          :label="t('settings.fields.locale')"
          icon="globe"
          :options="localeOptions"
        />
      </template>

      <!-- Fortschrittspunkte -->
      <div class="row" style="justify-content: center; gap: 8px; margin-top: auto">
        <span
          v-for="i in stepCount"
          :key="i"
          :style="{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: i - 1 === step ? 'var(--marine)' : 'var(--marine-10, #dde)',
            display: 'inline-block'
          }"
        />
      </div>
    </div>

    <template #actions>
      <BxBtn variant="ghost" :label="t('onboarding.skip')" @click="finish" />
      <BxBtn v-if="step > 0" variant="outline" :label="t('onboarding.back')" @click="step--" />
      <BxBtn
        variant="cta"
        :icon="step === stepCount - 1 ? 'check-in-circle' : 'arrow-right'"
        :label="step === stepCount - 1 ? t('onboarding.finish') : t('onboarding.next')"
        @click="next"
      />
    </template>
  </BxDialog>
</template>
