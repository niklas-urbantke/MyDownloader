<script setup lang="ts">
defineProps<{
  title: string
  sub?: string
}>()
</script>

<template>
  <div class="bx-page-head">
    <div class="left">
      <h1 class="bx-page-title">{{ title }}</h1>
      <p v-if="sub" class="bx-page-sub">{{ sub }}</p>
    </div>
    <div v-if="$slots.actions" class="right">
      <slot name="actions" />
    </div>
  </div>
</template>
