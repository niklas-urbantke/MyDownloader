<script setup lang="ts">
import AppIcon from './AppIcon.vue'

defineProps<{
  variant?: 'apple' | 'marine' | 'outline' | 'neg' | 'neutral' | 'warn'
  icon?: string
}>()
</script>

<template>
  <span class="chip" :class="variant ? `chip--${variant}` : ''">
    <AppIcon v-if="icon" :name="icon" />
    <slot />
  </span>
</template>
