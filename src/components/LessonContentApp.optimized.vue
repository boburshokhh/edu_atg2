<template>
  <div class="lesson-content-app h-screen bg-gray-50 overflow-hidden">
    <!-- Lesson Header -->
    <LessonHeader
      :station-id="stationId"
      :station="station"
      :current-lesson="currentLesson"
    />

    <!-- Main Content Layout -->
    <el-container class="max-w-[1920px] mx-auto flex-1 overflow-hidden">
      <!-- Left Sidebar (Lessons) -->
      <transition name="slide">
        <LessonSidebar
          v-show="showSidebar"
          :lessons="lessons"
          :current-lesson-index="currentLessonIndex"
          :current-topic-index="currentTopicIndex"
          :completed-topics="completedTopics"
          :passed-tests="passedTests"
          :is-test-mode="isTestMode"
          @select-lesson="handleSelectLesson"
          @select-test="handleSelectTest"
          @toggle-sidebar="handleToggleSidebar"
          :class="[
            'flex-shrink-0',
            isMobile ? 'sidebar-mobile' : 'sidebar-desktop'
          ]"
        />
      </transition>

      <!-- Mobile Overlay -->
      <div
        v-if="showSidebar && isMobile"
        @click="showSidebar = false"
        class="fixed inset-0 bg-black/50 z-30 lg:hidden"
      />

      <!-- Expand Left Sidebar Button -->
      <el-button
        v-if="!showSidebar && !isMobile"
        @click="showSidebar = true"
        class="sidebar-expand-btn sidebar-expand-btn-left"
        type="primary"
        circle
        :icon="Menu"
        title="Показать сайдбар"
      />

      <!-- Main Content Area -->
      <el-main class="flex-1 p-3 md:p-4 min-w-0 overflow-y-auto">
        <el-card class="lesson-content-card" shadow="never">
          <!-- Test Mode -->
          <div v-if="isTestMode" class="p-4">
            <TestQuiz 
              v-if="currentLessonTest"
              :test-data="currentLessonTest"
              @test-completed="handleTestCompleted"
              @test-started="handleTestStarted"
            />
            <el-empty v-else description="Тест для этого модуля пока недоступен" :image-size="80" />
          </div>

          <!-- Content Viewer -->
          <ContentViewer
            v-else
            :current-file="currentFile"
            :current-file-type="currentFileType"
            :current-zoom="currentZoom"
            @zoom-in="zoomIn"
            @zoom-out="zoomOut"
            @toggle-fullscreen="toggleFullscreen"
            @download-file="downloadFile"
          />

          <!-- Navigation and Tabs -->
          <div class="border-t border-gray-200">
            <!-- Navigation Buttons -->
            <div class="flex items-center justify-between px-3 md:px-4 py-3 bg-gray-50 gap-2">
              <el-button
                @click="previousLesson"
                :disabled="!hasPreviousLesson"
                :icon="ArrowLeft"
                size="small"
              >
                <span class="hidden sm:inline">Назад</span>
              </el-button>
              
              <div class="flex items-center gap-2">
                <el-button
                  v-if="!isTopicCompleted"
                  type="success"
                  @click="markAsCompleted"
                  :icon="Check"
                  size="small"
                >
                  <span class="hidden md:inline">Завершить</span>
                  <span class="md:hidden">✓</span>
                </el-button>
                <el-tag v-else type="success" size="small">
                  <el-icon><Check /></el-icon>
                  <span class="ml-1 hidden sm:inline">Завершено</span>
                </el-tag>
              </div>

              <el-button
                @click="nextLesson"
                :disabled="!hasNextLesson"
                type="primary"
                size="small"
              >
                <span class="hidden sm:inline">Далее</span>
                <el-icon class="sm:ml-2"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </el-main>

      <!-- Right Sidebar (Materials) -->
      <transition name="slide-right">
        <CourseMaterialsPanel
          v-show="showMaterialsSidebar"
          :main-materials="mainMaterials"
          :additional-materials="additionalMaterials"
          :current-file="currentFile"
          :topic-title="currentTopic?.title || currentLesson?.title || ''"
          @select-material="openMaterial"
          @toggle-sidebar="handleToggleMaterialsSidebar"
          :class="[
            'flex-shrink-0',
            isMobile ? 'materials-sidebar-mobile' : 'materials-sidebar-desktop'
          ]"
        />
      </transition>

      <!-- Expand Right Sidebar Button -->
      <el-button
        v-if="!showMaterialsSidebar && !isMobile"
        @click="showMaterialsSidebar = true"
        class="sidebar-expand-btn sidebar-expand-btn-right"
        type="primary"
        circle
        :icon="Menu"
        title="Показать материалы"
      />
    </el-container>

    <!-- Mobile Menu Button -->
    <el-button
      @click="showSidebar = !showSidebar"
      class="fixed bottom-4 left-4 z-40 lg:hidden w-12 h-12 rounded-full shadow-lg"
      type="primary"
      circle
    >
      <el-icon :size="20">
        <Menu v-if="!showSidebar" />
        <Close v-else />
      </el-icon>
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Check,
  ArrowLeft,
  ArrowRight,
  Menu,
  Close,
} from '@element-plus/icons-vue'

// Lazy imports для компонентов
import { defineAsyncComponent } from 'vue'

const LessonHeader = defineAsyncComponent(() => import('@/components/LessonHeader.vue'))
const LessonSidebar = defineAsyncComponent(() => import('@/components/LessonSidebar.vue'))
const TestQuiz = defineAsyncComponent(() => import('@/components/TestQuiz.vue'))
const ContentViewer = defineAsyncComponent(() => import('@/components/ContentViewer.vue'))
const CourseMaterialsPanel = defineAsyncComponent(() => import('@/components/CourseMaterialsPanel.vue'))

// Composables
import { useMaterials } from '@/composables/useMaterials'
import { useProgress } from '@/composables/useProgress'

// Data imports
import { stationsData } from '@/data/stationsData.js'
import testsData from '@/data/testsData.json'

// Services
import authService from '@/services/auth'

// Utils
import { throttle } from '@/utils/performance'

const route = useRoute()
const router = useRouter()

// ========== Composables ==========
const {
  mainMaterials,
  additionalMaterials,
  currentFile,
  currentFileType,
  isLoading: materialsLoading,
  loadTopicMaterialsDebounced,
  openMaterial,
  downloadFile
} = useMaterials()

const {
  completedTopics,
  passedTests,
  isTopicCompleted: checkTopicCompleted,
  markTopicAsCompleted,
  markTestAsPassed
} = useProgress()

// ========== Route params ==========
const stationId = computed(() => parseInt(route.params.id))
const currentLessonIndex = ref(parseInt(route.params.lessonIndex) || 0)
const currentTopicIndex = ref(parseInt(route.params.topicIndex) || 0)
const isTestMode = ref(false)

// ========== Data ==========
const station = computed(() => stationsData[stationId.value] || stationsData[1])
const lessons = computed(() => station.value?.courseProgram?.lessons || [])
const currentLesson = computed(() => lessons.value[currentLessonIndex.value])
const currentTopic = computed(() => currentLesson.value?.topics?.[currentTopicIndex.value])
const currentTopicId = computed(() => `${stationId.value}-${currentLessonIndex.value}-${currentTopicIndex.value}`)

// ========== UI State ==========
const currentZoom = ref(100)
const isMobile = ref(window.innerWidth < 1024)
const showSidebar = ref(!isMobile.value)
const showMaterialsSidebar = ref(!isMobile.value)

// ========== Tests ==========
const currentTopicTest = computed(() => {
  return testsData.tests.find(test => 
    test.lessonIndex === currentLessonIndex.value && 
    test.topicIndex === currentTopicIndex.value
  )
})

const currentLessonTest = computed(() => {
  return testsData.tests.find(test => 
    test.lessonIndex === currentLessonIndex.value && 
    test.topicIndex === null
  )
})

// ========== Computed ==========
const isTopicCompleted = computed(() => {
  return checkTopicCompleted(currentTopicId.value)
})

const hasPreviousLesson = computed(() => {
  if (currentTopicIndex.value > 0) return true
  if (currentLessonIndex.value > 0) return true
  return false
})

const hasNextLesson = computed(() => {
  const currentLessonTopics = currentLesson.value?.topics?.length || 0
  if (currentTopicIndex.value < currentLessonTopics - 1) return true
  if (currentLessonIndex.value < lessons.value.length - 1) return true
  return false
})

// ========== Methods ==========
const zoomIn = () => {
  if (currentZoom.value < 200) {
    currentZoom.value += 10
  }
}

const zoomOut = () => {
  if (currentZoom.value > 50) {
    currentZoom.value -= 10
  }
}

const toggleFullscreen = () => {
  // Реализуется в ContentViewer
}

const markAsCompleted = () => {
  if (markTopicAsCompleted(currentTopicId.value)) {
    ElMessage.success('Урок отмечен как завершенный!')
  }
}

const previousLesson = () => {
  isTestMode.value = false
  if (currentTopicIndex.value > 0) {
    currentTopicIndex.value--
  } else if (currentLessonIndex.value > 0) {
    currentLessonIndex.value--
    const prevLesson = lessons.value[currentLessonIndex.value]
    currentTopicIndex.value = (prevLesson.topics?.length || 1) - 1
  }
  updateRoute()
}

const nextLesson = () => {
  isTestMode.value = false
  const currentLessonTopics = currentLesson.value?.topics?.length || 0
  if (currentTopicIndex.value < currentLessonTopics - 1) {
    currentTopicIndex.value++
  } else if (currentLessonIndex.value < lessons.value.length - 1) {
    currentLessonIndex.value++
    currentTopicIndex.value = 0
  }
  updateRoute()
}

const updateRoute = () => {
  router.push({
    name: 'lesson-viewer',
    params: {
      id: stationId.value,
      lessonIndex: currentLessonIndex.value,
      topicIndex: currentTopicIndex.value
    }
  })
}

const handleSelectLesson = ({ lessonIndex, topicIndex }) => {
  currentLessonIndex.value = lessonIndex
  currentTopicIndex.value = topicIndex
  isTestMode.value = false
  updateRoute()
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleSelectTest = ({ lessonIndex }) => {
  currentLessonIndex.value = lessonIndex
  isTestMode.value = true
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleToggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

const handleToggleMaterialsSidebar = () => {
  showMaterialsSidebar.value = !showMaterialsSidebar.value
}

const handleTestCompleted = ({ score, isPassed }) => {
  const testToSave = isTestMode.value ? currentLessonTest.value : currentTopicTest.value
  
  if (isPassed && testToSave) {
    markTestAsPassed(testToSave.id)
    ElMessage.success(`Поздравляем! Вы успешно прошли тест с результатом ${score}%`)
    
    if (!isTestMode.value && !isTopicCompleted.value) {
      markAsCompleted()
    }
  }
}

const handleTestStarted = () => {
  // Можно добавить аналитику
}

// Throttled resize handler
const handleResize = throttle(() => {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 1024
  
  if (wasMobile && !isMobile.value) {
    showSidebar.value = true
    showMaterialsSidebar.value = true
  }
  if (!wasMobile && isMobile.value) {
    showSidebar.value = false
    showMaterialsSidebar.value = false
  }
}, 200)

// ========== Watchers ==========
watch(() => [currentLessonIndex.value, currentTopicIndex.value], () => {
  if (!isTestMode.value && currentLesson.value && currentTopic.value) {
    loadTopicMaterialsDebounced(currentLesson.value.title, currentTopic.value.code)
  }
}, { immediate: true })

// ========== Lifecycle ==========
onMounted(async () => {
  // Проверка аутентификации
  const authResult = await authService.checkAuth()
  if (!authResult.isAuthenticated) {
    ElMessage.warning('Для доступа к уроку необходимо войти в систему')
    router.push(`/station/${stationId.value}/courses`)
    return
  }

  // Подписка на события
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.lesson-content-app {
  padding-top: 0;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

:deep(.el-main) {
  padding: 0;
}

.lesson-content-card {
  border-radius: 12px;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter-from {
  transform: translateX(100%);
}

.slide-right-leave-to {
  transform: translateX(100%);
}

/* Sidebar Expand Buttons */
.sidebar-expand-btn {
  position: fixed;
  top: 80px;
  z-index: 50;
  width: 40px;
  height: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.sidebar-expand-btn-left {
  left: 16px;
}

.sidebar-expand-btn-right {
  right: 16px;
}

.sidebar-expand-btn:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: scale(1.1);
}
</style>

