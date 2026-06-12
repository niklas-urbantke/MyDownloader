<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 0–100, -1 = unbestimmt */
    value: number
    variant?: 'marine' | 'apple'
  }>(),
  { variant: 'marine' }
)

const indeterminate = computed(() => props.value < 0)
const width = computed(() => `${Math.min(100, Math.max(0, props.value))}%`)
</script>

<template>
  <div class="bx-progress" :class="`bx-progress--${variant}`">
    <div v-if="indeterminate" class="bx-progress-bar bx-progress-bar--indeterminate" />
    <div v-else class="bx-progress-bar" :style="{ width }" />
  </div>
</template>
