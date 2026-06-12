<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from './components/AppIcon.vue'
import AppLogo from './components/AppLogo.vue'
import ToastHost from './components/ToastHost.vue'
import { showToast } from './composables/toast'
import { useSettingsStore } from './stores/settings'
import { useDownloadsStore } from './stores/downloads'
import { useHistoryStore } from './stores/history'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const settingsStore = useSettingsStore()
const downloadsStore = useDownloadsStore()
const historyStore = useHistoryStore()

onMounted(async () => {
  await settingsStore.load()
  await Promise.all([downloadsStore.load(), historyStore.load()])

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
})

// Sidenav ist standardmäßig eingeklappt — Inhalt nutzt die volle Breite.
const navOpen = ref(false)

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
      { route: 'history', icon: 'time', labelKey: 'nav.history' }
    ] as NavItem[]
  },
  {
    label: t('nav.sections.system'),
    // Info bewusst nur im Footer — keine Dopplung in der Liste (Issue #5)
    items: [{ route: 'settings', icon: 'setting', labelKey: 'nav.settings' }] as NavItem[]
  }
])

const breadcrumb = computed(() => {
  const name = String(route.name ?? 'dashboard')
  if (name === 'dashboard') return [{ label: t('nav.dashboard') }]
  return [{ label: t('nav.dashboard'), route: 'dashboard' }, { label: t(`nav.${name}`) }]
})

function go(name: string): void {
  router.push({ name })
}
</script>

<template>
  <div class="bx-root">
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
      <div class="bx-nav-footer">
        <div class="bx-nav-item" @click="go('about')">
          <AppIcon name="help-in-circle" />
          <span class="label">{{ t('nav.about') }}</span>
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
  </div>
</template>
