<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { SpotifyPlaylist, SpotifyStatus, SpotifyTrack } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxChip from '../components/BxChip.vue'
import BxBanner from '../components/BxBanner.vue'
import AppIcon from '../components/AppIcon.vue'
import { useDownloadsStore } from '../stores/downloads'
import { useSettingsStore } from '../stores/settings'
import { showToast } from '../composables/toast'
import { formatDuration } from '../utils/format'

const { t } = useI18n()
const router = useRouter()
const downloads = useDownloadsStore()
const settingsStore = useSettingsStore()

const status = ref<SpotifyStatus | null>(null)
const loggingIn = ref(false)
const url = ref('')
const loading = ref(false)
const playlist = ref<SpotifyPlaylist | null>(null)
const excluded = ref<Set<number>>(new Set())
/** Manuell überschriebene Suchanfragen je Track-Index */
const queryOverrides = ref<Record<number, string>>({})

onMounted(async () => {
  status.value = await window.api.spotify.status()
})

async function login(): Promise<void> {
  loggingIn.value = true
  try {
    status.value = await window.api.spotify.login()
    if (status.value.loggedIn) showToast(t('spotify.loggedIn'))
  } finally {
    loggingIn.value = false
  }
}

async function loadPlaylist(): Promise<void> {
  if (!url.value.trim()) return
  loading.value = true
  playlist.value = null
  excluded.value = new Set()
  queryOverrides.value = {}
  try {
    playlist.value = await window.api.spotify.getPlaylist(url.value.trim())
    if (!playlist.value) showToast(t('spotify.loadFailed'), 'error')
  } finally {
    loading.value = false
  }
}

/** Standard-Suchanfrage: bevorzugt Album-/Topic-Treffer wie der v3-Loader */
function defaultQuery(track: SpotifyTrack): string {
  return `${track.artist} - ${track.title}`
}

function queryFor(index: number, track: SpotifyTrack): string {
  return queryOverrides.value[index] ?? defaultQuery(track)
}

function toggleExcluded(index: number): void {
  const set = new Set(excluded.value)
  if (set.has(index)) set.delete(index)
  else set.add(index)
  excluded.value = set
}

const selectedCount = computed(() =>
  playlist.value ? playlist.value.tracks.length - excluded.value.size : 0
)

async function importSelected(): Promise<void> {
  if (!playlist.value) return
  const requests = playlist.value.tracks
    .map((track, i) => ({ track, i }))
    .filter(({ i }) => !excluded.value.has(i))
    .map(({ track, i }) => ({
      // yt-dlp löst ytsearch1: selbst zum besten Treffer auf
      url: `ytsearch1:${queryFor(i, track)} official audio`,
      knownTitle: `${track.artist} - ${track.title}`,
      overrides: { mode: 'audio' as const }
    }))
  if (requests.length === 0) return
  await downloads.addMany(requests)
  showToast(t('download.addedMany', { n: requests.length }))
  router.push({ name: 'queue' })
}
</script>

<template>
  <PageHead :title="t('spotify.title')" :sub="t('spotify.subtitle')" />

  <div class="stack stack--lg">
    <!-- Kein Client konfiguriert / nicht angemeldet -->
    <BxBanner v-if="status && !status.configured" variant="info" icon="information-in-circle">
      {{ t('spotify.setupHint') }}
      <BxBtn
        variant="ghost"
        size="sm"
        :label="t('nav.settings')"
        @click="router.push({ name: 'settings' })"
      />
    </BxBanner>

    <BxCard v-if="status && status.configured && !status.loggedIn">
      <div class="row" style="gap: 16px; align-items: center">
        <AppIcon name="music" :size="28" style="color: var(--marine)" />
        <span style="flex: 1">{{ t('spotify.loginHint') }}</span>
        <BxBtn
          icon="link"
          variant="cta"
          :label="t('spotify.login')"
          :disabled="loggingIn"
          @click="login"
        />
      </div>
    </BxCard>

    <!-- Angemeldet: Playlist laden -->
    <template v-if="status?.loggedIn">
      <BxCard>
        <div class="stack">
          <div class="row" style="gap: 8px; align-items: center; flex-wrap: wrap">
            <BxChip icon="check-in-circle" variant="apple">
              {{ t('spotify.connectedAs', { name: status.displayName ?? 'Spotify' }) }}
            </BxChip>
          </div>
          <BxField
            v-model="url"
            icon="link"
            :placeholder="t('spotify.urlPlaceholder')"
            @enter="loadPlaylist"
          />
          <div class="row">
            <BxBtn
              icon="search"
              variant="outline"
              :label="t('spotify.load')"
              :disabled="loading || !url.trim()"
              @click="loadPlaylist"
            />
            <span class="spacer" />
            <BxBtn
              v-if="playlist"
              icon="download"
              variant="cta"
              :label="t('spotify.import', { n: selectedCount })"
              :disabled="selectedCount === 0"
              @click="importSelected"
            />
          </div>
        </div>
      </BxCard>

      <div v-if="loading" class="bx-card">
        <div class="bx-card-section" style="color: var(--fg2)">
          <AppIcon name="searching" /> {{ t('common.loading') }}
        </div>
      </div>

      <!-- Trackliste mit Matching-Vorschau -->
      <BxCard v-if="playlist" :padded="false" :title="`${playlist.title} — ${t('spotify.tracks', { n: playlist.tracks.length })}`">
        <table class="bx-table">
          <thead>
            <tr>
              <th style="width: 40px"></th>
              <th>{{ t('spotify.columns.track') }}</th>
              <th>{{ t('spotify.columns.query') }}</th>
              <th style="width: 80px">{{ t('spotify.columns.duration') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(track, i) in playlist.tracks"
              :key="i"
              :style="{ opacity: excluded.has(i) ? 0.4 : 1, cursor: 'default' }"
            >
              <td>
                <div
                  class="toggle"
                  :class="{ on: !excluded.has(i) }"
                  style="transform: scale(0.8)"
                  role="checkbox"
                  :aria-checked="!excluded.has(i)"
                  @click="toggleExcluded(i)"
                />
              </td>
              <td>
                <strong>{{ track.artist }}</strong> — {{ track.title }}
                <span v-if="track.album" style="color: var(--fg2)"> · {{ track.album }}</span>
              </td>
              <td>
                <input
                  class="spotify-query"
                  :value="queryFor(i, track)"
                  @input="queryOverrides[i] = ($event.target as HTMLInputElement).value"
                />
              </td>
              <td style="color: var(--fg2)">{{ formatDuration(track.durationSeconds) }}</td>
            </tr>
          </tbody>
        </table>
      </BxCard>
    </template>
  </div>
</template>

<style scoped>
.spotify-query {
  width: 100%;
  border: 1px solid var(--marine-10, #dde);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  background: transparent;
  color: inherit;
}
</style>
