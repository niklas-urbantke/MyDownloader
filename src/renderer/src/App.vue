<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from './components/AppIcon.vue'
import AppLogo from './components/AppLogo.vue'
import ToastHost from './components/ToastHost.vue'
import OnboardingDialog from './components/OnboardingDialog.vue'
import { showToast } from './composables/toast'
import { useSettingsStore } from './stores/settings'
import { useDownloadsStore } from './stores/downloads'
import { useHistoryStore } from './stores/history'
import { useTemplatesStore } from './stores/templates'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const settingsStore = useSettingsStore()
const downloadsStore = useDownloadsStore()
const historyStore = useHistoryStore()
const templatesStore = useTemplatesStore()

onMounted(async () => {
  await settingsStore.load()
  await Promise.all([downloadsStore.load(), historyStore.load(), templatesStore.load()])

  // Seitenleiste standardmäßig eingeblendet; Zustand wird gemerkt (Issue #12)
  navOpen.value = settingsStore.settings?.sidebarOpen ?? true
  watch(navOpen, (open) => {
    if (settingsStore.settings) settingsStore.settings.sidebarOpen = open
  })

  // Einrichtungsassistent beim ersten Start (Issue #31)
  showOnboarding.value = !(settingsStore.settings?.onboardingDone ?? true)
  watch(
    () => settingsStore.settings?.onboardingDone,
    (done) => {
      if (done === false) showOnboarding.value = true
    }
  )

  // Clipboard-Watcher: erkannte Video-URL als Toast mit Direkt-Aktion anbieten
  window.api.clipboard.onUrlDetected((url) => {
    showToast(t('clipboard.detected'), 'info', {
      actionLabel: t('clipboard.download'),
      onAction: () => {
        void downloadsStore.add({ url, startNow: true })
        router.push({ name: 'queue' })
      }
    })
  })

  // yt-dlp-Wartung beim Start: gemeldet wird nur, wenn wirklich etwas ansteht
  window.api.system.onYtDlpEvent((info) => {
    if (info.updated) {
      showToast(t('settings.binaries.autoUpdated', { v: info.current ?? '' }), 'info')
    } else if (info.latest && info.current) {
      showToast(
        t('settings.binaries.autoOutdated', { current: info.current, latest: info.latest }),
        'error',
        {
          actionLabel: t('settings.binaries.updateYtDlp'),
          onAction: () => router.push({ name: 'settings' })
        }
      )
    }
  })
})

// Sidenav-Zustand kommt aus den Einstellungen (Default: eingeblendet, Issue #12)
const navOpen = ref(true)
const showOnboarding = ref(false)

interface NavItem {
  route: string
  icon: string
  labelKey: string
}

const navGroups = computed(() => [
  {
    label: t('nav.sections.main'),
    items: [
      { route: 'dashboard', icon: 'grid-layout', labelKey: 'nav.dashboard' },
      { route: 'download', icon: 'download', labelKey: 'nav.download' },
      { route: 'queue', icon: 'checklist', labelKey: 'nav.queue' },
      { route: 'templates', icon: 'layout', labelKey: 'nav.templates' },
      { route: 'subscriptions', icon: 'reload', labelKey: 'nav.subscriptions' },
      { route: 'spotify', icon: 'music', labelKey: 'nav.spotify' },
      { route: 'history', icon: 'time', labelKey: 'nav.history' },
      { route: 'stats', icon: 'statistic', labelKey: 'nav.stats' }
    ] as NavItem[]
  },
  {
    label: t('nav.sections.system'),
    items: [
      { route: 'settings', icon: 'setting', labelKey: 'nav.settings' },
      { route: 'about', icon: 'help-in-circle', labelKey: 'nav.about' }
    ] as NavItem[]
  }
])

const breadcrumb = computed(() => {
  const name = String(route.name ?? 'dashboard')
  if (name === 'dashboard') return [{ label: t('nav.dashboard') }]
  if (name === 'template-edit') {
    return [
      { label: t('nav.dashboard'), route: 'dashboard' },
      { label: t('nav.templates'), route: 'templates' },
      { label: route.params.id === 'new' ? t('templates.create') : t('common.edit') }
    ]
  }
  return [{ label: t('nav.dashboard'), route: 'dashboard' }, { label: t(`nav.${name}`) }]
})

function go(name: string): void {
  router.push({ name })
}

// --- Drag & Drop für Links und URL-Listen (Issue #17) ---
const dragOver = ref(false)
let dragDepth = 0

function onDragEnter(e: DragEvent): void {
  e.preventDefault()
  dragDepth++
  dragOver.value = true
}

function onDragLeave(): void {
  dragDepth--
  if (dragDepth <= 0) {
    dragDepth = 0
    dragOver.value = false
  }
}

const pickUrls = (text: string): string[] =>
  text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => /^https?:\/\//.test(l))

async function onDrop(e: DragEvent): Promise<void> {
  e.preventDefault()
  dragDepth = 0
  dragOver.value = false
  const dt = e.dataTransfer
  if (!dt) return

  const urls: string[] = []
  const dropped = dt.getData('text/uri-list') || dt.getData('text/plain')
  if (dropped) urls.push(...pickUrls(dropped))
  // Textdateien mit einer URL pro Zeile → Batch-Import
  for (const file of Array.from(dt.files ?? [])) {
    if (file.name.toLowerCase().endsWith('.txt') || file.type === 'text/plain') {
      urls.push(...pickUrls(await file.text()))
    }
  }

  const unique = [...new Set(urls)]
  if (unique.length === 0) {
    showToast(t('dragdrop.nothing'), 'info')
    return
  }
  await downloadsStore.addMany(unique.map((url) => ({ url })))
  showToast(t('download.addedMany', { n: unique.length }))
  router.push({ name: 'queue' })
}
</script>

<template>
  <div
    class="bx-root"
    @dragenter="onDragEnter"
    @dragover.prevent
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <!-- Sidenav: standardmäßig komplett ausgeblendet (Breite 0) -->
    <nav class="bx-nav" :class="{ open: navOpen }">
      <div class="bx-nav-brand">
        <AppLogo :size="30" wordmark inverse />
      </div>
      <div class="bx-nav-list">
        <div v-for="(group, gi) in navGroups" :key="gi">
          <div class="bx-nav-section-label">{{ group.label }}</div>
          <div
            v-for="item in group.items"
            :key="item.route"
            class="bx-nav-item"
            :class="{ active: route.name === item.route }"
            :title="t(item.labelKey)"
            @click="go(item.route)"
          >
            <AppIcon :name="item.icon" />
            <span class="label">{{ t(item.labelKey) }}</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="bx-main">
      <header class="bx-header">
        <div
          class="bx-header-toggle"
          :title="t('nav.menu')"
          role="button"
          tabindex="0"
          @click="navOpen = !navOpen"
          @keydown.enter="navOpen = !navOpen"
        >
          <AppIcon name="side-nav" />
        </div>
        <div class="bx-breadcrumb">
          <template v-for="(crumb, i) in breadcrumb" :key="i">
            <span
              v-if="i < breadcrumb.length - 1"
              class="crumb"
              @click="crumb.route && go(crumb.route)"
              >{{ crumb.label }}</span
            >
            <span v-if="i < breadcrumb.length - 1" class="sep">/</span>
            <span v-else class="here">{{ crumb.label }}</span>
          </template>
        </div>
        <div class="row" style="gap: 10px">
          <button
            v-if="downloadsStore.activeItems.length > 0"
            class="bx-header-chip"
            type="button"
            @click="go('queue')"
          >
            <AppIcon name="download" />
            <span>{{
              t('dashboard.badges.active', { n: downloadsStore.activeItems.length })
            }}</span>
          </button>
          <button class="bx-header-chip" type="button" @click="go('download')">
            <AppIcon name="add" />
            <span>{{ t('nav.download') }}</span>
          </button>
        </div>
      </header>

      <main class="bx-page">
        <router-view />
      </main>
    </div>

    <ToastHost />
    <OnboardingDialog :open="showOnboarding" @close="showOnboarding = false" />

    <!-- Drop-Zone-Overlay (Issue #17) -->
    <div v-if="dragOver" class="drop-overlay">
      <div class="drop-overlay-inner">
        <AppIcon name="download" :size="48" />
        <p>{{ t('dragdrop.hint') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drop-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 48, 99, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.drop-overlay-inner {
  background: var(--bg1, #fff);
  color: var(--marine, #003063);
  border: 3px dashed var(--marine, #003063);
  border-radius: 16px;
  padding: 48px 64px;
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
}
</style>
