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
  void window.api.system.openExternal('https://github.com/niklas-urbantke/MyDownloader')
}
</script>

<template>
  <PageHead :title="t('about.title')" :sub="t('about.subtitle')" />

  <div class="stack stack--lg" style="max-width: 760px">
    <BxCard>
      <div class="row" style="gap: 20px; align-items: center">
        <AppLogo :size="64" />
        <div class="stack stack--sm">
          <h2 class="t-display-2" style="margin: 0">{{ t('app.name') }}</h2>
          <div class="row" style="gap: 8px">
            <BxChip v-if="info" variant="marine">{{
              t('about.version', { v: info.version })
            }}</BxChip>
            <BxChip v-if="info" variant="neutral">Electron {{ info.electronVersion }}</BxChip>
            <BxChip v-if="info" variant="neutral">{{ info.platform }}/{{ info.arch }}</BxChip>
          </div>
          <p class="t-body2" style="margin: 0; color: var(--fg2)">{{ t('about.stack') }}</p>
        </div>
        <span class="spacer" />
        <BxBtn icon="globe" variant="outline" label="GitHub" @click="openRepo" />
      </div>
    </BxCard>

    <BxCard :title="t('about.features')">
      <div class="about-features">
        <div v-for="(feature, i) in featureList()" :key="i" class="row" style="gap: 10px">
          <AppIcon name="check-in-circle" style="color: var(--apple)" />
          <span class="t-body2">{{ feature }}</span>
        </div>
      </div>
    </BxCard>

    <!-- Updates (Issues #33 / #37) -->
    <BxCard :title="t('about.updates.title')">
      <div class="stack">
        <div class="row" style="gap: 12px; flex-wrap: wrap; align-items: center">
          <BxBtn
            icon="cloud-download"
            variant="outline"
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
          <BxChip v-if="update?.status === 'checking'" variant="neutral">
            {{ t('about.updates.checking') }}
          </BxChip>
          <BxChip v-else-if="update?.status === 'not-available'" icon="check-in-circle" variant="apple">
            {{ t('about.updates.upToDate') }}
          </BxChip>
          <BxChip v-else-if="update?.status === 'error'" icon="attention" variant="neg">
            {{ update.message }}
          </BxChip>
        </div>

        <template v-if="update?.status === 'available'">
          <div class="row" style="gap: 12px; align-items: center; flex-wrap: wrap">
            <BxChip icon="information-in-circle" variant="marine">
              {{ t('about.updates.available', { v: update.version ?? '' }) }}
            </BxChip>
            <BxBtn
              icon="download"
              variant="cta"
              size="sm"
              :label="t('about.updates.download')"
              @click="downloadUpdate"
            />
          </div>
          <p v-if="update.notes" class="t-body2" style="margin: 0; color: var(--fg2); white-space: pre-wrap">
            {{ update.notes }}
          </p>
        </template>

        <template v-else-if="update?.status === 'downloading'">
          <BxProgress :value="update.percent ?? -1" variant="marine" />
        </template>

        <template v-else-if="update?.status === 'downloaded'">
          <div class="row" style="gap: 12px; align-items: center">
            <BxChip icon="check-in-circle" variant="apple">
              {{ t('about.updates.readyToInstall', { v: update.version ?? '' }) }}
            </BxChip>
            <BxBtn
              icon="replay"
              variant="cta"
              size="sm"
              :label="t('about.updates.installNow')"
              @click="installUpdate"
            />
          </div>
        </template>
      </div>
    </BxCard>

    <BxCard :title="t('about.openSource')">
      <p class="t-body2" style="margin: 0; color: var(--fg2)">
        MIT-Lizenz · yt-dlp (Unlicense) · FFmpeg (GPL/LGPL) · Electron (MIT) · Vue (MIT)
      </p>
    </BxCard>
  </div>
</template>

<style scoped>
.about-features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 24px;
}
@media (max-width: 700px) {
  .about-features {
    grid-template-columns: 1fr;
  }
}
</style>
