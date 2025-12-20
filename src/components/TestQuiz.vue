<template>
  <div class="test-quiz">
    <!-- Test Header -->
    <div v-if="!testStarted && !testCompleted" class="test-intro">
      <el-card shadow="hover" class="intro-card">
        <div class="text-center">
          <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <el-icon :size="40" class="text-white">
              <Document />
            </el-icon>
          </div>
          
          <h2 class="text-2xl font-bold text-gray-900 mb-3">{{ testData.title }}</h2>
          <p class="text-gray-600 mb-6">{{ testData.description }}</p>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="stat-card">
              <div class="text-2xl font-bold text-blue-600">{{ testData.questions?.length || 0 }}</div>
              <div class="text-xs text-gray-600">Вопросов</div>
            </div>
            <div class="stat-card">
              <div class="text-2xl font-bold text-green-600">{{ testData.passingScore || 70 }}%</div>
              <div class="text-xs text-gray-600">Проходной балл</div>
            </div>
            <div class="stat-card">
              <div class="text-2xl font-bold text-purple-600">{{ testData.timeLimit || 30 }}</div>
              <div class="text-xs text-gray-600">Минут</div>
            </div>
            <div class="stat-card">
              <div class="text-2xl font-bold text-orange-600">{{ testData.attempts || '∞' }}</div>
              <div class="text-xs text-gray-600">Попыток</div>
            </div>
          </div>

          <el-button type="primary" size="large" @click="startTest" class="px-8">
            <el-icon class="mr-2"><VideoPlay /></el-icon>
            Начать тест
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- Test Progress -->
    <div v-if="testStarted && !testCompleted" class="test-content">
      <!-- Progress Bar -->
      <div class="sticky top-0 z-10 bg-white border-b border-gray-200 p-2 shadow-sm">
        <div class="max-w-4xl mx-auto">
          <div class="flex items-center justify-between mb-1.5">
            <div class="flex items-center gap-3">
              <span class="text-xs font-semibold text-gray-600">
                Вопрос {{ currentQuestionIndex + 1 }} / {{ testData.questions.length }}
              </span>
              <el-tag v-if="timeRemaining" :type="timeRemaining < 300 ? 'danger' : 'info'" size="small" effect="plain" class="!border-none !bg-gray-100">
                <el-icon class="mr-1"><Timer /></el-icon>
                {{ formatTime(timeRemaining) }}
              </el-tag>
            </div>
            <el-button type="danger" text bg size="small" @click="confirmExit">
              <el-icon class="mr-1"><Close /></el-icon>
              Выйти
            </el-button>
          </div>
          <el-progress 
            :percentage="progress" 
            :stroke-width="4"
            :show-text="false"
            :color="progressColor"
          />
        </div>
      </div>

      <!-- Question Card -->
      <div class="max-w-3xl mx-auto p-3 md:p-4">
        <el-card shadow="never" class="question-card border-none !shadow-none md:!border md:!shadow-sm md:rounded-xl">
          <div class="mb-4">
            <div class="flex items-start gap-3 mb-3">
              <div class="w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center flex-shrink-0 border border-blue-100">
                <span class="text-blue-600 font-bold text-sm">{{ currentQuestionIndex + 1 }}</span>
              </div>
              <div class="flex-1">
                <h3 class="text-base font-bold text-gray-900 mb-1 leading-tight">
                  {{ currentQuestion.question }}
                </h3>
                <el-tag v-if="currentQuestion.points" size="small" type="warning" effect="plain" class="!h-5 !px-1.5 !text-xs">
                  {{ currentQuestion.points }} {{ currentQuestion.points === 1 ? 'балл' : 'балла' }}
                </el-tag>
              </div>
            </div>

            <!-- Image if exists -->
            <div v-if="currentQuestion.image" class="mb-3">
              <img :src="currentQuestion.image" :alt="currentQuestion.question" class="max-w-full rounded-lg border border-gray-100" />
            </div>
          </div>

          <!-- Answer Options -->
          <div class="space-y-2 mb-4">
            <div
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              @click="selectAnswer(index)"
              :class="[
                'option-card',
                selectedAnswers[currentQuestionIndex] === index ? 'selected' : '',
                showExplanation && index === currentQuestion.correctAnswer ? 'correct' : '',
                showExplanation && selectedAnswers[currentQuestionIndex] === index && index !== currentQuestion.correctAnswer ? 'incorrect' : ''
              ]"
            >
              <div class="flex items-center gap-3">
                <div class="option-indicator text-xs">
                  <span>{{ String.fromCharCode(65 + index) }}</span>
                </div>
                <span class="flex-1 text-sm text-gray-700 leading-snug">{{ option }}</span>
                <el-icon v-if="showExplanation && index === currentQuestion.correctAnswer" class="text-green-600">
                  <Check />
                </el-icon>
                <el-icon v-if="showExplanation && selectedAnswers[currentQuestionIndex] === index && index !== currentQuestion.correctAnswer" class="text-red-600">
                  <Close />
                </el-icon>
              </div>
            </div>
          </div>

          <!-- Navigation - перемещено внутрь карточки выше -->
          <div class="border-t border-gray-100 pt-4 mt-4">
            <div class="flex items-center justify-between flex-wrap gap-3">
              <el-button
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
                :icon="ArrowLeft"
                size="default"
              >
                Назад
              </el-button>

              <div class="flex flex-col items-end gap-1.5">
                <div class="flex gap-2">
                  <el-button
                    v-if="currentQuestionIndex < testData.questions.length - 1"
                    @click="nextQuestion"
                    type="primary"
                    :disabled="selectedAnswers[currentQuestionIndex] === undefined || selectedAnswers[currentQuestionIndex] === null"
                    size="default"
                  >
                    Далее
                    <el-icon class="ml-2"><ArrowRight /></el-icon>
                  </el-button>
                  <el-button
                    v-else
                    @click="submitTest"
                    type="success"
                    :disabled="selectedAnswers[currentQuestionIndex] === undefined || selectedAnswers[currentQuestionIndex] === null"
                    size="default"
                  >
                    Завершить тест
                    <el-icon class="ml-2"><Check /></el-icon>
                  </el-button>
                </div>
                <p 
                  v-if="selectedAnswers[currentQuestionIndex] === undefined || selectedAnswers[currentQuestionIndex] === null"
                  class="text-xs text-gray-500 text-right"
                >
                  Выберите ответ, чтобы продолжить
                </p>
              </div>
            </div>
          </div>

          <!-- Explanation -->
          <el-alert
            v-if="showExplanation && currentQuestion.explanation"
            :type="selectedAnswers[currentQuestionIndex] === currentQuestion.correctAnswer ? 'success' : 'info'"
            :closable="false"
            class="mt-4"
          >
            <template #title>
              <strong>Пояснение:</strong>
            </template>
            {{ currentQuestion.explanation }}
          </el-alert>
        </el-card>

        <!-- Question Navigator - REMOVED as requested -->
        <!-- <div class="mt-4">
          <el-card shadow="never" class="bg-gray-50">
            <div class="text-sm font-semibold text-gray-700 mb-2">Навигация по вопросам:</div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="(q, index) in testData.questions"
                :key="index"
                @click="goToQuestion(index)"
                :class="[
                  'question-nav-btn',
                  currentQuestionIndex === index ? 'active' : '',
                  selectedAnswers[index] !== undefined ? 'answered' : ''
                ]"
              >
                {{ index + 1 }}
              </button>
            </div>
          </el-card>
        </div> -->
      </div>
    </div>

    <!-- Test Results -->
    <div v-if="testCompleted" class="test-results">
      <el-card shadow="hover" class="results-card">
        <div class="text-center">
          <div 
            :class="[
              'w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-6',
              isPassed ? 'bg-gradient-to-br from-green-400 to-green-600' : 'bg-gradient-to-br from-red-400 to-red-600'
            ]"
          >
            <el-icon :size="60" class="text-white">
              <component :is="isPassed ? SuccessFilled : CircleCloseFilled" />
            </el-icon>
          </div>

          <h2 class="text-3xl font-bold mb-2" :class="isPassed ? 'text-green-600' : 'text-red-600'">
            {{ isPassed ? 'Тест пройден!' : 'Тест не пройден' }}
          </h2>
          <p class="text-xl text-gray-600 mb-6">
            Ваш результат: <strong class="text-2xl">{{ score }}%</strong>
          </p>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="result-stat">
              <div class="text-3xl font-bold text-blue-600">{{ correctAnswersCount }}</div>
              <div class="text-sm text-gray-600">Правильных</div>
            </div>
            <div class="result-stat">
              <div class="text-3xl font-bold text-red-600">{{ wrongAnswersCount }}</div>
              <div class="text-sm text-gray-600">Неправильных</div>
            </div>
            <div class="result-stat">
              <div class="text-3xl font-bold text-green-600">{{ score }}%</div>
              <div class="text-sm text-gray-600">Процент</div>
            </div>
            <div class="result-stat">
              <div class="text-3xl font-bold text-purple-600">{{ testData.passingScore }}%</div>
              <div class="text-sm text-gray-600">Проходной</div>
            </div>
          </div>

          <el-alert
            v-if="isPassed"
            type="success"
            :closable="false"
            class="mb-6"
          >
            <template #title>
              Поздравляем! Вы успешно прошли тест и можете перейти к следующему уроку.
            </template>
          </el-alert>

          <el-alert
            v-else
            type="warning"
            :closable="false"
            class="mb-6"
          >
            <template #title>
              К сожалению, вы не набрали проходной балл. Рекомендуем повторить материал и попробовать еще раз.
            </template>
          </el-alert>

          <div class="flex gap-4 justify-center">
            <el-button @click="reviewAnswers" size="large">
              <el-icon class="mr-2"><View /></el-icon>
              Просмотреть ответы
            </el-button>
            <el-button type="primary" @click="retryTest" size="large" v-if="!isPassed">
              <el-icon class="mr-2"><RefreshRight /></el-icon>
              Попробовать снова
            </el-button>
            <el-button type="success" @click="$emit('test-completed', { score, isPassed })" size="large" v-if="isPassed">
              <el-icon class="mr-2"><ArrowRight /></el-icon>
              Продолжить обучение
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  VideoPlay,
  Timer,
  Close,
  Check,
  ArrowLeft,
  ArrowRight,
  SuccessFilled,
  CircleCloseFilled,
  View,
  RefreshRight
} from '@element-plus/icons-vue'

const props = defineProps({
  testData: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['test-completed', 'test-started'])

// State
const testStarted = ref(false)
const testCompleted = ref(false)
const currentQuestionIndex = ref(0)
const selectedAnswers = ref({})
const timeRemaining = ref(0)
const timerInterval = ref(null)
const showExplanation = ref(false)

// Computed
const currentQuestion = computed(() => {
  return props.testData.questions[currentQuestionIndex.value]
})

const progress = computed(() => {
  return Math.round(((currentQuestionIndex.value + 1) / props.testData.questions.length) * 100)
})

const progressColor = computed(() => {
  if (progress.value < 30) return '#f56c6c'
  if (progress.value < 70) return '#e6a23c'
  return '#67c23a'
})

const allQuestionsAnswered = computed(() => {
  return props.testData.questions.every((_, index) => selectedAnswers.value[index] !== undefined)
})

const correctAnswersCount = computed(() => {
  let count = 0
  props.testData.questions.forEach((q, index) => {
    if (selectedAnswers.value[index] === q.correctAnswer) {
      count++
    }
  })
  return count
})

const wrongAnswersCount = computed(() => {
  return props.testData.questions.length - correctAnswersCount.value
})

const score = computed(() => {
  return Math.round((correctAnswersCount.value / props.testData.questions.length) * 100)
})

const isPassed = computed(() => {
  return score.value >= (props.testData.passingScore || 70)
})

// Methods
const startTest = () => {
  testStarted.value = true
  testCompleted.value = false
  currentQuestionIndex.value = 0
  selectedAnswers.value = {}
  showExplanation.value = false
  
  // Start timer if time limit exists
  if (props.testData.timeLimit) {
    timeRemaining.value = props.testData.timeLimit * 60 // Convert to seconds
    startTimer()
  }
  
  emit('test-started')
}

const startTimer = () => {
  timerInterval.value = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      clearInterval(timerInterval.value)
      ElMessage.warning('Время вышло!')
      submitTest()
    }
  }, 1000)
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const selectAnswer = (index) => {
  if (!showExplanation.value) {
    selectedAnswers.value[currentQuestionIndex.value] = index
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < props.testData.questions.length - 1) {
    currentQuestionIndex.value++
    showExplanation.value = false
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    showExplanation.value = false
  }
}

const goToQuestion = (index) => {
  currentQuestionIndex.value = index
  showExplanation.value = false
}

const submitTest = async () => {
  if (!allQuestionsAnswered.value) {
    try {
      await ElMessageBox.confirm(
        'Вы ответили не на все вопросы. Продолжить?',
        'Внимание',
        {
          confirmButtonText: 'Да, завершить',
          cancelButtonText: 'Отмена',
          type: 'warning'
        }
      )
    } catch {
      return
    }
  }

  // Stop timer
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }

  testCompleted.value = true
  testStarted.value = false

  // Save results to localStorage
  saveTestResults()

  ElMessage.success('Тест завершен!')
}

const reviewAnswers = () => {
  testCompleted.value = false
  testStarted.value = true
  currentQuestionIndex.value = 0
  showExplanation.value = true
}

const retryTest = () => {
  testStarted.value = false
  testCompleted.value = false
  currentQuestionIndex.value = 0
  selectedAnswers.value = {}
  timeRemaining.value = 0
  showExplanation.value = false
}

const confirmExit = async () => {
  try {
    await ElMessageBox.confirm(
      'Вы уверены, что хотите выйти? Прогресс будет потерян.',
      'Подтверждение',
      {
        confirmButtonText: 'Да, выйти',
        cancelButtonText: 'Отмена',
        type: 'warning'
      }
    )
    
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
    }
    
    testStarted.value = false
    selectedAnswers.value = {}
  } catch {
    // Cancelled
  }
}

const saveTestResults = () => {
  try {
    const results = {
      testId: props.testData.id,
      score: score.value,
      isPassed: isPassed.value,
      correctAnswers: correctAnswersCount.value,
      totalQuestions: props.testData.questions.length,
      timestamp: new Date().toISOString()
    }

    const existingResults = JSON.parse(localStorage.getItem('testResults') || '[]')
    existingResults.push(results)
    localStorage.setItem('testResults', JSON.stringify(existingResults))
  } catch (error) {
    console.error('Error saving test results:', error)
  }
}

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>

<style scoped>
.test-quiz {
  min-height: 400px;
}

.intro-card {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px;
}

.stat-card {
  padding: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  text-align: center;
}

.question-card {
  transition: all 0.3s ease;
}

.option-card {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.option-card:hover {
  border-color: #3b82f6;
  background: #eff6ff;
  transform: translateX(4px);
}

.option-card.selected {
  border-color: #3b82f6;
  background: #dbeafe;
}

.option-card.correct {
  border-color: #10b981;
  background: #d1fae5;
}

.option-card.incorrect {
  border-color: #ef4444;
  background: #fee2e2;
}

.option-indicator {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #6b7280;
  flex-shrink: 0;
  font-size: 12px;
}

.option-card.selected .option-indicator {
  background: #3b82f6;
  color: white;
}

.option-card.correct .option-indicator {
  background: #10b981;
  color: white;
}

.option-card.incorrect .option-indicator {
  background: #ef4444;
  color: white;
}

.question-nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  background: white;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
}

.question-nav-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.question-nav-btn.active {
  border-color: #3b82f6;
  background: #3b82f6;
  color: white;
}

.question-nav-btn.answered {
  border-color: #10b981;
  background: #d1fae5;
  color: #10b981;
}

.results-card {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px;
}

.result-stat {
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
  text-align: center;
}
</style>

