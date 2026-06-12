<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { DownloadTemplate } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxChip from '../components/BxChip.vue'
import BxDialog from '../components/BxDialog.vue'
import AppIcon from '../components/AppIcon.vue'
import { useTemplatesStore } from '../stores/templates'

const { t } = useI18n()
const router = useRouter()
const templates = useTemplatesStore()

const deleteTarget = ref<DownloadTemplate | null>(null)

function modeLabel(template: DownloadTemplate): string {
  if (template.mode === 'both') return t('templates.modeBoth')
  return template.mode === 'audio' ? t('download.options.audio') : t('download.options.video')
}

function formatSummary(template: DownloadTemplate): string {
  if (template.mode === 'audio') return template.audioFormat.toUpperCase()
  if (template.mode === 'video')
    return `${template.videoContainer.toUpperCase()} · ${template.videoQuality === 'best' ? 'max' : template.videoQuality + 'p'}`
  return `${template.videoContainer.toUpperCase()} + ${template.audioFormat.toUpperCase()}`
}

async function confirmDelete(): Promise<void> {
  if (deleteTarget.value) {
    await templates.remove(deleteTarget.value.id)
    deleteTarget.value = null
  }
}
</script>

<template>
  <PageHead :title="t('templates.title')" :sub="t('templates.subtitle')">
    <template #actions>
      <BxBtn
        icon="add"
        variant="cta"
        :label="t('templates.create')"
        @click="router.push({ name: 'template-edit', params: { id: 'new' } })"
      />
    </template>
  </PageHead>

  <div v-if="templates.entries.length === 0" class="bx-card">
    <div class="bx-card-section" style="color: var(--fg2); text-align: center; padding: 48px">
      <AppIcon name="layout" :size="40" style="color: var(--marine-40)" />
      <p>{{ t('templates.empty') }}</p>
    </div>
  </div>

  <div v-else class="bx-tiles">
    <button
      v-for="template in templates.entries"
      :key="template.id"
      class="bx-tile"
      type="button"
      @click="router.push({ name: 'template-edit', params: { id: template.id } })"
    >
      <div class="bx-tile-head">
        <div class="bx-tile-icon">
          <AppIcon
            :name="template.mode === 'audio' ? 'music' : template.mode === 'video' ? 'video-player' : 'layout'"
          />
        </div>
        <div class="bx-tile-headtext">
          <span class="bx-tile-label">{{ template.name }}</span>
          <span class="bx-tile-sub">{{
            template.folder || t('templates.defaultFolder')
          }}</span>
        </div>
        <AppIcon name="pencil" class="bx-tile-chev" />
      </div>
      <div class="bx-tile-badges">
        <span class="bx-tile-badge bx-tile-badge--meta">{{ modeLabel(template) }}</span>
        <span class="bx-tile-badge bx-tile-badge--meta">{{ formatSummary(template) }}</span>
        <span v-if="template.writeSubtitles" class="bx-tile-badge bx-tile-badge--new">{{
          t('settings.sections.subtitles')
        }}</span>
        <span class="spacer" />
        <BxChip
          variant="neg"
          icon="trash"
          style="cursor: pointer"
          @click.stop="deleteTarget = template"
          >{{ t('common.delete') }}</BxChip
        >
      </div>
    </button>
  </div>

  <BxDialog
    :open="!!deleteTarget"
    :title="t('templates.deleteTitle')"
    @close="deleteTarget = null"
  >
    {{ t('templates.deleteQuestion', { name: deleteTarget?.name ?? '' }) }}
    <template #actions>
      <BxBtn variant="ghost" :label="t('common.cancel')" @click="deleteTarget = null" />
      <BxBtn variant="danger" icon="trash" :label="t('common.delete')" @click="confirmDelete" />
    </template>
  </BxDialog>
</template>
