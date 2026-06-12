<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    variant?: 'apple' | 'info' | 'warn'
    icon?: string
  }>(),
  { variant: 'apple' }
)

const effectiveIcon = computed(() => {
  if (props.icon) return props.icon
  if (props.variant === 'info') return 'help-in-circle'
  if (props.variant === 'warn') return 'attention-in-circle'
  return 'information-in-circle'
})
</script>

<template>
  <div class="bx-banner" :class="variant !== 'apple' ? `bx-banner--${variant}` : ''">
    <AppIcon :name="effectiveIcon" />
    <div><slot /></div>
  </div>
</template>
