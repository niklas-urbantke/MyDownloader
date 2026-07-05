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
    <div class="bx-tiles">
      <BxStat :label="t('stats.kpi.total')" :value="stats.totalDownloads" />
      <BxStat :label="t('stats.kpi.completed')" :value="stats.completed" />
      <BxStat :label="t('stats.kpi.successRate')" :value="successRate" />
      <BxStat :label="t('stats.kpi.totalSize')" :value="formatBytes(stats.totalBytes)" />
    </div>

    <!-- Downloads pro Monat -->
    <BxCard :title="t('stats.perMonth')">
      <div style="overflow-x: auto">
        <svg
          :width="chart.width"
          :height="chart.height"
          :viewBox="`0 0 ${chart.width} ${chart.height}`"
          role="img"
        >
          <g v-for="(bar, i) in chart.bars" :key="i">
            <rect
              :x="bar.x"
              :y="bar.y"
              :width="bar.w"
              :height="Math.max(2, bar.h)"
              rx="4"
              fill="var(--marine, #003063)"
              opacity="0.85"
            />
            <text
              :x="bar.x + bar.w / 2"
              :y="bar.y - 6"
              text-anchor="middle"
              font-size="11"
              fill="var(--fg2, #667)"
            >
              {{ bar.count }}
            </text>
            <text
              :x="bar.x + bar.w / 2"
              :y="chart.height - 6"
              text-anchor="middle"
              font-size="11"
              fill="var(--fg2, #667)"
            >
              {{ bar.label }}
            </text>
          </g>
        </svg>
      </div>
    </BxCard>

    <div class="bx-form-grid">
      <!-- Top-Künstler/Kanäle -->
      <div class="col-6">
        <BxCard :title="t('stats.topUploaders')" :padded="false">
          <table class="bx-table">
            <tbody>
              <tr v-for="u in stats.topUploaders" :key="u.name" style="cursor: default">
                <td>{{ u.name }}</td>
                <td style="width: 80px; text-align: right; color: var(--fg2)">{{ u.count }}</td>
              </tr>
              <tr v-if="stats.topUploaders.length === 0">
                <td style="color: var(--fg2)">{{ t('stats.noData') }}</td>
              </tr>
            </tbody>
          </table>
        </BxCard>
      </div>
      <!-- Formate -->
      <div class="col-6">
        <BxCard :title="t('stats.formats')">
          <div class="row" style="flex-wrap: wrap; gap: 8px">
            <BxChip v-for="f in stats.formats" :key="f.format" variant="neutral">
              {{ f.format.toUpperCase() }} · {{ f.count }}
            </BxChip>
            <span v-if="stats.formats.length === 0" style="color: var(--fg2)">
              {{ t('stats.noData') }}
            </span>
          </div>
        </BxCard>
      </div>
    </div>
  </div>
</template>
