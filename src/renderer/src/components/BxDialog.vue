<script setup lang="ts">
defineProps<{
  open: boolean
  title: string
  /** Breitere Variante fuer formularlastige Dialoge (Onboarding, Metadaten) */
  wide?: boolean
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal__backdrop" @click="emit('close')">
      <div
        class="modal glass glass--strong"
        :class="{ 'modal--wide': wide }"
        role="dialog"
        aria-modal="true"
        @click.stop
      >
        <h3 class="modal__title">{{ title }}</h3>
        <div class="modal__body"><slot /></div>
        <div class="modal__actions">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
