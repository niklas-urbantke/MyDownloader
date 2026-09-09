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
  { value: 'audio', label: t('download.options.audio'), icon: 'activity' },
  { value: 'video', label: t('download.options.video'), icon: 'image' },
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
  try {
    await templates.save(form.value)
  } catch (err) {
    // Ohne diesen Zweig bleibt ein fehlgeschlagenes Speichern komplett
    // unsichtbar, der Button „tut nichts“.
    showToast(t('templates.saveFailed', { error: String(err) }), 'error')
    return
  }
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
        icon="x"
        variant="ghost"
        :label="t('common.cancel')"
        @click="router.push({ name: 'templates' })"
      />
      <BxBtn icon="check-circle" variant="primary" :label="t('common.save')" @click="save" />
    </template>
  </PageHead>

  <div class="stack stack--lg form-page">
    <BxCard :title="t('templates.sections.general')">
      <div class="form-grid">
        <div class="col-6">
          <BxField
            v-model="form.name"
            :label="t('templates.fields.name')"
            icon="edit"
            :error="nameError || undefined"
            :placeholder="t('templates.namePlaceholder')"
            @update:model-value="nameError = ''"
          />
        </div>
        <div class="col-6">
          <div class="field">
            <span class="label">{{ t('download.options.mode') }}</span>
            <BxSegmented v-model="form.mode" :options="modeOptions" />
          </div>
        </div>
        <div class="col-12">
          <BxToggle v-model="form.writeSubtitles" :label="t('settings.fields.writeSubtitles')" />
        </div>
      </div>
    </BxCard>

    <BxCard v-if="showAudio" :title="t('settings.sections.audio')">
      <div class="form-grid">
        <div class="col-6">
          <BxSelect
            v-model="form.audioFormat"
            :label="t('settings.fields.audioFormat')"
            icon="activity"
            :options="audioFormatOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="form.audioQuality"
            :label="t('settings.fields.audioQuality')"
            icon="sliders"
            :options="audioQualityOptions"
          />
        </div>
      </div>
    </BxCard>

    <BxCard v-if="showVideo" :title="t('settings.sections.video')">
      <div class="form-grid">
        <div class="col-6">
          <BxSelect
            v-model="form.videoContainer"
            :label="t('settings.fields.videoContainer')"
            icon="image"
            :options="containerOptions"
          />
        </div>
        <div class="col-6">
          <BxSelect
            v-model="form.videoQuality"
            :label="t('settings.fields.videoQuality')"
            icon="maximize"
            :options="videoQualityOptions"
          />
        </div>
        <!-- Zusätzliche Qualitätsstufen (Issue #10) -->
        <div class="col-12">
          <div class="field">
            <span class="label">{{ t('download.options.extraQualities') }}</span>
            <div class="cluster">
              <BxChip
                v-for="q in videoQualityOptions"
                :key="q.value"
                :variant="
                  (form.extraVideoQualities ?? []).includes(q.value as never) ? 'accent' : 'slate'
                "
                class="quality-chip"
                @click="toggleExtraQuality(q.value)"
              >
                {{ q.label }}
              </BxChip>
            </div>
            <span class="help">{{ t('download.options.extraQualitiesHint') }}</span>
          </div>
        </div>
      </div>
    </BxCard>

    <BxCard :title="t('templates.sections.folders')">
      <div class="form-grid">
        <div :class="form.mode === 'both' ? 'col-6' : 'col-12'">
          <BxField
            v-model="form.folder"
            :label="
              form.mode === 'both'
                ? t('templates.fields.videoFolder')
                : t('download.options.folder')
            "
            icon="folder"
            :placeholder="settingsStore.settings?.downloadFolder ?? ''"
          >
            <template #append>
              <BxBtn
                size="sm"
                variant="secondary"
                icon="folder"
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
                variant="secondary"
                icon="folder"
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

<style scoped>
/* Formularseite: begrenzte Zeilenlaenge, damit die Felder nicht
   ueber die volle Fensterbreite laufen. */
.form-page {
  max-width: 56rem;
}

/* Die Qualitaetsstufen sind Schalter, keine reinen Anzeigen. */
.quality-chip {
  cursor: pointer;
}
</style>
