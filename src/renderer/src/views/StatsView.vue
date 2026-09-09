<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { StatsSummary } from '@shared/types'
import PageHead from '../components/PageHead.vue'
import BxCard from '../components/BxCard.vue'
import BxStat from '../components/BxStat.vue'
import BxChip from '../components/BxChip.vue'
import { formatBytes } from '../utils/format'

const { t, locale } = useI18n()

const stats = ref<StatsSummary | null>(null)

onMounted(async () => {
  stats.value = await window.api.stats.compute()
})

const successRate = computed(() => {
  if (!stats.value || stats.value.totalDownloads === 0) return '–'
  return `${Math.round((stats.value.completed / stats.value.totalDownloads) * 100)} %`
})

/** Balkendiagramm-Geometrie (inline SVG, keine Chart-Bibliothek nötig) */
const chart = computed(() => {
  const months = stats.value?.perMonth ?? []
  const max = Math.max(1, ...months.map((m) => m.count))
  const barW = 48
  const gap = 14
  const height = 180
  return {
    width: months.length * (barW + gap) + gap,
    height: height + 40,
    bars: months.map((m, i) => {
      const h = Math.round((m.count / max) * height)
      const label = new Intl.DateTimeFormat(locale.value, { month: 'short' }).format(
        new Date(`${m.month}-01T00:00:00`)
      )
      return {
        x: gap + i * (barW + gap),
        y: height - h + 20,
        w: barW,
        h,
        count: m.count,
        label
      }
    })
  }
})
</script>

<template>
  <PageHead :title="t('stats.title')" :sub="t('stats.subtitle')" />

  <div v-if="stats" class="stack stack--lg">
    <!-- KPIs -->
    <div class="grid-auto" style="--col-min: 14rem">
      <BxStat :label="t('stats.kpi.total')" :value="stats.totalDownloads" />
      <BxStat :label="t('stats.kpi.completed')" :value="stats.completed" />
      <BxStat :label="t('stats.kpi.successRate')" :value="successRate" />
      <BxStat :label="t('stats.kpi.totalSize')" :value="formatBytes(stats.totalBytes)" />
    </div>

    <!-- Downloads pro Monat -->
    <BxCard :title="t('stats.perMonth')">
      <div class="chart-scroll">
        <svg
          :width="chart.width"
          :height="chart.height"
          :viewBox="`0 0 ${chart.width} ${chart.height}`"
          role="img"
        >
          <g v-for="(bar, i) in chart.bars" :key="i">
            <rect
              class="chart__bar"
              :x="bar.x"
              :y="bar.y"
              :width="bar.w"
              :height="Math.max(2, bar.h)"
              rx="4"
            />
            <text class="chart__value" :x="bar.x + bar.w / 2" :y="bar.y - 6" text-anchor="middle">
              {{ bar.count }}
            </text>
            <text
              class="chart__label"
              :x="bar.x + bar.w / 2"
              :y="chart.height - 6"
              text-anchor="middle"
            >
              {{ bar.label }}
            </text>
          </g>
        </svg>
      </div>
    </BxCard>

    <div class="form-grid">
      <!-- Top-Künstler/Kanäle -->
      <div class="col-6">
        <BxCard :title="t('stats.topUploaders')" :padded="false">
          <table class="table table--plain">
            <tbody>
              <tr v-for="u in stats.topUploaders" :key="u.name">
                <td>{{ u.name }}</td>
                <td class="text-secondary uploader-count">{{ u.count }}</td>
              </tr>
              <tr v-if="stats.topUploaders.length === 0">
                <td class="text-secondary">{{ t('stats.noData') }}</td>
              </tr>
            </tbody>
          </table>
        </BxCard>
      </div>
      <!-- Formate -->
      <div class="col-6">
        <BxCard :title="t('stats.formats')">
          <div class="cluster" style="--cluster-gap: var(--space-2)">
            <BxChip v-for="f in stats.formats" :key="f.format" variant="slate">
              {{ f.format.toUpperCase() }} · {{ f.count }}
            </BxChip>
            <span v-if="stats.formats.length === 0" class="text-secondary">
              {{ t('stats.noData') }}
            </span>
          </div>
        </BxCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Das Diagramm rollt waagerecht, wenn viele Monate anfallen. */
.chart-scroll {
  overflow-x: auto;
}

.chart__bar {
  fill: var(--color-accent);
  opacity: 0.85;
}
.chart__value,
.chart__label {
  fill: var(--color-text-secondary);
  font-size: var(--text-xs);
}
.chart__value {
  font-weight: var(--font-semibold);
}

.uploader-count {
  width: 5rem;
  text-align: end;
}
</style>
