<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    subtitle?: string
    padded?: boolean
  }>(),
  { padded: true }
)
</script>

<template>
  <div class="bx-card">
    <div v-if="title || $slots.action" class="bx-card-head">
      <div>
        <h3 v-if="title" class="bx-card-title">{{ title }}</h3>
        <div v-if="subtitle" class="bx-card-sub">{{ subtitle }}</div>
      </div>
      <slot name="action" />
    </div>
    <div v-if="padded" class="bx-card-section"><slot /></div>
    <slot v-else />
  </div>
</template>
