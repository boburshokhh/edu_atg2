<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <el-input 
        v-model="search" 
        placeholder="Поиск станции" 
        clearable 
        class="max-w-md"
        :prefix-icon="Search"
      />
      <el-tag type="info" size="large">
        <el-icon class="mr-1"><Document /></el-icon>
        {{ filteredStations.length }} станций
      </el-tag>
    </div>

    <el-card shadow="never" class="border border-gray-200">
      <el-table 
        :data="filteredStations" 
        stripe 
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: '600' }"
        v-loading="loading"
      >
        <el-table-column prop="name" label="Станция" min-width="220" fixed="left">
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <el-icon class="text-blue-500"><Location /></el-icon>
              <span class="font-medium text-gray-900">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="short_name" label="Код" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.short_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="course_programs" label="Курсов" width="110" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-1">
              <el-icon class="text-purple-500"><Document /></el-icon>
              <span class="font-semibold text-gray-900">{{ row.course_programs || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="total_enrollments" label="Подписок" width="120" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-1">
              <el-icon class="text-blue-500"><User /></el-icon>
              <span class="font-semibold text-gray-900">{{ row.total_enrollments || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="active_enrollments" label="Активных" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">
              {{ row.active_enrollments || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="completed_enrollments" label="Завершено" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="success" effect="dark" size="small">
              {{ row.completed_enrollments || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="average_progress" label="Средний прогресс" width="180" align="center">
          <template #default="{ row }">
            <div class="flex flex-col items-center gap-1">
              <el-progress 
                :percentage="Math.round(row.average_progress || 0)" 
                :stroke-width="10" 
                :show-text="false"
                :color="getProgressColor(row.average_progress)"
              />
              <span class="text-xs font-medium text-gray-600">
                {{ Math.round(row.average_progress || 0) }}%
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="average_test_score" label="Средний балл" width="140" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-1">
              <el-icon class="text-orange-500"><Trophy /></el-icon>
              <span class="font-semibold text-gray-900">
                {{ row.average_test_score ? row.average_test_score.toFixed(1) : '0.0' }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="total_materials" label="Материалы" width="130" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-1">
              <el-icon class="text-green-500"><Files /></el-icon>
              <span class="font-semibold text-gray-900">{{ row.total_materials || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="active_users" label="Активные пользователи" width="160" align="center">
          <template #default="{ row }">
            <el-tag type="warning" size="small">
              <el-icon class="mr-1"><UserFilled /></el-icon>
              {{ row.active_users || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Детали" width="130" fixed="right" align="center">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              :icon="View"
              @click="$router.push(`/admin/analytics/stations/${row.station_id}`)"
            >
              Детали
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Search, 
  Document, 
  Location, 
  User, 
  UserFilled, 
  Trophy, 
  Files, 
  View 
} from '@element-plus/icons-vue'
import adminAnalyticsService from '@/services/adminAnalyticsService'

const stations = ref([])
const search = ref('')
const loading = ref(false)

const filteredStations = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return stations.value
  return stations.value.filter(station =>
    (station.name || '').toLowerCase().includes(query) ||
    (station.short_name || '').toLowerCase().includes(query)
  )
})

const getProgressColor = (progress) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 60) return '#e6a23c'
  if (progress >= 40) return '#f56c6c'
  return '#909399'
}

onMounted(async () => {
  loading.value = true
  try {
    stations.value = await adminAnalyticsService.getStationsAnalytics()
  } finally {
    loading.value = false
  }
})
</script>
