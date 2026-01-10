<template>
  <div class="test-questions-editor">
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-md font-semibold">
        Вопросы теста
      </h4>
      <div class="flex gap-2">
        <el-button
          v-if="questions.length > 0 && testData"
          type="info"
          size="small"
          @click="exportToJSON"
        >
          <el-icon class="mr-1">
            <Download />
          </el-icon>
          Экспорт в JSON
        </el-button>
        <el-button
          type="primary"
          size="small"
          @click="addQuestion"
        >
          <el-icon class="mr-1">
            <Plus />
          </el-icon>
          Добавить вопрос
        </el-button>
      </div>
    </div>

    <div
      v-if="questions.length === 0"
      class="text-center py-8 text-gray-500"
    >
      Нет вопросов. Добавьте первый вопрос.
    </div>

    <div
      v-for="(question, qIndex) in questions"
      :key="qIndex"
      class="mb-4 p-4 border border-gray-200 rounded-lg"
    >
      <div class="flex items-start justify-between mb-3">
        <h5 class="text-sm font-semibold">
          Вопрос {{ qIndex + 1 }}
        </h5>
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

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Баллы">
              <el-input-number
                v-model="question.points"
                :min="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Изображение">
              <el-input
                v-model="question.image"
                placeholder="URL изображения или MinIO key"
              />
            </el-form-item>
          </el-col>
        </el-row>

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
      v-if="questions.length > 0"
      type="success"
      size="large"
      :loading="saving"
      class="mt-4 w-full"
      @click="handleSave"
    >
      <el-icon class="mr-2">
        <Check />
      </el-icon>
      Сохранить все вопросы
    </el-button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Plus, Delete, Close, Check, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import testService from '@/services/testService'

const props = defineProps({
  testId: {
    type: Number,
    required: true
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save'])

const questions = ref([])
const loading = ref(false)
const testData = ref(null)

const loadQuestions = async () => {
  if (!props.testId) return

  loading.value = true
  try {
    const test = await testService.getTest(props.testId, 'final')
    testData.value = test
    questions.value = (test.questions || []).map(q => ({
      question: q.question || '',
      options: [...(q.options || [])],
      correctAnswer: q.correctAnswer !== undefined ? q.correctAnswer : 0,
      points: q.points || 1,
      image: q.image || '',
      explanation: q.explanation || ''
    }))
  } catch (error) {
    ElMessage.error('Ошибка загрузки вопросов: ' + error.message)
  } finally {
    loading.value = false
  }
}

const addQuestion = () => {
  questions.value.push({
    question: '',
    options: ['', ''],
    correctAnswer: 0,
    points: 1,
    image: '',
    explanation: ''
  })
}

const removeQuestion = (index) => {
  questions.value.splice(index, 1)
}

const addOption = (questionIndex) => {
  if (questions.value[questionIndex].options.length < 10) {
    questions.value[questionIndex].options.push('')
  } else {
    ElMessage.warning('Максимум 10 вариантов ответа')
  }
}

const removeOption = (questionIndex, optionIndex) => {
  if (questions.value[questionIndex].options.length > 2) {
    questions.value[questionIndex].options.splice(optionIndex, 1)
    // Adjust correct answer if needed
    if (questions.value[questionIndex].correctAnswer >= optionIndex) {
      questions.value[questionIndex].correctAnswer = Math.max(0, questions.value[questionIndex].correctAnswer - 1)
    }
  } else {
    ElMessage.warning('Минимум 2 варианта ответа')
  }
}

const handleSave = async () => {
  // Validate questions
  for (let i = 0; i < questions.value.length; i++) {
    const q = questions.value[i]
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

  emit('save', props.testId, questions.value)
}

const exportToJSON = () => {
  if (!questions.value || questions.value.length === 0) {
    ElMessage.warning('Нет вопросов для экспорта')
    return
  }

  if (!testData.value) {
    ElMessage.warning('Данные теста не загружены')
    return
  }

  try {
    // Преобразуем данные теста в формат testsData.json
    const exportData = {
      id: `test-final-${testData.value.id}`,
      lessonIndex: null,
      topicIndex: null,
      isFinalTest: true,
      title: testData.value.title || '',
      description: testData.value.description || '',
      timeLimit: testData.value.time_limit || 30,
      passingScore: testData.value.passing_score || 70,
      attempts: testData.value.attempts || null,
      questions: questions.value.map((q, index) => ({
        id: `q${index + 1}`,
        question: q.question || '',
        options: Array.isArray(q.options) ? q.options : [],
        correctAnswer: q.correctAnswer !== undefined && q.correctAnswer !== null ? q.correctAnswer : 0,
        points: q.points || 1,
        image: q.image || '',
        explanation: q.explanation || ''
      }))
    }

    // Создаем JSON строку с форматированием (2 пробела для отступов)
    const jsonString = JSON.stringify(exportData, null, 2)
    
    // Создаем blob и скачиваем файл
    const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // Генерируем безопасное имя файла
    const safeTitle = (testData.value.title || 'test')
      .replace(/[^a-z0-9а-яё\s]/gi, '_')
      .replace(/\s+/g, '_')
      .toLowerCase()
      .substring(0, 50)
    
    link.download = `test_${testData.value.id}_${safeTitle}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('Тест успешно экспортирован в JSON')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('Ошибка экспорта: ' + error.message)
  }
}

watch(() => props.testId, (newId) => {
  if (newId) {
    loadQuestions()
  } else {
    questions.value = []
    testData.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.test-questions-editor {
  max-height: 600px;
  overflow-y: auto;
}
</style>

