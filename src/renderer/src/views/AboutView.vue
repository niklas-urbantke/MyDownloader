<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="bx-page-head">
    <div class="left">
      <h1 class="bx-page-title">{{ t('about.title') }}</h1>
      <p class="bx-page-sub">{{ t('about.subtitle') }}</p>
    </div>
  </div>
</template>
