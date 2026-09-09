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
  <div class="card">
    <div v-if="title || $slots.action" class="card__header spread">
      <div>
        <h3 v-if="title">{{ title }}</h3>
        <p v-if="subtitle" class="help">{{ subtitle }}</p>
      </div>
      <slot name="action" />
    </div>
    <div v-if="padded" class="card__body"><slot /></div>
    <slot v-else />
  </div>
</template>
