<script setup lang="ts">
// Eigenes App-Zeichen: abgerundetes Quadrat im Akzentton mit einem
// Download-Pfeil in eine Ablage. Alle Farben kommen aus den Tokens,
// damit das Zeichen jedem der vier Themes folgt.
withDefaults(
  defineProps<{
    size?: number
    /** Wortmarke "MyDownloader" daneben anzeigen */
    wordmark?: boolean
  }>(),
  { size: 32 }
)
</script>

<template>
  <span class="app-logo" :style="{ gap: wordmark ? 'var(--space-3)' : '0' }">
    <svg
      :width="size"
      :height="size"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect width="64" height="64" rx="14" fill="var(--color-accent)" />
      <path
        d="M32 12v24M32 36l-10-10M32 36l10-10"
        stroke="var(--color-on-accent)"
        stroke-width="6"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M16 44v4a4 4 0 0 0 4 4h24a4 4 0 0 0 4-4v-4"
        stroke="var(--color-on-accent)"
        stroke-width="5"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.75"
      />
    </svg>
    <span v-if="wordmark" class="app-logo__word">MyDownloader</span>
  </span>
</template>
