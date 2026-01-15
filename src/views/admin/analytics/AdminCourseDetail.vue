<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-24">
    <div class="max-w-6xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ course?.course_program?.title || 'Курс' }}
          </h1>
          <p class="text-sm text-gray-500">
            {{ course?.course_program?.station_name || 'Станция' }}
          </p>
        </div>
        <el-button plain @click="$router.push('/admin/analytics')">
          Назад
        </el-button>
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
          <apexchart type="radar" height="260" :options="materialOptions" :series="materialSeries" />
        </el-card>
      </div>

      <el-card>
        <template #header>Результаты тестов по урокам</template>
        <apexchart type="bar" height="260" :options="testsOptions" :series="testsSeries" />
      </el-card>

      <el-card>
        <template #header>Участники курса</template>
        <el-table :data="participants" stripe>
          <el-table-column label="Пользователь" min-width="240">
            <template #default="{ row }">
              <div class="flex items-center gap-3">
                <el-avatar :src="row.avatar_url" :size="36">
                  {{ (row.full_name || row.username || 'U').charAt(0) }}
                </el-avatar>
                <div>
                  <div class="font-medium text-gray-900">{{ row.full_name || row.username }}</div>
                  <div class="text-xs text-gray-500">{{ row.email }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="position" label="Должность" min-width="160" />
          <el-table-column prop="progress_percent" label="Прогресс" width="140">
            <template #default="{ row }">
              <el-progress :percentage="row.progress_percent || 0" :stroke-width="8" :show-text="false" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Статус" width="120" />
          <el-table-column prop="last_activity" label="Активность" width="180" />
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

const route = useRoute()
const course = ref(null)
const participants = ref([])

const statusSeries = computed(() => [
  course.value?.enrollments?.by_status?.not_started || 0,
  course.value?.enrollments?.by_status?.in_progress || 0,
  course.value?.enrollments?.by_status?.completed || 0
])
const statusOptions = computed(() => ({
  labels: ['Не начат', 'В процессе', 'Завершен'],
  colors: ['#f59e0b', '#3b82f6', '#10b981'],
  legend: { position: 'bottom' }
}))

const progressOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: (course.value?.enrollments?.progress_distribution || []).map(item => item.range) },
  colors: ['#6366f1'],
  plotOptions: { bar: { borderRadius: 6 } }
}))
const progressSeries = computed(() => [
  { name: 'Участники', data: (course.value?.enrollments?.progress_distribution || []).map(item => item.count) }
])

const activityOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 3, colors: ['#3b82f6'] },
  xaxis: { categories: (course.value?.activity_timeline || []).map(item => item.date) },
  colors: ['#3b82f6']
}))
const activitySeries = computed(() => [
  { name: 'Материалы', data: (course.value?.activity_timeline || []).map(item => item.materials_viewed) }
])

const materialOptions = computed(() => ({
  chart: { type: 'radar', toolbar: { show: false } },
  labels: ['Видео', 'PDF', 'Тексты', 'Презентации', 'Тесты'],
  colors: ['#0ea5e9']
}))
const materialSeries = computed(() => [
  {
    name: 'Просмотрено',
    data: [
      course.value?.materials?.by_type?.video?.completed || 0,
      course.value?.materials?.by_type?.pdf?.completed || 0,
      course.value?.materials?.by_type?.text?.completed || 0,
      course.value?.materials?.by_type?.presentation?.completed || 0,
      course.value?.materials?.by_type?.test?.completed || 0
    ]
  }
])

const testsOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { categories: (course.value?.test_results?.by_lesson || []).map(item => item.lesson_title) },
  colors: ['#10b981'],
  plotOptions: { bar: { borderRadius: 6 } }
}))
const testsSeries = computed(() => [
  { name: 'Средний балл', data: (course.value?.test_results?.by_lesson || []).map(item => item.average_score) }
])

onMounted(async () => {
  const courseId = route.params.id
  course.value = await adminAnalyticsService.getCourseDetail(courseId)
  participants.value = await adminAnalyticsService.getCourseParticipants(courseId)
})
</script>

<script>
export default { components: { apexchart: VueApexCharts } }
</script>
