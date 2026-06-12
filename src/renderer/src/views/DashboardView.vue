<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHead from '../components/PageHead.vue'
import BxStat from '../components/BxStat.vue'
import BxTile from '../components/BxTile.vue'
import BxCard from '../components/BxCard.vue'
import BxChip from '../components/BxChip.vue'
import AppIcon from '../components/AppIcon.vue'
import { useDownloadsStore } from '../stores/downloads'
import { useHistoryStore } from '../stores/history'
import { formatDateTime } from '../utils/format'

const { t, locale } = useI18n()
const router = useRouter()
const downloads = useDownloadsStore()
const history = useHistoryStore()

const recent = computed(() => history.entries.slice(0, 6))

const completedTodayHistory = computed(() => {
  const today = new Date().toDateString()
  return history.entries.filter(
    (e) => e.status === 'completed' && new Date(e.timestamp).toDateString() === today
  ).length
})

function go(name: string): void {
  router.push({ name })
}
</script>

<template>
  <PageHead :title="t('dashboard.title')" :sub="t('dashboard.subtitle')" />

  <!-- KPIs -->
  <div class="bx-tiles" style="margin-bottom: 28px">
    <BxStat :label="t('dashboard.kpi.active')" :value="downloads.activeItems.length" />
    <BxStat :label="t('dashboard.kpi.queued')" :value="downloads.queuedItems.length" />
    <BxStat :label="t('dashboard.kpi.completedToday')" :value="completedTodayHistory" />
    <BxStat :label="t('dashboard.kpi.total')" :value="history.entries.length" />
  </div>

  <!-- Anwendungs-Kacheln: der primäre Einstieg -->
  <div class="bx-tile-group">
    <div class="bx-section-head">
      <h2 class="bx-section-title">{{ t('dashboard.groups.download') }}</h2>
    </div>
    <div class="bx-tiles">
      <BxTile
        icon="download"
        :label="t('dashboard.tiles.download.label')"
        :sub="t('dashboard.tiles.download.sub')"
        @click="go('download')"
      />
      <BxTile
        icon="checklist"
        :label="t('dashboard.tiles.queue.label')"
        :sub="t('dashboard.tiles.queue.sub')"
        @click="go('queue')"
      >
        <template v-if="downloads.items.length > 0" #badges>
          <span v-if="downloads.activeItems.length > 0" class="bx-tile-badge bx-tile-badge--new">
            <strong>{{ t('dashboard.badges.active', { n: downloads.activeItems.length }) }}</strong>
          </span>
          <span v-if="downloads.queuedItems.length > 0" class="bx-tile-badge bx-tile-badge--todo">
            {{ t('dashboard.badges.queued', { n: downloads.queuedItems.length }) }}
          </span>
          <span v-if="downloads.errorItems.length > 0" class="bx-tile-badge bx-tile-badge--overdue">
            {{ t('dashboard.badges.errors', { n: downloads.errorItems.length }) }}
          </span>
          <span
            v-if="
              downloads.activeItems.length === 0 &&
              downloads.queuedItems.length === 0 &&
              downloads.errorItems.length === 0
            "
            class="bx-tile-badge bx-tile-badge--empty"
          >
            <AppIcon name="check-in-circle" />
            <span>{{ t('common.allDone') }}</span>
          </span>
        </template>
      </BxTile>
    </div>
  </div>

  <div class="bx-tile-group">
    <div class="bx-section-head">
      <h2 class="bx-section-title">{{ t('dashboard.groups.library') }}</h2>
    </div>
    <div class="bx-tiles">
      <BxTile
        icon="time"
        :label="t('dashboard.tiles.history.label')"
        :sub="t('dashboard.tiles.history.sub')"
        @click="go('history')"
      >
        <template v-if="history.entries.length > 0" #badges>
          <span class="bx-tile-badge bx-tile-badge--meta">
            {{ t('dashboard.badges.entries', { n: history.entries.length }) }}
          </span>
          <span v-if="completedTodayHistory > 0" class="bx-tile-badge bx-tile-badge--new">
            {{ t('dashboard.badges.completedToday', { n: completedTodayHistory }) }}
          </span>
        </template>
      </BxTile>
      <BxTile
        icon="setting"
        :label="t('dashboard.tiles.settings.label')"
        :sub="t('dashboard.tiles.settings.sub')"
        @click="go('settings')"
      />
    </div>
  </div>

  <!-- Zuletzt heruntergeladen -->
  <BxCard v-if="recent.length > 0" :title="t('dashboard.recent')" :padded="false">
    <table class="bx-table">
      <tbody>
        <tr v-for="entry in recent" :key="entry.id" @click="go('history')">
          <td style="width: 40px">
            <AppIcon
              class="row-icon"
              :name="entry.isPlaylist ? 'checklist' : entry.mode === 'audio' ? 'music' : 'video-player'"
            />
          </td>
          <td>
            <strong>{{ entry.title }}</strong>
            <span v-if="entry.uploader" style="color: var(--fg2)"> · {{ entry.uploader }}</span>
          </td>
          <td style="width: 90px">
            <BxChip variant="neutral">{{ entry.format.toUpperCase() }}</BxChip>
          </td>
          <td style="width: 180px; color: var(--fg2)">
            {{ formatDateTime(entry.timestamp, locale) }}
          </td>
        </tr>
      </tbody>
    </table>
  </BxCard>
</template>
