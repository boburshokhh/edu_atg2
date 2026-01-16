<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-24">
    <div class="max-w-6xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div 
            class="w-16 h-16 rounded-full overflow-hidden ring-2 ring-offset-2 transition-all hover:ring-offset-4 shrink-0 cursor-pointer"
            :class="getAvatarUrl(user) && !imageError
              ? 'ring-blue-500' 
              : 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-300'"
            @click="getAvatarUrl(user) && !imageError ? showAvatarPreview = true : null"
          >
            <img 
              v-if="getAvatarUrl(user) && !imageError" 
              :src="getAvatarUrl(user)" 
              :alt="user?.full_name || user?.username"
              class="w-full h-full object-cover transition-transform duration-300"
              @error="handleImageError"
            >
            <div
              v-else
              class="w-full h-full flex items-center justify-center text-white text-xl font-semibold"
            >
              {{ (user?.full_name || user?.username || 'U').charAt(0).toUpperCase() }}
            </div>
          </div>
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">
              {{ user?.full_name || user?.username }}
            </h1>
            <p class="text-sm text-gray-500">{{ user?.email }}</p>
            <p class="text-xs text-gray-400">{{ user?.position || 'Должность не указана' }}</p>
          </div>
        </div>
        <el-button plain @click="$router.push('/admin/analytics')">Назад</el-button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="stat-card">
          <div class="stat-label">Активных курсов</div>
          <div class="stat-value">{{ activeCourses }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Завершено</div>
          <div class="stat-value">{{ completedCourses }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Средний прогресс</div>
          <div class="stat-value">{{ averageProgress }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Средний балл</div>
          <div class="stat-value">{{ averageScore }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <el-card>
          <template #header>Материалы по типам</template>
          <apexchart type="donut" height="260" :options="materialsOptions" :series="materialsSeries" />
        </el-card>
        <el-card>
          <template #header>Прогресс по курсам</template>
          <apexchart type="bar" height="260" :options="progressOptions" :series="progressSeries" />
        </el-card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <el-card>
          <template #header>Активность по дням</template>
          <apexchart type="area" height="260" :options="activityOptions" :series="activitySeries" />
        </el-card>
        <el-card>
          <template #header>Динамика баллов</template>
          <apexchart type="line" height="260" :options="scoresOptions" :series="scoresSeries" />
        </el-card>
      </div>

      <el-card>
        <template #header>Курсы пользователя</template>
        <el-table :data="enrollments" stripe>
          <el-table-column prop="course_title" label="Курс" min-width="240" />
          <el-table-column prop="station_name" label="Станция" min-width="160" />
          <el-table-column prop="progress_percent" label="Прогресс" width="140">
            <template #default="{ row }">
              <el-progress :percentage="row.progress_percent || 0" :stroke-width="8" :show-text="false" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Статус" width="120" />
          <el-table-column prop="last_activity" label="Активность" width="180" />
        </el-table>
      </el-card>

      <el-card>
        <template #header>История тестов</template>
        <el-table :data="testResults" stripe>
          <el-table-column prop="test_title" label="Тест" min-width="240" />
          <el-table-column prop="test_type" label="Тип" width="120" />
          <el-table-column prop="score" label="Баллы" width="120" />
          <el-table-column prop="completed_at" label="Дата" width="180" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import adminAnalyticsService from '@/services/adminAnalyticsService'
import { getFrontendUrl } from '@/services/minioService'

const route = useRoute()
const userData = ref(null)
const imageError = ref(false)
const showAvatarPreview = ref(false)

const getAvatarUrl = (user) => {
  if (!user?.avatar_url) return null
  try {
    return getFrontendUrl(user.avatar_url)
  } catch {
    return user.avatar_url
  }
}

const handleImageError = () => {
  imageError.value = true
}

const user = computed(() => userData.value?.user)
const enrollments = computed(() => userData.value?.enrollments || [])
const testResults = computed(() => userData.value?.test_results || [])

const activeCourses = computed(() => enrollments.value.filter(e => e.status === 'in_progress').length)
const completedCourses = computed(() => enrollments.value.filter(e => e.status === 'completed').length)
const averageProgress = computed(() => {
  if (!enrollments.value.length) return 0
  const sum = enrollments.value.reduce((acc, e) => acc + (e.progress_percent || 0), 0)
  return Math.round(sum / enrollments.value.length)
})
const averageScore = computed(() => {
  if (!testResults.value.length) return 0
  const sum = testResults.value.reduce((acc, t) => acc + (t.score || 0), 0)
  return Math.round(sum / testResults.value.length)
})

const materialsSeries = computed(() => [
  userData.value?.materials?.by_type?.video || 0,
  userData.value?.materials?.by_type?.pdf || 0,
  userData.value?.materials?.by_type?.test || 0
])
const materialsOptions = computed(() => ({
  labels: ['Видео', 'PDF', 'Тесты'],
  colors: ['#3b82f6', '#f59e0b', '#ef4444'],
  legend: { position: 'bottom' }
}))

const progressOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: enrollments.value.map(e => e.course_title) },
  colors: ['#6366f1'],
  plotOptions: { bar: { borderRadius: 6 } }
}))
const progressSeries = computed(() => [
  { name: 'Прогресс', data: enrollments.value.map(e => e.progress_percent || 0) }
])

const activityOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#3b82f6'] },
  xaxis: { categories: (userData.value?.activity_timeline || []).map(item => item.date) },
  colors: ['#3b82f6']
}))
const activitySeries = computed(() => [
  { name: 'Материалы', data: (userData.value?.activity_timeline || []).map(item => item.materials_viewed) }
])

const scoresOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  stroke: { curve: 'smooth', width: 3 },
  xaxis: { categories: testResults.value.map(item => item.completed_at) },
  colors: ['#10b981']
}))
const scoresSeries = computed(() => [
  { name: 'Баллы', data: testResults.value.map(item => item.score || 0) }
])

onMounted(async () => {
  userData.value = await adminAnalyticsService.getUserDetail(route.params.id)
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
  @apply text-2xl font-semibold text-gray-900 mt-1;
}
</style>
