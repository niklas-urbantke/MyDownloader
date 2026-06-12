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
  <div class="bx-card">
    <div class="bx-stat">
      <div class="bx-stat-label">{{ label }}</div>
      <div class="bx-stat-value">
        <AppIcon v-if="icon" :name="icon" :size="24" style="margin-right: 8px" />{{ value }}
      </div>
      <div v-if="delta" class="bx-stat-delta" :class="{ neg: deltaDir === 'down' }">
        <AppIcon :name="deltaDir === 'down' ? 'arrow-down' : 'arrow-up1'" />
        <span>{{ delta }}</span>
      </div>
    </div>
  </div>
</template>
