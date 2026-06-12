<script setup lang="ts">
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    label?: string
    icon?: string
    placeholder?: string
    type?: string
    hint?: string
    error?: string
    readonly?: boolean
    multiline?: boolean
    rows?: number
    disabled?: boolean
  }>(),
  { type: 'text', rows: 4 }
)

const model = defineModel<string>({ default: '' })

defineEmits<{ enter: [] }>()

defineOptions({ inheritAttrs: false })

const displayValue = (): string => model.value || ''
void props
</script>

<template>
  <div class="f">
    <div v-if="label" class="f-label">{{ label }}</div>

    <!-- Read-only: gleiche Silhouette, ruhiger Hintergrund (View-Modus) -->
    <div v-if="readonly" class="f-readonly" :class="{ 'f-readonly--block': multiline }">
      <AppIcon v-if="icon" :name="icon" />
      <span style="white-space: pre-wrap; line-height: 1.5">
        <template v-if="displayValue()">{{ displayValue() }}</template>
        <span v-else style="color: var(--fg3)">—</span>
      </span>
    </div>

    <div
      v-else
      class="f-control"
      :class="{ 'f-control--multiline': multiline, 'f-control--disabled': disabled }"
      :style="error ? { borderColor: '#C10015' } : undefined"
    >
      <AppIcon v-if="icon" :name="icon" />
      <textarea
        v-if="multiline"
        v-model="model"
        :placeholder="placeholder"
        :rows="rows"
        :disabled="disabled"
        v-bind="$attrs"
      />
      <input
        v-else
        v-model="model"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        v-bind="$attrs"
        @keydown.enter="$emit('enter')"
      />
      <slot name="append" />
    </div>

    <div v-if="error || hint" class="f-hint" :class="{ err: !!error }">{{ error || hint }}</div>
  </div>
</template>
