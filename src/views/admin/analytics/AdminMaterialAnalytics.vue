<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div v-for="(item, key) in materialsByType" :key="key" class="stat-card">
        <div class="stat-label">{{ labels[key] }}</div>
        <div class="stat-value">{{ item.total || 0 }}</div>
        <div class="stat-sub">Просмотрено: {{ item.viewed || item.completed || 0 }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <el-card>
        <template #header>Распределение материалов</template>
        <apexchart type="donut" height="260" :options="donutOptions" :series="donutSeries" />
      </el-card>
      <el-card>
        <template #header>Процент просмотра</template>
        <apexchart type="bar" height="260" :options="barOptions" :series="barSeries" />
      </el-card>
    </div>

    <el-card>
      <template #header>Самые просматриваемые материалы</template>
      <el-table :data="mostViewed" stripe>
        <el-table-column prop="course_title" label="Курс" min-width="220" />
        <el-table-column prop="material_type" label="Тип" width="120" />
        <el-table-column prop="material_key" label="Материал" min-width="240" />
        <el-table-column prop="view_count" label="Просмотров" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import adminAnalyticsService from '@/services/adminAnalyticsService'

const data = ref({ by_type: {}, most_viewed: [] })
const labels = {
  video: 'Видео',
  pdf: 'PDF',
  text: 'Тексты',
  presentation: 'Презентации',
  test: 'Тесты'
}

const materialsByType = computed(() => data.value.by_type || {})
const mostViewed = computed(() => data.value.most_viewed || [])

const donutSeries = computed(() => Object.keys(labels).map(key => materialsByType.value[key]?.total || 0))
const donutOptions = computed(() => ({
  labels: Object.values(labels),
  colors: ['#3b82f6', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444'],
  legend: { position: 'bottom' }
}))

const barSeries = computed(() => [
  {
    name: 'Процент',
    data: Object.keys(labels).map(key => materialsByType.value[key]?.completion_rate || 0)
  }
])
const barOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: Object.values(labels) },
  colors: ['#6366f1'],
  plotOptions: { bar: { borderRadius: 6 } }
}))

onMounted(async () => {
  data.value = await adminAnalyticsService.getMaterialsAnalytics()
})
</script>

<script>
export default { components: { apexchart: VueApexCharts } }
</script>

<style scoped>
.stat-card {
  @apply bg-white rounded-2xl border border-gray-100 p-4 shadow-sm;
}
.stat-label {
  @apply text-xs text-gray-500;
}
.stat-value {
  @apply text-xl font-semibold text-gray-900 mt-1;
}
.stat-sub {
  @apply text-xs text-gray-400;
}
</style>
