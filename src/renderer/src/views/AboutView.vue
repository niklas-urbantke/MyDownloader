<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AppInfo } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxChip from '../components/BxChip.vue'
import BxBtn from '../components/BxBtn.vue'
import AppLogo from '../components/AppLogo.vue'
import AppIcon from '../components/AppIcon.vue'

const { t, tm } = useI18n()

const info = ref<AppInfo | null>(null)

onMounted(async () => {
  info.value = await window.api.system.appInfo()
})

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
