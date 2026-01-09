<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <div>
        <el-button
          class="mr-4"
          @click="$router.push('/admin')"
        >
          <el-icon class="mr-2">
            <ArrowLeft />
          </el-icon>
          Назад
        </el-button>
        <h1 class="text-2xl font-bold text-gray-800 inline-block">
          Управление тестами
        </h1>
      </div>
      <el-button
        type="primary"
        @click="showCreateDialog = true"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon>
        Создать тест
      </el-button>
    </div>

    <el-tabs
      v-model="activeTab"
      @tab-change="loadTests"
    >
      <el-tab-pane
        label="Тесты уроков"
        name="lesson"
      />
      <el-tab-pane
        label="Финальные тесты"
        name="final"
      />
    </el-tabs>

    <el-table
      v-loading="loading"
      :data="tests"
      stripe
      style="width: 100%"
      class="mt-4"
    >
      <el-table-column
        prop="title"
        label="Название"
        min-width="200"
      />
      <el-table-column
        prop="description"
        label="Описание"
        min-width="250"
        show-overflow-tooltip
      />
      <el-table-column
        prop="questions_count"
        label="Вопросов"
        width="100"
        align="center"
      />
      <el-table-column
        prop="passing_score"
        label="Проходной балл"
        width="130"
        align="center"
      >
        <template #default="{ row }">
          {{ row.passing_score }}%
        </template>
      </el-table-column>
      <el-table-column
        prop="time_limit"
        label="Время (мин)"
        width="120"
        align="center"
      />
      <el-table-column
        prop="attempts"
        label="Попыток"
        width="100"
        align="center"
      >
        <template #default="{ row }">
          {{ row.attempts || '∞' }}
        </template>
      </el-table-column>
      <el-table-column
        prop="is_active"
        label="Статус"
        width="100"
        align="center"
      >
        <template #default="{ row }">
          <el-tag
            :type="row.is_active ? 'success' : 'info'"
            size="small"
          >
            {{ row.is_active ? 'Активен' : 'Неактивен' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="Действия"
        width="200"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="editTest(row)"
          >
            Редактировать
          </el-button>
          <el-popconfirm
            title="Удалить тест?"
            @confirm="deleteTest(row)"
          >
            <template #reference>
              <el-button
                type="danger"
                size="small"
              >
                Удалить
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create Test Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="Создать тест"
      width="600px"
    >
      <el-form
        :model="newTest"
        label-width="150px"
      >
        <el-form-item
          label="Тип теста"
          required
        >
          <el-select
            v-model="newTest.test_type"
            style="width: 100%"
            @change="onTestTypeChange"
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

        <el-form-item
          v-if="newTest.test_type === 'lesson'"
          label="ID урока"
          required
        >
          <el-input-number
            v-model="newTest.lesson_id"
            :min="1"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item
          v-if="newTest.test_type === 'final'"
          label="ID программы курса"
          required
        >
          <el-input-number
            v-model="newTest.course_program_id"
            :min="1"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item
          label="Название"
          required
        >
          <el-input
            v-model="newTest.title"
            placeholder="Введите название теста"
          />
        </el-form-item>

        <el-form-item label="Описание">
          <el-input
            v-model="newTest.description"
            type="textarea"
            :rows="3"
            placeholder="Введите описание теста"
          />
        </el-form-item>

        <el-form-item label="Проходной балл (%)">
          <el-input-number
            v-model="newTest.passing_score"
            :min="0"
            :max="100"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="Время (минут)">
          <el-input-number
            v-model="newTest.time_limit"
            :min="1"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="Попыток">
          <el-input-number
            v-model="newTest.attempts"
            :min="1"
            style="width: 100%"
            placeholder="Оставьте пустым для неограниченного"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          :loading="creating"
          @click="createTest"
        >
          Создать
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import testService from '@/services/testService'

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const activeTab = ref('lesson')
const tests = ref([])
const showCreateDialog = ref(false)

const newTest = ref({
  test_type: 'lesson',
  lesson_id: null,
  course_program_id: null,
  title: '',
  description: '',
  passing_score: 70,
  time_limit: 30,
  attempts: null
})

const loadTests = async () => {
  loading.value = true
  try {
    const data = await testService.getTests(activeTab.value)
    tests.value = data
  } catch (error) {
    ElMessage.error('Ошибка загрузки тестов: ' + error.message)
  } finally {
    loading.value = false
  }
}

const onTestTypeChange = () => {
  newTest.value.lesson_id = null
  newTest.value.course_program_id = null
}

const createTest = async () => {
  if (!newTest.value.title) {
    ElMessage.warning('Введите название теста')
    return
  }

  if (newTest.value.test_type === 'lesson' && !newTest.value.lesson_id) {
    ElMessage.warning('Введите ID урока')
    return
  }

  if (newTest.value.test_type === 'final' && !newTest.value.course_program_id) {
    ElMessage.warning('Введите ID программы курса')
    return
  }

  creating.value = true
  try {
    const result = await testService.createTest(newTest.value)
    ElMessage.success('Тест создан')
    showCreateDialog.value = false
    newTest.value = {
      test_type: 'lesson',
      lesson_id: null,
      course_program_id: null,
      title: '',
      description: '',
      passing_score: 70,
      time_limit: 30,
      attempts: null
    }
    await loadTests()
    // Navigate to editor
    router.push(`/admin/tests/${result.test_type}/${result.id}`)
  } catch (error) {
    ElMessage.error('Ошибка создания теста: ' + error.message)
  } finally {
    creating.value = false
  }
}

const editTest = (test) => {
  router.push(`/admin/tests/${test.test_type}/${test.id}`)
}

const deleteTest = async (test) => {
  try {
    await testService.deleteTest(test.id, test.test_type)
    ElMessage.success('Тест удален')
    await loadTests()
  } catch (error) {
    ElMessage.error('Ошибка удаления теста: ' + error.message)
  }
}

onMounted(() => {
  loadTests()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

