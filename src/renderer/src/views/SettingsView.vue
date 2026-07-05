<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AccountStatus, BinaryStatus, SpotifyStatus } from '@shared/types'
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
  spotify.value = await window.api.spotify.status()
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

// --- Spotify (Issue #35) ---
const spotify = ref<SpotifyStatus | null>(null)
const spotifyBusy = ref(false)

async function spotifyLogin(): Promise<void> {
  spotifyBusy.value = true
  try {
    spotify.value = await window.api.spotify.login()
    if (spotify.value.loggedIn) showToast(t('spotify.loggedIn'))
  } finally {
    spotifyBusy.value = false
  }
}

async function spotifyLogout(): Promise<void> {
  spotify.value = await window.api.spotify.logout()
}

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
  { value: 'colorful', label: t('settings.fields.themeColorful'), icon: 'color-palette' },
  { value: 'flat', label: t('settings.fields.themeFlat'), icon: 'color-palette' },
  { value: 'system', label: t('settings.fields.themeSystem'), icon: 'sun-moon' }
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
        <div v-if="settings.filenameTemplate === 'custom'" class="col-12">
          <BxField
            v-model="settings.customFilenameTemplate"
            :label="t('settings.fields.customFilenameTemplate')"
            icon="pencil-line"
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
        <!-- Lautstärke-Normalisierung (Issue #26) -->
        <div class="col-6">
          <BxSelect
            v-model="settings.normalizeAudio"
            :label="t('settings.fields.normalizeAudio')"
            icon="setting-horizontal"
            :options="normalizeOptions"
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="lufsProxy"
            :label="t('settings.fields.targetLufs')"
            icon="line-chart"
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
            icon="time"
            :disabled="!settings.scheduleEnabled"
          />
        </div>
        <div class="col-6">
          <BxField
            v-model="settings.scheduleTo"
            type="time"
            :label="t('settings.fields.scheduleTo')"
            icon="time"
            :disabled="!settings.scheduleEnabled"
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
            icon="cloud-download"
            :options="autoUpdateOptions"
          />
        </div>
      </div>
    </BxCard>

    <!-- YouTube-Konto (Issue #13) -->
    <BxCard :title="t('settings.account.title')">
      <div class="stack">
        <p class="t-body2" style="margin: 0; color: var(--fg2)">
          {{ t('settings.account.description') }}
        </p>
        <div class="row" style="gap: 12px; flex-wrap: wrap; align-items: center">
          <BxChip
            :variant="account?.loggedIn ? 'apple' : 'neutral'"
            :icon="account?.loggedIn ? 'check-in-circle' : 'male-user'"
          >
            {{ account?.loggedIn ? t('settings.account.statusLoggedIn') : t('settings.account.statusLoggedOut') }}
          </BxChip>
          <span class="spacer" />
          <BxBtn
            v-if="!account?.loggedIn"
            icon="male-user"
            variant="cta"
            :label="t('settings.account.login')"
            :disabled="accountBusy"
            @click="accountLogin"
          />
          <BxBtn
            v-else
            icon="cancel"
            variant="outline"
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

    <!-- Spotify (Issue #35) -->
    <BxCard :title="t('settings.spotify.title')">
      <div class="stack">
        <p class="t-body2" style="margin: 0; color: var(--fg2)">
          {{ t('settings.spotify.description') }}
        </p>
        <BxField
          v-model="settings.spotifyClientId"
          :label="t('settings.spotify.clientId')"
          icon="key"
          :hint="t('settings.spotify.clientIdHint')"
          placeholder="z. B. 5f2a…"
        />
        <div class="row" style="gap: 12px; flex-wrap: wrap; align-items: center">
          <BxChip
            :variant="spotify?.loggedIn ? 'apple' : 'neutral'"
            :icon="spotify?.loggedIn ? 'check-in-circle' : 'music'"
          >
            {{
              spotify?.loggedIn
                ? t('spotify.connectedAs', { name: spotify.displayName ?? 'Spotify' })
                : t('settings.spotify.statusLoggedOut')
            }}
          </BxChip>
          <span class="spacer" />
          <BxBtn
            v-if="!spotify?.loggedIn"
            icon="link"
            variant="cta"
            :label="t('spotify.login')"
            :disabled="spotifyBusy || !settings.spotifyClientId.trim()"
            @click="spotifyLogin"
          />
          <BxBtn
            v-else
            icon="cancel"
            variant="outline"
            :label="t('settings.account.logout')"
            :disabled="spotifyBusy"
            @click="spotifyLogout"
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

    <!-- v3-Import -->
    <BxCard :title="t('settings.importV3.title')">
      <div class="stack">
        <p class="t-body2" style="margin: 0; color: var(--fg2)">
          {{ t('settings.importV3.description') }}
        </p>
        <div class="row" style="gap: 12px; flex-wrap: wrap">
          <BxBtn
            icon="upload"
            variant="outline"
            :label="t('settings.importV3.action')"
            :disabled="importing"
            @click="runImportV3"
          />
          <BxBtn
            icon="replay"
            variant="ghost"
            :label="t('settings.restartOnboarding')"
            @click="restartOnboarding"
          />
        </div>
      </div>
    </BxCard>
  </div>
</template>
