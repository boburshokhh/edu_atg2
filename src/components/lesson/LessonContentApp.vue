<template>
  <div 
    ref="fullscreenContainer" 
    :class="[
      'lesson-content-app h-screen overflow-hidden flex flex-col transition-colors duration-200',
      isDark ? 'dark bg-gray-900' : 'bg-gray-50'
    ]"
  >
    <!-- Header -->
    <LessonHeader
      :current-file-name="currentFileName"
      :is-topic-completed="isTopicCompleted"
      :is-comments-open="isCommentsOpen"
      :is-materials-sidebar-open="showMaterialsSidebar"
      :is-fullscreen="isFullscreen"
      :is-dark="isDark"
      :current-lesson-index="currentLessonIndex"
      :course-title="courseTitle"
      @mark-complete="markAsCompleted"
      @toggle-sidebar="handleToggleSidebar"
      @toggle-comments="handleToggleComments"
      @toggle-materials-sidebar="handleToggleMaterialsSidebar"
      @toggle-fullscreen="toggleFullscreen"
      @toggle-dark-mode="toggleDarkMode"
    />

    <!-- Main Layout -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- Left Sidebar -->
      <transition name="slide">
        <LessonSidebar
          v-show="showSidebar && !isFullscreen"
          :lessons="processedLessons"
          :current-lesson-index="isFinalTestMode ? -1 : currentLessonIndex"
          :current-topic-index="currentTopicIndex"
          :current-file="currentFile"
          :completed-topics="completedTopics"
          :passed-tests="passedTests"
          :is-test-mode="isTestMode"
          :course-title="courseTitle"
          :final-test="courseProgram?.finalTest"
          :is-mobile="isMobile"
          :is-dark="isDark"
          @select-lesson="handleSelectLesson"
          @select-test="handleSelectTest"
          @select-final-test="handleSelectFinalTest"
          @select-file="handleSelectFile"
          @toggle-sidebar="handleToggleSidebar"
        />
      </transition>

      <!-- Mobile Overlay -->
      <div
        v-if="showSidebar && isMobile"
        class="mobile-overlay"
        @click="showSidebar = false"
      />

      <!-- Main Content Area -->
      <main 
        :class="[
          'flex-1 flex flex-col h-full relative min-h-0 min-w-0 transition-colors duration-200',
          isDark ? 'bg-black/40' : 'bg-gray-100'
        ]"
      >
        <!-- Content Area -->
        <div class="flex-1 min-h-0 flex flex-col">
          <!-- Test Mode -->
          <div
            v-if="isTestMode"
            class="test-container flex-1 min-h-0 overflow-auto p-8"
          >
            <TestQuiz 
              v-if="currentLessonTest"
              :test-data="currentLessonTest"
              @test-completed="handleTestCompleted"
              @test-started="handleTestStarted"
            />
            <el-empty
              v-else-if="loadingTest"
              description="Загрузка теста..."
              :image-size="80"
            />
            <el-empty
              v-else
              description="Тест для этого курса пока недоступен"
              :image-size="80"
            />
          </div>

          <!-- Content Viewer -->
          <ContentViewer
            v-else
            :current-file="currentFile"
            :current-file-type="currentFileType"
            :is-dark="isDark"
            :is-topic-completed="isTopicCompleted"
            :has-previous="hasPreviousLesson"
            :has-next="hasNextLesson"
            @download-file="downloadFile"
            @previous="previousLesson"
            @next="nextLesson"
            @mark-complete="markAsCompleted"
            @material-viewed="handleMaterialViewed"
          />
        </div>
      </main>

      <!-- Right Sidebar - Materials -->
      <transition name="slide-right">
        <CourseMaterialsPanel
          v-if="showMaterialsSidebar && !isFullscreen && !isTestMode"
          :main-materials="mainMaterials"
          :additional-materials="additionalMaterials"
          :current-file="currentFile"
          :topic-title="currentTopic?.title || ''"
          :is-dark="isDark"
          @select-material="openMaterial"
          @toggle-sidebar="showMaterialsSidebar = false"
        />
      </transition>

      <!-- Comments Sidebar -->
      <CommentsSidebar
        v-if="isCommentsOpen && !isFullscreen"
        :is-open="isCommentsOpen && !isFullscreen"
        :station-id="stationId"
        :lesson-index="currentLessonIndex"
        :topic-index="currentTopicIndex"
        :file-object-key="currentFile?.objectName || currentFile?.objectKey"
        @close="isCommentsOpen = false"
      />

      <!-- Mobile Overlay for Comments -->
      <div
        v-if="isCommentsOpen && isMobile"
        class="mobile-overlay"
        @click="isCommentsOpen = false"
      />

      <!-- Mobile Overlay for Materials -->
      <div
        v-if="showMaterialsSidebar && isMobile"
        class="mobile-overlay"
        @click="showMaterialsSidebar = false"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// Menu and Close icons removed - menu access only through header
import LessonHeader from '@/components/lesson/LessonHeader.vue'
import LessonSidebar from '@/components/lesson/LessonSidebar.vue'
import TestQuiz from '@/components/lesson/TestQuiz.vue'
import CommentsSidebar from '@/components/lesson/CommentsSidebar.vue'
import CourseMaterialsPanel from '@/components/lesson/CourseMaterialsPanel.vue'
import testsData from '@/data/testsData.json'
import minioService from '@/services/minioService'
import authService from '@/services/auth'
import stationService from '@/services/stationService'
import testService from '@/services/testService'
import courseService from '@/services/courseService'
import { useFullscreen } from '@/composables/useFullscreen'
import { useBreakpoints } from '@/composables/useBreakpoints'

const ContentViewer = defineAsyncComponent(() => import('@/components/lesson/ContentViewer.vue'))

const route = useRoute()
const router = useRouter()

// Dark mode
const isDark = ref(false)
const toggleDarkMode = () => {
  isDark.value = !isDark.value
  localStorage.setItem('darkMode', isDark.value ? 'true' : 'false')
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// Load dark mode preference
const loadDarkModePreference = () => {
  const saved = localStorage.getItem('darkMode')
  isDark.value = saved === 'true'
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  }
}

// Route params
const stationId = computed(() => parseInt(route.params.id))
const currentLessonIndex = ref(parseInt(route.params.lessonIndex) || 0)
const currentTopicIndex = ref(parseInt(route.params.topicIndex) || 0)
const isTestMode = ref(false)
const isFinalTestMode = ref(false)

// Data
const station = ref(null)
const courseProgram = ref(null)
const lessons = computed(() => courseProgram.value?.lessons || [])

// Computed for course title
const courseTitle = computed(() => {
  return courseProgram.value?.title || station.value?.shortName || 'Курс обучения'
})

const loadStationAndProgram = async () => {
  try {
    const stationResp = await stationService.getStation(stationId.value)
    station.value = stationResp?.station || null
  } catch (e) {
    console.error('[LessonContentApp] Failed to load station:', e)
    station.value = null
  }
  try {
    courseProgram.value = await stationService.getStationCourseProgram(stationId.value)
  } catch (e) {
    console.error('[LessonContentApp] Failed to load course program:', e)
    courseProgram.value = null
  }
}

// Функция для удаления префикса "Урок N" из названия
const getLessonTitle = (title) => {
  if (!title) return ''
  return title
    .replace(/^Урок\s*№?\s*\d+\s*:?\s*/i, '')
    .replace(/^Урок\s*№?\s*\d+\s*/i, '')
    .trim()
}

// Обработанные уроки без префикса "Урок N"
const processedLessons = computed(() => {
  return lessons.value.map(lesson => ({
    ...lesson,
    title: getLessonTitle(lesson.title)
  }))
})

const currentLesson = computed(() => lessons.value[currentLessonIndex.value])

const currentTopic = computed(() => currentLesson.value?.topics?.[currentTopicIndex.value])

// ID for tracking completed topics
const currentTopicId = computed(() => `${stationId.value}-${currentLessonIndex.value}-${currentTopicIndex.value}`)

// Current file
const currentFile = ref(null)
const mainMaterials = ref([])
const additionalMaterials = ref([])
const completedMaterialKeys = new Set()

const currentFileType = computed(() => {
  const f = currentFile.value
  if (!f) return 'unknown'
  const t = String(f.type || f.mimeType || f.mime_type || '').toLowerCase()
  const name = String(
    f.original_name ||
      f.originalName ||
      f.fileName ||
      f.file_name ||
      ''
  ).toLowerCase()
  
  if (
    t.includes('pdf') ||
    t === 'application/pdf' ||
    name.endsWith('.pdf')
  ) {
    return 'pdf'
  }
  
  if (
    t.includes('video') ||
    name.endsWith('.mp4') ||
    name.endsWith('.webm') ||
    name.endsWith('.ogg') ||
    name.endsWith('.mov')
  ) {
    return 'video'
  }
  
  return 'unknown'
})

// Функция для очистки названия файла от "_OUTLINE" или "_outline"
const cleanFileName = (fileName) => {
  if (!fileName) return 'Файл'
  // Убираем "_OUTLINE" или "_outline" из названия (может быть в начале или в конце)
  // Обрабатываем различные варианты: O_OUTLINE, _OUTLINE, OUTLINE, _outline, outline
  return fileName
    .replace(/^O_OUTLINE\s+/i, '')  // Убираем "O_OUTLINE " в начале
    .replace(/^O_outline\s+/i, '')  // Убираем "O_outline " в начале
    .replace(/\s*_OUTLINE$/i, '')    // Убираем " _OUTLINE" в конце
    .replace(/\s*_outline$/i, '')    // Убираем " _outline" в конце
    .replace(/\s*OUTLINE$/i, '')     // Убираем " OUTLINE" в конце
    .replace(/\s*outline$/i, '')     // Убираем " outline" в конце
    .trim()                           // Убираем лишние пробелы
}

const currentFileName = computed(() => {
  if (!currentFile.value) return ''
  const fileName = currentFile.value.original_name || currentFile.value.originalName || currentFile.value.fileName || currentFile.value.file_name || 'Файл'
  return cleanFileName(fileName)
})

const downloadFile = async (file) => {
  if (!file) return
  
  const direct = file.url || file.file_url
  if (direct) {
    window.open(direct, '_blank')
    return
  }
  const key = file.objectName || file.object_key || file.objectKey
  if (!key) {
    ElMessage.warning('Файл недоступен')
    return
  }
  try {
    const url = await minioService.getPresignedDownloadUrl(key, 60 * 60, file.type || null)
    window.open(url, '_blank')
  } catch (e) {
    ElMessage.error('Не удалось открыть файл')
  }
}

// Tests
const passedTests = ref(new Set())
const courseTest = ref(null)
const loadingTest = ref(false)
const lessonTest = ref(null)

const currentTopicTest = computed(() => {
  // Legacy support - can be removed later
  return testsData.tests.find(test => 
    test.lessonIndex === currentLessonIndex.value && 
    test.topicIndex === currentTopicIndex.value
  )
})

const currentLessonTest = computed(() => {
  // If in final test mode, use course test
  if (isFinalTestMode.value && courseTest.value) {
    return courseTest.value
  }
  
  // Use lesson test from API if available
  if (lessonTest.value && isTestMode.value && !isFinalTestMode.value) {
    return lessonTest.value
  }
  
  // Use course test from API if available (for any test mode)
  if (courseTest.value && isTestMode.value) {
    return courseTest.value
  }
  
  // Legacy fallback for lesson tests
  return testsData.tests.find(test => 
    test.lessonIndex === currentLessonIndex.value && 
    test.topicIndex === null
  )
})

const loadCourseTest = async () => {
  if (!courseProgram.value?.id) {
    courseTest.value = null
    return
  }

  loadingTest.value = true
  try {
    const test = await testService.getTestByCourseProgram(courseProgram.value.id)
    if (test) {
      // Transform API data to TestQuiz format
      courseTest.value = {
        id: test.id,
        title: test.title,
        description: test.description,
        questions: test.questions || [],
        passingScore: test.passingScore,
        timeLimit: test.timeLimit,
        attempts: test.attempts,
        testType: 'final' // Always 'final' for course program tests
      }
    } else {
      courseTest.value = null
    }
  } catch (error) {
    console.error('[LessonContentApp] Failed to load course test:', error)
    courseTest.value = null
  } finally {
    loadingTest.value = false
  }
}

const loadLessonTest = async (lessonId) => {
  if (!lessonId) {
    lessonTest.value = null
    return
  }

  loadingTest.value = true
  try {
    const test = await testService.getLessonTest(lessonId)
    if (test) {
      // Transform API data to TestQuiz format
      lessonTest.value = {
        id: test.id,
        title: test.title,
        description: test.description,
        questions: test.questions || [],
        passingScore: test.passingScore,
        timeLimit: test.timeLimit,
        attempts: test.attempts,
        testType: 'lesson' // Always 'lesson' for lesson tests
      }
    } else {
      lessonTest.value = null
    }
  } catch (error) {
    console.error('[LessonContentApp] Failed to load lesson test:', error)
    lessonTest.value = null
  } finally {
    loadingTest.value = false
  }
}

// Progress
const completedTopics = ref(new Set())
const courseProgress = computed(() => {
  let totalTopics = 0
  lessons.value.forEach(lesson => {
    totalTopics += lesson.topics?.length || 0
  })
  if (totalTopics === 0) return 0
  return Math.round((completedTopics.value.size / totalTopics) * 100)
})

// UI State
const fullscreenContainer = ref(null)
const { isFullscreen, toggleFullscreen } = useFullscreen(fullscreenContainer)
const { isMobile, isTablet, isDesktop } = useBreakpoints()
const showSidebar = ref(isDesktop.value)
const showMaterialsSidebar = ref(isDesktop.value)
const isCommentsOpen = ref(false)

// Handle breakpoint changes
watch([isMobile, isTablet, isDesktop], ([mobile, tablet, desktop]) => {
  if (desktop) {
    showSidebar.value = true
    showMaterialsSidebar.value = true
  }
  if (mobile || tablet) {
    showSidebar.value = false
    showMaterialsSidebar.value = false
    isCommentsOpen.value = false
  }
})

// Check if topic is completed
const isTopicCompleted = computed(() => {
  return completedTopics.value.has(currentTopicId.value)
})

// Navigation
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

// Methods
const loadTopicMaterials = async () => {
  try {
    if (!currentLesson.value || !currentTopic.value) {
      mainMaterials.value = []
      additionalMaterials.value = []
      currentFile.value = null
      return
    }

    const dbFiles = Array.isArray(currentTopic.value?.files) ? currentTopic.value.files : []
    
    // Логирование для анализа "_outline" - проверка данных из API
    if (dbFiles.length > 0) {
      const filesWithOutline = dbFiles.filter(f => {
        const name = (f.originalName || f.original_name || f.fileName || f.file_name || f.title || '').toLowerCase()
        return name.includes('outline') || name.includes('_outline')
      })
      if (filesWithOutline.length > 0) {
        console.warn('[LessonContentApp] API returned files with "_outline" in name:', {
          topicId: currentTopic.value?.id,
          topicTitle: currentTopic.value?.title,
          filesCount: filesWithOutline.length,
          files: filesWithOutline.map(f => ({
            id: f.id,
            originalName: f.originalName,
            original_name: f.original_name,
            fileName: f.fileName,
            file_name: f.file_name,
            title: f.title,
            objectKey: f.objectKey || f.object_key
          }))
        })
      }
    }
    
    if (dbFiles.length === 0) {
      mainMaterials.value = []
      additionalMaterials.value = []
      currentFile.value = null
      return
    }

    const filePromises = dbFiles.map(async (f) => {
      try {
        const fileType = f.fileType || f.file_type
        const objectKey = f.objectKey || f.object_key || f.objectName || f.object_name
        const originalName = f.originalName || f.original_name || f.fileName || f.file_name || f.title || 'file'
        const fileSize = f.fileSize ?? f.file_size ?? null
        const mimeType = f.mimeType || f.mime_type || null
        const isMain = f.isMain ?? f.is_main ?? false

        // Логирование для анализа "_outline" в названиях файлов
        if (originalName && (originalName.toLowerCase().includes('outline') || originalName.toLowerCase().includes('_outline'))) {
          console.warn('[LessonContentApp] Found file with "_outline" in name:', {
            fileId: f.id,
            originalName: originalName,
            originalName_from_api: f.originalName,
            original_name_from_api: f.original_name,
            fileName_from_api: f.fileName,
            file_name_from_api: f.file_name,
            title_from_api: f.title,
            objectKey: objectKey,
            fileType: fileType,
            rawFileData: f
          })
        }

        if (!objectKey) {
          return null
        }

        const nameForDetect = String(originalName || objectKey || '').toLowerCase()
        
        const contentType =
          mimeType ||
          (fileType === 'video' || nameForDetect.endsWith('.mp4') || nameForDetect.endsWith('.webm') || nameForDetect.endsWith('.ogg') || nameForDetect.endsWith('.ogv') || nameForDetect.endsWith('.mov')
              ? (nameForDetect.endsWith('.webm')
                ? 'video/webm'
                : nameForDetect.endsWith('.ogg') || nameForDetect.endsWith('.ogv')
                  ? 'video/ogg'
                  : nameForDetect.endsWith('.mov')
                    ? 'video/quicktime'
                    : 'video/mp4')
              : 'application/octet-stream')

        const fileUrl = await minioService.getPresignedDownloadUrl(objectKey, 60 * 60, contentType)

        return {
          id: f.id,
          objectName: objectKey,
          fileName: originalName,
          original_name: originalName,
          originalName: originalName,
          file_size: fileSize,
          url: fileUrl,
          file_url: fileUrl,
          type: contentType,
          is_main_file: !!isMain
        }
      } catch (e) {
        console.error('[LessonContentApp] Failed to process topic file:', f, e)
        return null
      }
    })

    const results = await Promise.allSettled(filePromises)
    const allFiles = results
      .filter(r => r.status === 'fulfilled' && r.value !== null)
      .map(r => r.value)

    const mainFiles = allFiles.filter(f => f.is_main_file)
    const additionals = allFiles.filter(f => !f.is_main_file)

    mainMaterials.value = mainFiles
    additionalMaterials.value = additionals

    if (mainFiles.length > 0) {
      currentFile.value = mainFiles[0]
    } else if (additionals.length > 0) {
      currentFile.value = additionals[0]
    } else {
      currentFile.value = null
    }
  } catch (error) {
    console.error('[LessonContentApp] Error loading topic materials:', error)
    ElMessage.error('Не удалось загрузить материалы урока')
    mainMaterials.value = []
    additionalMaterials.value = []
    currentFile.value = null
  }
}

const openMaterial = (material) => {
  currentFile.value = material
}

const registerMaterialCompletion = async (materialType, materialKey) => {
  if (!materialType || !materialKey) return
  const dedupeKey = `${materialType}:${materialKey}`
  if (completedMaterialKeys.has(dedupeKey)) return
  completedMaterialKeys.add(dedupeKey)

  const user = authService.getCurrentUser()
  if (!user || !courseProgram.value?.id) return

  await courseService.markMaterialComplete(courseProgram.value.id, materialType, materialKey)
}

const handleMaterialViewed = async ({ file, type }) => {
  if (!file || !courseProgram.value?.id) return
  const typeMap = {
    video: 'video',
    pdf: 'pdf'
  }
  const materialType = typeMap[type] || 'presentation'
  const materialKey =
    file.objectName ||
    file.objectKey ||
    file.id ||
    file.original_name ||
    file.originalName ||
    `lesson:${currentLessonIndex.value}-topic:${currentTopicIndex.value}`
  await registerMaterialCompletion(materialType, materialKey)
}

const markAsCompleted = async () => {
  completedTopics.value.add(currentTopicId.value)
  localStorage.setItem('completedTopics', JSON.stringify([...completedTopics.value]))
  ElMessage.success('Урок отмечен как завершенный!')
  const topicKey = currentTopic.value?.topicKey || currentTopicId.value
  await registerMaterialCompletion('text', `topic:${topicKey}`)
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
  isFinalTestMode.value = false
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleSelectFinalTest = () => {
  isTestMode.value = true
  isFinalTestMode.value = true
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleToggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

const handleToggleComments = () => {
  isCommentsOpen.value = !isCommentsOpen.value
}

const handleToggleMaterialsSidebar = () => {
  showMaterialsSidebar.value = !showMaterialsSidebar.value
}

const handleSelectFile = async ({ lessonIndex, topicIndex, file }) => {
  currentLessonIndex.value = lessonIndex
  currentTopicIndex.value = topicIndex
  isTestMode.value = false
  
  try {
    const fileType = file.fileType || file.file_type
    const objectKey = file.objectKey || file.object_key || file.objectName || file.object_name
    const originalName = file.originalName || file.original_name || file.fileName || file.file_name || file.title || 'file'
    const fileSize = file.fileSize ?? file.file_size ?? null
    const mimeType = file.mimeType || file.mime_type || null
    const isMain = file.isMain ?? file.is_main ?? false

    if (!objectKey) {
      ElMessage.warning('Файл недоступен')
      return
    }

    const nameForDetect = String(originalName || objectKey || '').toLowerCase()
    
    const contentType =
      mimeType ||
      (fileType === 'video' || nameForDetect.endsWith('.mp4') || nameForDetect.endsWith('.webm') || nameForDetect.endsWith('.ogg') || nameForDetect.endsWith('.ogv') || nameForDetect.endsWith('.mov')
        ? (nameForDetect.endsWith('.webm')
          ? 'video/webm'
          : nameForDetect.endsWith('.ogg') || nameForDetect.endsWith('.ogv')
            ? 'video/ogg'
            : nameForDetect.endsWith('.mov')
              ? 'video/quicktime'
              : 'video/mp4')
        : 'application/octet-stream')

    const fileUrl = await minioService.getPresignedDownloadUrl(objectKey, 60 * 60, contentType)

    currentFile.value = {
      id: file.id,
      objectName: objectKey,
      fileName: originalName,
      original_name: originalName,
      originalName: originalName,
      file_size: fileSize,
      url: fileUrl,
      file_url: fileUrl,
      type: contentType,
      is_main_file: !!isMain
    }
    
    updateRoute()
    if (isMobile.value) {
      showSidebar.value = false
    }
  } catch (error) {
    console.error('[LessonContentApp] Error processing selected file:', error)
    ElMessage.error('Не удалось загрузить файл')
  }
}

const handleTestCompleted = async ({ score, isPassed }) => {
  const testToSave = isTestMode.value ? currentLessonTest.value : currentTopicTest.value
  
  if (isPassed && testToSave) {
    // Save test result to backend
    try {
      const user = authService.getCurrentUser()
      if (user && testToSave.id) {
        const testId = testToSave.id
        const testType = isFinalTestMode.value ? 'final' : 'lesson'
        const totalQuestions = Array.isArray(testToSave.questions) ? testToSave.questions.length : 0
        const correctAnswers = totalQuestions > 0 ? Math.round((score / 100) * totalQuestions) : 0

        await testService.saveTestResult({
          test_id: testId,
          test_type: testType,
          score,
          is_passed: isPassed,
          correct_answers: correctAnswers,
          total_questions: totalQuestions
        })

        const testKey = isFinalTestMode.value ? `final_${testId}` : testId
        passedTests.value.add(testKey)
        savePassedTests()
      } else {
        // Fallback to localStorage
        const testKey = isFinalTestMode.value ? `final_${testToSave.id}` : testToSave.id
        passedTests.value.add(testKey)
        savePassedTests()
      }
    } catch (error) {
      console.error('[LessonContentApp] Error saving test result:', error)
      // Fallback to localStorage
      const testKey = isFinalTestMode.value ? `final_${testToSave.id}` : testToSave.id
      passedTests.value.add(testKey)
      savePassedTests()
    }
    
    ElMessage.success(`Поздравляем! Вы успешно прошли тест с результатом ${score}%`)
    
    if (!isTestMode.value && !isTopicCompleted.value) {
      markAsCompleted()
    }
  }
}

const handleTestStarted = () => {
  // Test started handler
}

const loadCompletedTopics = () => {
  try {
    const saved = localStorage.getItem('completedTopics')
    if (saved) {
      completedTopics.value = new Set(JSON.parse(saved))
    }
  } catch (error) {
    console.error('Error loading completed topics:', error)
  }
}

const loadPassedTests = () => {
  try {
    const saved = localStorage.getItem('passedTests')
    if (saved) {
      passedTests.value = new Set(JSON.parse(saved))
    }
  } catch (error) {
    console.error('Error loading passed tests:', error)
  }
}

const savePassedTests = () => {
  try {
    localStorage.setItem('passedTests', JSON.stringify([...passedTests.value]))
  } catch (error) {
    console.error('Error saving passed tests:', error)
  }
}

// Watch for lesson changes to load lesson test
watch(() => currentLesson.value?.id, async (lessonId) => {
  // Load lesson test when lesson changes
  if (lessonId && !isFinalTestMode.value) {
    await loadLessonTest(lessonId)
  } else {
    lessonTest.value = null
  }
}, { immediate: true })

watch(() => [currentLessonIndex.value, currentTopicIndex.value], () => {
  if (!isTestMode.value) {
    loadTopicMaterials()
  }
}, { immediate: true })

// Watch for course program changes to load test
watch(() => courseProgram.value?.id, (newId) => {
  if (newId) {
    loadCourseTest()
  }
}, { immediate: true })

onMounted(async () => {
  loadDarkModePreference()
  
  const authResult = await authService.checkAuth()
  if (!authResult.isAuthenticated) {
    ElMessage.warning('Для доступа к уроку необходимо войти в систему')
    router.push(`/station/${stationId.value}/courses`)
    return
  }

  await loadStationAndProgram()

  loadCompletedTopics()
  loadPassedTests()
  loadTopicMaterials()
  
  // Load course test if program is available
  if (courseProgram.value?.id) {
    await loadCourseTest()
  }
})
</script>

<style scoped>
.lesson-content-app {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  height: 100vh;
}

/* Transitions */
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

/* Test Container */
.test-container {
  padding: 1rem;
  width: 100%;
  max-width: 100%;
  overflow: auto;
}

@media (min-width: 768px) {
  .test-container {
    padding: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .test-container {
    padding: 2rem;
  }
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 30;
}

/* Mobile menu now accessible only via header hamburger button */
</style>
