<script setup lang="ts">
// Icon aus dem urbDesign-Sprite: <AppIcon name="download" />
// Das Sprite ist in index.html eingebettet, damit currentColor und die
// Verlaufs-Striche greifen. Die Namen sind die <symbol id="..."> aus
// design/icons.svg.
defineProps<{
  name: string
  /** Kantenlaenge in Pixeln. Ohne Angabe gilt die Groesse aus dem Baukasten. */
  size?: number
}>()
</script>

<template>
  <svg
    class="icon"
    :style="size ? { '--icon-size': `${size}px` } : undefined"
    aria-hidden="true"
    focusable="false"
  >
    <use :href="`#${name}`" />
  </svg>
</template>
