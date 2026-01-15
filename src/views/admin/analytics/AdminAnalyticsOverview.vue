<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="stat-card">
        <div class="stat-label">Всего пользователей</div>
        <div class="stat-value">{{ overview?.total_users || 0 }}</div>
        <div class="stat-sub">Активных за 30 дней: {{ overview?.active_users || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Подписок на курсы</div>
        <div class="stat-value">{{ overview?.total_enrollments || 0 }}</div>
        <div class="stat-sub">В процессе: {{ overview?.active_enrollments || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Средний прогресс</div>
        <div class="stat-value">{{ overview?.average_progress || 0 }}%</div>
        <div class="stat-sub">Средний балл: {{ overview?.average_test_score || 0 }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <el-card>
        <template #header>
          <div class="text-sm font-semibold text-gray-700">Активность по дням</div>
        </template>
        <apexchart type="area" height="280" :options="areaOptions" :series="areaSeries" />
      </el-card>
      <el-card>
        <template #header>
          <div class="text-sm font-semibold text-gray-700">Статусы подписок</div>
        </template>
        <apexchart type="donut" height="280" :options="donutOptions" :series="donutSeries" />
      </el-card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <el-card>
        <template #header>
          <div class="text-sm font-semibold text-gray-700">Топ курсов по участникам</div>
        </template>
        <apexchart type="bar" height="280" :options="barOptions" :series="barSeries" />
      </el-card>
      <el-card>
        <template #header>
          <div class="text-sm font-semibold text-gray-700">Подписки и завершения</div>
        </template>
        <apexchart type="line" height="280" :options="lineOptions" :series="lineSeries" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import adminAnalyticsService from '@/services/adminAnalyticsService'

const overview = ref(null)
const courses = ref([])

const activityDates = computed(() => (overview.value?.activity_timeline || []).map(item => item.date))
const activityMaterials = computed(() => (overview.value?.activity_timeline || []).map(item => item.materials_viewed))
const activityEnrollments = computed(() => (overview.value?.activity_timeline || []).map(item => item.enrollments))
const activityCompletions = computed(() => (overview.value?.activity_timeline || []).map(item => item.completions))

const areaOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#3b82f6'] },
  xaxis: { categories: activityDates.value },
  colors: ['#3b82f6'],
  tooltip: { y: { formatter: val => `${val} просмотров` } }
}))
const areaSeries = computed(() => [
  { name: 'Материалы', data: activityMaterials.value }
])

const donutSeries = computed(() => [
  overview.value?.enrollments_by_status?.not_started || 0,
  overview.value?.enrollments_by_status?.in_progress || 0,
  overview.value?.enrollments_by_status?.completed || 0
])
const donutOptions = computed(() => ({
  labels: ['Не начат', 'В процессе', 'Завершен'],
  colors: ['#f59e0b', '#3b82f6', '#10b981'],
  legend: { position: 'bottom' }
}))

const topCourses = computed(() => {
  return [...courses.value]
    .sort((a, b) => (b.total_enrollments || 0) - (a.total_enrollments || 0))
    .slice(0, 5)
})
const barOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: topCourses.value.map(c => c.title) },
  plotOptions: { bar: { borderRadius: 6, horizontal: false } },
  colors: ['#6366f1']
}))
const barSeries = computed(() => [
  { name: 'Участники', data: topCourses.value.map(c => c.total_enrollments || 0) }
])

const lineOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  stroke: { curve: 'smooth', width: 3 },
  xaxis: { categories: activityDates.value },
  colors: ['#3b82f6', '#10b981']
}))
const lineSeries = computed(() => [
  { name: 'Подписки', data: activityEnrollments.value },
  { name: 'Завершения', data: activityCompletions.value }
])

onMounted(async () => {
  overview.value = await adminAnalyticsService.getOverviewStats()
  courses.value = await adminAnalyticsService.getCoursesAnalytics()
})
</script>

<script>
export default {
  components: { apexchart: VueApexCharts }
}
</script>

<style scoped>
.stat-card {
  @apply bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow;
}
.stat-label {
  @apply text-sm text-gray-500;
}
.stat-value {
  @apply text-2xl font-semibold text-gray-900 mt-1;
}
.stat-sub {
  @apply text-xs text-gray-400 mt-1;
}
</style>
