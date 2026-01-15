<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <el-input v-model="search" placeholder="Поиск станции" clearable class="max-w-md" />
      <el-tag type="info">{{ filteredStations.length }} станций</el-tag>
    </div>

    <el-table :data="filteredStations" stripe style="width: 100%">
      <el-table-column prop="name" label="Станция" min-width="220" />
      <el-table-column prop="short_name" label="Код" width="100" />
      <el-table-column prop="course_programs" label="Курсов" width="100" />
      <el-table-column prop="total_enrollments" label="Подписок" width="110" />
      <el-table-column prop="active_enrollments" label="Активных" width="110" />
      <el-table-column prop="completed_enrollments" label="Завершено" width="110" />
      <el-table-column prop="average_progress" label="Средний прогресс" width="160">
        <template #default="{ row }">
          <el-progress :percentage="row.average_progress || 0" :stroke-width="8" :show-text="false" />
        </template>
      </el-table-column>
      <el-table-column prop="average_test_score" label="Средний балл" width="140" />
      <el-table-column prop="total_materials" label="Материалы" width="120" />
      <el-table-column prop="active_users" label="Активные" width="120" />
      <el-table-column label="Детали" width="120">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="$router.push(`/admin/analytics/stations/${row.station_id}`)">
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

const stations = ref([])
const search = ref('')

const filteredStations = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return stations.value
  return stations.value.filter(station =>
    (station.name || '').toLowerCase().includes(query) ||
    (station.short_name || '').toLowerCase().includes(query)
  )
})

onMounted(async () => {
  stations.value = await adminAnalyticsService.getStationsAnalytics()
})
</script>
