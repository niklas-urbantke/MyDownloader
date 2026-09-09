<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 0-100, -1 = unbestimmt */
    value: number
    variant?: 'accent' | 'success'
  }>(),
  { variant: 'accent' }
)

const indeterminate = computed(() => props.value < 0)
const width = computed(() => `${Math.min(100, Math.max(0, props.value))}%`)
</script>

<template>
  <div
    class="progress"
    :class="[indeterminate ? 'progress--indeterminate' : '', `progress--${variant}`]"
    role="progressbar"
  >
    <div class="progress__bar" :style="indeterminate ? undefined : { width }" />
  </div>
</template>
