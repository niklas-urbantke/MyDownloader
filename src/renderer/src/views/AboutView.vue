<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AppInfo, UpdateEventPayload } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxChip from '../components/BxChip.vue'
import BxBtn from '../components/BxBtn.vue'
import BxProgress from '../components/BxProgress.vue'
import AppLogo from '../components/AppLogo.vue'
import AppIcon from '../components/AppIcon.vue'
import { showToast } from '../composables/toast'

const { t, tm } = useI18n()

const info = ref<AppInfo | null>(null)
const update = ref<UpdateEventPayload | null>(null)
let unsub: (() => void) | null = null

onMounted(async () => {
  info.value = await window.api.system.appInfo()
  unsub = window.api.updates.onEvent((payload) => {
    update.value = payload
  })
})

onUnmounted(() => unsub?.())

function checkUpdates(): void {
  void window.api.updates.check()
}

function downloadUpdate(): void {
  void window.api.updates.download()
}

function installUpdate(): void {
  void window.api.updates.install()
}

async function installUrbUpdate(): Promise<void> {
  const result = await window.api.updates.installUrbUpdate()
  if (result.message === 'cancelled') return
  showToast(result.message, result.ok ? 'success' : 'error')
}

const featureList = (): string[] => {
  const list = tm('about.featureList')
  return Array.isArray(list) ? list.map(String) : []
}

function openRepo(): void {
  void window.api.system.openExternal('https://github.com/niklas-urbantke/YouTube-Downloader')
}
</script>

<template>
  <PageHead :title="t('about.title')" :sub="t('about.subtitle')" />

  <div class="stack stack--lg about-page">
    <BxCard>
      <div class="cluster about-head">
        <AppLogo :size="64" />
        <div class="stack stack--sm">
          <h2>{{ t('app.name') }}</h2>
          <div class="cluster" style="--cluster-gap: var(--space-2)">
            <BxChip v-if="info" variant="accent">{{
              t('about.version', { v: info.version })
            }}</BxChip>
            <BxChip v-if="info" variant="slate">Electron {{ info.electronVersion }}</BxChip>
            <BxChip v-if="info" variant="slate">{{ info.platform }}/{{ info.arch }}</BxChip>
          </div>
          <p class="text-secondary about-text">{{ t('about.stack') }}</p>
        </div>
        <span class="spacer" />
        <BxBtn icon="globe" variant="secondary" label="GitHub" @click="openRepo" />
      </div>
    </BxCard>

    <BxCard :title="t('about.features')">
      <div class="grid-auto" style="--col-min: 18rem; --grid-gap: var(--space-3) var(--space-6)">
        <div v-for="(feature, i) in featureList()" :key="i" class="cluster about-feature">
          <AppIcon name="check-circle" class="icon--success" />
          <span class="about-text">{{ feature }}</span>
        </div>
      </div>
    </BxCard>

    <!-- Updates (Issues #33 / #37) -->
    <BxCard :title="t('about.updates.title')">
      <div class="stack">
        <div class="cluster">
          <BxBtn
            icon="download"
            variant="secondary"
            :label="t('about.checkUpdates')"
            :disabled="update?.status === 'checking' || update?.status === 'downloading'"
            @click="checkUpdates"
          />
          <BxBtn
            icon="package"
            variant="ghost"
            :label="t('about.updates.fromFile')"
            @click="installUrbUpdate"
          />
          <span class="spacer" />
          <BxChip v-if="update?.status === 'checking'" variant="slate">
            {{ t('about.updates.checking') }}
          </BxChip>
          <BxChip v-else-if="update?.status === 'not-available'" icon="check-circle" variant="success">
            {{ t('about.updates.upToDate') }}
          </BxChip>
          <BxChip v-else-if="update?.status === 'error'" icon="alert-triangle" variant="danger">
            {{ update.message }}
          </BxChip>
        </div>

        <template v-if="update?.status === 'available'">
          <div class="cluster">
            <BxChip icon="info" variant="accent">
              {{ t('about.updates.available', { v: update.version ?? '' }) }}
            </BxChip>
            <BxBtn
              icon="download"
              variant="primary"
              size="sm"
              :label="t('about.updates.download')"
              @click="downloadUpdate"
            />
          </div>
          <p v-if="update.notes" class="text-secondary about-text about-notes">
            {{ update.notes }}
          </p>
        </template>

        <template v-else-if="update?.status === 'downloading'">
          <BxProgress :value="update.percent ?? -1" variant="accent" />
        </template>

        <template v-else-if="update?.status === 'downloaded'">
          <div class="cluster">
            <BxChip icon="check-circle" variant="success">
              {{ t('about.updates.readyToInstall', { v: update.version ?? '' }) }}
            </BxChip>
            <BxBtn
              icon="rotate-cw"
              variant="primary"
              size="sm"
              :label="t('about.updates.installNow')"
              @click="installUpdate"
            />
          </div>
        </template>
      </div>
    </BxCard>

    <BxCard :title="t('about.openSource')">
      <p class="text-secondary about-text">
        MIT-Lizenz · yt-dlp (Unlicense) · FFmpeg (GPL/LGPL) · Electron (MIT) · Vue (MIT)
      </p>
    </BxCard>
  </div>
</template>

<style scoped>
/* Lesebreite der Seite. */
.about-page {
  max-width: 47.5rem;
}

/* Zeichen, Name und Schaltfläche in einer Zeile. */
.about-head {
  --cluster-gap: var(--space-5);
  flex-wrap: nowrap;
}

.about-feature {
  --cluster-gap: var(--space-3);
  flex-wrap: nowrap;
  align-items: flex-start;
}

.about-text {
  font-size: var(--text-sm);
}
.about-notes {
  white-space: pre-wrap;
}
</style>
