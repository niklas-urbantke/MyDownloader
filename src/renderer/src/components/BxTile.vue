<script setup lang="ts">
import AppIcon from './AppIcon.vue'

withDefaults(
  defineProps<{
    icon: string
    label: string
    sub?: string
    /** Ton der Glaskachel aus dem Baukasten (urbDesign). */
    tone?: 'azure' | 'indigo' | 'amber' | 'jade' | 'rose' | 'slate'
  }>(),
  { tone: 'azure' }
)

defineEmits<{ click: [] }>()
</script>

<template>
  <button class="card tile" :class="`tone-${tone}`" type="button" @click="$emit('click')">
    <div class="tile__head">
      <span class="icon-tile tile__icon" :class="`icon-tile--${tone}`" aria-hidden="true">
        <AppIcon :name="icon" />
      </span>
      <span class="tile__text">
        <span class="tile__label">{{ label }}</span>
        <span v-if="sub" class="tile__sub">{{ sub }}</span>
      </span>
      <AppIcon name="chevron-right" class="tile__chevron icon--sm" />
    </div>
    <div class="tile__badges">
      <slot name="badges">
        <span class="badge badge--success">
          <AppIcon name="check-circle" class="icon--xs" />
          <span>{{ $t('common.allDone') }}</span>
        </span>
      </slot>
    </div>
  </button>
</template>
