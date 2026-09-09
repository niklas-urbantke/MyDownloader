<script setup lang="ts">
import AppIcon from './AppIcon.vue'

defineProps<{
  label: string
  value: string | number
  delta?: string
  deltaDir?: 'up' | 'down'
  icon?: string
}>()
</script>

<template>
  <div class="card">
    <div class="stat">
      <div class="stat__label">{{ label }}</div>
      <div class="stat__value">
        <AppIcon v-if="icon" :name="icon" class="icon--lg icon--accent" />
        <span>{{ value }}</span>
      </div>
      <div v-if="delta" class="stat__delta" :class="{ 'is-down': deltaDir === 'down' }">
        <AppIcon :name="deltaDir === 'down' ? 'arrow-down' : 'arrow-up'" class="icon--xs" />
        <span>{{ delta }}</span>
      </div>
    </div>
  </div>
</template>
