<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxBanner from '../components/BxBanner.vue'
import { useDownloadsStore } from '../stores/downloads'
import { useSettingsStore } from '../stores/settings'
import { showToast } from '../composables/toast'

const { t } = useI18n()
const router = useRouter()
const downloads = useDownloadsStore()
const settingsStore = useSettingsStore()

/**
 * Link auf einen einzelnen Song, dieselbe Erkennung wie im Main-Prozess
 * (open.spotify.com/track/…, auch mit /intl-xx/, sowie spotify:track:…).
 * Hier nur, um die Schaltfläche zu sperren und früh zu warnen.
 */
const TRACK_LINK = /(?:open\.spotify\.com\/(?:intl-[a-z-]+\/)?track\/|spotify:track:)[A-Za-z0-9]+/

const url = ref('')
const adding = ref(false)

const isTrackLink = computed(() => TRACK_LINK.test(url.value.trim()))

/** Erst meckern, wenn wirklich etwas Falsches im Feld steht. */
const linkError = computed(() =>
  url.value.trim() && !isTrackLink.value ? t('spotify.invalidLink') : ''
)

/**
 * Nur ein Hinweis, wo gesucht wird. Aufgelöst wird die Suche erst im
 * Main-Prozess, wenn der Titel an die Reihe kommt.
 */
const sourceHint = computed(() =>
  settingsStore.settings?.musicSource === 'youtube'
    ? t('spotify.sourceYoutube')
    : t('spotify.sourceYtmusic')
)

async function addTrack(): Promise<void> {
  if (!isTrackLink.value || adding.value) return
  adding.value = true
  try {
    // Der Link geht so, wie er ist, in die Warteschlange: Künstler und Titel
    // liest der Main-Prozess erst, wenn der Eintrag an die Reihe kommt, und
    // macht daraus die YouTube-Suche.
    await downloads.add({
      url: url.value.trim(),
      startNow: true,
      overrides: { mode: 'audio' }
    })
    showToast(t('download.added'))
    url.value = ''
    router.push({ name: 'queue' })
  } finally {
    adding.value = false
  }
}
</script>

<template>
  <PageHead :title="t('spotify.title')" :sub="t('spotify.subtitle')" />

  <div class="stack stack--lg">
    <BxCard>
      <div class="stack">
        <p class="text-secondary">{{ t('spotify.howItWorks') }}</p>
        <BxField
          v-model="url"
          icon="link"
          :label="t('spotify.linkLabel')"
          :placeholder="t('spotify.urlPlaceholder')"
          :hint="t('spotify.linkHint')"
          :error="linkError"
          @enter="addTrack"
        />
        <div class="cluster">
          <BxBtn
            icon="download"
            variant="primary"
            :label="t('spotify.load')"
            :disabled="adding || !isTrackLink"
            @click="addTrack"
          />
        </div>
      </div>
    </BxCard>

    <!-- Woher der Titel geholt wird, wenn keine feste URL vorliegt -->
    <BxBanner variant="info" icon="activity">{{ sourceHint }}</BxBanner>

    <BxBanner variant="info" icon="clock">{{ t('spotify.playlistsLater') }}</BxBanner>
  </div>
</template>
