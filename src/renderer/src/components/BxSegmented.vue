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
  <div class="segmented" role="group">
    <button
      v-for="o in options"
      :key="o.value"
      class="segmented__item"
      :class="{ 'is-selected': o.value === model }"
      :aria-pressed="o.value === model"
      type="button"
      @click="model = o.value"
    >
      <AppIcon v-if="o.icon" :name="o.icon" class="icon--sm" />
      <span>{{ o.label }}</span>
    </button>
  </div>
</template>
