<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    /** Die Hinweis-Arten des Baukastens (urbDesign). */
    variant?: 'success' | 'info' | 'warning' | 'danger'
    icon?: string
  }>(),
  { variant: 'success' }
)

const effectiveIcon = computed(() => {
  if (props.icon) return props.icon
  if (props.variant === 'info') return 'info'
  if (props.variant === 'warning') return 'alert-triangle'
  if (props.variant === 'danger') return 'x-circle'
  return 'check-circle'
})
</script>

<template>
  <div class="alert" :class="`alert--${variant}`">
    <span class="alert__icon"><AppIcon :name="effectiveIcon" /></span>
    <div><slot /></div>
  </div>
</template>
