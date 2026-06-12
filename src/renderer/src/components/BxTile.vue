<script setup lang="ts">
import AppIcon from './AppIcon.vue'

defineProps<{
  icon: string
  label: string
  sub?: string
}>()

defineEmits<{ click: [] }>()
</script>

<template>
  <button class="bx-tile" type="button" @click="$emit('click')">
    <div class="bx-tile-head">
      <div class="bx-tile-icon"><AppIcon :name="icon" /></div>
      <div class="bx-tile-headtext">
        <span class="bx-tile-label">{{ label }}</span>
        <span v-if="sub" class="bx-tile-sub">{{ sub }}</span>
      </div>
      <AppIcon name="arrow-right" class="bx-tile-chev" />
    </div>
    <div class="bx-tile-badges">
      <slot name="badges">
        <span class="bx-tile-badge bx-tile-badge--empty">
          <AppIcon name="check-in-circle" />
          <span>{{ $t('common.allDone') }}</span>
        </span>
      </slot>
    </div>
  </button>
</template>
