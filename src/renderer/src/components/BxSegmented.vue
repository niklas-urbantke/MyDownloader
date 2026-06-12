<script setup lang="ts">
import AppIcon from './AppIcon.vue'

export interface SegmentOption {
  value: string
  label: string
  icon?: string
}

defineProps<{ options: SegmentOption[] }>()

const model = defineModel<string>({ required: true })
</script>

<template>
  <div class="bx-seg">
    <button
      v-for="o in options"
      :key="o.value"
      :class="{ active: o.value === model }"
      type="button"
      @click="model = o.value"
    >
      <AppIcon v-if="o.icon" :name="o.icon" />
      <span>{{ o.label }}</span>
    </button>
  </div>
</template>
