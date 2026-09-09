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
  <div class="field">
    <span v-if="label" class="label">{{ label }}</span>

    <div v-if="readonly" class="input field__static">
      <AppIcon v-if="icon" :name="icon" class="icon--sm" />
      <span>{{ currentLabel }}</span>
    </div>

    <div v-else class="field__group" :class="{ 'field__group--icon': !!icon }">
      <AppIcon v-if="icon" :name="icon" class="icon--sm" />
      <select v-model="model" class="select">
        <option v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}</option>
      </select>
    </div>

    <span v-if="hint" class="help">{{ hint }}</span>
  </div>
</template>
