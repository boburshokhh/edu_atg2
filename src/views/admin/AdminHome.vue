<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-24">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-2xl font-semibold text-gray-900">
            Панель администратора
          </h1>
          <el-button
            plain
            @click="$router.push('/')"
          >
            <el-icon class="mr-1">
              <ArrowLeft />
            </el-icon>
            Назад
          </el-button>
        </div>
        <p class="text-sm text-gray-500">
          Управление контентом и настройками платформы
        </p>
      </div>

      <!-- Admin Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-8">
        <!-- Stations Card -->
        <el-card
          shadow="hover"
          class="cursor-pointer"
          @click="$router.push('/admin/stations')"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-3">
                <el-icon class="text-blue-600 mr-2" :size="20">
                  <OfficeBuilding />
                </el-icon>
                <h3 class="text-lg font-medium text-gray-900">
                  Станции
                </h3>
              </div>
              <p class="text-sm text-gray-500 mb-4">
                Управление компрессорными станциями, их описаниями, оборудованием и курсами
              </p>
              <el-button
                text
                type="primary"
                size="small"
              >
                Перейти
                <el-icon class="ml-1">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- Analytics Card -->
        <el-card
          shadow="hover"
          class="cursor-pointer"
          @click="$router.push('/admin/course-analytics')"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-3">
                <el-icon class="text-purple-600 mr-2" :size="20">
                  <DataLine />
                </el-icon>
                <h3 class="text-lg font-medium text-gray-900">
                  Аналитика курсов
                </h3>
              </div>
              <p class="text-sm text-gray-500 mb-4">
                Подписки, прогресс, материалы и результаты тестов по станциям
              </p>
              <el-button
                text
                type="primary"
                size="small"
              >
                Перейти
                <el-icon class="ml-1">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- Departments Card -->
        <el-card
          shadow="hover"
          class="cursor-pointer"
          @click="$router.push('/admin/departments')"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-3">
                <el-icon class="text-green-600 mr-2" :size="20">
                  <Folder />
                </el-icon>
                <h3 class="text-lg font-medium text-gray-900">
                  Отделы
                </h3>
              </div>
              <p class="text-sm text-gray-500 mb-4">
                Управление структурными подразделениями компании, их описаниями и изображениями
              </p>
              <el-button
                text
                type="primary"
                size="small"
              >
                Перейти
                <el-icon class="ml-1">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Statistics -->
      <el-card>
        <template #header>
          <div class="text-base font-medium text-gray-900">
            Статистика
          </div>
        </template>
        <el-row :gutter="16">
          <el-col :xs="12" :sm="4">
            <div class="text-center py-4">
              <div class="text-2xl font-semibold text-gray-900 mb-1">
                {{ stationsCount }}
              </div>
              <div class="text-xs text-gray-500">
                Станций
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="4">
            <div class="text-center py-4">
              <div class="text-2xl font-semibold text-gray-900 mb-1">
                {{ departmentsCount }}
              </div>
              <div class="text-xs text-gray-500">
                Отделов
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="4">
            <div class="text-center py-4">
              <el-tag type="success" size="small">
                Активна
              </el-tag>
              <div class="text-xs text-gray-500 mt-1">
                Система
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, OfficeBuilding, Folder, DataLine } from '@element-plus/icons-vue'
import stationService from '@/services/stationService'
import departmentService from '@/services/departmentService'

const stationsCount = ref(0)
const departmentsCount = ref(0)

const loadStats = async () => {
  try {
    // Load stations count
    const stations = await stationService.getStations()
    stationsCount.value = stations.length || 0

    // Load departments count
    const departments = await departmentService.getDepartments()
    departmentsCount.value = departments.length || 0
  } catch (error) {
    console.error('Error loading stats:', error)
    ElMessage.warning('Не удалось загрузить статистику')
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
:deep(.el-card) {
  border: 1px solid #e5e7eb;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>

