<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DownloadItem } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxChip from '../components/BxChip.vue'
import BxProgress from '../components/BxProgress.vue'
import BxBanner from '../components/BxBanner.vue'
import BxDialog from '../components/BxDialog.vue'
import AppIcon from '../components/AppIcon.vue'
import { useDownloadsStore } from '../stores/downloads'
import { showToast } from '../composables/toast'
import { formatSpeed, formatEta, formatBytes, formatDateTime, isHttpUrl } from '../utils/format'

const { t, locale } = useI18n()
const downloads = useDownloadsStore()

const isScheduled = (item: DownloadItem): boolean =>
  item.status === 'queued' && !!item.scheduledAt && Date.parse(item.scheduledAt) > Date.now()

const fileInput = ref<HTMLInputElement | null>(null)
const confirmCancelAll = ref(false)

// Log-Dialog
const logItem = ref<DownloadItem | null>(null)
const logBox = ref<HTMLElement | null>(null)
const logLines = computed(() => (logItem.value ? (downloads.logs[logItem.value.id] ?? []) : []))

watch(
  () => logLines.value.length,
  async () => {
    await nextTick()
    logBox.value?.scrollTo({ top: logBox.value.scrollHeight })
  }
)

async function openLog(item: DownloadItem): Promise<void> {
  await downloads.fetchLog(item.id)
  logItem.value = item
}

const statusChipVariant = (status: DownloadItem['status']): 'apple' | 'marine' | 'neg' | 'neutral' | 'warn' => {
  switch (status) {
    case 'completed':
      return 'apple'
    case 'downloading':
    case 'converting':
    case 'fetching-info':
      return 'marine'
    case 'error':
      return 'neg'
    case 'cancelled':
      return 'warn'
    default:
      return 'neutral'
  }
}

const isActive = (item: DownloadItem): boolean =>
  item.status === 'downloading' || item.status === 'converting' || item.status === 'fetching-info'

function importFromFile(): void {
  fileInput.value?.click()
}

async function onFilePicked(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  const text = await file.text()
  await addUrls(text)
}

async function importFromClipboard(): Promise<void> {
  try {
    const text = await navigator.clipboard.readText()
    await addUrls(text)
  } catch {
    /* Zwischenablage nicht lesbar */
  }
}

async function addUrls(text: string): Promise<void> {
  const urls = text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => isHttpUrl(l))
  if (urls.length === 0) return
  await downloads.addMany(urls.map((url) => ({ url })))
  showToast(t('download.addedMany', { n: urls.length }))
}

async function cancelAll(): Promise<void> {
  for (const item of downloads.items) {
    if (item.status === 'queued' || isActive(item)) await downloads.cancel(item.id)
  }
  confirmCancelAll.value = false
}

function showInFolder(item: DownloadItem): void {
  const file = item.outputFiles.at(-1)
  if (file) void window.api.system.showInFolder(file)
  else void window.api.system.openPath(item.destination)
}
</script>

<template>
  <PageHead :title="t('queue.title')" :sub="t('queue.subtitle')">
    <template #actions>
      <BxBtn
        v-if="!downloads.processing"
        icon="play"
        variant="cta"
        :label="t('queue.start')"
        :disabled="downloads.queuedItems.length === 0"
        @click="downloads.startQueue()"
      />
      <BxBtn
        v-else
        icon="pause"
        variant="outline"
        :label="t('queue.pause')"
        @click="downloads.pauseQueue()"
      />
      <BxBtn
        icon="paper"
        variant="ghost"
        :label="t('queue.importFile')"
        @click="importFromFile"
      />
      <BxBtn
        icon="clipboard"
        variant="ghost"
        :label="t('queue.importClipboard')"
        @click="importFromClipboard"
      />
      <BxBtn
        icon="trash"
        variant="outline"
        :label="t('queue.clearFinished')"
        @click="downloads.clearFinished()"
      />
      <BxBtn
        icon="cancel"
        variant="danger"
        :label="t('queue.cancelAll')"
        :disabled="downloads.activeItems.length === 0 && downloads.queuedItems.length === 0"
        @click="confirmCancelAll = true"
      />
    </template>
  </PageHead>

  <input ref="fileInput" type="file" accept=".txt,text/plain" hidden @change="onFilePicked" />

  <div v-if="downloads.items.length === 0" class="bx-card">
    <div class="bx-card-section" style="color: var(--fg2); text-align: center; padding: 48px">
      <AppIcon name="checklist" :size="40" style="color: var(--marine-40)" />
      <p>{{ t('queue.empty') }}</p>
    </div>
  </div>

  <BxBanner
    v-if="downloads.queuedItems.length > 0 && !downloads.processing"
    variant="info"
    style="margin-bottom: 16px"
  >
    {{ t('queue.notStartedHint', { n: downloads.queuedItems.length }) }}
  </BxBanner>

  <div v-if="downloads.items.length > 0" class="stack">
    <BxCard v-for="(item, index) in downloads.items" :key="item.id" :padded="false">
      <div class="bx-card-section">
        <div class="row" style="align-items: flex-start; gap: 16px">
          <img
            v-if="item.thumbnailUrl"
            :src="item.thumbnailUrl"
            alt=""
            style="width: 120px; border-radius: 8px; border: 1px solid var(--marine-10)"
          />
          <div v-else class="bx-tile-icon" style="flex-shrink: 0">
            <AppIcon
              :name="item.isPlaylist ? 'checklist' : item.mode === 'audio' ? 'music' : 'video-player'"
            />
          </div>

          <div class="stack stack--sm" style="flex: 1; min-width: 0">
            <div class="row" style="gap: 10px; flex-wrap: wrap">
              <strong style="font-size: 1rem; color: var(--marine)">{{ item.title }}</strong>
              <BxChip :variant="statusChipVariant(item.status)">
                {{ t(`status.${item.status}`) }}
              </BxChip>
              <BxChip variant="neutral">{{ item.format.toUpperCase() }}</BxChip>
              <BxChip v-if="isScheduled(item)" icon="time" variant="outline">
                {{ t('queue.scheduledFor', { when: formatDateTime(item.scheduledAt!, locale) }) }}
              </BxChip>
              <BxChip
                v-if="item.isPlaylist && item.progress.playlistIndex && item.progress.playlistCount"
                variant="outline"
              >
                {{
                  t('queue.playlistProgress', {
                    current: item.progress.playlistIndex,
                    total: item.progress.playlistCount
                  })
                }}
              </BxChip>
            </div>

            <template v-if="isActive(item)">
              <BxProgress
                :value="item.status === 'converting' ? -1 : item.progress.percent"
                :variant="item.status === 'converting' ? 'apple' : 'marine'"
              />
              <div class="row" style="gap: 16px; color: var(--fg2); font-size: 12px">
                <span v-if="item.progress.percent >= 0">
                  {{ item.progress.percent.toFixed(0) }} % ·
                  {{ formatBytes(item.progress.downloadedBytes) }}
                  <template v-if="item.progress.totalBytes">
                    / {{ formatBytes(item.progress.totalBytes) }}
                  </template>
                </span>
                <span>{{ t('queue.speed') }}: {{ formatSpeed(item.progress.speed) }}</span>
                <span>{{ t('queue.eta') }}: {{ formatEta(item.progress.eta) }}</span>
              </div>
            </template>

            <div
              v-if="item.status === 'error' && item.errorMessage"
              style="color: #c10015; font-size: 12px; word-break: break-word"
            >
              {{ item.errorMessage }}
            </div>
          </div>

          <div class="row" style="flex-shrink: 0">
            <template v-if="item.status === 'queued'">
              <BxBtn
                icon="arrow-up"
                variant="ghost"
                size="sm"
                :title="t('queue.moveUp')"
                :disabled="index === 0"
                @click="downloads.move(item.id, 'up')"
              />
              <BxBtn
                icon="arrow-down"
                variant="ghost"
                size="sm"
                :title="t('queue.moveDown')"
                :disabled="index === downloads.items.length - 1"
                @click="downloads.move(item.id, 'down')"
              />
            </template>
            <BxBtn
              v-if="item.status === 'completed'"
              icon="folder"
              variant="ghost"
              size="sm"
              :title="t('common.showInFolder')"
              @click="showInFolder(item)"
            />
            <BxBtn
              v-if="item.status === 'error' || item.status === 'cancelled'"
              icon="replay"
              variant="outline"
              size="sm"
              :label="t('common.retry')"
              @click="downloads.retry(item.id)"
            />
            <BxBtn
              v-if="item.status === 'downloading' || item.status === 'converting'"
              icon="pause"
              variant="ghost"
              size="sm"
              :title="t('queue.pauseItem')"
              @click="downloads.pause(item.id)"
            />
            <BxBtn
              v-if="item.status === 'paused'"
              icon="play"
              variant="outline"
              size="sm"
              :label="t('queue.resumeItem')"
              @click="downloads.resume(item.id)"
            />
            <BxBtn
              icon="note"
              variant="ghost"
              size="sm"
              :title="t('queue.showLog')"
              @click="openLog(item)"
            />
            <BxBtn
              v-if="isActive(item) || item.status === 'queued' || item.status === 'paused'"
              icon="cancel"
              variant="ghost"
              size="sm"
              :title="t('common.cancel')"
              @click="downloads.cancel(item.id)"
            />
            <BxBtn
              v-else
              icon="trash"
              variant="ghost"
              size="sm"
              :title="t('common.remove')"
              @click="downloads.remove(item.id)"
            />
          </div>
        </div>
      </div>
    </BxCard>
  </div>

  <!-- Log-Dialog -->
  <BxDialog
    :open="!!logItem"
    :title="`${t('queue.log')} — ${logItem?.title ?? ''}`"
    @close="logItem = null"
  >
    <div
      ref="logBox"
      style="
        max-height: 360px;
        overflow: auto;
        background: var(--marine-dark);
        color: #cfe3ff;
        border-radius: 8px;
        padding: 12px;
        font: 11px/1.6 var(--font-mono);
        white-space: pre-wrap;
        word-break: break-all;
      "
    >
      <div v-for="(line, i) in logLines" :key="i">{{ line }}</div>
      <div v-if="logLines.length === 0" style="color: var(--marine-60)">—</div>
    </div>
    <template #actions>
      <BxBtn variant="ghost" :label="t('common.close')" @click="logItem = null" />
    </template>
  </BxDialog>

  <!-- Alle abbrechen bestätigen -->
  <BxDialog
    :open="confirmCancelAll"
    :title="t('queue.cancelAll')"
    @close="confirmCancelAll = false"
  >
    {{ t('queue.confirmCancelAll') }}
    <template #actions>
      <BxBtn variant="ghost" :label="t('common.cancel')" @click="confirmCancelAll = false" />
      <BxBtn variant="danger" icon="cancel" :label="t('common.confirm')" @click="cancelAll" />
    </template>
  </BxDialog>
</template>
