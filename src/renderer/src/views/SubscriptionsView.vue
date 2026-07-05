<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Subscription } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxBtn from '../components/BxBtn.vue'
import BxField from '../components/BxField.vue'
import BxSelect from '../components/BxSelect.vue'
import BxChip from '../components/BxChip.vue'
import BxToggle from '../components/BxToggle.vue'
import BxDialog from '../components/BxDialog.vue'
import AppIcon from '../components/AppIcon.vue'
import { useTemplatesStore } from '../stores/templates'
import { useSettingsStore } from '../stores/settings'
import { showToast } from '../composables/toast'
import { formatDateTime, isHttpUrl } from '../utils/format'

const { t, locale } = useI18n()
const templates = useTemplatesStore()
const settingsStore = useSettingsStore()

const subs = ref<Subscription[]>([])
const adding = ref(false)
const checkingId = ref('')
const deleteTarget = ref<Subscription | null>(null)

// Formular für ein neues Abo
const newUrl = ref('')
const newFolder = ref('')
const newTemplateId = ref('')
const newInterval = ref('360')

let unsub: (() => void) | null = null

onMounted(async () => {
  subs.value = await window.api.subscriptions.list()
  unsub = window.api.subscriptions.onChanged((list) => {
    subs.value = list
  })
})

onUnmounted(() => unsub?.())

const intervalOptions = computed(() => [
  { value: '60', label: t('subscriptions.interval.hourly') },
  { value: '360', label: t('subscriptions.interval.sixHours') },
  { value: '720', label: t('subscriptions.interval.twelveHours') },
  { value: '1440', label: t('subscriptions.interval.daily') }
])

const templateOptions = computed(() => [
  { value: '', label: t('templates.manual') },
  ...templates.entries.map((tp) => ({ value: tp.id, label: tp.name }))
])

async function pickFolder(): Promise<void> {
  const picked = await window.api.settings.pickFolder(
    newFolder.value || settingsStore.settings?.downloadFolder
  )
  if (picked) newFolder.value = picked
}

async function addSubscription(): Promise<void> {
  if (!isHttpUrl(newUrl.value)) return
  adding.value = true
  try {
    await window.api.subscriptions.add(newUrl.value.trim(), {
      folder: newFolder.value || undefined,
      templateId: newTemplateId.value || undefined,
      intervalMinutes: Number.parseInt(newInterval.value, 10)
    })
    subs.value = await window.api.subscriptions.list()
    showToast(t('subscriptions.added'))
    newUrl.value = ''
    newFolder.value = ''
    newTemplateId.value = ''
  } catch (err) {
    showToast(
      t('subscriptions.addFailed', {
        msg: err instanceof Error ? err.message.split('\n')[0] : String(err)
      }),
      'error'
    )
  } finally {
    adding.value = false
  }
}

async function checkNow(sub: Subscription): Promise<void> {
  checkingId.value = sub.id
  try {
    const found = await window.api.subscriptions.checkNow(sub.id)
    showToast(
      found > 0 ? t('subscriptions.foundNew', { n: found }) : t('subscriptions.nothingNew')
    )
    subs.value = await window.api.subscriptions.list()
  } finally {
    checkingId.value = ''
  }
}

async function toggleEnabled(sub: Subscription, enabled: boolean): Promise<void> {
  await window.api.subscriptions.update({ id: sub.id, enabled })
}

async function setInterval(sub: Subscription, value: string): Promise<void> {
  await window.api.subscriptions.update({ id: sub.id, intervalMinutes: Number.parseInt(value, 10) })
}

async function confirmDelete(): Promise<void> {
  if (!deleteTarget.value) return
  await window.api.subscriptions.remove(deleteTarget.value.id)
  subs.value = await window.api.subscriptions.list()
  deleteTarget.value = null
}
</script>

<template>
  <PageHead :title="t('subscriptions.title')" :sub="t('subscriptions.subtitle')" />

  <div class="stack stack--lg">
    <!-- Neues Abo -->
    <BxCard :title="t('subscriptions.addTitle')">
      <div class="bx-form-grid">
        <div class="col-12">
          <BxField
            v-model="newUrl"
            icon="link"
            :label="t('subscriptions.fields.url')"
            :placeholder="t('subscriptions.fields.urlPlaceholder')"
            @enter="addSubscription"
          />
        </div>
        <div class="col-4">
          <BxField v-model="newFolder" :label="t('download.options.folder')" icon="folder"
            :placeholder="settingsStore.settings?.downloadFolder ?? ''">
            <template #append>
              <BxBtn size="sm" variant="outline" icon="manage-folder"
                :label="t('settings.fields.browse')" @click="pickFolder" />
            </template>
          </BxField>
        </div>
        <div class="col-4">
          <BxSelect
            v-model="newTemplateId"
            :label="t('templates.useTemplate')"
            icon="layout"
            :options="templateOptions"
          />
        </div>
        <div class="col-4">
          <BxSelect
            v-model="newInterval"
            :label="t('subscriptions.fields.interval')"
            icon="time"
            :options="intervalOptions"
          />
        </div>
        <div class="col-12">
          <div class="row">
            <span class="spacer" />
            <BxBtn
              icon="add"
              variant="cta"
              :label="t('subscriptions.add')"
              :disabled="!isHttpUrl(newUrl) || adding"
              @click="addSubscription"
            />
          </div>
        </div>
      </div>
    </BxCard>

    <!-- Bestehende Abos -->
    <div v-if="subs.length === 0" class="bx-card">
      <div class="bx-card-section" style="color: var(--fg2); text-align: center; padding: 48px">
        <AppIcon name="replay" :size="40" style="color: var(--marine-40)" />
        <p>{{ t('subscriptions.empty') }}</p>
      </div>
    </div>

    <div v-else class="stack">
      <BxCard v-for="sub in subs" :key="sub.id" :padded="false">
        <div class="bx-card-section">
          <div class="row" style="gap: 16px; flex-wrap: wrap; align-items: center">
            <div class="stack stack--sm" style="flex: 1; min-width: 260px">
              <div class="row" style="gap: 10px; flex-wrap: wrap">
                <strong style="font-size: 1rem; color: var(--marine)">{{ sub.title }}</strong>
                <BxChip v-if="!sub.enabled" variant="warn">{{ t('subscriptions.pausedChip') }}</BxChip>
                <BxChip v-if="sub.lastNewCount > 0" variant="apple">
                  {{ t('subscriptions.newChip', { n: sub.lastNewCount }) }}
                </BxChip>
              </div>
              <div style="color: var(--fg2); font-size: 12px">
                {{ sub.knownVideoIds.length }} {{ t('subscriptions.knownVideos') }}
                <template v-if="sub.lastCheckedAt">
                  · {{ t('subscriptions.lastChecked', { when: formatDateTime(sub.lastCheckedAt, locale) }) }}
                </template>
                <template v-if="sub.folder"> · {{ sub.folder }}</template>
              </div>
            </div>
            <div style="width: 160px">
              <BxSelect
                :model-value="String(sub.intervalMinutes)"
                icon="time"
                :options="intervalOptions"
                @update:model-value="(v: string) => setInterval(sub, v)"
              />
            </div>
            <BxToggle
              :model-value="sub.enabled"
              :label="t('subscriptions.enabled')"
              @update:model-value="(v: boolean) => toggleEnabled(sub, v)"
            />
            <BxBtn
              icon="reload"
              variant="outline"
              size="sm"
              :label="t('subscriptions.checkNow')"
              :disabled="checkingId === sub.id"
              @click="checkNow(sub)"
            />
            <BxBtn
              icon="trash"
              variant="ghost"
              size="sm"
              :title="t('common.delete')"
              @click="deleteTarget = sub"
            />
          </div>
        </div>
      </BxCard>
    </div>
  </div>

  <BxDialog
    :open="!!deleteTarget"
    :title="t('subscriptions.deleteTitle')"
    @close="deleteTarget = null"
  >
    {{ t('subscriptions.deleteQuestion', { name: deleteTarget?.title ?? '' }) }}
    <template #actions>
      <BxBtn variant="ghost" :label="t('common.cancel')" @click="deleteTarget = null" />
      <BxBtn variant="danger" icon="trash" :label="t('common.delete')" @click="confirmDelete" />
    </template>
  </BxDialog>
</template>
