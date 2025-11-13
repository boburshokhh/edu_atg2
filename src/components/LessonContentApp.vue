<template>
  <div class="lesson-content-app h-screen bg-gray-50 overflow-hidden">
    <!-- Lesson Header with User Account -->
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

          <!-- PDF/Video Viewer -->
          <div 
            v-else 
            ref="fullscreenContainer"
            class="relative bg-gray-100" 
            :class="isFullscreen ? 'fixed inset-0 z-50' : ''"
          >
            <!-- Controls Bar -->
            <div 
              v-if="!isFullscreen || currentFileType !== 'video'"
              class="absolute top-2 left-2 right-2 z-10 flex items-center justify-between"
            >
              <div class="flex items-center gap-1.5">
                <el-button 
                  :icon="ZoomOut" 
                  circle 
                  size="small"
                  @click="zoomOut"
                  class="bg-white/90 backdrop-blur-sm"
                  :disabled="currentFileType === 'video' && isFullscreen"
                />
                <el-button 
                  :icon="ZoomIn" 
                  circle 
                  size="small"
                  @click="zoomIn"
                  class="bg-white/90 backdrop-blur-sm"
                  :disabled="currentFileType === 'video' && isFullscreen"
                />
                <el-tag class="bg-white/90 backdrop-blur-sm">
                  {{ currentZoom }}%
                </el-tag>
              </div>
              <div class="flex items-center gap-1.5">
                <el-button 
                  :icon="FullScreen" 
                  circle 
                  size="small"
                  @click="toggleFullscreen"
                  class="bg-white/90 backdrop-blur-sm"
                  title="Полный экран"
                />
              </div>
            </div>

            <!-- PDF Viewer -->
            <PdfViewer
              v-if="currentFile && currentFileType === 'pdf'"
              :source="currentFile.url || currentFile.file_url"
              :zoom="currentZoom"
              :is-fullscreen="isFullscreen"
            />

            <!-- Video Player -->
            <div 
              v-else-if="currentFile && currentFileType === 'video'"
              :class="[
                'video-content-viewer flex items-center justify-center',
                isFullscreen ? 'h-screen bg-black' : ''
              ]"
              :style="isFullscreen ? {} : { 
                transform: `scale(${currentZoom / 100})`,
                transformOrigin: 'center center'
              }"
            >
              <vue-plyr
                ref="videoPlayer"
                :class="isFullscreen ? 'w-full h-full' : 'w-full max-w-full'"
                :key="currentFile.url || currentFile.file_url"
                style="max-height: 100vh;"
              >
                <video
                  :src="currentFile.url || currentFile.file_url"
                  preload="metadata"
                  playsinline
                  crossorigin="anonymous"
                >
                  Ваш браузер не поддерживает воспроизведение видео.
                </video>
              </vue-plyr>
            </div>

            <!-- Unsupported File Type -->
            <div 
              v-else-if="currentFile && currentFileType === 'unknown'"
              class="flex flex-col items-center justify-center min-h-[400px] p-8"
            >
              <el-icon :size="64" class="text-gray-400 mb-4">
                <Document />
              </el-icon>
              <h3 class="text-lg font-semibold text-gray-700 mb-2">
                Неподдерживаемый формат файла
              </h3>
              <p class="text-sm text-gray-500 mb-4">
                {{ currentFile.original_name || currentFile.originalName || 'Файл' }}
              </p>
              <el-button 
                type="primary" 
                @click="downloadFile(currentFile)"
              >
                Скачать файл
              </el-button>
            </div>

            <!-- No Content Placeholder -->
            <div v-else class="flex items-center justify-center min-h-[400px]">
              <el-empty description="Выберите материал для просмотра" :image-size="80" />
            </div>
          </div>

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
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ZoomIn, 
  ZoomOut, 
  Check,
  ArrowLeft,
  ArrowRight,
  FullScreen,
  Menu,
  Close,
  VideoPlay,
  Document
} from '@element-plus/icons-vue'
import LessonHeader from '@/components/LessonHeader.vue'
import LessonSidebar from '@/components/LessonSidebar.vue'
import TestQuiz from '@/components/TestQuiz.vue'
import PdfViewer from '@/components/PdfViewer.vue'
import CourseMaterialsPanel from '@/components/CourseMaterialsPanel.vue'
import { stationsData } from '@/data/stationsData.js'
import courseMaterials from '@/data/courseMaterials.json'
import testsData from '@/data/testsData.json'
import minioService from '@/services/minioService'
import pdfService from '@/services/pdfService'
import authService from '@/services/auth'

const route = useRoute()
const router = useRouter()

// Route params
const stationId = computed(() => parseInt(route.params.id))
const currentLessonIndex = ref(parseInt(route.params.lessonIndex) || 0)
const currentTopicIndex = ref(parseInt(route.params.topicIndex) || 0)
const isTestMode = ref(false)

// Data
const station = computed(() => stationsData[stationId.value] || stationsData[1])
const lessons = computed(() => station.value?.courseProgram?.lessons || [])
const currentLesson = computed(() => lessons.value[currentLessonIndex.value])
const currentTopic = computed(() => currentLesson.value?.topics?.[currentTopicIndex.value])

// ID for tracking completed topics
const currentTopicId = computed(() => `${stationId.value}-${currentLessonIndex.value}-${currentTopicIndex.value}`)

// PDF State
const pdfPages = ref([])
const totalPages = ref(0)
const canvasRefs = ref([])
const currentZoom = ref(100)
const pdfViewerContainer = ref(null)
const currentPdfDocument = ref(null)
const fullscreenContainer = ref(null)

// Current file
const currentFile = ref(null)
const mainMaterials = ref([])
const additionalMaterials = ref([])

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
const isMobile = ref(window.innerWidth < 1024)
const showSidebar = ref(!isMobile.value) // По умолчанию виден на десктопе, скрыт на мобильном
const showMaterialsSidebar = ref(!isMobile.value) // По умолчанию виден на десктопе, скрыт на мобильном

// Handle window resize
const handleResize = () => {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 1024
  
  // При переходе с мобильного на десктоп показываем сайдбары
  if (wasMobile && !isMobile.value) {
    showSidebar.value = true
    showMaterialsSidebar.value = true
  }
  // При переходе с десктопа на мобильный скрываем сайдбары
  if (!wasMobile && isMobile.value) {
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
const setCanvasRef = (el, index) => {
  if (el) {
    canvasRefs.value[index] = el
  }
}

const loadTopicMaterials = async () => {
  try {
    const lessonData = courseMaterials.lessons.find(l => 
      l.lessonTitle === currentLesson.value.title ||
      l.lessonTitle.replace(':', '.') === currentLesson.value.title.replace(':', '.')
    )

    if (!lessonData) {
      console.warn('Lesson data not found')
      return
    }

    const topicData = lessonData.topics.find(t => {
      const topicCodeNormalized = (t.topicCode || '').replace(/\.$/, '').trim()
      const topicCodeFromData = (currentTopic.value.code || '').replace(/\.$/, '').trim()
      return topicCodeNormalized === topicCodeFromData
    })

    if (!topicData || !topicData.files) {
      console.warn('Topic data not found')
      return
    }

    const mainFiles = []
    const additionals = []

    for (const fileConfig of topicData.files) {
      try {
        // Determine MIME type based on file extension and config
        const fileName = (fileConfig.fileName || fileConfig.objectName || '').toLowerCase()
        let mimeType = 'application/octet-stream'
        
        // Check by fileConfig.fileType first
        if (fileConfig.fileType === 'pdf') {
          mimeType = 'application/pdf'
        } else if (fileConfig.fileType === 'video') {
          // Determine specific video MIME type by extension
          if (fileName.endsWith('.webm')) {
            mimeType = 'video/webm'
          } else if (fileName.endsWith('.ogg')) {
            mimeType = 'video/ogg'
          } else if (fileName.endsWith('.mov')) {
            mimeType = 'video/quicktime'
          } else {
            mimeType = 'video/mp4'
          }
        } else {
          // Auto-detect by extension if fileType not specified
          if (fileName.endsWith('.pdf')) {
            mimeType = 'application/pdf'
          } else if (fileName.endsWith('.mp4')) {
            mimeType = 'video/mp4'
          } else if (fileName.endsWith('.webm')) {
            mimeType = 'video/webm'
          } else if (fileName.endsWith('.ogg')) {
            mimeType = 'video/ogg'
          } else if (fileName.endsWith('.mov')) {
            mimeType = 'video/quicktime'
          } else if (fileName.endsWith('.avi')) {
            mimeType = 'video/x-msvideo'
          } else if (fileName.endsWith('.mkv')) {
            mimeType = 'video/x-matroska'
          }
        }
        
        const fileUrl = await minioService.getPresignedDownloadUrl(
          fileConfig.objectName,
          7 * 24 * 60 * 60,
          mimeType
        )

        const fileObject = {
          objectName: fileConfig.objectName,
          fileName: fileConfig.fileName,
          original_name: fileConfig.fileName,
          originalName: fileConfig.fileName,
          file_size: fileConfig.fileSize,
          sizeFormatted: fileConfig.sizeFormatted,
          url: fileUrl,
          file_url: fileUrl,
          type: mimeType
        }

        if (fileConfig.is_main_file) {
          mainFiles.push(fileObject)
        } else {
          additionals.push(fileObject)
        }
      } catch (error) {
        console.error('Error loading file:', error)
      }
    }

    mainMaterials.value = mainFiles
    additionalMaterials.value = additionals

    if (mainFiles.length > 0) {
      currentFile.value = mainFiles[0]
      const fileType = detectFileType(currentFile.value)
      if (fileType === 'pdf') {
        await loadPdfDocument(currentFile.value)
      }
    }
  } catch (error) {
    console.error('Error loading topic materials:', error)
    ElMessage.error('Не удалось загрузить материалы урока')
  }
}

const loadPdfDocument = async (file) => {
  if (!file || !file.url) return
  
  try {
    const pdf = await pdfService.loadPdfDocument(file.url)
    currentPdfDocument.value = pdf
    totalPages.value = pdf.numPages
    pdfPages.value = new Array(totalPages.value).fill(null)
    
    await nextTick()
    await renderAllPages(pdf)
  } catch (error) {
    console.error('Error loading PDF:', error)
    ElMessage.error('Не удалось загрузить PDF документ')
  }
}

const renderAllPages = async (pdf) => {
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 300))
  
  for (let pageNum = 1; pageNum <= totalPages.value; pageNum++) {
    try {
      const page = await pdfService.getPdfPage(pdf, pageNum)
      let canvas = canvasRefs.value[pageNum - 1]
      
      let retries = 0
      while (!canvas && retries < 5) {
        await new Promise(resolve => setTimeout(resolve, 100))
        canvas = canvasRefs.value[pageNum - 1]
        retries++
      }
      
      if (!canvas) continue
      
      const optimalScale = pdfService.calculateOptimalScale(page, 1000)
      await pdfService.renderPdfPage(page, canvas, optimalScale)
    } catch (error) {
      console.error(`Error rendering page ${pageNum}:`, error)
    }
  }
}

// File type detection
const detectFileType = (file) => {
  if (!file) return 'unknown'
  
  const fileName = (file.original_name || file.originalName || file.fileName || '').toLowerCase()
  const fileType = (file.type || '').toLowerCase()
  const url = (file.url || file.file_url || '').toLowerCase()
  
  // Check by MIME type first (most reliable)
  if (fileType.includes('pdf') || fileType === 'application/pdf') {
    return 'pdf'
  }
  
  if (fileType.includes('video')) {
    return 'video'
  }
  
  // Check by file extension
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v', '.3gp']
  const pdfExtensions = ['.pdf']
  
  // Check URL extension
  if (url) {
    for (const ext of pdfExtensions) {
      if (url.includes(ext)) return 'pdf'
    }
    for (const ext of videoExtensions) {
      if (url.includes(ext)) return 'video'
    }
  }
  
  // Check filename extension
  if (fileName) {
    for (const ext of pdfExtensions) {
      if (fileName.endsWith(ext)) return 'pdf'
    }
    for (const ext of videoExtensions) {
      if (fileName.endsWith(ext)) return 'video'
    }
  }
  
  // Check by objectName if available
  const objectName = (file.objectName || '').toLowerCase()
  if (objectName) {
    for (const ext of pdfExtensions) {
      if (objectName.endsWith(ext)) return 'pdf'
    }
    for (const ext of videoExtensions) {
      if (objectName.endsWith(ext)) return 'video'
    }
  }
  
  return 'unknown'
}

const isVideoFile = (file) => {
  return detectFileType(file) === 'video'
}

const isPdfFile = (file) => {
  return detectFileType(file) === 'pdf'
}

// Computed property for current file type
const currentFileType = computed(() => {
  if (!currentFile.value) return 'unknown'
  return detectFileType(currentFile.value)
})

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
  // Если это видео, используем встроенный fullscreen Plyr
  if (currentFileType.value === 'video' && videoPlayer.value && videoPlayer.value.player) {
    try {
      if (!isFullscreen.value) {
        await videoPlayer.value.player.fullscreen.enter()
        isFullscreen.value = true
      } else {
        await videoPlayer.value.player.fullscreen.exit()
        isFullscreen.value = false
      }
    } catch (error) {
      console.error('Error toggling Plyr fullscreen:', error)
      // Fallback to container fullscreen
      toggleContainerFullscreen()
    }
  } else if (fullscreenContainer.value) {
    // Для PDF используем стандартный fullscreen API
    toggleContainerFullscreen()
  }
}

const toggleContainerFullscreen = async () => {
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
  // Проверяем стандартный fullscreen API
  if (!document.fullscreenElement && 
      !document.webkitFullscreenElement && 
      !document.mozFullScreenElement && 
      !document.msFullscreenElement) {
    // Проверяем Plyr fullscreen для видео
    if (currentFileType.value === 'video' && videoPlayer.value && videoPlayer.value.player) {
      if (!videoPlayer.value.player.fullscreen.active) {
        isFullscreen.value = false
        document.body.style.overflow = ''
      }
    } else {
      isFullscreen.value = false
      document.body.style.overflow = ''
    }
  }
}

const openMaterial = (material) => {
  currentFile.value = material
  const fileType = detectFileType(material)
  if (fileType === 'pdf') {
    loadPdfDocument(material)
  }
}

const downloadFile = (file) => {
  if (!file || (!file.url && !file.file_url)) {
    ElMessage.error('URL файла недоступен')
    return
  }
  
  const url = file.url || file.file_url
  const link = document.createElement('a')
  link.href = url
  link.download = file.original_name || file.originalName || file.fileName || 'download'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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

// Watch for current file changes to auto-load PDF or update video
watch(() => currentFile.value, async (newFile, oldFile) => {
  if (newFile && newFile !== oldFile) {
    if (currentFileType.value === 'pdf') {
      await loadPdfDocument(newFile)
    } else if (currentFileType.value === 'video' && videoPlayer.value && videoPlayer.value.player) {
      // Обновляем источник видео в Plyr
      const player = videoPlayer.value.player
      if (player.media) {
        player.source = {
          type: 'video',
          sources: [{
            src: newFile.url || newFile.file_url,
            type: newFile.type || 'video/mp4'
          }]
        }
      }
    }
  }
}, { immediate: false })

onMounted(async () => {
  const authResult = await authService.checkAuth()
  if (!authResult.isAuthenticated) {
    ElMessage.warning('Для доступа к уроку необходимо войти в систему')
    router.push(`/station/${stationId.value}/courses`)
    return
  }

  loadCompletedTopics()
  loadPassedTests()
  loadTopicMaterials()
  
  window.addEventListener('resize', handleResize)
  
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
  
  // Добавляем обработчики событий Plyr для видео
  watch(() => videoPlayer.value, (plyrComponent) => {
    if (plyrComponent && plyrComponent.player) {
      const player = plyrComponent.player
      
      // Обработчик входа в fullscreen
      player.on('enterfullscreen', () => {
        isFullscreen.value = true
        document.body.style.overflow = 'hidden'
      })
      
      // Обработчик выхода из fullscreen
      player.on('exitfullscreen', () => {
        isFullscreen.value = false
        document.body.style.overflow = ''
      })
    }
  }, { immediate: true })
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

.pdf-content-viewer {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.pdf-content-viewer .pdf-canvas {
  user-drag: none;
  -webkit-user-drag: none;
  display: block;
  max-width: 100%;
  height: auto;
  image-orientation: from-image;
  -webkit-image-orientation: from-image;
}

.pdf-content-viewer > div {
  transition: transform 0.2s ease-out;
  will-change: transform;
}

.video-content-viewer {
  transition: transform 0.2s ease-out;
  will-change: transform;
  overflow: hidden;
}

.video-content-viewer :deep(.plyr) {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100vh;
}

.video-content-viewer :deep(.plyr__video-wrapper) {
  width: 100%;
  height: 100%;
}

.video-content-viewer :deep(.plyr__video) {
  width: 100%;
  height: 100%;
  object-fit: contain;
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

:deep(.lesson-tabs) {
  .el-tabs__header {
    margin: 0;
    padding: 0 16px;
    background: #f9fafb;
  }
  
  .el-tabs__nav-wrap::after {
    display: none;
  }
  
  .el-tabs__item {
    font-weight: 600;
    font-size: 13px;
    padding: 0 12px;
  }
}

@media (max-width: 768px) {
  :deep(.el-tabs__item) {
    font-size: 12px;
    padding: 0 8px;
  }
}

.material-card {
  cursor: pointer;
  transition: all 0.2s;
}

.material-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.material-card-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.material-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.material-icon-video {
  background-color: #fee2e2;
  color: #dc2626;
}

.material-icon-doc {
  background-color: #dbeafe;
  color: #2563eb;
}

.material-info {
  flex: 1;
  min-width: 0;
}

.material-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  padding: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-size {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
  padding: 0;
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

