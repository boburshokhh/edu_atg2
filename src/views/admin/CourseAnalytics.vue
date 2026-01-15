<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-24">
    <div class="max-w-7xl mx-auto space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">
            Аналитика по программам обучения
          </h1>
          <p class="text-sm text-gray-500">
            Подписки, прогресс и результаты тестов по станциям
          </p>
        </div>
        <el-button plain @click="$router.push('/admin')">
          <el-icon class="mr-1"><ArrowLeft /></el-icon>
          Назад
        </el-button>
      </div>

      <el-card class="border border-gray-100">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1">
            <p class="text-sm text-gray-500 mb-1">Станция</p>
            <el-select
              v-model="selectedStationId"
              placeholder="Выберите станцию"
              filterable
              clearable
              class="w-full"
              :loading="loadingStations"
            >
              <el-option
                v-for="station in stations"
                :key="station.id"
                :label="station.name"
                :value="station.id"
              />
            </el-select>
          </div>
          <el-button
            type="primary"
            :disabled="!selectedStationId"
            :loading="loadingAnalytics"
            @click="loadAnalytics"
          >
            Применить
          </el-button>
        </div>
      </el-card>

      <div
        v-if="!selectedStationId"
        class="rounded-2xl border border-dashed border-gray-200 bg-white p-10 text-center text-gray-500"
      >
        Выберите станцию, чтобы посмотреть аналитику.
      </div>

      <template v-else>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="stat-card">
            <p class="text-sm text-gray-500">Всего подписок</p>
            <p class="text-3xl font-semibold text-gray-900">{{ analytics.kpi.totalEnrollments }}</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-gray-500">Активных курсов</p>
            <p class="text-3xl font-semibold text-gray-900">{{ analytics.kpi.activeEnrollments }}</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-gray-500">Завершено</p>
            <p class="text-3xl font-semibold text-gray-900">{{ analytics.kpi.completedEnrollments }}</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-gray-500">Средний прогресс</p>
            <p class="text-3xl font-semibold text-gray-900">{{ analytics.kpi.averageProgress }}%</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-gray-500">Средний балл тестов</p>
            <p class="text-3xl font-semibold text-gray-900">{{ analytics.kpi.averageTestScore }}/100</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-gray-500">Просмотрено материалов</p>
            <p class="text-3xl font-semibold text-gray-900">{{ analytics.kpi.completedMaterials }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <el-card class="border border-gray-100">
            <template #header>
              <span class="font-medium text-gray-900">Топ программ по подпискам</span>
            </template>
            <apexchart
              type="bar"
              height="320"
              :options="barOptions"
              :series="barSeries"
            />
          </el-card>

          <el-card class="border border-gray-100">
            <template #header>
              <span class="font-medium text-gray-900">Распределение прогресса</span>
            </template>
            <apexchart
              type="donut"
              height="320"
              :options="progressDonutOptions"
              :series="progressDonutSeries"
            />
          </el-card>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <el-card class="border border-gray-100">
            <template #header>
              <span class="font-medium text-gray-900">Типы материалов</span>
            </template>
            <apexchart
              type="donut"
              height="320"
              :options="materialsDonutOptions"
              :series="materialsDonutSeries"
            />
          </el-card>
          <el-card class="border border-gray-100">
            <template #header>
              <span class="font-medium text-gray-900">Активность по дням</span>
            </template>
            <apexchart
              type="area"
              height="320"
              :options="activityOptions"
              :series="activitySeries"
            />
          </el-card>
        </div>

        <el-card class="border border-gray-100">
          <template #header>
            <span class="font-medium text-gray-900">Средний балл по программам</span>
          </template>
          <apexchart
            type="bar"
            height="320"
            :options="scoreBarOptions"
            :series="scoreBarSeries"
          />
        </el-card>

        <el-card class="border border-gray-100">
          <template #header>
            <span class="font-medium text-gray-900">Пользователи и прогресс</span>
          </template>
          <el-table :data="analytics.userTable" stripe>
            <el-table-column prop="user_name" label="Пользователь" min-width="180" />
            <el-table-column prop="program_title" label="Программа" min-width="220" />
            <el-table-column prop="status" label="Статус" width="140">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'in_progress' ? 'warning' : 'info'">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress_percent" label="Прогресс" width="120">
              <template #default="{ row }">
                {{ row.progress_percent }}%
              </template>
            </el-table-column>
            <el-table-column prop="materials_completed" label="Материалы" width="120" />
            <el-table-column prop="average_score" label="Средний балл" width="140" />
            <el-table-column prop="last_activity" label="Последняя активность" min-width="180" />
          </el-table>
        </el-card>

        <el-card class="border border-gray-100">
          <template #header>
            <span class="font-medium text-gray-900">Сводка по программам</span>
          </template>
          <el-table :data="analytics.programTable" stripe>
            <el-table-column prop="program_title" label="Программа" min-width="220" />
            <el-table-column prop="enrollments" label="Подписки" width="120" />
            <el-table-column prop="average_progress" label="Средний прогресс" width="160" />
            <el-table-column prop="active_count" label="Активных" width="120" />
            <el-table-column prop="completed_count" label="Завершено" width="140" />
            <el-table-column prop="average_score" label="Средний балл" width="140" />
          </el-table>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { ArrowLeft } from '@element-plus/icons-vue'
import stationService from '@/services/stationService'
import adminAnalyticsService from '@/services/adminAnalyticsService'
import { ElMessage } from 'element-plus'

const apexchart = VueApexCharts

const stations = ref([])
const loadingStations = ref(false)
const selectedStationId = ref(null)
const loadingAnalytics = ref(false)
const analytics = ref({
  kpi: {
    totalEnrollments: 0,
    activeEnrollments: 0,
    completedEnrollments: 0,
    averageProgress: 0,
    averageTestScore: 0,
    completedMaterials: 0
  },
  charts: {
    programEnrollments: [],
    progressBuckets: [],
    materials: [],
    activityByDay: []
  },
  userTable: [],
  programTable: []
})

const barSeries = ref([{ name: 'Подписки', data: [] }])
const barOptions = ref({
  chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
  plotOptions: { bar: { borderRadius: 6, horizontal: false } },
  dataLabels: { enabled: false },
  xaxis: { categories: [], labels: { style: { colors: '#9ca3af' } } },
  yaxis: { labels: { style: { colors: '#9ca3af' } } },
  colors: ['#2563eb']
})

const progressDonutSeries = ref([])
const progressDonutOptions = ref({
  chart: { type: 'donut', fontFamily: 'Inter, sans-serif' },
  labels: ['0-25%', '26-50%', '51-75%', '76-100%'],
  colors: ['#93c5fd', '#60a5fa', '#2563eb', '#1e40af']
})

const materialsDonutSeries = ref([])
const materialsDonutOptions = ref({
  chart: { type: 'donut', fontFamily: 'Inter, sans-serif' },
  labels: ['Видео', 'PDF', 'Тексты', 'Презентации', 'Тесты'],
  colors: ['#3b82f6', '#f59e0b', '#10b981', '#8b5cf6', '#f97316']
})

const scoreBarSeries = ref([{ name: 'Средний балл', data: [] }])
const scoreBarOptions = ref({
  chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
  plotOptions: { bar: { borderRadius: 6, horizontal: false } },
  dataLabels: { enabled: false },
  xaxis: { categories: [], labels: { style: { colors: '#9ca3af' } } },
  yaxis: { labels: { style: { colors: '#9ca3af' } }, max: 100 },
  colors: ['#10b981']
})

const activitySeries = ref([{ name: 'Активность', data: [] }])
const activityOptions = ref({
  chart: { type: 'area', toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#f97316'] },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.4,
      opacityTo: 0.05,
      stops: [0, 100]
    }
  },
  xaxis: { categories: [], labels: { style: { colors: '#9ca3af' } } },
  yaxis: { labels: { style: { colors: '#9ca3af' } } }
})

const statusLabel = (status) => {
  const map = {
    not_started: 'Не начат',
    in_progress: 'В процессе',
    completed: 'Завершен'
  }
  return map[status] || status
}

const loadStations = async () => {
  loadingStations.value = true
  try {
    stations.value = await stationService.getStations()
  } catch (error) {
    ElMessage.error('Не удалось загрузить станции')
  } finally {
    loadingStations.value = false
  }
}

const loadAnalytics = async () => {
  if (!selectedStationId.value) return
  loadingAnalytics.value = true
  const result = await adminAnalyticsService.getCourseAnalytics(selectedStationId.value)
  loadingAnalytics.value = false
  if (!result.success) {
    ElMessage.error(result.error || 'Ошибка загрузки аналитики')
    return
  }
  analytics.value = result.data

  const programLabels = result.data.charts.programEnrollments.map((row) => row.label)
  const programCounts = result.data.charts.programEnrollments.map((row) => row.value)
  barOptions.value = {
    ...barOptions.value,
    xaxis: { ...barOptions.value.xaxis, categories: programLabels }
  }
  barSeries.value = [{ name: 'Подписки', data: programCounts }]

  progressDonutSeries.value = result.data.charts.progressBuckets.map((row) => row.value)

  const materialsMap = result.data.charts.materials.reduce((acc, row) => {
    acc[row.label] = row.value
    return acc
  }, {})
  materialsDonutSeries.value = [
    materialsMap.video || 0,
    materialsMap.pdf || 0,
    materialsMap.text || 0,
    materialsMap.presentation || 0,
    materialsMap.test || 0
  ]

  scoreBarOptions.value = {
    ...scoreBarOptions.value,
    xaxis: { ...scoreBarOptions.value.xaxis, categories: result.data.programTable.map((row) => row.program_title) }
  }
  scoreBarSeries.value = [{ name: 'Средний балл', data: result.data.programTable.map((row) => row.average_score) }]

  activityOptions.value = {
    ...activityOptions.value,
    xaxis: { ...activityOptions.value.xaxis, categories: result.data.charts.activityByDay.map((row) => row.label) }
  }
  activitySeries.value = [{ name: 'Активность', data: result.data.charts.activityByDay.map((row) => row.value) }]
}

loadStations()
</script>

<style scoped>
.stat-card {
  @apply bg-white p-5 rounded-2xl border border-gray-100 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1;
}
</style>
