<template>
  <div class="lesson-content-app min-h-screen bg-gray-50">
    <!-- Lesson Header with User Account -->
    <LessonHeader
      :station-id="stationId"
      :station="station"
      :current-lesson="processedCurrentLesson"
    />

    <!-- Main Content Layout -->
    <el-container class="main-container">
      <!-- Left Sidebar (Lessons) -->
      <transition name="slide">
        <LessonSidebar
          v-show="showSidebar"
          :lessons="processedLessons"
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

      <!-- Mobile Overlay for Left Sidebar -->
      <div
        v-if="showSidebar && isMobile"
        @click="showSidebar = false"
        class="mobile-overlay"
      ></div>

      <!-- Mobile Overlay for Right Sidebar (Materials) -->
      <div
        v-if="showMaterialsSidebar && isMobile"
        @click="showMaterialsSidebar = false"
        class="mobile-overlay"
      ></div>

      <!-- Expand Left Sidebar Button (when sidebar is hidden) -->
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
      <el-main class="main-content-area">
        <el-card class="lesson-content-card" shadow="never">
          <!-- Test Mode -->
          <div v-if="isTestMode" class="test-container">
            <TestQuiz 
              v-if="currentLessonTest"
              :test-data="currentLessonTest"
              @test-completed="handleTestCompleted"
              @test-started="handleTestStarted"
            />
            <el-empty v-else description="Тест для этого модуля пока недоступен" :image-size="80" />
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

          <!-- Navigation and Tabs -->
          <div class="navigation-section">
            <!-- Navigation Buttons -->
            <div class="navigation-buttons">
              <el-button
                @click="previousLesson"
                :disabled="!hasPreviousLesson"
                :icon="ArrowLeft"
                size="small"
                class="nav-btn"
              >
                <span class="nav-btn-text">Назад</span>
              </el-button>
              
              <div class="nav-center">
                <el-button
                  v-if="!isTopicCompleted"
                  type="success"
                  @click="markAsCompleted"
                  :icon="Check"
                  size="small"
                  class="nav-btn"
                >
                  <span class="nav-btn-text-desktop">Завершить</span>
                  <span class="nav-btn-text-mobile">✓</span>
                </el-button>
                <el-tag v-else type="success" size="small" class="completed-tag">
                  <el-icon><Check /></el-icon>
                  <span class="completed-text">Завершено</span>
                </el-tag>
              </div>

              <el-button
                @click="nextLesson"
                :disabled="!hasNextLesson"
                type="primary"
                size="small"
                class="nav-btn"
              >
                <span class="nav-btn-text">Далее</span>
                <el-icon class="nav-icon"><ArrowRight /></el-icon>
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

      <!-- Expand Right Sidebar Button (when sidebar is hidden) -->
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

    <!-- Mobile Menu Buttons -->
    <el-button
      @click="showSidebar = !showSidebar"
      class="mobile-menu-btn mobile-menu-btn-left"
      type="primary"
      circle
    >
      <el-icon class="mobile-menu-icon">
        <Menu v-if="!showSidebar" />
        <Close v-else />
      </el-icon>
    </el-button>

    <!-- Mobile Materials Button -->
    <el-button
      @click="showMaterialsSidebar = !showMaterialsSidebar"
      class="mobile-menu-btn mobile-menu-btn-right"
      type="primary"
      circle
    >
      <el-icon class="mobile-menu-icon">
        <Folder v-if="!showMaterialsSidebar" />
        <Close v-else />
      </el-icon>
    </el-button>
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
import LessonHeader from '@/components/LessonHeader.vue'
import LessonSidebar from '@/components/LessonSidebar.vue'
import TestQuiz from '@/components/TestQuiz.vue'
import CourseMaterialsPanel from '@/components/CourseMaterialsPanel.vue'
import courseMaterials from '@/data/courseMaterials.json'
import testsData from '@/data/testsData.json'
import minioService from '@/services/minioService'
import authService from '@/services/auth'
import stationService from '@/services/stationService'

const ContentViewer = defineAsyncComponent(() => import('@/components/ContentViewer.vue'))

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

// Fast lookup for materials by stable topicKey (preferred over title/code matching)
const materialsByTopicKey = computed(() => {
  const m = new Map()
  try {
    const lessons = courseMaterials?.lessons || []
    for (const l of lessons) {
      for (const t of l.topics || []) {
        if (t?.topicKey) {
          m.set(t.topicKey, t)
        }
      }
    }
  } catch (e) {
    console.warn('[LessonContentApp] Failed to build materialsByTopicKey index', e)
  }
  return m
})

const fallbackWarned = ref(new Set())

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
  const t = (f.type || '').toLowerCase()
  const name = (f.original_name || f.originalName || '').toLowerCase()
  if (t.includes('pdf') || name.endsWith('.pdf')) return 'pdf'
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
    const url = await minioService.getPresignedDownloadUrl(key, 7 * 24 * 60 * 60, file.type || null)
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

// Handle window resize
const handleResize = () => {
  const wasMobile = isMobile.value
  const wasTablet = isTablet.value
  const currentWidth = window.innerWidth
  
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
      return
    }

    // 1) Prefer DB-backed topic files (course_program_topic_files)
    const dbFiles = Array.isArray(currentTopic.value?.files) ? currentTopic.value.files : []
    if (dbFiles.length > 0) {
      const filePromises = dbFiles.map(async (f) => {
        try {
          const fileType = f.fileType || f.file_type
          const objectKey = f.objectKey || f.object_key || f.objectName || f.object_name
          const originalName = f.originalName || f.original_name || f.fileName || f.file_name || f.title || 'file'
          const fileSize = f.fileSize ?? f.file_size ?? null
          const mimeType = f.mimeType || f.mime_type || null
          const isMain = f.isMain ?? f.is_main ?? false

          const nameForDetect = String(originalName || objectKey || '').toLowerCase()
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

          if (!objectKey) {
            console.warn('[LessonContentApp] Topic file missing objectKey:', f)
            return null
          }

          const fileUrl = await minioService.getPresignedDownloadUrl(objectKey, 7 * 24 * 60 * 60, contentType)

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
            is_main_file: !!(isMain && (fileType === 'pdf' || contentType.includes('pdf')))
          }
        } catch (e) {
          console.error('[LessonContentApp] Failed to presign topic file:', f, e)
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
      return
    }

    // Prefer stable topicKey mapping
    let topicData = null
    const stableKey = currentTopic.value?.topicKey || currentTopic.value?.topic_key
    if (stableKey && materialsByTopicKey.value.has(stableKey)) {
      topicData = materialsByTopicKey.value.get(stableKey)
    } else {
      // Fallback legacy lookup by lesson title + topic code
      const lessonData = courseMaterials.lessons.find(l => 
        l.lessonTitle === currentLesson.value.title ||
        l.lessonTitle.replace(':', '.') === currentLesson.value.title.replace(':', '.')
      )

      if (!lessonData) {
        console.warn('[LessonContentApp] DB topic files empty; fallback lesson not found in courseMaterials.json')
        return
      }

      topicData = lessonData.topics.find(t => {
        const topicCodeNormalized = (t.topicCode || '').replace(/\.$/, '').trim()
        const topicCodeFromData = (currentTopic.value.code || '').replace(/\.$/, '').trim()
        return topicCodeNormalized === topicCodeFromData
      })
    }

    if (!topicData || !topicData.files) {
      console.warn('[LessonContentApp] DB topic files empty; fallback topic not found in courseMaterials.json')
      return
    }

    // Warn once per topic when using legacy JSON fallback
    if (stableKey && !fallbackWarned.value.has(stableKey)) {
      fallbackWarned.value.add(stableKey)
      ElMessage.warning('Материалы загружены из legacy JSON (в БД нет файлов для этой темы)')
    }

    // ✅ ПАРАЛЛЕЛЬНАЯ загрузка всех presigned URL
    const filePromises = topicData.files.map(async (fileConfig) => {
      try {
        const contentType = fileConfig.fileType === 'pdf' 
          ? 'application/pdf' 
          : fileConfig.fileType === 'video' 
            ? 'video/mp4' 
            : 'application/octet-stream'
            
        const fileUrl = await minioService.getPresignedDownloadUrl(
          fileConfig.objectName,
          7 * 24 * 60 * 60,
          contentType
        )

        return {
          objectName: fileConfig.objectName,
          fileName: fileConfig.fileName,
          original_name: fileConfig.fileName,
          originalName: fileConfig.fileName,
          file_size: fileConfig.fileSize,
          sizeFormatted: fileConfig.sizeFormatted,
          url: fileUrl,
          file_url: fileUrl,
          type: contentType,
          is_main_file: fileConfig.is_main_file
        }
      } catch (error) {
        console.error('Error loading file:', error)
        return null
      }
    })

    // ✅ Ждем все файлы параллельно
    const fileResults = await Promise.allSettled(filePromises)
    const allFiles = fileResults
      .filter(r => r.status === 'fulfilled' && r.value !== null)
      .map(r => r.value)

    // Разделяем на основные и дополнительные
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
    console.error('Error loading topic materials:', error)
    ElMessage.error('Не удалось загрузить материалы урока')
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
  padding-top: 0;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  height: 100vh;
}

/* Main Container */
.main-container {
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-wrap: nowrap;
  overflow: hidden;
  height: calc(100vh - clamp(3.5rem, 10vw, 4.5rem)); /* Вычитаем высоту header */
}

:deep(.el-main) {
  padding: 0;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.main-content-area {
  flex: 1;
  min-width: 0;
  padding: clamp(0.5rem, 1.5vw, 1rem) !important;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.lesson-content-card {
  border-radius: clamp(0.5rem, 1vw, 0.75rem);
  width: 100%;
  max-width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

/* Navigation Section */
.navigation-section {
  border-top: 1px solid #e5e7eb;
  width: 100%;
  flex-shrink: 0;
}

.navigation-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: clamp(0.5rem, 1.5vw, 0.75rem) clamp(0.5rem, 2vw, 1rem);
  background: #f9fafb;
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

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 30;
}

/* Mobile Menu Buttons */
.mobile-menu-btn {
  position: fixed;
  bottom: clamp(1rem, 4vw, 1.5rem);
  z-index: 40;
  width: clamp(3rem, 8vw, 3.5rem);
  height: clamp(3rem, 8vw, 3.5rem);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.mobile-menu-btn-left {
  left: clamp(1rem, 4vw, 1.5rem);
}

.mobile-menu-btn-right {
  right: clamp(1rem, 4vw, 1.5rem);
}

.mobile-menu-icon {
  font-size: clamp(1rem, 3vw, 1.25rem);
}

/* Sidebar Expand Buttons */
.sidebar-expand-btn {
  position: fixed;
  top: clamp(4.5rem, 12vw, 5rem);
  z-index: 50;
  width: clamp(2.5rem, 6vw, 2.75rem);
  height: clamp(2.5rem, 6vw, 2.75rem);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.sidebar-expand-btn-left {
  left: clamp(0.75rem, 2vw, 1rem);
}

.sidebar-expand-btn-right {
  right: clamp(0.75rem, 2vw, 1rem);
}

.sidebar-expand-btn:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: scale(1.1);
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

/* Media Queries */
/* Mobile phones (max-width: 480px) */
@media (max-width: 480px) {
  .main-content-area {
    padding: clamp(0.5rem, 2vw, 0.75rem) !important;
}

  .controls-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: clamp(0.25rem, 1.5vw, 0.5rem);
}

  .controls-group {
    width: 100%;
    justify-content: space-between;
  }

  .navigation-buttons {
    flex-direction: column;
    gap: clamp(0.5rem, 2vw, 0.75rem);
  }

  .nav-btn {
    width: 100%;
  justify-content: center;
  }

  .nav-center {
    width: 100%;
    justify-content: center;
  }

  .completed-text {
    display: inline;
}
}

/* Tablets (max-width: 768px) */
@media (max-width: 768px) {
  .nav-btn-text-desktop {
    display: none;
  }

  .nav-btn-text-mobile {
    display: inline;
  }

  .completed-text {
    display: none;
}

  .mobile-overlay {
    display: block;
  }
}

/* Small laptops (max-width: 1024px) */
@media (max-width: 1024px) {
  .main-container {
    flex-wrap: wrap;
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
}

/* Desktop (min-width: 1025px) */
@media (min-width: 1025px) {
  .main-container {
    max-width: 1920px;
  }

  .nav-btn-text {
    display: inline;
  }

  .nav-btn-text-desktop {
    display: inline;
  }

  .nav-btn-text-mobile {
    display: none;
}

  .completed-text {
    display: inline;
  }

  .mobile-overlay {
    display: none;
  }
}

/* Wide monitors (min-width: 1440px) */
@media (min-width: 1440px) {
  .main-container {
    max-width: 1920px;
    margin: 0 auto;
  }

  .viewer-container {
    min-height: clamp(31.25rem, 60vh, 43.75rem);
  }
}

/* Hide mobile menu on desktop */
@media (min-width: 1025px) {
  .mobile-menu-btn {
    display: none;
}
}

/* Mobile phones - adjust button positions */
@media (max-width: 480px) {
  .mobile-menu-btn-left {
    left: clamp(0.75rem, 3vw, 1rem);
    bottom: clamp(0.75rem, 3vw, 1rem);
}

  .mobile-menu-btn-right {
    right: clamp(0.75rem, 3vw, 1rem);
    bottom: clamp(0.75rem, 3vw, 1rem);
  }
}
</style>

