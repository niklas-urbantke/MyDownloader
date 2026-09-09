<script setup lang="ts">
defineProps<{
  label?: string
  hint?: string
  disabled?: boolean
}>()

const model = defineModel<boolean>({ default: false })
</script>

<template>
  <label class="switch" :class="{ 'is-disabled': disabled }">
    <input v-model="model" type="checkbox" :disabled="disabled" />
    <span class="switch__track" />
    <span v-if="label" class="switch__text">
      <span>{{ label }}</span>
      <span v-if="hint" class="help">{{ hint }}</span>
    </span>
  </label>
</template>
