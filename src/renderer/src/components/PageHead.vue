<script setup lang="ts">
defineProps<{
  title: string
  sub?: string
}>()
</script>

<template>
  <div class="page-head">
    <div class="page-head__text">
      <h1 class="page-head__title">{{ title }}</h1>
      <p v-if="sub" class="page-head__sub">{{ sub }}</p>
    </div>
    <div v-if="$slots.actions" class="page-head__actions">
      <slot name="actions" />
    </div>
  </div>
</template>
