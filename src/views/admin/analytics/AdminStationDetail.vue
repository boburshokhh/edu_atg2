<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-24">
    <div class="max-w-6xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ station?.station?.name || 'Станция' }}
          </h1>
          <p class="text-sm text-gray-500">
            {{ station?.station?.short_name || 'Станция' }}
          </p>
        </div>
        <el-button plain @click="$router.push('/admin/analytics')">
          Назад
        </el-button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="stat-card">
          <div class="stat-label">Курсов</div>
          <div class="stat-value">{{ station?.overview?.total_courses || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Подписок</div>
          <div class="stat-value">{{ station?.overview?.total_enrollments || 0 }}</div>
          <div class="stat-sub">Активных: {{ station?.overview?.active_enrollments || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Средний прогресс</div>
          <div class="stat-value">{{ station?.overview?.average_progress || 0 }}%</div>
          <div class="stat-sub">Пользователей: {{ station?.overview?.unique_users || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Средний балл</div>
          <div class="stat-value">{{ station?.overview?.average_test_score || 0 }}</div>
          <div class="stat-sub">Часы обучения: {{ station?.overview?.total_hours_studied || 0 }}</div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <el-card>
          <template #header>Статусы подписок</template>
          <apexchart type="donut" height="260" :options="statusOptions" :series="statusSeries" />
        </el-card>
        <el-card>
          <template #header>Распределение прогресса</template>
          <apexchart type="bar" height="260" :options="progressOptions" :series="progressSeries" />
        </el-card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <el-card>
          <template #header>Активность по дням</template>
          <apexchart type="area" height="260" :options="activityOptions" :series="activitySeries" />
        </el-card>
        <el-card>
          <template #header>Материалы по типам</template>
          <apexchart type="donut" height="260" :options="materialsOptions" :series="materialsSeries" />
        </el-card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="stat-card">
          <div class="stat-label">Попыток тестов</div>
          <div class="stat-value">{{ station?.test_results?.total_attempts || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Процент сдачи</div>
          <div class="stat-value">{{ station?.test_results?.pass_rate || 0 }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Средний балл</div>
          <div class="stat-value">{{ station?.test_results?.average_score || 0 }}</div>
        </div>
      </div>

      <el-card>
        <template #header>Курсы станции</template>
        <el-table :data="station?.courses || []" stripe>
          <el-table-column prop="title" label="Курс" min-width="220" />
          <el-table-column prop="total_enrollments" label="Подписок" width="120" />
          <el-table-column prop="active_enrollments" label="Активных" width="120" />
          <el-table-column prop="completed_enrollments" label="Завершено" width="120" />
          <el-table-column prop="average_progress" label="Средний прогресс" width="160">
            <template #default="{ row }">
              <el-progress :percentage="row.average_progress || 0" :stroke-width="8" :show-text="false" />
            </template>
          </el-table-column>
          <el-table-column prop="test_results.average_score" label="Средний балл" width="140">
            <template #default="{ row }">
              {{ row.test_results?.average_score || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="Детали" width="120">
            <template #default="{ row }">
              <el-button size="small" type="primary" plain @click="$router.push(`/admin/analytics/courses/${row.course_program_id}`)">
                Открыть
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card>
        <template #header>Самые просматриваемые материалы</template>
        <el-table :data="station?.materials?.most_viewed || []" stripe>
          <el-table-column prop="course_title" label="Курс" min-width="200" />
          <el-table-column prop="material_type" label="Тип" width="120" />
          <el-table-column prop="material_key" label="Материал" min-width="240" />
          <el-table-column prop="view_count" label="Просмотров" width="120" />
        </el-table>
      </el-card>

      <el-card>
        <template #header>Участники станции</template>
        <el-table :data="participants" stripe>
          <el-table-column label="Пользователь" min-width="240">
            <template #default="{ row }">
              <div class="flex items-center gap-3">
                <div 
                  class="w-9 h-9 rounded-full overflow-hidden ring-2 ring-offset-2 transition-all shrink-0"
                  :class="getAvatarUrl(row) && !imageErrors[row.user_id]
                    ? 'ring-blue-500' 
                    : 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-300'"
                >
                  <img 
                    v-if="getAvatarUrl(row) && !imageErrors[row.user_id]" 
                    :src="getAvatarUrl(row)" 
                    :alt="row.full_name || row.username"
                    class="w-full h-full object-cover"
                    @error="() => handleImageError(row.user_id)"
                  >
                  <div
                    v-else
                    class="w-full h-full flex items-center justify-center text-white text-xs font-semibold"
                  >
                    {{ (row.full_name || row.username || 'U').charAt(0).toUpperCase() }}
                  </div>
                </div>
                <div class="min-w-0">
                  <div class="font-medium text-gray-900 truncate">{{ row.full_name || row.username }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ row.email }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="position" label="Должность" min-width="160" />
          <el-table-column prop="total_enrollments" label="Курсов" width="110" />
          <el-table-column prop="average_progress" label="Прогресс" width="140">
            <template #default="{ row }">
              <el-progress :percentage="row.average_progress || 0" :stroke-width="8" :show-text="false" />
            </template>
          </el-table-column>
          <el-table-column prop="average_test_score" label="Средний балл" width="140" />
          <el-table-column prop="last_activity" label="Активность" width="180" />
          <el-table-column label="Профиль" width="120">
            <template #default="{ row }">
              <el-button size="small" type="primary" plain @click="$router.push(`/admin/analytics/users/${row.user_id}`)">
                Открыть
              </el-button>
            </template>
          </el-table-column>
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
const station = ref(null)
const participants = ref([])
const imageErrors = ref({})

const getAvatarUrl = (user) => {
  if (!user.avatar_url) return null
  try {
    return getFrontendUrl(user.avatar_url)
  } catch {
    return user.avatar_url
  }
}

const handleImageError = (userId) => {
  imageErrors.value[userId] = true
}

const statusSeries = computed(() => [
  station.value?.enrollments?.by_status?.not_started || 0,
  station.value?.enrollments?.by_status?.in_progress || 0,
  station.value?.enrollments?.by_status?.completed || 0
])
const statusOptions = computed(() => ({
  labels: ['Не начат', 'В процессе', 'Завершен'],
  colors: ['#f59e0b', '#3b82f6', '#10b981'],
  legend: { position: 'bottom' }
}))

const progressOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: (station.value?.enrollments?.progress_distribution || []).map(item => item.range) },
  colors: ['#6366f1'],
  plotOptions: { bar: { borderRadius: 6 } }
}))
const progressSeries = computed(() => [
  { name: 'Участники', data: (station.value?.enrollments?.progress_distribution || []).map(item => item.count) }
])

const activityOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#3b82f6'] },
  xaxis: { categories: (station.value?.activity_timeline || []).map(item => item.date) },
  colors: ['#3b82f6']
}))
const activitySeries = computed(() => [
  { name: 'Материалы', data: (station.value?.activity_timeline || []).map(item => item.materials_viewed) }
])

const materialsOptions = computed(() => ({
  labels: ['Видео', 'PDF', 'Тесты'],
  colors: ['#3b82f6', '#f59e0b', '#ef4444'],
  legend: { position: 'bottom' }
}))
const materialsSeries = computed(() => {
  const data = station.value?.materials?.by_type || {}
  return [
    data.video?.total || 0,
    data.pdf?.total || 0,
    data.test?.total || 0
  ]
})

onMounted(async () => {
  const stationId = route.params.id
  station.value = await adminAnalyticsService.getStationDetail(stationId)
  participants.value = await adminAnalyticsService.getStationParticipants(stationId)
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
