<script setup lang="ts">
import type { AccentName } from '@shared/types'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AccountStatus, BinaryStatus } from '@shared/types'
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
const importing = ref(false)

async function runImportV3(): Promise<void> {
  importing.value = true
  try {
    const result = await window.api.system.importV3()
    if (result.ok) {
      showToast(
        t('settings.importV3.done', {
          settings: result.settingsImported,
          history: result.historyImported
        })
      )
      await store.load()
    }
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  binaries.value = await window.api.system.binaries()
  account.value = await window.api.account.status()
})

// --- Konto (Issue #13) ---
const account = ref<AccountStatus | null>(null)
const accountBusy = ref(false)

async function accountLogin(): Promise<void> {
  accountBusy.value = true
  try {
    account.value = await window.api.account.login()
    if (account.value.loggedIn) showToast(t('settings.account.loggedIn'))
  } finally {
    accountBusy.value = false
  }
}

async function accountLogout(): Promise<void> {
  accountBusy.value = true
  try {
    account.value = await window.api.account.logout()
  } finally {
    accountBusy.value = false
  }
}

// Spotify braucht hier nichts mehr: Ein einzelner Songlink lässt sich ohne
// Registrierung auflösen, deshalb gibt es weder Client-ID noch Anmeldung.

// --- Onboarding erneut starten (Issue #31) ---
function restartOnboarding(): void {
  if (settings.value) settings.value.onboardingDone = false
}

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
  { value: 'index-title', label: t('settings.fields.filenameIndexTitle') },
  { value: 'custom', label: t('settings.fields.filenameCustom') }
])

// Live-Vorschau des eigenen Schemas (Issue #28)
const customPreview = computed(() => {
  const raw = settings.value?.customFilenameTemplate ?? ''
  const sample = raw
    .replace(/\{artist\}/g, 'Künstler')
    .replace(/\{album\}/g, 'Album')
    .replace(/\{title\}/g, 'Titel')
    .replace(/\{track\}/g, '01')
    .replace(/\{year\}/g, '2026')
    .replace(/\{playlist\}/g, 'Playlist')
  return `${sample || '…'}.mp3`
})

// Quelle für Suchen ohne feste URL (z. B. Spotify-Import): YouTube Music
// trifft die Albumfassung, die normale Suche fast immer das Musikvideo
const musicSourceOptions = computed(() => [
  { value: 'ytmusic', label: t('settings.fields.musicSourceYtmusic') },
  { value: 'youtube', label: t('settings.fields.musicSourceYoutube') }
])

const normalizeOptions = computed(() => [
  { value: 'off', label: t('settings.fields.normalizeOff') },
  { value: 'replaygain', label: t('settings.fields.normalizeReplaygain') },
  { value: 'loudnorm', label: t('settings.fields.normalizeLoudnorm') }
])

const lufsProxy = computed({
  get: () => String(settings.value?.targetLufs ?? -14),
  set: (v: string) => {
    if (!settings.value) return
    const n = Number.parseFloat(v.replace(',', '.'))
    if (Number.isFinite(n) && n <= -5 && n >= -30) settings.value.targetLufs = n
  }
})
const concurrencyOptions = ['1', '2', '3', '4', '5'].map((v) => ({ value: v, label: v }))
const themeOptions = computed(() => [
  { value: 'light', label: t('settings.fields.themeLight'), icon: 'sun' },
  { value: 'dark', label: t('settings.fields.themeDark'), icon: 'moon' },
  { value: 'system', label: t('settings.fields.themeSystem'), icon: 'monitor' }
])
/** Zwei Token-Saetze, beide gibt es in Hell und Dunkel. */
const styleOptions = computed(() => [
  { value: 'classic', label: t('settings.fields.styleClassic'), icon: 'square' },
  { value: 'aero', label: t('settings.fields.styleAero'), icon: 'layers' }
])
/** Die sechs Markentoene. Wirken nur im Stil "aero". */
const accentOptions = computed(() => [
  { value: 'azure', label: t('settings.fields.accentAzure') },
  { value: 'indigo', label: t('settings.fields.accentIndigo') },
  { value: 'amber', label: t('settings.fields.accentAmber') },
  { value: 'jade', label: t('settings.fields.accentJade') },
  { value: 'rose', label: t('settings.fields.accentRose') },
  { value: 'slate', label: t('settings.fields.accentSlate') }
])
const localeOptions = computed(() => [
  { value: 'de', label: 'Deutsch' },
  { value: 'en', label: 'English' },
  { value: 'system', label: t('settings.fields.localeSystem') }
])
const autoUpdateOptions = computed(() => [
  { value: 'auto', label: t('settings.fields.autoUpdateAuto') },
  { value: 'notify', label: t('settings.fields.autoUpdateNotify') },
  { value: 'off', label: t('settings.fields.autoUpdateOff') }
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
      <div class="form-grid">
        <div class="col-12">
          <BxField
            v-model="settings.downloadFolder"
            :label="t('settings.fields.downloadFolder')"
            icon="folder"
          >
            <template #append>
              <BxBtn
                size="sm"
                variant="secondary"
                icon="folder"
                :label="t('settings.fields.browse')"
                @click="store.pickDownloadFolder()"
              />
            </template>
          </BxField>
        </div>
        <div class="col-6">
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
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.filenameTemplate"
            :label="t('settings.fields.filenameTemplate')"
            icon="edit"
            :options="filenameOptions"
          />
        </div>
        <div v-if="settings.filenameTemplate === 'custom'" class="col-12">
          <BxField
            v-model="settings.customFilenameTemplate"
            :label="t('settings.fields.customFilenameTemplate')"
            icon="edit"
            placeholder="{artist}/{album}/{track} - {title}"
            :hint="t('settings.fields.customFilenamePreview', { preview: customPreview })"
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
      <div class="form-grid">
        <div class="col-6">
          <BxSelect
            v-model="settings.audioFormat"
            :label="t('settings.fields.audioFormat')"
            icon="activity"
            :options="audioFormatOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.audioQuality"
            :label="t('settings.fields.audioQuality')"
            icon="sliders"
            :options="audioQualityOptions"
          />
        </div>
        <div class="col-6">
          <BxToggle v-model="settings.embedThumbnail" :label="t('settings.fields.embedThumbnail')" />
        </div>
        <div class="col-6">
          <BxToggle v-model="settings.embedMetadata" :label="t('settings.fields.embedMetadata')" />
        </div>
        <!-- Musikquelle für Suchen ohne feste URL -->
        <div class="col-12">
          <BxSelect
            v-model="settings.musicSource"
            :label="t('settings.fields.musicSource')"
            icon="activity"
            :options="musicSourceOptions"
            :hint="t('settings.fields.musicSourceHint')"
          />
        </div>
        <!-- Lautstärke-Normalisierung (Issue #26) -->
        <div class="col-6">
          <BxSelect
            v-model="settings.normalizeAudio"
            :label="t('settings.fields.normalizeAudio')"
            icon="sliders"
            :options="normalizeOptions"
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="lufsProxy"
            :label="t('settings.fields.targetLufs')"
            icon="activity"
            :hint="t('settings.fields.targetLufsHint')"
            :disabled="settings.normalizeAudio === 'off'"
          />
        </div>
        <!-- Songtexte (Issue #27) -->
        <div class="col-12">
          <BxToggle
            v-model="settings.fetchLyrics"
            :label="t('settings.fields.fetchLyrics')"
            :hint="t('settings.fields.fetchLyricsHint')"
          />
        </div>
      </div>
    </BxCard>

    <!-- Video -->
    <BxCard :title="t('settings.sections.video')">
      <div class="form-grid">
        <div class="col-6">
          <BxSelect
            v-model="settings.videoContainer"
            :label="t('settings.fields.videoContainer')"
            icon="image"
            :options="containerOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.videoQuality"
            :label="t('settings.fields.videoQuality')"
            icon="maximize"
            :options="videoQualityOptions"
          />
        </div>
      </div>
    </BxCard>

    <!-- Untertitel -->
    <BxCard :title="t('settings.sections.subtitles')">
      <div class="form-grid">
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
      <div class="form-grid">
        <div class="col-6">
          <BxField
            v-model="settings.speedLimit"
            :label="t('settings.fields.speedLimit')"
            icon="zap"
            :hint="t('settings.fields.speedLimitHint')"
            placeholder="∞"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="concurrencyProxy"
            :label="t('settings.fields.concurrency')"
            icon="power"
            :options="concurrencyOptions"
          />
        </div>
        <!-- Tägliches Download-Zeitfenster (Issue #22) -->
        <div class="col-12">
          <BxToggle
            v-model="settings.scheduleEnabled"
            :label="t('settings.fields.scheduleEnabled')"
            :hint="t('settings.fields.scheduleHint')"
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="settings.scheduleFrom"
            type="time"
            :label="t('settings.fields.scheduleFrom')"
            icon="clock"
            :disabled="!settings.scheduleEnabled"
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="settings.scheduleTo"
            type="time"
            :label="t('settings.fields.scheduleTo')"
            icon="clock"
            :disabled="!settings.scheduleEnabled"
          />
        </div>
      </div>
    </BxCard>

    <!-- Erweitert -->
    <BxCard :title="t('settings.sections.advanced')">
      <div class="form-grid">
        <div class="col-12">
          <BxToggle v-model="settings.sponsorBlock" :label="t('settings.fields.sponsorBlock')" />
        </div>
        <div class="col-12">
          <BxField
            v-model="settings.extraArgs"
            :label="t('settings.fields.extraArgs')"
            icon="sliders"
            :hint="t('settings.fields.extraArgsHint')"
            placeholder="--cookies-from-browser firefox"
          />
        </div>
      </div>
    </BxCard>

    <!-- Darstellung -->
    <BxCard :title="t('settings.sections.appearance')">
      <div class="form-grid">
        <div class="col-6">
          <div class="field">
            <span class="label">{{ t('settings.fields.theme') }}</span>
            <BxSegmented v-model="settings.theme" :options="themeOptions" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <span class="label">{{ t('settings.fields.style') }}</span>
            <BxSegmented v-model="settings.style" :options="styleOptions" />
            <span class="help">{{ t('settings.fields.styleHint') }}</span>
          </div>
        </div>

        <!-- Akzent und die zwei Schalter wirken nur im neuen Stil. -->
        <div v-if="settings.style === 'aero'" class="col-12">
          <div class="field">
            <span class="label">{{ t('settings.fields.accent') }}</span>
            <div class="cluster accent-choice">
              <button
                v-for="a in accentOptions"
                :key="a.value"
                type="button"
                class="btn btn--sm accent-btn"
                :class="settings.accent === a.value ? 'btn--primary' : 'btn--secondary'"
                @click="settings.accent = a.value as AccentName"
              >
                <span class="accent-dot" :style="{ backgroundColor: `var(--tone-${a.value})` }" />
                {{ a.label }}
              </button>
            </div>
          </div>
        </div>
        <div v-if="settings.style === 'aero'" class="col-6">
          <BxToggle v-model="settings.glass" :label="t('settings.fields.glass')" />
        </div>
        <div v-if="settings.style === 'aero'" class="col-6">
          <BxToggle v-model="settings.vivid" :label="t('settings.fields.vivid')" />
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
        <!-- Tray & Auto-Updates (Issues #14 / #33) -->
        <div class="col-6">
          <BxToggle
            v-model="settings.closeToTray"
            :label="t('settings.fields.closeToTray')"
            :hint="t('settings.fields.closeToTrayHint')"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="settings.autoUpdate"
            :label="t('settings.fields.autoUpdate')"
            icon="cloud"
            :options="autoUpdateOptions"
          />
        </div>
      </div>
    </BxCard>

    <!-- YouTube-Konto (Issue #13) -->
    <BxCard :title="t('settings.account.title')">
      <div class="stack">
        <p class="text-secondary">
          {{ t('settings.account.description') }}
        </p>
        <div class="cluster">
          <BxChip
            :variant="account?.loggedIn ? 'success' : 'slate'"
            :icon="account?.loggedIn ? 'check-circle' : 'user'"
          >
            {{ account?.loggedIn ? t('settings.account.statusLoggedIn') : t('settings.account.statusLoggedOut') }}
          </BxChip>
          <span class="spacer" />
          <BxBtn
            v-if="!account?.loggedIn"
            icon="user"
            variant="primary"
            :label="t('settings.account.login')"
            :disabled="accountBusy"
            @click="accountLogin"
          />
          <BxBtn
            v-else
            icon="x"
            variant="secondary"
            :label="t('settings.account.logout')"
            :disabled="accountBusy"
            @click="accountLogout"
          />
        </div>
        <BxToggle
          v-model="settings.useAccountCookies"
          :label="t('settings.account.useCookies')"
          :hint="t('settings.account.useCookiesHint')"
          :disabled="!account?.loggedIn"
        />
      </div>
    </BxCard>

    <!-- System & Wartung -->
    <BxCard :title="t('settings.binaries.title')">
      <div class="stack">
        <div class="cluster">
          <BxChip
            :variant="binaries?.ytDlp.available ? 'success' : 'danger'"
            :icon="binaries?.ytDlp.available ? 'check-circle' : 'x-circle'"
          >
            {{ t('settings.binaries.ytdlp') }}
            {{
              binaries?.ytDlp.version
                ? t('settings.binaries.version', { v: binaries.ytDlp.version })
                : t('settings.binaries.missing')
            }}
          </BxChip>
          <BxChip
            :variant="binaries?.ffmpeg.available ? 'success' : 'danger'"
            :icon="binaries?.ffmpeg.available ? 'check-circle' : 'x-circle'"
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
            icon="cloud"
            variant="secondary"
            :label="t('settings.binaries.updateYtDlp')"
            :disabled="updatingYtDlp || !binaries?.ytDlp.available"
            @click="updateYtDlp"
          />
        </div>
        <BxBanner v-if="binaries && (!binaries.ytDlp.available || !binaries.ffmpeg.available)" variant="warning">
          {{ t('dashboard.badges.binariesMissing') }}
        </BxBanner>
      </div>
    </BxCard>

    <!-- v3-Import -->
    <BxCard :title="t('settings.importV3.title')">
      <div class="stack">
        <p class="text-secondary">
          {{ t('settings.importV3.description') }}
        </p>
        <div class="cluster">
          <BxBtn
            icon="upload"
            variant="secondary"
            :label="t('settings.importV3.action')"
            :disabled="importing"
            @click="runImportV3"
          />
          <BxBtn
            icon="rotate-cw"
            variant="ghost"
            :label="t('settings.restartOnboarding')"
            @click="restartOnboarding"
          />
        </div>
      </div>
    </BxCard>
  </div>
</template>

<style scoped>
/* Farbiger Punkt am Akzent-Knopf, damit man sieht, was man waehlt. */
.accent-btn {
  gap: var(--space-2);
}
.accent-dot {
  inline-size: 0.75rem;
  block-size: 0.75rem;
  border-radius: var(--radius-full);
  border: var(--border-thin) solid var(--color-border-strong);
}
</style>
