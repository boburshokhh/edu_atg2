<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center mb-6">
      <el-button
        class="mr-4"
        @click="$router.push('/admin')"
      >
        <el-icon class="mr-2">
          <ArrowLeft />
        </el-icon>
        Назад
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">
        Результаты тестов
      </h1>
    </div>

    <!-- Filters -->
    <el-card class="mb-6">
      <el-form
        :inline="true"
        label-width="120px"
      >
        <el-form-item label="Тип теста">
          <el-select
            v-model="filters.test_type"
            clearable
            placeholder="Все типы"
            style="width: 200px"
            @change="loadResults"
          >
            <el-option
              label="Тест урока"
              value="lesson"
            />
            <el-option
              label="Финальный тест"
              value="final"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="ID теста">
          <el-input-number
            v-model="filters.test_id"
            :min="1"
            clearable
            style="width: 150px"
            @change="loadResults"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="loadResults"
          >
            <el-icon class="mr-2">
              <Search />
            </el-icon>
            Поиск
          </el-button>
          <el-button @click="resetFilters">
            Сбросить
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Results Table -->
    <el-card v-loading="loading">
      <el-table
        :data="results"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
        />
        <el-table-column
          prop="test_type"
          label="Тип"
          width="120"
        >
          <template #default="{ row }">
            <el-tag
              :type="row.test_type === 'lesson' ? 'primary' : 'success'"
              size="small"
            >
              {{ row.test_type === 'lesson' ? 'Урок' : 'Финальный' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="test_id"
          label="ID теста"
          width="100"
          align="center"
        />
        <el-table-column
          prop="user_name"
          label="Пользователь"
          min-width="150"
        />
        <el-table-column
          prop="score"
          label="Балл"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <span
              :class="[
                'font-bold',
                row.is_passed ? 'text-green-600' : 'text-red-600'
              ]"
            >
              {{ row.score }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column
          prop="correct_answers"
          label="Правильно"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            {{ row.correct_answers }} / {{ row.total_questions }}
          </template>
        </el-table-column>
        <el-table-column
          prop="is_passed"
          label="Статус"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              :type="row.is_passed ? 'success' : 'danger'"
              size="small"
            >
              {{ row.is_passed ? 'Пройден' : 'Не пройден' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="time_spent"
          label="Время (сек)"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            {{ row.time_spent || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="completed_at"
          label="Дата прохождения"
          width="180"
        >
          <template #default="{ row }">
            {{ formatDate(row.completed_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="Действия"
          width="120"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewDetails(row)"
            >
              Детали
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div
        v-if="results.length === 0 && !loading"
        class="text-center py-8 text-gray-500"
      >
        Нет результатов
      </div>
    </el-card>

    <!-- Result Details Dialog -->
    <el-dialog
      v-model="showDetailsDialog"
      title="Детали результата"
      width="800px"
    >
      <div
        v-if="selectedResult"
        class="space-y-4"
      >
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="ID результата">
            {{ selectedResult.id }}
          </el-descriptions-item>
          <el-descriptions-item label="Тип теста">
            <el-tag
              :type="selectedResult.test_type === 'lesson' ? 'primary' : 'success'"
              size="small"
            >
              {{ selectedResult.test_type === 'lesson' ? 'Урок' : 'Финальный' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="ID теста">
            {{ selectedResult.test_id }}
          </el-descriptions-item>
          <el-descriptions-item label="Пользователь">
            {{ selectedResult.user_name }}
          </el-descriptions-item>
          <el-descriptions-item label="Балл">
            <span
              :class="[
                'font-bold text-lg',
                selectedResult.is_passed ? 'text-green-600' : 'text-red-600'
              ]"
            >
              {{ selectedResult.score }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Статус">
            <el-tag
              :type="selectedResult.is_passed ? 'success' : 'danger'"
              size="small"
            >
              {{ selectedResult.is_passed ? 'Пройден' : 'Не пройден' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Правильных ответов">
            {{ selectedResult.correct_answers }} / {{ selectedResult.total_questions }}
          </el-descriptions-item>
          <el-descriptions-item label="Время">
            {{ selectedResult.time_spent ? selectedResult.time_spent + ' сек' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item
            label="Дата прохождения"
            :span="2"
          >
            {{ formatDate(selectedResult.completed_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <div
          v-if="selectedResult.answers_data"
          class="mt-4"
        >
          <h3 class="text-lg font-semibold mb-2">
            Ответы пользователя:
          </h3>
          <pre class="bg-gray-50 p-4 rounded text-sm overflow-auto">{{ JSON.stringify(selectedResult.answers_data, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import testService from '@/services/testService'

const router = useRouter()

const loading = ref(false)
const results = ref([])
const showDetailsDialog = ref(false)
const selectedResult = ref(null)

const filters = ref({
  test_type: null,
  test_id: null,
  user_id: null
})

const loadResults = async () => {
  loading.value = true
  try {
    const filterData = {}
    if (filters.value.test_type) filterData.test_type = filters.value.test_type
    if (filters.value.test_id) filterData.test_id = filters.value.test_id
    if (filters.value.user_id) filterData.user_id = filters.value.user_id

    const data = await testService.getTestResults(filterData)
    results.value = data
  } catch (error) {
    ElMessage.error('Ошибка загрузки результатов: ' + error.message)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    test_type: null,
    test_id: null,
    user_id: null
  }
  loadResults()
}

const viewDetails = async (result) => {
  try {
    const data = await testService.getTestResult(result.id)
    selectedResult.value = data
    showDetailsDialog.value = true
  } catch (error) {
    ElMessage.error('Ошибка загрузки деталей: ' + error.message)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadResults()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

