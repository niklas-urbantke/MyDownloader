<script setup lang="ts">
defineProps<{
  label?: string
  hint?: string
  disabled?: boolean
}>()

const model = defineModel<boolean>({ default: false })

function toggle(): void {
  model.value = !model.value
}
</script>

<template>
  <div class="sw-row" :class="{ 'sw-row--disabled': disabled }">
    <div
      class="toggle"
      :class="{ on: model }"
      role="switch"
      :aria-checked="model"
      tabindex="0"
      @click="!disabled && toggle()"
      @keydown.space.prevent="!disabled && toggle()"
      @keydown.enter.prevent="!disabled && toggle()"
    />
    <div v-if="label" class="sw-text" @click="!disabled && toggle()">
      <span class="sw-label">{{ label }}</span>
      <span v-if="hint" class="sw-hint">{{ hint }}</span>
    </div>
  </div>
</template>
