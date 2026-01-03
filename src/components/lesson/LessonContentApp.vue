<template>
  <div class="lesson-content-app">
    <!-- Lesson Header with User Account -->
    <LessonHeader
      :station-id="stationId"
      :station="station"
      :current-lesson="processedCurrentLesson"
      :show-sidebar="showSidebar"
      :show-materials-sidebar="showMaterialsSidebar"
      @toggle-sidebar="handleToggleSidebar"
      @toggle-materials-sidebar="handleToggleMaterialsSidebar"
    />

    <!-- Main Content Layout - CSS Grid -->
    <main class="lesson-grid">
      <!-- Main Content Area -->
      <section class="content-area">
        <!-- Test Mode -->
        <div
          v-if="isTestMode"
          class="test-container"
        >
          <TestQuiz 
            v-if="currentLessonTest"
            :test-data="currentLessonTest"
            @test-completed="handleTestCompleted"
            @test-started="handleTestStarted"
          />
          <el-empty
            v-else
            description="Тест для этого модуля пока недоступен"
            :image-size="80"
          />
        </div>

        <!-- Content Viewer (PDF/Video/Other) -->
        <ContentViewer
          v-else
          :current-file="currentFile"
          :current-file-type="currentFileType"
          :current-zoom="currentZoom"
          @zoom-in="zoomIn"
          @zoom-out="zoomOut"
          @download-file="downloadFile"
        />

        <!-- Desktop Navigation (hidden on mobile) -->
        <div class="navigation-section-desktop">
          <div class="navigation-buttons">
            <el-button
              :disabled="!hasPreviousLesson"
              :icon="ArrowLeft"
              size="small"
              plain
              class="nav-btn"
              aria-label="Предыдущий урок"
              @click="previousLesson"
            >
              <span class="nav-btn-text">Назад</span>
            </el-button>
            
            <div class="nav-center">
              <el-button
                v-if="!isTopicCompleted"
                type="success"
                :icon="Check"
                size="small"
                plain
                class="nav-btn"
                aria-label="Завершить урок"
                @click="markAsCompleted"
              >
                <span class="nav-btn-text">Завершить</span>
              </el-button>
              <el-tag
                v-else
                type="success"
                size="small"
                class="completed-tag"
                role="status"
                aria-label="Урок завершен"
              >
                <el-icon><Check /></el-icon>
                <span class="completed-text">Завершено</span>
              </el-tag>
            </div>

            <el-button
              :disabled="!hasNextLesson"
              type="primary"
              size="small"
              class="nav-btn"
              aria-label="Следующий урок"
              @click="nextLesson"
            >
              <span class="nav-btn-text">Далее</span>
              <el-icon class="nav-icon">
                <ArrowRight />
              </el-icon>
            </el-button>
          </div>
        </div>
      </section>
    </main>

    <!-- Left Sidebar Drawer (Lessons) -->
    <el-drawer
      v-model="showSidebar"
      :direction="isMobile || isTablet ? 'btt' : 'ltr'"
      :size="isMobile || isTablet ? '85vh' : drawerSize"
      :with-header="false"
      :modal="true"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      class="sidebar-drawer sidebar-drawer-left"
      role="navigation"
      aria-label="Навигация по урокам"
      @close="handleToggleSidebar"
      @opened="handleDrawerOpened('left')"
    >
      <LessonSidebar
        :lessons="processedLessons"
        :current-lesson-index="currentLessonIndex"
        :current-topic-index="currentTopicIndex"
        :completed-topics="completedTopics"
        :passed-tests="passedTests"
        :is-test-mode="isTestMode"
        @select-lesson="handleSelectLesson"
        @select-test="handleSelectTest"
        @toggle-sidebar="handleToggleSidebar"
      />
    </el-drawer>

    <!-- Right Sidebar Drawer (Materials) -->
    <el-drawer
      v-model="showMaterialsSidebar"
      :direction="isMobile || isTablet ? 'btt' : 'rtl'"
      :size="isMobile || isTablet ? '85vh' : drawerSize"
      :with-header="false"
      :modal="true"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      class="sidebar-drawer sidebar-drawer-right"
      role="complementary"
      aria-label="Материалы курса"
      @close="handleToggleMaterialsSidebar"
      @opened="handleDrawerOpened('right')"
    >
      <CourseMaterialsPanel
        :main-materials="mainMaterials"
        :additional-materials="additionalMaterials"
        :current-file="currentFile"
        :topic-title="currentTopic?.title || currentLesson?.title || ''"
        @select-material="openMaterial"
        @toggle-sidebar="handleToggleMaterialsSidebar"
      />
    </el-drawer>

    <!-- Mobile Navigation Footer -->
    <MobileNavigationFooter
      :has-previous="hasPreviousLesson"
      :has-next="hasNextLesson"
      :is-completed="isTopicCompleted"
      :is-visible="!isTestMode && (isMobile || isTablet)"
      @previous="previousLesson"
      @next="nextLesson"
      @complete="markAsCompleted"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ZoomIn, 
  ZoomOut, 
  Check,
  ArrowLeft,
  ArrowRight,
  Menu,
  Close,
  VideoPlay,
  Document,
  Folder
} from '@element-plus/icons-vue'
import LessonHeader from '@/components/lesson/LessonHeader.vue'
import LessonSidebar from '@/components/lesson/LessonSidebar.vue'
import TestQuiz from '@/components/lesson/TestQuiz.vue'
import CourseMaterialsPanel from '@/components/lesson/CourseMaterialsPanel.vue'
import MobileNavigationFooter from '@/components/lesson/MobileNavigationFooter.vue'
import testsData from '@/data/testsData.json'
import minioService from '@/services/minioService'
import authService from '@/services/auth'
import stationService from '@/services/stationService'

const ContentViewer = defineAsyncComponent(() => import('@/components/lesson/ContentViewer.vue'))

const route = useRoute()
const router = useRouter()

// Route params
const stationId = computed(() => parseInt(route.params.id))
const currentLessonIndex = ref(parseInt(route.params.lessonIndex) || 0)
const currentTopicIndex = ref(parseInt(route.params.topicIndex) || 0)
const isTestMode = ref(false)

// Data
const station = ref(null)
const courseProgram = ref(null)
const lessons = computed(() => courseProgram.value?.lessons || [])

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
  // Убираем паттерны: "Урок N:", "Урок № N:", "Урок N " и т.д.
  return title
    .replace(/^Урок\s*№?\s*\d+\s*:?\s*/i, '') // Убираем "Урок N:" или "Урок № N:"
    .replace(/^Урок\s*№?\s*\d+\s*/i, '') // Убираем "Урок N " или "Урок № N "
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

// Обработанный текущий урок без префикса "Урок N"
const processedCurrentLesson = computed(() => {
  if (!currentLesson.value) return null
  return {
    ...currentLesson.value,
    title: getLessonTitle(currentLesson.value.title)
  }
})

const currentTopic = computed(() => currentLesson.value?.topics?.[currentTopicIndex.value])

// ID for tracking completed topics
const currentTopicId = computed(() => `${stationId.value}-${currentLessonIndex.value}-${currentTopicIndex.value}`)

// Viewer state
const currentZoom = ref(100)

// Current file
const currentFile = ref(null)
const mainMaterials = ref([])
const additionalMaterials = ref([])

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
  
  // Определение PDF (приоритет)
  if (
    t.includes('pdf') ||
    t === 'application/pdf' ||
    name.endsWith('.pdf')
  ) {
    return 'pdf'
  }
  
  // Определение видео
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

const downloadFile = async (file) => {
  if (!file) return
  
  // Безопасность: запрещаем скачивание PDF документов
  const fileType = (file.type || '').toLowerCase()
  const fileName = (file.original_name || file.originalName || '').toLowerCase()
  const isPdf = fileType.includes('pdf') || fileType === 'application/pdf' || fileName.endsWith('.pdf')
  
  if (isPdf) {
    ElMessage.warning('Скачивание конфиденциальных PDF документов запрещено')
    return
  }
  
  // Для других типов файлов разрешаем скачивание (видео, изображения и т.д.)
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
    // Уменьшенный TTL для временных ссылок (1 час вместо 7 дней)
    const url = await minioService.getPresignedDownloadUrl(key, 60 * 60, file.type || null)
    window.open(url, '_blank')
  } catch (e) {
    ElMessage.error('Не удалось открыть файл')
  }
}

// Comments
const comments = ref([])

// Tests
const passedTests = ref(new Set())
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
const isFullscreen = ref(false)
const isMobile = ref(window.innerWidth < 768)
const isTablet = ref(window.innerWidth >= 768 && window.innerWidth < 1024)
const showSidebar = ref(window.innerWidth >= 1024) // По умолчанию виден на десктопе, скрыт на мобильном
const showMaterialsSidebar = ref(window.innerWidth >= 1024) // По умолчанию виден на десктопе, скрыт на мобильном
// Drawer size calculation (reactive to window width)
const windowWidth = ref(window.innerWidth)
const drawerSize = computed(() => {
  // Calculate drawer size based on viewport width (20% of viewport, min 18rem, max 20rem)
  const vw = windowWidth.value
  const calculated = Math.max(288, Math.min(320, vw * 0.2)) // 18rem = 288px, 20rem = 320px
  return `${calculated}px`
})

// Handle window resize
const handleResize = () => {
  const wasMobile = isMobile.value
  const wasTablet = isTablet.value
  const currentWidth = window.innerWidth
  
  windowWidth.value = currentWidth
  isMobile.value = currentWidth < 768
  isTablet.value = currentWidth >= 768 && currentWidth < 1024
  
  // При переходе с мобильного/планшета на десктоп показываем сайдбары
  if ((wasMobile || wasTablet) && !isMobile.value && !isTablet.value) {
    showSidebar.value = true
    showMaterialsSidebar.value = true
  }
  // При переходе с десктопа на мобильный/планшет скрываем сайдбары
  if (!wasMobile && !wasTablet && (isMobile.value || isTablet.value)) {
    showSidebar.value = false
    showMaterialsSidebar.value = false
  }
}

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
      // Очищаем материалы если нет урока/темы
      mainMaterials.value = []
      additionalMaterials.value = []
      currentFile.value = null
      return
    }

    // Загружаем материалы только из БД (course_program_topic_files)
    const dbFiles = Array.isArray(currentTopic.value?.files) ? currentTopic.value.files : []
    
    if (dbFiles.length === 0) {
      // Нет файлов в БД - показываем пустое состояние
      console.info('[LessonContentApp] No files found in DB for topic:', {
        lessonIndex: currentLessonIndex.value,
        topicIndex: currentTopicIndex.value,
        topicCode: currentTopic.value?.code
      })
      mainMaterials.value = []
      additionalMaterials.value = []
      currentFile.value = null
      return
    }

    // ✅ ПАРАЛЛЕЛЬНАЯ загрузка всех файлов из БД
    const filePromises = dbFiles.map(async (f) => {
      try {
        const fileType = f.fileType || f.file_type
        const objectKey = f.objectKey || f.object_key || f.objectName || f.object_name
        const originalName = f.originalName || f.original_name || f.fileName || f.file_name || f.title || 'file'
        const fileSize = f.fileSize ?? f.file_size ?? null
        const mimeType = f.mimeType || f.mime_type || null
        const isMain = f.isMain ?? f.is_main ?? false

        if (!objectKey) {
          console.warn('[LessonContentApp] Topic file missing objectKey:', f)
          return null
        }

        const nameForDetect = String(originalName || objectKey || '').toLowerCase()
        
        // Определяем Content-Type: приоритет у mimeType из БД, затем по типу/расширению
        const contentType =
          mimeType ||
          (fileType === 'pdf' || nameForDetect.endsWith('.pdf')
            ? 'application/pdf'
            : fileType === 'video' || nameForDetect.endsWith('.mp4') || nameForDetect.endsWith('.webm') || nameForDetect.endsWith('.ogg') || nameForDetect.endsWith('.ogv') || nameForDetect.endsWith('.mov')
              ? (nameForDetect.endsWith('.webm')
                ? 'video/webm'
                : nameForDetect.endsWith('.ogg') || nameForDetect.endsWith('.ogv')
                  ? 'video/ogg'
                  : nameForDetect.endsWith('.mov')
                    ? 'video/quicktime'
                    : 'video/mp4')
              : 'application/octet-stream')

        // Безопасность: для PDF используем streaming endpoint, для других - presigned URLs с коротким TTL
        const isPdf = fileType === 'pdf' || contentType.includes('pdf') || nameForDetect.endsWith('.pdf')
        
        let fileUrl = null
        if (isPdf) {
          // PDF: используем streaming endpoint (безопаснее, нет прямого доступа)
          // URL будет формироваться в SecurePDFViewer компоненте
          fileUrl = null // Не нужен presigned URL для PDF
        } else {
          // Для видео и других файлов: presigned URL с коротким TTL (1 час вместо 7 дней)
          fileUrl = await minioService.getPresignedDownloadUrl(objectKey, 60 * 60, contentType)
        }

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
          // is_main_file определяется только из БД (isMain), независимо от типа файла
          is_main_file: !!isMain
        }
      } catch (e) {
        console.error('[LessonContentApp] Failed to process topic file:', f, e)
        return null
      }
    })

    // ✅ Ждем все файлы параллельно
    const results = await Promise.allSettled(filePromises)
    const allFiles = results
      .filter(r => r.status === 'fulfilled' && r.value !== null)
      .map(r => r.value)

    // Разделяем на основные и дополнительные
    const mainFiles = allFiles.filter(f => f.is_main_file)
    const additionals = allFiles.filter(f => !f.is_main_file)

    mainMaterials.value = mainFiles
    additionalMaterials.value = additionals

    // Устанавливаем текущий файл (приоритет у основных файлов)
    if (mainFiles.length > 0) {
      currentFile.value = mainFiles[0]
    } else if (additionals.length > 0) {
      currentFile.value = additionals[0]
    } else {
      currentFile.value = null
    }

    console.log('[LessonContentApp] Materials loaded from DB:', {
      total: allFiles.length,
      main: mainFiles.length,
      additional: additionals.length,
      topicCode: currentTopic.value?.code
    })
  } catch (error) {
    console.error('[LessonContentApp] Error loading topic materials:', error)
    ElMessage.error('Не удалось загрузить материалы урока')
    // Очищаем состояние при ошибке
    mainMaterials.value = []
    additionalMaterials.value = []
    currentFile.value = null
  }
}

const isVideoFile = (file) => {
  if (!file) return false
  const fileName = (file.original_name || file.originalName || '').toLowerCase()
  const fileType = (file.type || '').toLowerCase()
  return fileName.endsWith('.mp4') || 
         fileName.endsWith('.webm') || 
         fileName.endsWith('.ogg') ||
         fileName.endsWith('.mov') ||
         fileType.includes('video')
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

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

const toggleFullscreen = async () => {
  if (!fullscreenContainer.value) return
  
  try {
    if (!isFullscreen.value) {
      if (fullscreenContainer.value.requestFullscreen) {
        await fullscreenContainer.value.requestFullscreen()
      } else if (fullscreenContainer.value.webkitRequestFullscreen) {
        await fullscreenContainer.value.webkitRequestFullscreen()
      } else if (fullscreenContainer.value.mozRequestFullScreen) {
        await fullscreenContainer.value.mozRequestFullScreen()
      } else if (fullscreenContainer.value.msRequestFullscreen) {
        await fullscreenContainer.value.msRequestFullscreen()
      }
      
      isFullscreen.value = true
      document.body.style.overflow = 'hidden'
    } else {
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        await document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        await document.msExitFullscreen()
      }
      
      isFullscreen.value = false
      document.body.style.overflow = ''
    }
  } catch (error) {
    console.error('Error toggling fullscreen:', error)
    isFullscreen.value = !isFullscreen.value
    if (isFullscreen.value) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement && 
      !document.webkitFullscreenElement && 
      !document.mozFullScreenElement && 
      !document.msFullscreenElement) {
    isFullscreen.value = false
    document.body.style.overflow = ''
  }
}

const openMaterial = (material) => {
  currentFile.value = material
  console.log('[LessonContentApp] Material selected:', {
    objectName: material?.objectName || material?.object_key || material?.objectKey,
    name: material?.original_name || material?.originalName || material?.fileName || material?.file_name,
    type: material?.type || material?.mimeType || material?.mime_type,
  })
}

const markAsCompleted = () => {
  completedTopics.value.add(currentTopicId.value)
  localStorage.setItem('completedTopics', JSON.stringify([...completedTopics.value]))
  ElMessage.success('Урок отмечен как завершенный!')
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

// Focus management for drawers
const handleDrawerOpened = (side) => {
  // Focus management will be handled by Element Plus Drawer component
  // But we can add screen reader announcements if needed
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    const announcement = side === 'left' 
      ? 'Открыта навигация по урокам'
      : 'Открыты материалы курса'
    // Note: Screen reader will automatically announce drawer opening
  }
}

const handleTestCompleted = ({ score, isPassed }) => {
  const testToSave = isTestMode.value ? currentLessonTest.value : currentTopicTest.value
  
  if (isPassed && testToSave) {
    passedTests.value.add(testToSave.id)
    savePassedTests()
    ElMessage.success(`Поздравляем! Вы успешно прошли тест с результатом ${score}%`)
    
    if (!isTestMode.value && !isTopicCompleted.value) {
      markAsCompleted()
    }
  }
}

const handleTestStarted = () => {
  console.log('Test started')
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

watch(() => [currentLessonIndex.value, currentTopicIndex.value], () => {
  if (!isTestMode.value) {
    loadTopicMaterials()
  }
}, { immediate: true })

onMounted(async () => {
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
  
  window.addEventListener('resize', handleResize)
  
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  
  if (isFullscreen.value) {
    document.body.style.overflow = ''
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(() => {})
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen().catch(() => {})
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen().catch(() => {})
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen().catch(() => {})
    }
  }
})
</script>

<style scoped>
.lesson-content-app {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

/* CSS Grid Layout */
.lesson-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
  height: calc(100vh - clamp(3.5rem, 10vw, 4.5rem));
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  gap: 0;
}

/* Content Area */
.content-area {
  background: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  padding: clamp(1rem, 2vw, 1.5rem);
  gap: 1rem;
}

/* Test Container */
.test-container {
  padding: clamp(0.75rem, 2vw, 1rem);
  width: 100%;
  max-width: 100%;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Viewer Container */
.viewer-container {
  position: relative;
  background: #f3f4f6;
  width: 100%;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.viewer-container.fullscreen-mode {
  position: fixed;
  inset: 0;
  z-index: 50;
  min-height: 100vh;
  aspect-ratio: auto;
}

/* Controls Bar */
.controls-bar {
  position: absolute;
  top: clamp(0.25rem, 1vw, 0.5rem);
  left: clamp(0.25rem, 1vw, 0.5rem);
  right: clamp(0.25rem, 1vw, 0.5rem);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(0.25rem, 1vw, 0.5rem);
  flex-wrap: wrap;
}

.controls-group {
  display: flex;
  align-items: center;
  gap: clamp(0.25rem, 1vw, 0.375rem);
  flex-wrap: wrap;
}

.control-btn {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(4px);
  width: clamp(2rem, 5vw, 2.5rem);
  height: clamp(2rem, 5vw, 2.5rem);
}

.zoom-tag {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(4px);
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  padding: clamp(0.25rem, 0.5vw, 0.375rem) clamp(0.5rem, 1vw, 0.75rem);
}

/* Video Viewer */
.video-content-viewer {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: clamp(0.5rem, 2vw, 1rem);
}

.video-content-viewer.fullscreen-video {
  height: 100vh;
  background: #000;
  padding: 0;
}

.video-player {
  width: 100%;
  max-width: 100%;
  height: auto;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.2s ease-out;
  will-change: transform;
}

/* Empty Placeholder */
.empty-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: clamp(20rem, 50vh, 25rem);
  width: 100%;
}

/* Desktop Navigation Section */
.navigation-section-desktop {
  border-top: 1px solid #e5e7eb;
  width: 100%;
  flex-shrink: 0;
  padding-top: clamp(0.75rem, 1.5vw, 1rem);
}

.navigation-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(0.5rem, 1.5vw, 1rem);
  flex-wrap: wrap;
}

.nav-btn {
  min-width: clamp(2.5rem, 8vw, 4rem);
  font-size: clamp(0.75rem, 2vw, 0.875rem);
}

.nav-btn-text {
  display: inline;
}

.nav-btn-text-desktop {
  display: none;
}

.nav-btn-text-mobile {
  display: inline;
}

.nav-center {
  display: flex;
  align-items: center;
  gap: clamp(0.25rem, 1vw, 0.5rem);
}

.completed-tag {
  font-size: clamp(0.75rem, 2vw, 0.875rem);
  padding: clamp(0.25rem, 0.5vw, 0.375rem) clamp(0.5rem, 1vw, 0.75rem);
}

.completed-text {
  margin-left: clamp(0.25rem, 0.5vw, 0.5rem);
  display: none;
}

.nav-icon {
  margin-left: clamp(0.25rem, 0.5vw, 0.5rem);
}

/* Custom Scrollbars */
.sidebar-left,
.sidebar-right,
.content-area {
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.sidebar-left:hover,
.sidebar-right:hover,
.content-area:hover {
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.sidebar-left::-webkit-scrollbar,
.sidebar-right::-webkit-scrollbar,
.content-area::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.sidebar-left::-webkit-scrollbar-track,
.sidebar-right::-webkit-scrollbar-track,
.content-area::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-left::-webkit-scrollbar-thumb,
.sidebar-right::-webkit-scrollbar-thumb,
.content-area::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 3px;
  transition: background 0.2s;
}

.sidebar-left:hover::-webkit-scrollbar-thumb,
.sidebar-right:hover::-webkit-scrollbar-thumb,
.content-area:hover::-webkit-scrollbar-thumb {
  background: #c1c1c1;
}

.sidebar-left:hover::-webkit-scrollbar-thumb:hover,
.sidebar-right:hover::-webkit-scrollbar-thumb:hover,
.content-area:hover::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Drawer Styles */
:deep(.sidebar-drawer .el-drawer__body) {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

:deep(.sidebar-drawer-left .el-drawer) {
  border-right: 1px solid #e5e7eb;
}

:deep(.sidebar-drawer-right .el-drawer) {
  border-left: 1px solid #e5e7eb;
}

/* Responsive Layout */
@media (max-width: 1023px) {
  .content-area {
    width: 100%;
    padding: clamp(0.75rem, 2vw, 1rem);
  }

  .navigation-section-desktop {
    display: none; /* Mobile footer handles navigation */
  }
}

/* Desktop (min-width: 1024px) */
@media (min-width: 1024px) {
  .content-area {
    padding: clamp(1.5rem, 2.5vw, 2rem);
    max-width: 1920px;
    margin: 0 auto;
  }
}

/* Wide monitors (min-width: 1440px) */
@media (min-width: 1440px) {
  .lesson-grid {
    max-width: 1920px;
    margin: 0 auto;
  }
}
</style>

