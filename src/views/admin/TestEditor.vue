<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center mb-6">
      <el-button
        class="mr-4"
        @click="$router.push('/admin/tests')"
      >
        <el-icon class="mr-2">
          <ArrowLeft />
        </el-icon>
        Назад
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">
        {{ isEditing ? `Редактирование теста: ${test.title || 'Загрузка...'}` : 'Новый тест' }}
      </h1>
    </div>

    <el-card
      v-loading="loading"
      class="mb-6"
    >
      <el-form
        :model="test"
        label-width="200px"
        class="max-w-4xl"
      >
        <el-form-item
          label="Название"
          required
        >
          <el-input
            v-model="test.title"
            placeholder="Введите название теста"
          />
        </el-form-item>

        <el-form-item label="Описание">
          <el-input
            v-model="test.description"
            type="textarea"
            :rows="3"
            placeholder="Введите описание теста"
          />
        </el-form-item>

        <el-form-item label="Проходной балл (%)">
          <el-input-number
            v-model="test.passing_score"
            :min="0"
            :max="100"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="Время (минут)">
          <el-input-number
            v-model="test.time_limit"
            :min="1"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="Попыток">
          <el-input-number
            v-model="test.attempts"
            :min="1"
            style="width: 200px"
            placeholder="Оставьте пустым для неограниченного"
          />
        </el-form-item>

        <el-form-item label="Статус">
          <el-switch
            v-model="test.is_active"
            active-text="Активен"
            inactive-text="Неактивен"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="saving"
            @click="saveTest"
          >
            Сохранить настройки
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Questions Section -->
    <el-card>
      <template #header>
        <div class="flex items-center justify-between">
          <span class="text-lg font-semibold">Вопросы теста</span>
          <el-button
            type="primary"
            @click="addQuestion"
          >
            <el-icon class="mr-2">
              <Plus />
            </el-icon>
            Добавить вопрос
          </el-button>
        </div>
      </template>

      <div
        v-if="test.questions && test.questions.length === 0"
        class="text-center py-8 text-gray-500"
      >
        Нет вопросов. Добавьте первый вопрос.
      </div>

      <div
        v-for="(question, qIndex) in test.questions"
        :key="qIndex"
        class="mb-6 p-4 border border-gray-200 rounded-lg"
      >
        <div class="flex items-start justify-between mb-4">
          <h3 class="text-lg font-semibold">
            Вопрос {{ qIndex + 1 }}
          </h3>
          <el-button
            type="danger"
            size="small"
            @click="removeQuestion(qIndex)"
          >
            <el-icon class="mr-1">
              <Delete />
            </el-icon>
            Удалить
          </el-button>
        </div>

        <el-form
          :model="question"
          label-width="120px"
        >
          <el-form-item
            label="Текст вопроса"
            required
          >
            <el-input
              v-model="question.question"
              type="textarea"
              :rows="2"
              placeholder="Введите текст вопроса"
            />
          </el-form-item>

          <el-form-item label="Баллы">
            <el-input-number
              v-model="question.points"
              :min="1"
              style="width: 150px"
            />
          </el-form-item>

          <el-form-item label="Изображение">
            <el-input
              v-model="question.image"
              placeholder="URL изображения или MinIO key"
            />
          </el-form-item>

          <el-form-item label="Пояснение">
            <el-input
              v-model="question.explanation"
              type="textarea"
              :rows="2"
              placeholder="Пояснение к правильному ответу"
            />
          </el-form-item>

          <el-form-item label="Варианты ответов">
            <div class="space-y-2 w-full">
              <div
                v-for="(option, optIndex) in question.options"
                :key="optIndex"
                class="flex items-center gap-2"
              >
                <el-radio
                  v-model="question.correctAnswer"
                  :label="optIndex"
                  class="mr-2"
                >
                  Правильный
                </el-radio>
                <el-input
                  v-model="question.options[optIndex]"
                  :placeholder="`Вариант ${String.fromCharCode(65 + optIndex)}`"
                  class="flex-1"
                />
                <el-button
                  type="danger"
                  size="small"
                  :disabled="question.options.length <= 2"
                  @click="removeOption(qIndex, optIndex)"
                >
                  <el-icon>
                    <Close />
                  </el-icon>
                </el-button>
              </div>
              <el-button
                type="primary"
                size="small"
                @click="addOption(qIndex)"
              >
                <el-icon class="mr-1">
                  <Plus />
                </el-icon>
                Добавить вариант
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <el-button
        v-if="test.questions && test.questions.length > 0"
        type="success"
        size="large"
        :loading="savingQuestions"
        class="mt-4"
        @click="saveQuestions"
      >
        <el-icon class="mr-2">
          <Check />
        </el-icon>
        Сохранить все вопросы
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete, Close, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import testService from '@/services/testService'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const savingQuestions = ref(false)

const test = ref({
  id: null,
  title: '',
  description: '',
  passing_score: 70,
  time_limit: 30,
  attempts: null,
  is_active: true,
  questions: []
})

const isEditing = computed(() => {
  return route.params.testId && route.params.testId !== 'new'
})

const loadTest = async () => {
  if (!isEditing.value) {
    return
  }

  loading.value = true
  try {
    const testType = route.params.testType
    const testId = parseInt(route.params.testId)
    const data = await testService.getTest(testId, testType)
    
    if (data) {
      test.value = {
        id: data.id,
        title: data.title || '',
        description: data.description || '',
        passing_score: data.passing_score || 70,
        time_limit: data.time_limit || 30,
        attempts: data.attempts,
        is_active: data.is_active !== undefined ? data.is_active : true,
        questions: data.questions || []
      }
    }
  } catch (error) {
    ElMessage.error('Ошибка загрузки теста: ' + error.message)
  } finally {
    loading.value = false
  }
}

const saveTest = async () => {
  if (!test.value.title) {
    ElMessage.warning('Введите название теста')
    return
  }

  saving.value = true
  try {
    const testType = route.params.testType
    const testId = test.value.id

    if (isEditing.value) {
      await testService.updateTest(testId, testType, {
        title: test.value.title,
        description: test.value.description,
        passing_score: test.value.passing_score,
        time_limit: test.value.time_limit,
        attempts: test.value.attempts,
        is_active: test.value.is_active
      })
      ElMessage.success('Настройки теста сохранены')
    } else {
      ElMessage.warning('Сначала создайте тест')
    }
  } catch (error) {
    ElMessage.error('Ошибка сохранения: ' + error.message)
  } finally {
    saving.value = false
  }
}

const addQuestion = () => {
  if (!test.value.questions) {
    test.value.questions = []
  }
  test.value.questions.push({
    question: '',
    options: ['', ''],
    correctAnswer: 0,
    points: 1,
    image: '',
    explanation: ''
  })
}

const removeQuestion = (index) => {
  test.value.questions.splice(index, 1)
}

const addOption = (questionIndex) => {
  if (test.value.questions[questionIndex].options.length < 10) {
    test.value.questions[questionIndex].options.push('')
  } else {
    ElMessage.warning('Максимум 10 вариантов ответа')
  }
}

const removeOption = (questionIndex, optionIndex) => {
  if (test.value.questions[questionIndex].options.length > 2) {
    test.value.questions[questionIndex].options.splice(optionIndex, 1)
    // Adjust correct answer if needed
    if (test.value.questions[questionIndex].correctAnswer >= optionIndex) {
      test.value.questions[questionIndex].correctAnswer = Math.max(0, test.value.questions[questionIndex].correctAnswer - 1)
    }
  } else {
    ElMessage.warning('Минимум 2 варианта ответа')
  }
}

const saveQuestions = async () => {
  // Validate questions
  for (let i = 0; i < test.value.questions.length; i++) {
    const q = test.value.questions[i]
    if (!q.question || !q.question.trim()) {
      ElMessage.warning(`Вопрос ${i + 1}: введите текст вопроса`)
      return
    }
    if (q.options.length < 2) {
      ElMessage.warning(`Вопрос ${i + 1}: минимум 2 варианта ответа`)
      return
    }
    const hasEmptyOptions = q.options.some(opt => !opt || !opt.trim())
    if (hasEmptyOptions) {
      ElMessage.warning(`Вопрос ${i + 1}: все варианты ответа должны быть заполнены`)
      return
    }
    if (q.correctAnswer === null || q.correctAnswer === undefined) {
      ElMessage.warning(`Вопрос ${i + 1}: выберите правильный ответ`)
      return
    }
  }

  savingQuestions.value = true
  try {
    const testType = route.params.testType
    const testId = test.value.id

    if (!isEditing.value || !testId) {
      ElMessage.warning('Сначала сохраните настройки теста')
      return
    }

    await testService.updateTestQuestions(testId, testType, test.value.questions)
    ElMessage.success('Вопросы сохранены')
  } catch (error) {
    ElMessage.error('Ошибка сохранения вопросов: ' + error.message)
  } finally {
    savingQuestions.value = false
  }
}

onMounted(() => {
  loadTest()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

