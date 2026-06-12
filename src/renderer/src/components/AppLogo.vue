<script setup lang="ts">
// Eigenes neutrales App-Logo (bewusst keine Batix-Wortmarke):
// abgerundetes Marine-Quadrat mit Apple-grünem Download-Pfeil in eine Ablage.
withDefaults(
  defineProps<{
    size?: number
    /** Wortmarke "MyDownloader" daneben anzeigen */
    wordmark?: boolean
    /** Für dunkle Flächen (Sidenav): Wortmarke in Weiß */
    inverse?: boolean
  }>(),
  { size: 32 }
)
</script>

<template>
  <span class="app-logo" :style="{ gap: wordmark ? '10px' : '0' }">
    <svg
      :width="size"
      :height="size"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="64" height="64" rx="14" :fill="inverse ? '#FFFFFF' : '#003063'" />
      <path
        d="M32 12v24M32 36l-10-10M32 36l10-10"
        stroke="#8FC01A"
        stroke-width="6"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M16 44v4a4 4 0 0 0 4 4h24a4 4 0 0 0 4-4v-4"
        :stroke="inverse ? '#003063' : '#FFFFFF'"
        stroke-width="5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <span
      v-if="wordmark"
      class="app-logo-word"
      :style="{ color: inverse ? '#FFFFFF' : 'var(--marine)' }"
      >MyDownloader</span
    >
  </span>
</template>

<style scoped>
.app-logo {
  display: inline-flex;
  align-items: center;
}
.app-logo-word {
  font-family: var(--font-h);
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: -0.01em;
  white-space: nowrap;
}
</style>
