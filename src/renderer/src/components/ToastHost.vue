<script setup lang="ts">
import AppIcon from './AppIcon.vue'
import { useToasts, dismissToast } from '../composables/toast'

const state = useToasts()

const iconFor = (variant: string): string =>
  variant === 'error' ? 'x-circle' : variant === 'info' ? 'info' : 'check-circle'

const toneFor = (variant: string): string =>
  variant === 'error' ? 'toast--danger' : variant === 'info' ? '' : 'toast--success'
</script>

<template>
  <Teleport to="body">
    <div class="toast-stack">
      <div v-for="t in state.toasts" :key="t.id" class="toast" :class="toneFor(t.variant)">
        <AppIcon :name="iconFor(t.variant)" />
        <span>{{ t.message }}</span>
        <button
          v-if="t.actionLabel"
          class="btn btn--ghost btn--sm"
          type="button"
          @click="t.onAction?.(), dismissToast(t.id)"
        >
          {{ t.actionLabel }}
        </button>
        <button class="toast__close" type="button" aria-label="OK" @click="dismissToast(t.id)">
          <AppIcon name="x" class="icon--sm" />
        </button>
      </div>
    </div>
  </Teleport>
</template>
