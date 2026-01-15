<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <el-input v-model="search" placeholder="Поиск курса" clearable class="max-w-md" />
      <el-tag type="info">{{ filteredCourses.length }} курсов</el-tag>
    </div>

    <el-table :data="filteredCourses" stripe style="width: 100%">
      <el-table-column prop="title" label="Курс" min-width="220" />
      <el-table-column prop="station_name" label="Станция" min-width="160" />
      <el-table-column prop="total_enrollments" label="Участников" width="120" />
      <el-table-column prop="active_enrollments" label="Активных" width="120" />
      <el-table-column prop="completed_enrollments" label="Завершено" width="120" />
      <el-table-column prop="average_progress" label="Средний прогресс" width="160">
        <template #default="{ row }">
          <el-progress :percentage="row.average_progress || 0" :stroke-width="8" :show-text="false" />
        </template>
      </el-table-column>
      <el-table-column prop="average_test_score" label="Средний балл" width="140" />
      <el-table-column label="Детали" width="120">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="$router.push(`/admin/analytics/courses/${row.course_program_id}`)">
            Открыть
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import adminAnalyticsService from '@/services/adminAnalyticsService'

const courses = ref([])
const search = ref('')

const filteredCourses = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return courses.value
  return courses.value.filter(course =>
    (course.title || '').toLowerCase().includes(query) ||
    (course.station_name || '').toLowerCase().includes(query)
  )
})

onMounted(async () => {
  courses.value = await adminAnalyticsService.getCoursesAnalytics()
})
</script>
