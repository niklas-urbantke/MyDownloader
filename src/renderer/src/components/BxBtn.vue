<script setup lang="ts">
import AppIcon from './AppIcon.vue'

withDefaults(
  defineProps<{
    label?: string
    icon?: string
    iconRight?: string
    /** Die Schaltflaechen-Arten des Baukastens (urbDesign). */
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'glass'
    size?: 'sm' | 'lg'
    disabled?: boolean
    type?: 'button' | 'submit'
  }>(),
  { variant: 'primary', type: 'button' }
)

defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <button
    class="btn"
    :class="[
      `btn--${variant}`,
      size ? `btn--${size}` : '',
      !label && !$slots.default ? 'btn--icon' : ''
    ]"
    :type="type"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <AppIcon v-if="icon" :name="icon" class="icon--sm" />
    <span v-if="label || $slots.default"><slot>{{ label }}</slot></span>
    <AppIcon v-if="iconRight" :name="iconRight" class="icon--sm" />
  </button>
</template>
