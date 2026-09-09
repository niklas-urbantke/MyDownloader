<script setup lang="ts">
import AppIcon from './AppIcon.vue'

withDefaults(
  defineProps<{
    /** Die Abzeichen-Toene des Baukastens (urbDesign). */
    variant?:
      | 'accent'
      | 'success'
      | 'warning'
      | 'danger'
      | 'slate'
      | 'azure'
      | 'indigo'
      | 'amber'
      | 'jade'
      | 'rose'
    icon?: string
  }>(),
  { variant: 'slate' }
)
</script>

<template>
  <span class="badge" :class="`badge--${variant}`">
    <AppIcon v-if="icon" :name="icon" class="icon--xs" />
    <slot />
  </span>
</template>
