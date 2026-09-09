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
  { value: 'colorful', label: t('settings.fields.themeColorful'), icon: 'image' },
  { value: 'flat', label: t('settings.fields.themeFlat'), icon: 'image' },
  { value: 'system', label: t('settings.fields.themeSystem'), icon: 'sun' }
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
  <BxDialog :open="open" :title="t('onboarding.title')" wide @close="finish">
    <div v-if="settings" class="stack stack--lg onboarding">
      <!-- Schritt 1: Willkommen + Komponenten-Check -->
      <template v-if="step === 0">
        <div class="cluster" style="--cluster-gap: var(--space-4)">
          <AppLogo :size="52" />
          <div class="stack stack--sm">
            <h2>{{ t('onboarding.welcome') }}</h2>
            <p class="text-secondary">{{ t('onboarding.welcomeText') }}</p>
          </div>
        </div>
        <div class="cluster">
          <BxChip
            :variant="binaries?.ytDlp.available ? 'success' : 'danger'"
            :icon="binaries?.ytDlp.available ? 'check-circle' : 'x-circle'"
          >
            yt-dlp
            {{
              binaries?.ytDlp.available
                ? t('settings.binaries.available')
                : t('settings.binaries.missing')
            }}
          </BxChip>
          <BxChip
            :variant="binaries?.ffmpeg.available ? 'success' : 'danger'"
            :icon="binaries?.ffmpeg.available ? 'check-circle' : 'x-circle'"
          >
            FFmpeg
            {{
              binaries?.ffmpeg.available
                ? t('settings.binaries.available')
                : t('settings.binaries.missing')
            }}
          </BxChip>
        </div>
      </template>

      <!-- Schritt 2: Zielordner -->
      <template v-else-if="step === 1">
        <h2>{{ t('onboarding.folderTitle') }}</h2>
        <BxField
          v-model="settings.downloadFolder"
          icon="folder"
          :label="t('settings.fields.downloadFolder')"
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
      </template>

      <!-- Schritt 3: Format & Qualität -->
      <template v-else-if="step === 2">
        <h2>{{ t('onboarding.formatTitle') }}</h2>
        <div class="field">
          <span class="label">{{ t('settings.fields.mode') }}</span>
          <BxSegmented
            v-model="settings.mode"
            :options="[
              { value: 'audio', label: t('settings.fields.modeAudio'), icon: 'activity' },
              { value: 'video', label: t('settings.fields.modeVideo'), icon: 'image' }
            ]"
          />
        </div>
        <div class="form-grid">
          <div class="col-6">
            <BxSelect
              v-if="settings.mode === 'audio'"
              v-model="settings.audioFormat"
              icon="activity"
              :label="t('settings.fields.audioFormat')"
              :options="audioFormatOptions"
            />
            <BxSelect
              v-else
              v-model="settings.videoQuality"
              icon="image"
              :label="t('settings.fields.videoQuality')"
              :options="videoQualityOptions"
            />
          </div>
        </div>
      </template>

      <!-- Schritt 4: Darstellung -->
      <template v-else>
        <h2>{{ t('onboarding.appearanceTitle') }}</h2>
        <div class="field">
          <span class="label">{{ t('settings.fields.theme') }}</span>
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
      <div class="cluster onboarding__dots">
        <span
          v-for="i in stepCount"
          :key="i"
          class="onboarding__dot"
          :class="{ 'is-active': i - 1 === step }"
        />
      </div>
    </div>

    <template #actions>
      <BxBtn variant="ghost" :label="t('onboarding.skip')" @click="finish" />
      <BxBtn v-if="step > 0" variant="secondary" :label="t('onboarding.back')" @click="step--" />
      <BxBtn
        variant="primary"
        :icon="step === stepCount - 1 ? 'check-circle' : 'arrow-right'"
        :label="step === stepCount - 1 ? t('onboarding.finish') : t('onboarding.next')"
        @click="next"
      />
    </template>
  </BxDialog>
</template>

<style scoped>
/* Feste Mindesthoehe, damit die Schritte nicht springen. */
.onboarding {
  min-width: 0;
  min-height: 19rem;
}

/* Schrittanzeige: der aktuelle Punkt traegt die Akzentfarbe. */
.onboarding__dots {
  --cluster-gap: var(--space-2);
  justify-content: center;
  margin-block-start: auto;
}

.onboarding__dot {
  display: inline-block;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: var(--radius-full);
  background-color: var(--color-border-strong);
}

.onboarding__dot.is-active {
  background-color: var(--color-accent);
}
</style>
