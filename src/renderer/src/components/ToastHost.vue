<script setup lang="ts">
import AppIcon from './AppIcon.vue'
import { useToasts, dismissToast } from '../composables/toast'

const state = useToasts()

const iconFor = (variant: string): string =>
  variant === 'error' ? 'cancel-in-circle' : variant === 'info' ? 'information-in-circle' : 'check-in-circle'
</script>

<template>
  <Teleport to="body">
    <div class="bx-toast-stack">
      <div
        v-for="t in state.toasts"
        :key="t.id"
        class="bx-toast"
        :class="{ 'bx-toast--error': t.variant === 'error' }"
      >
        <AppIcon :name="iconFor(t.variant)" />
        <span>{{ t.message }}</span>
        <button
          v-if="t.actionLabel"
          type="button"
          @click="t.onAction?.(), dismissToast(t.id)"
        >
          {{ t.actionLabel }}
        </button>
        <button v-else type="button" @click="dismissToast(t.id)">OK</button>
      </div>
    </div>
  </Teleport>
</template>
