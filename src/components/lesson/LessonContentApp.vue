<template>
  <div class="lesson-content-app flex flex-1 h-full overflow-hidden bg-background-light dark:bg-background-dark">
    <!-- Main Content Layout -->
    <div class="flex flex-1 h-full overflow-hidden">
      <!-- Left Sidebar (Lessons) -->
      <LessonSidebar
        v-show="showSidebar"
        :lessons="processedLessons"
        :current-lesson-index="currentLessonIndex"
        :current-topic-index="currentTopicIndex"
        :completed-topics="completedTopics"
        :passed-tests="passedTests"
        :is-test-mode="isTestMode"
        :course-title="courseTitle"
        :course-progress="courseProgress"
        :current-file="currentFile"
        :station-id="stationId"
        @select-lesson="handleSelectLesson"
        @select-test="handleSelectTest"
        @select-file="handleSelectFile"
        @toggle-sidebar="handleToggleSidebar"
      />

      <!-- Mobile Overlay for Left Sidebar -->
      <div
        v-if="showSidebar && isMobile"
        class="mobile-overlay"
        @click="showSidebar = false"
      />

      <!-- Main Content Area -->
      <main class="flex-1 bg-white dark:bg-slate-900 flex flex-col h-full relative overflow-hidden">
        <!-- Lesson Header -->
        <LessonHeader
          :station-id="stationId"
          :station="station"
          :current-lesson="processedCurrentLesson"
          :current-file="currentFile"
          :current-zoom="currentZoom"
          :is-topic-completed="isTopicCompleted"
          @zoom-in="zoomIn"
          @zoom-out="zoomOut"
          @mark-complete="markAsCompleted"
          @toggle-menu="showSidebar = !showSidebar"
        />

        <!-- Content Area -->
        <div class="flex-1 overflow-auto p-8 flex justify-center bg-white dark:bg-slate-900 relative">
          <!-- Test Mode -->
          <div
            v-if="isTestMode"
            class="test-container w-full max-w-4xl"
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
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// Icons removed - using Material Symbols now
import LessonHeader from '@/components/lesson/LessonHeader.vue'
import LessonSidebar from '@/components/lesson/LessonSidebar.vue'
import TestQuiz from '@/components/lesson/TestQuiz.vue'
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

// Course title
const courseTitle = computed(() => {
  return station.value?.name || courseProgram.value?.title || 'Курс обучения'
})

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

// Handle window resize
const handleResize = () => {
  const wasMobile = isMobile.value
  const wasTablet = isTablet.value
  const currentWidth = window.innerWidth
  
  isMobile.value = currentWidth < 768
  isTablet.value = currentWidth >= 768 && currentWidth < 1024
  
  // При переходе с мобильного/планшета на десктоп показываем сайдбар
  if ((wasMobile || wasTablet) && !isMobile.value && !isTablet.value) {
    showSidebar.value = true
  }
  // При переходе с десктопа на мобильный/планшет скрываем сайдбар
  if (!wasMobile && !wasTablet && (isMobile.value || isTablet.value)) {
    showSidebar.value = false
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

const isSelectingFile = ref(false) // Flag to prevent loadTopicMaterials from overriding selected file

const handleSelectFile = async ({ lessonIndex, topicIndex, file }) => {
  // Set flag to prevent loadTopicMaterials from overriding
  isSelectingFile.value = true
  
  // Set current lesson and topic first
  currentLessonIndex.value = lessonIndex
  currentTopicIndex.value = topicIndex
  isTestMode.value = false
  
  // Process file similar to loadTopicMaterials
  try {
    const fileType = file.fileType || file.file_type
    const objectKey = file.objectKey || file.object_key || file.objectName || file.object_name
    const originalName = file.originalName || file.original_name || file.fileName || file.file_name || file.title || 'file'
    const fileSize = file.fileSize ?? file.file_size ?? null
    const mimeType = file.mimeType || file.mime_type || null

    if (!objectKey) {
      ElMessage.warning('Файл недоступен')
      isSelectingFile.value = false
      return
    }

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

    const isPdf = fileType === 'pdf' || contentType.includes('pdf') || nameForDetect.endsWith('.pdf')
    
    let fileUrl = null
    if (!isPdf) {
      fileUrl = await minioService.getPresignedDownloadUrl(objectKey, 60 * 60, contentType)
    }

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
      is_main_file: file.isMain ?? file.is_main ?? false
    }

    // Update route after setting file
    updateRoute()
    
    // Reset flag after a short delay to allow watch to complete
    await nextTick()
    setTimeout(() => {
      isSelectingFile.value = false
    }, 200)
  } catch (error) {
    console.error('[LessonContentApp] Error loading file:', error)
    ElMessage.error('Не удалось загрузить файл')
    isSelectingFile.value = false
  }
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
  if (!isTestMode.value && !isSelectingFile.value) {
    // Загружаем материалы для текущей темы
    // Но не перезагружаем, если пользователь только что выбрал файл
    loadTopicMaterials()
  }
}, { immediate: true })

// Watch for file changes to update current file in sidebar
watch(() => currentFile.value, (newFile) => {
  if (newFile) {
    console.log('[LessonContentApp] Current file updated:', {
      objectName: newFile.objectName || newFile.object_key,
      name: newFile.originalName || newFile.original_name
    })
  }
})

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


/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 30;
}

</style>

