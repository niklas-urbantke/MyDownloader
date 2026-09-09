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
  <div class="field">
    <span v-if="label" class="label">{{ label }}</span>

    <!-- Nur lesen: gleiche Silhouette wie ein Feld, ruhiger Inhalt -->
    <div
      v-if="readonly"
      class="input field__static"
      :class="{ 'field__static--block': multiline }"
    >
      <AppIcon v-if="icon" :name="icon" class="icon--sm" />
      <span>
        <template v-if="displayValue()">{{ displayValue() }}</template>
        <span v-else class="text-muted">&mdash;</span>
      </span>
    </div>

    <div
      v-else
      class="field__group"
      :class="{ 'field__group--icon': !!icon, 'field__group--multiline': multiline }"
    >
      <AppIcon v-if="icon" :name="icon" class="icon--sm" />
      <textarea
        v-if="multiline"
        v-model="model"
        class="textarea"
        :class="{ 'input--error': !!error }"
        :placeholder="placeholder"
        :rows="rows"
        :disabled="disabled"
        v-bind="$attrs"
      />
      <input
        v-else
        v-model="model"
        class="input"
        :class="{ 'input--error': !!error }"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        v-bind="$attrs"
        @keydown.enter="$emit('enter')"
      />
      <span v-if="$slots.append" class="field__append"><slot name="append" /></span>
    </div>

    <span v-if="error || hint" class="help" :class="{ 'help--error': !!error }">
      {{ error || hint }}
    </span>
  </div>
</template>
