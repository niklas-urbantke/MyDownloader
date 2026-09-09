<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { HistoryEntry } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxChip from '../components/BxChip.vue'
import BxField from '../components/BxField.vue'
import BxSegmented from '../components/BxSegmented.vue'
import BxDialog from '../components/BxDialog.vue'
import MetadataDialog from '../components/MetadataDialog.vue'
import AppIcon from '../components/AppIcon.vue'
import { useHistoryStore } from '../stores/history'
import { useDownloadsStore } from '../stores/downloads'
import { showToast } from '../composables/toast'
import { formatDateTime } from '../utils/format'

const { t, locale } = useI18n()
const history = useHistoryStore()
const downloads = useDownloadsStore()

const search = ref('')
const filter = ref('all')
const period = ref('all')
const confirmClear = ref(false)

const filterOptions = computed(() => [
  { value: 'all', label: t('history.filter.all') },
  { value: 'audio', label: t('history.filter.audio'), icon: 'activity' },
  { value: 'video', label: t('history.filter.video'), icon: 'image' },
  { value: 'playlists', label: t('history.filter.playlists'), icon: 'list' },
  { value: 'errors', label: t('history.filter.errors'), icon: 'alert-triangle' }
])

const periodOptions = computed(() => [
  { value: 'all', label: t('history.period.all') },
  { value: 'today', label: t('history.period.today') },
  { value: 'week', label: t('history.period.week') },
  { value: 'month', label: t('history.period.month') }
])

const periodStart = computed<number>(() => {
  const now = new Date()
  switch (period.value) {
    case 'today':
      return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
    case 'week':
      return now.getTime() - 7 * 24 * 60 * 60 * 1000
    case 'month':
      return now.getTime() - 30 * 24 * 60 * 60 * 1000
    default:
      return 0
  }
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const since = periodStart.value
  return history.entries.filter((e) => {
    if (since > 0 && new Date(e.timestamp).getTime() < since) return false
    if (filter.value === 'audio' && (e.mode !== 'audio' || e.status !== 'completed')) return false
    if (filter.value === 'video' && (e.mode !== 'video' || e.status !== 'completed')) return false
    if (filter.value === 'playlists' && !e.isPlaylist) return false
    if (filter.value === 'errors' && e.status !== 'error') return false
    if (!q) return true
    return (
      e.title.toLowerCase().includes(q) ||
      (e.uploader ?? '').toLowerCase().includes(q) ||
      e.url.toLowerCase().includes(q)
    )
  })
})

async function showInFolder(entry: HistoryEntry): Promise<void> {
  const file = entry.outputFiles.at(-1)
  if (file) {
    const ok = await window.api.system.showInFolder(file)
    if (!ok) {
      showToast(t('history.fileMissing'), 'error')
      void window.api.system.openPath(entry.destination)
    }
  } else {
    void window.api.system.openPath(entry.destination)
  }
}

async function redownload(entry: HistoryEntry): Promise<void> {
  await downloads.add({ url: entry.url, knownTitle: entry.title, startNow: true })
  showToast(t('download.added'))
}

async function copyUrl(entry: HistoryEntry): Promise<void> {
  await navigator.clipboard.writeText(entry.url)
}

async function clearAll(): Promise<void> {
  await history.clear()
  confirmClear.value = false
}

// --- Metadaten-Editor (Issue #25) ---
const AUDIO_RE = /\.(mp3|m4a|opus|flac|wav)$/i
const metaFiles = ref<string[]>([])

const audioFilesOf = (entry: HistoryEntry): string[] =>
  entry.outputFiles.filter((f) => AUDIO_RE.test(f))

function editTags(entry: HistoryEntry): void {
  metaFiles.value = audioFilesOf(entry)
}
</script>

<template>
  <PageHead :title="t('history.title')" :sub="t('history.subtitle')">
    <template #actions>
      <BxBtn
        icon="trash"
        variant="secondary"
        :label="t('history.clearAll')"
        :disabled="history.entries.length === 0"
        @click="confirmClear = true"
      />
    </template>
  </PageHead>

  <div class="stack">
    <div class="cluster" style="--cluster-gap: var(--space-4)">
      <div style="flex: 1; min-width: 260px">
        <BxField v-model="search" icon="search" :placeholder="t('history.searchPlaceholder')" />
      </div>
      <BxSegmented v-model="filter" :options="filterOptions" />
      <BxSegmented v-model="period" :options="periodOptions" />
    </div>

    <BxCard v-if="filtered.length === 0" :padded="false">
      <div class="empty">
        <span class="empty__icon">
          <AppIcon name="clock" class="icon--xl icon--duo" />
        </span>
        <p class="empty__title">{{ t('history.empty') }}</p>
      </div>
    </BxCard>

    <BxCard v-else :padded="false">
      <table class="table table--plain">
        <thead>
          <tr>
            <th style="width: 40px"></th>
            <th>{{ t('history.columns.title') }}</th>
            <th style="width: 90px">{{ t('history.columns.format') }}</th>
            <th style="width: 110px">{{ t('history.columns.status') }}</th>
            <th style="width: 170px">{{ t('history.columns.when') }}</th>
            <th style="width: 150px"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in filtered" :key="entry.id">
            <td>
              <AppIcon
                :name="entry.isPlaylist ? 'list' : entry.mode === 'audio' ? 'activity' : 'image'"
              />
            </td>
            <td>
              <strong>{{ entry.title }}</strong>
              <span v-if="entry.uploader" class="text-muted"> · {{ entry.uploader }}</span>
            </td>
            <td>
              <BxChip variant="slate">{{ entry.format.toUpperCase() }}</BxChip>
            </td>
            <td>
              <BxChip
                :variant="
                  entry.status === 'completed'
                    ? 'success'
                    : entry.status === 'error'
                      ? 'danger'
                      : 'warning'
                "
              >
                {{ t(`status.${entry.status}`) }}
              </BxChip>
            </td>
            <td class="text-muted">{{ formatDateTime(entry.timestamp, locale) }}</td>
            <td>
              <div class="cluster" style="justify-content: flex-end">
                <BxBtn
                  icon="folder"
                  variant="ghost"
                  size="sm"
                  :title="t('common.showInFolder')"
                  @click="showInFolder(entry)"
                />
                <BxBtn
                  icon="replay"
                  variant="ghost"
                  size="sm"
                  :title="t('history.redownload')"
                  @click="redownload(entry)"
                />
                <BxBtn
                  v-if="audioFilesOf(entry).length > 0"
                  icon="pencil"
                  variant="ghost"
                  size="sm"
                  :title="t('metadata.title')"
                  @click="editTags(entry)"
                />
                <BxBtn
                  icon="link"
                  variant="ghost"
                  size="sm"
                  :title="t('common.copyUrl')"
                  @click="copyUrl(entry)"
                />
                <BxBtn
                  icon="trash"
                  variant="ghost"
                  size="sm"
                  :title="t('common.remove')"
                  @click="history.remove(entry.id)"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </BxCard>
  </div>

  <MetadataDialog :open="metaFiles.length > 0" :files="metaFiles" @close="metaFiles = []" />

  <BxDialog :open="confirmClear" :title="t('history.clearAll')" @close="confirmClear = false">
    {{ t('history.confirmClear') }}
    <template #actions>
      <BxBtn variant="ghost" :label="t('common.cancel')" @click="confirmClear = false" />
      <BxBtn variant="danger" icon="trash" :label="t('common.confirm')" @click="clearAll" />
    </template>
  </BxDialog>
</template>
