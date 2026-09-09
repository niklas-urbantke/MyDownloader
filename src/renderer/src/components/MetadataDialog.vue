<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MusicBrainzSuggestion, TrackTags } from '@shared/types'
import BxDialog from './BxDialog.vue'
import BxBtn from './BxBtn.vue'
import BxField from './BxField.vue'
import BxSelect from './BxSelect.vue'
import BxChip from './BxChip.vue'
import { showToast } from '../composables/toast'

const props = defineProps<{
  open: boolean
  /** Audio-Dateien, deren Tags bearbeitet werden können */
  files: string[]
}>()

const emit = defineEmits<{ close: [] }>()

const { t } = useI18n()

const emptyTags = (): TrackTags => ({
  title: '',
  artist: '',
  album: '',
  albumArtist: '',
  track: '',
  genre: '',
  date: '',
  comment: ''
})

const selectedFile = ref('')
const tags = ref<TrackTags>(emptyTags())
const coverPath = ref<string | null>(null)
const loading = ref(false)
const saving = ref(false)
const searching = ref(false)
const suggestions = ref<MusicBrainzSuggestion[]>([])

const fileOptions = computed(() =>
  props.files.map((f) => ({ value: f, label: f.split(/[\\/]/).at(-1) ?? f }))
)

watch(
  () => [props.open, props.files] as const,
  async ([open]) => {
    if (!open) return
    suggestions.value = []
    coverPath.value = null
    selectedFile.value = props.files[0] ?? ''
  },
  { immediate: true }
)

watch(selectedFile, async (file) => {
  if (!file) return
  loading.value = true
  suggestions.value = []
  coverPath.value = null
  try {
    tags.value = await window.api.metadata.read(file)
  } finally {
    loading.value = false
  }
})

async function searchMusicBrainz(): Promise<void> {
  if (!tags.value.title && !tags.value.artist) return
  searching.value = true
  try {
    suggestions.value = await window.api.metadata.searchMusicBrainz(
      tags.value.artist,
      tags.value.title
    )
    if (suggestions.value.length === 0) showToast(t('metadata.noSuggestions'), 'info')
  } finally {
    searching.value = false
  }
}

function applySuggestion(s: MusicBrainzSuggestion): void {
  tags.value.title = s.title || tags.value.title
  tags.value.artist = s.artist || tags.value.artist
  if (s.album) tags.value.album = s.album
  if (s.date) tags.value.date = s.date
}

async function pickCover(): Promise<void> {
  const picked = await window.api.metadata.pickImage()
  if (picked) coverPath.value = picked
}

async function save(applyAlbumToAll = false): Promise<void> {
  if (!selectedFile.value) return
  saving.value = true
  try {
    const result = await window.api.metadata.write(selectedFile.value, tags.value, coverPath.value)
    if (!result.ok) {
      showToast(t('metadata.saveFailed', { msg: result.message }), 'error')
      return
    }
    // Optional Album/Künstler/Genre auf alle weiteren Dateien übertragen
    if (applyAlbumToAll) {
      for (const file of props.files) {
        if (file === selectedFile.value) continue
        const existing = await window.api.metadata.read(file)
        await window.api.metadata.write(
          file,
          {
            ...existing,
            artist: tags.value.artist || existing.artist,
            album: tags.value.album || existing.album,
            albumArtist: tags.value.albumArtist || existing.albumArtist,
            genre: tags.value.genre || existing.genre,
            date: tags.value.date || existing.date
          },
          coverPath.value
        )
      }
    }
    showToast(t('metadata.saved'))
    emit('close')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <BxDialog :open="open" :title="t('metadata.title')" wide @close="emit('close')">
    <div class="stack dialog-body">
      <BxSelect
        v-if="files.length > 1"
        v-model="selectedFile"
        :label="t('metadata.file')"
        icon="activity"
        :options="fileOptions"
      />

      <div v-if="loading" class="cluster text-secondary">
        <span class="spinner" aria-hidden="true" />
        <span>{{ t('common.loading') }}</span>
      </div>

      <template v-else>
        <div class="form-grid">
          <div class="col-6">
            <BxField v-model="tags.title" :label="t('metadata.fields.title')" icon="edit" />
          </div>
          <div class="col-6">
            <BxField v-model="tags.artist" :label="t('metadata.fields.artist')" icon="user" />
          </div>
          <div class="col-6">
            <BxField v-model="tags.album" :label="t('metadata.fields.album')" icon="layout" />
          </div>
          <div class="col-6">
            <BxField
              v-model="tags.albumArtist"
              :label="t('metadata.fields.albumArtist')"
              icon="users"
            />
          </div>
          <div class="col-4">
            <BxField v-model="tags.track" :label="t('metadata.fields.track')" icon="list" />
          </div>
          <div class="col-4">
            <BxField v-model="tags.genre" :label="t('metadata.fields.genre')" icon="tag" />
          </div>
          <div class="col-4">
            <BxField v-model="tags.date" :label="t('metadata.fields.year')" icon="calendar" />
          </div>
        </div>

        <!-- Cover -->
        <div class="cluster">
          <BxBtn
            icon="image"
            variant="secondary"
            size="sm"
            :label="t('metadata.pickCover')"
            @click="pickCover"
          />
          <BxChip v-if="coverPath" icon="check-circle" variant="success">
            {{ coverPath.split(/[\\/]/).at(-1) }}
          </BxChip>
        </div>

        <!-- MusicBrainz -->
        <div class="stack stack--sm">
          <div class="cluster">
            <BxBtn
              icon="search"
              variant="secondary"
              size="sm"
              :label="t('metadata.searchMusicBrainz')"
              :disabled="searching || (!tags.title && !tags.artist)"
              @click="searchMusicBrainz"
            />
          </div>
          <table v-if="suggestions.length > 0" class="table table--plain">
            <tbody>
              <tr v-for="(s, i) in suggestions" :key="i">
                <td>
                  <strong>{{ s.artist }}</strong> — {{ s.title }}
                  <span v-if="s.album" class="text-secondary"> · {{ s.album }}</span>
                  <span v-if="s.date" class="text-secondary"> ({{ s.date }})</span>
                </td>
                <td class="suggestion-action">
                  <BxBtn
                    size="sm"
                    variant="ghost"
                    icon="check-circle"
                    :label="t('metadata.apply')"
                    @click="applySuggestion(s)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <template #actions>
      <BxBtn variant="ghost" :label="t('common.cancel')" @click="emit('close')" />
      <BxBtn
        v-if="files.length > 1"
        variant="secondary"
        icon="list"
        :label="t('metadata.saveAll')"
        :disabled="saving || loading"
        @click="save(true)"
      />
      <BxBtn
        variant="primary"
        icon="check-circle"
        :label="t('common.save')"
        :disabled="saving || loading"
        @click="save(false)"
      />
    </template>
  </BxDialog>
</template>

<style scoped>
/* Der Dialog darf nicht an langen Dateinamen aufgehen. */
.dialog-body {
  min-width: 0;
}

.suggestion-action {
  width: 7.5rem;
  text-align: end;
}
</style>
