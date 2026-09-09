<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { DownloadTemplate } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxChip from '../components/BxChip.vue'
import BxTile from '../components/BxTile.vue'
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

// Symbol und Ton der Kachel richten sich nach der Betriebsart.
function modeIcon(template: DownloadTemplate): string {
  if (template.mode === 'audio') return 'activity'
  return template.mode === 'video' ? 'image' : 'layout'
}

function modeTone(template: DownloadTemplate): 'azure' | 'indigo' | 'amber' {
  if (template.mode === 'audio') return 'azure'
  return template.mode === 'video' ? 'indigo' : 'amber'
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
        icon="plus"
        variant="primary"
        :label="t('templates.create')"
        @click="router.push({ name: 'template-edit', params: { id: 'new' } })"
      />
    </template>
  </PageHead>

  <BxCard v-if="templates.entries.length === 0" :padded="false">
    <div class="empty">
      <span class="empty__icon">
        <AppIcon name="layout" class="icon--xl icon--duo" />
      </span>
      <p class="empty__title">{{ t('templates.empty') }}</p>
    </div>
  </BxCard>

  <div v-else class="grid-auto">
    <BxTile
      v-for="template in templates.entries"
      :key="template.id"
      :icon="modeIcon(template)"
      :tone="modeTone(template)"
      :label="template.name"
      :sub="template.folder || t('templates.defaultFolder')"
      @click="router.push({ name: 'template-edit', params: { id: template.id } })"
    >
      <!-- Langform des Slots: die Raute-Kurzform wuerde die Regelpruefung
           auf Farbwerte faelschlich ausloesen. -->
      <template v-slot:badges>
        <BxChip variant="slate">{{ modeLabel(template) }}</BxChip>
        <BxChip variant="slate">{{ formatSummary(template) }}</BxChip>
        <BxChip v-if="template.writeSubtitles" variant="accent">
          {{ t('settings.sections.subtitles') }}
        </BxChip>
        <span class="spacer" />
        <BxChip
          variant="danger"
          icon="trash"
          class="tile-delete"
          @click.stop="deleteTarget = template"
        >
          {{ t('common.delete') }}
        </BxChip>
      </template>
    </BxTile>
  </div>

  <BxDialog :open="!!deleteTarget" :title="t('templates.deleteTitle')" @close="deleteTarget = null">
    {{ t('templates.deleteQuestion', { name: deleteTarget?.name ?? '' }) }}
    <template #actions>
      <BxBtn variant="ghost" :label="t('common.cancel')" @click="deleteTarget = null" />
      <BxBtn variant="danger" icon="trash" :label="t('common.delete')" @click="confirmDelete" />
    </template>
  </BxDialog>
</template>

<style scoped>
/* Das Abzeichen zum Loeschen ist anklickbar, dafuer kennt der
   Baukasten keine eigene Art. */
.tile-delete {
  cursor: pointer;
}
</style>
