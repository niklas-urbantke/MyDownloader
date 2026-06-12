<script setup lang="ts">
// Batix-Icon-Font: <AppIcon name="download" /> → <i class="bxfr bxf-download" />
defineProps<{
  name: string
  size?: number
}>()
</script>

<template>
  <i
    class="bxfr"
    :class="`bxf-${name}`"
    :style="size ? { fontSize: `${size}px` } : undefined"
    aria-hidden="true"
  />
</template>
