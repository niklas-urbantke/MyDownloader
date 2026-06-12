<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="bx-page-head">
    <div class="left">
      <h1 class="bx-page-title">{{ t('queue.title') }}</h1>
      <p class="bx-page-sub">{{ t('queue.subtitle') }}</p>
    </div>
  </div>
</template>
