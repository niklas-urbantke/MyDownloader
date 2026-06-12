<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

export interface SelectOption {
  value: string
  label: string
}

const props = defineProps<{
  label?: string
  icon?: string
  options: SelectOption[]
  readonly?: boolean
  hint?: string
}>()

const model = defineModel<string>({ default: '' })

const currentLabel = computed(
  () => props.options.find((o) => o.value === model.value)?.label ?? '—'
)
</script>

<template>
  <div class="f">
    <div v-if="label" class="f-label">{{ label }}</div>

    <div v-if="readonly" class="f-readonly">
      <AppIcon v-if="icon" :name="icon" />
      <span>{{ currentLabel }}</span>
    </div>

    <!-- Select liegt als Overlay über der gesamten Box — komplette Fläche klickbar -->
    <div v-else class="f-control f-control--select" :class="{ 'has-icon': !!icon }">
      <AppIcon v-if="icon" :name="icon" class="f-deco" />
      <select v-model="model">
        <option v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}</option>
      </select>
      <AppIcon name="arrow-down" class="f-deco f-deco--arrow" />
    </div>

    <div v-if="hint" class="f-hint">{{ hint }}</div>
  </div>
</template>
