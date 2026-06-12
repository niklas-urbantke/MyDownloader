<script setup lang="ts">
defineProps<{
  open: boolean
  title: string
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="bx-dialog-scrim" @click="emit('close')">
      <div class="bx-dialog" @click.stop>
        <div class="bx-dialog-head">
          <h3>{{ title }}</h3>
        </div>
        <div class="bx-dialog-body"><slot /></div>
        <div class="bx-dialog-actions">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
