<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { DownloadTemplate } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxSelect from '../components/BxSelect.vue'
import BxSegmented from '../components/BxSegmented.vue'
import BxToggle from '../components/BxToggle.vue'
import BxChip from '../components/BxChip.vue'
import { useTemplatesStore, emptyTemplate } from '../stores/templates'
import { useSettingsStore } from '../stores/settings'
import { showToast } from '../composables/toast'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const templates = useTemplatesStore()
const settingsStore = useSettingsStore()

const isNew = computed(() => route.params.id === 'new')
const form = ref<DownloadTemplate>(emptyTemplate())
const nameError = ref('')

onMounted(async () => {
  if (!templates.loaded) await templates.load()
  if (!isNew.value) {
    const existing = templates.byId(String(route.params.id))
    if (existing) form.value = { ...existing }
    else router.replace({ name: 'templates' })
  }
})

const modeOptions = computed(() => [
  { value: 'audio', label: t('download.options.audio'), icon: 'music' },
  { value: 'video', label: t('download.options.video'), icon: 'video-player' },
  { value: 'both', label: t('templates.modeBoth'), icon: 'layout' }
])
const audioFormatOptions = ['mp3', 'm4a', 'opus', 'flac', 'wav'].map((v) => ({
  value: v,
  label: v.toUpperCase()
}))
const audioQualityOptions = computed(() => [
  { value: '0', label: t('settings.fields.audioQualityBest') },
  { value: '2', label: '2' },
  { value: '5', label: '5' },
  { value: '7', label: '7' },
  { value: '9', label: t('settings.fields.audioQualitySmallest') }
])
const containerOptions = ['mp4', 'mkv', 'webm'].map((v) => ({ value: v, label: v.toUpperCase() }))
const videoQualityOptions = computed(() => [
  { value: 'best', label: t('settings.fields.videoQualityBest') },
  { value: '2160', label: '2160p (4K)' },
  { value: '1440', label: '1440p' },
  { value: '1080', label: '1080p' },
  { value: '720', label: '720p' },
  { value: '480', label: '480p' }
])

const showAudio = computed(() => form.value.mode !== 'video')
const showVideo = computed(() => form.value.mode !== 'audio')

function toggleExtraQuality(q: string): void {
  const list = form.value.extraVideoQualities ?? (form.value.extraVideoQualities = [])
  const idx = list.indexOf(q as (typeof list)[number])
  if (idx === -1) list.push(q as (typeof list)[number])
  else list.splice(idx, 1)
}

async function pick(field: 'folder' | 'audioFolder'): Promise<void> {
  const picked = await window.api.settings.pickFolder(
    form.value[field] || settingsStore.settings?.downloadFolder
  )
  if (picked) form.value[field] = picked
}

async function save(): Promise<void> {
  if (!form.value.name.trim()) {
    nameError.value = t('templates.nameRequired')
    return
  }
  await templates.save(form.value)
  showToast(t('templates.saved', { name: form.value.name }))
  router.push({ name: 'templates' })
}
</script>

<template>
  <PageHead
    :title="isNew ? t('templates.createTitle') : t('templates.editTitle', { name: form.name })"
    :sub="t('templates.editSubtitle')"
  >
    <template #actions>
      <BxBtn
        icon="cancel"
        variant="ghost"
        :label="t('common.cancel')"
        @click="router.push({ name: 'templates' })"
      />
      <BxBtn icon="check-in-circle" variant="cta" :label="t('common.save')" @click="save" />
    </template>
  </PageHead>

  <div class="stack stack--lg" style="max-width: 900px">
    <BxCard :title="t('templates.sections.general')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxField
            v-model="form.name"
            :label="t('templates.fields.name')"
            icon="pencil-line"
            :error="nameError || undefined"
            :placeholder="t('templates.namePlaceholder')"
            @update:model-value="nameError = ''"
          />
        </div>
        <div class="col-6">
          <div class="f">
            <div class="f-label">{{ t('download.options.mode') }}</div>
            <BxSegmented v-model="form.mode" :options="modeOptions" />
          </div>
        </div>
        <div class="col-12">
          <BxToggle v-model="form.writeSubtitles" :label="t('settings.fields.writeSubtitles')" />
        </div>
      </div>
    </BxCard>

    <BxCard v-if="showAudio" :title="t('settings.sections.audio')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxSelect
            v-model="form.audioFormat"
            :label="t('settings.fields.audioFormat')"
            icon="music"
            :options="audioFormatOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="form.audioQuality"
            :label="t('settings.fields.audioQuality')"
            icon="setting-horizontal"
            :options="audioQualityOptions"
          />
        </div>
      </div>
    </BxCard>

    <BxCard v-if="showVideo" :title="t('settings.sections.video')">
      <div class="bx-form-grid">
        <div class="col-6">
          <BxSelect
            v-model="form.videoContainer"
            :label="t('settings.fields.videoContainer')"
            icon="video-player"
            :options="containerOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="form.videoQuality"
            :label="t('settings.fields.videoQuality')"
            icon="full-screen"
            :options="videoQualityOptions"
          />
        </div>
        <!-- Zusätzliche Qualitätsstufen (Issue #10) -->
        <div class="col-12">
          <div class="f">
            <div class="f-label">{{ t('download.options.extraQualities') }}</div>
            <div class="row" style="flex-wrap: wrap; gap: 8px">
              <BxChip
                v-for="q in videoQualityOptions"
                :key="q.value"
                :variant="(form.extraVideoQualities ?? []).includes(q.value as never) ? 'marine' : 'neutral'"
                style="cursor: pointer"
                @click="toggleExtraQuality(q.value)"
              >
                {{ q.label }}
              </BxChip>
            </div>
            <div class="f-hint">{{ t('download.options.extraQualitiesHint') }}</div>
          </div>
        </div>
      </div>
    </BxCard>

    <BxCard :title="t('templates.sections.folders')">
      <div class="bx-form-grid">
        <div :class="form.mode === 'both' ? 'col-6' : 'col-12'">
          <BxField
            v-model="form.folder"
            :label="form.mode === 'both' ? t('templates.fields.videoFolder') : t('download.options.folder')"
            icon="folder"
            :placeholder="settingsStore.settings?.downloadFolder ?? ''"
          >
            <template #append>
              <BxBtn
                size="sm"
                variant="outline"
                icon="manage-folder"
                :label="t('settings.fields.browse')"
                @click="pick('folder')"
              />
            </template>
          </BxField>
        </div>
        <div v-if="form.mode === 'both'" class="col-6">
          <BxField
            v-model="form.audioFolder"
            :label="t('templates.fields.audioFolder')"
            icon="folder"
            :placeholder="form.folder || (settingsStore.settings?.downloadFolder ?? '')"
          >
            <template #append>
              <BxBtn
                size="sm"
                variant="outline"
                icon="manage-folder"
                :label="t('settings.fields.browse')"
                @click="pick('audioFolder')"
              />
            </template>
          </BxField>
        </div>
      </div>
    </BxCard>
  </div>
</template>
