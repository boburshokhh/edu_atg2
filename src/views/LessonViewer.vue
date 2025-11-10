<template>
  <div class="lesson-viewer min-h-screen bg-gray-50">
    <!-- Compact Header -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-[1920px] mx-auto px-4 py-3">
        <!-- Breadcrumb -->
        <nav class="flex items-center space-x-1.5 text-xs text-gray-600 mb-2">
          <router-link :to="`/stations`" class="hover:text-blue-600 transition-colors">
            Станции
          </router-link>
          <ChevronRightIcon class="w-3 h-3" />
          <router-link :to="`/station/${stationId}`" class="hover:text-blue-600 transition-colors">
            {{ station?.shortName }}
          </router-link>
          <ChevronRightIcon class="w-3 h-3" />
          <router-link :to="`/station/${stationId}/courses`" class="hover:text-blue-600 transition-colors">
            Программа
          </router-link>
          <ChevronRightIcon class="w-3 h-3" />
          <span class="text-gray-900 font-medium truncate max-w-[200px]">{{ currentLesson?.title }}</span>
        </nav>

        <!-- Compact Title and Progress -->
        <div class="flex items-center justify-between gap-4">
          <div class="flex-1 min-w-0">
            <h1 class="text-lg md:text-xl font-bold text-gray-900 mb-0.5 truncate">
              {{ currentTopic?.title || currentLesson?.title }}
            </h1>
          </div>
          
          <!-- Compact Progress -->
          <div class="flex items-center gap-2">
            <el-progress 
              :percentage="courseProgress" 
              :stroke-width="6"
              :width="50"
              type="circle"
              :color="progressColor"
              class="hidden sm:block"
            />
            <div class="text-right">
              <div class="text-xs text-gray-600">Прогресс</div>
              <div class="text-lg font-bold text-blue-600">{{ courseProgress }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-[1920px] mx-auto">
      <div class="flex relative">
        <!-- Mobile Menu Button -->
        <button
          @click="showSidebar = !showSidebar"
          class="fixed bottom-4 left-4 z-40 lg:hidden w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition-colors"
        >
          <el-icon :size="20">
            <Menu v-if="!showSidebar" />
            <Close v-else />
          </el-icon>
        </button>

        <!-- Sidebar with Mobile Overlay -->
        <div
          v-if="showSidebar"
          @click="showSidebar = false"
          class="fixed inset-0 bg-black/50 z-30 lg:hidden"
        ></div>
        
        <transition name="slide">
          <LessonSidebar
            v-show="showSidebar || !isMobile"
            :lessons="lessons"
            :current-lesson-index="currentLessonIndex"
            :current-topic-index="currentTopicIndex"
            :completed-topics="completedTopics"
            :passed-tests="passedTests"
            :is-test-mode="isTestMode"
            @select-lesson="handleSelectLesson"
            @select-test="handleSelectTest"
            :class="[
              'flex-shrink-0',
              isMobile ? 'fixed left-0 top-0 h-screen z-40' : 'sticky top-0'
            ]"
          />
        </transition>

        <!-- Main Content Area -->
        <div class="flex-1 p-3 md:p-4 min-w-0">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
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
              <!-- Compact Controls Bar -->
              <div class="absolute top-2 left-2 right-2 z-10 flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <el-button 
                    :icon="ZoomOut" 
                    circle 
                    size="small"
                    @click="zoomOut"
                    class="bg-white/90 backdrop-blur-sm"
                  />
                  <el-button 
                    :icon="ZoomIn" 
                    circle 
                    size="small"
                    @click="zoomIn"
                    class="bg-white/90 backdrop-blur-sm"
                  />
                  <span class="bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg text-xs font-medium shadow-sm">
                    {{ currentZoom }}%
                  </span>
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

              <!-- PDF Viewer - Compact -->
              <div 
                v-if="currentFile && currentFile.type?.includes('pdf')"
                :class="[
                  'pdf-content-viewer overflow-y-auto',
                  isFullscreen ? 'h-screen p-4' : 'min-h-[400px] max-h-[500px] p-4'
                ]"
                @contextmenu.prevent
                ref="pdfViewerContainer"
              >
                <div 
                  class="max-w-3xl mx-auto"
                  :style="{ 
                    transform: `scale(${currentZoom / 100})`,
                    transformOrigin: 'top center'
                  }"
                >
                  <div
                    v-for="(page, index) in pdfPages"
                    :key="`page-${index}`"
                    class="mb-4 bg-white shadow-md rounded"
                  >
                    <canvas 
                      :ref="el => setCanvasRef(el, index)"
                      class="w-full pdf-canvas"
                      style="image-orientation: from-image;"
                    ></canvas>
                  </div>
                </div>
                
                <!-- Compact Page Info -->
                <div class="text-center py-2">
                  <span class="text-xs text-gray-600">
                    Страница 1-{{ totalPages }} из {{ totalPages }}
                  </span>
                </div>
              </div>

              <!-- Video Player - Compact -->
              <div 
                v-else-if="currentFile && isVideoFile(currentFile)"
                :class="[
                  'video-content-viewer flex items-center justify-center',
                  isFullscreen ? 'h-screen bg-black' : ''
                ]"
              >
                <video
                  ref="videoPlayer"
                  class="w-full"
                  :class="isFullscreen ? 'max-h-screen' : 'max-h-[500px]'"
                  :style="{ 
                    transform: `scale(${currentZoom / 100})`,
                    transformOrigin: 'center center'
                  }"
                  controls
                  :src="currentFile.url || currentFile.file_url"
                >
                  Ваш браузер не поддерживает воспроизведение видео.
                </video>
              </div>

              <!-- No Content Placeholder -->
              <div v-else class="flex items-center justify-center min-h-[400px]">
                <div class="text-center">
                  <DocumentTextIcon class="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p class="text-sm text-gray-500">Выберите материал для просмотра</p>
                </div>
              </div>
            </div>

            <!-- Navigation and Tabs -->
            <div class="border-t border-gray-200">
              <!-- Compact Navigation Buttons -->
              <div class="flex items-center justify-between px-3 md:px-4 py-3 bg-gray-50 gap-2">
                <el-button
                  @click="previousLesson"
                  :disabled="!hasPreviousLesson"
                  :icon="ArrowLeft"
                  size="small"
                  class="text-xs md:text-sm"
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
                    class="text-xs md:text-sm"
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
                  class="text-xs md:text-sm"
                >
                  <span class="hidden sm:inline">Далее</span>
                  <el-icon class="sm:ml-2"><ArrowRight /></el-icon>
                </el-button>
              </div>

              <!-- Compact Tabs -->
              <el-tabs v-model="activeTab" class="lesson-tabs">
                <el-tab-pane name="materials">
                  <template #label>
                    <span>Материалы</span>
                  </template>
                  <div class="p-3 md:p-4">
                    <h3 class="text-base font-bold text-gray-900 mb-3">
                      Дополнительные материалы
                    </h3>
                    
                    <div v-if="additionalMaterials.length > 0" class="grid grid-cols-1 gap-2">
                      <div
                        v-for="(material, index) in additionalMaterials"
                        :key="index"
                        class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                        @click="openMaterial(material)"
                      >
                        <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                             :class="isVideoFile(material) ? 'bg-red-100' : 'bg-blue-100'">
                          <PlayCircleIcon v-if="isVideoFile(material)" class="w-5 h-5 text-red-600" />
                          <DocumentTextIcon v-else class="w-5 h-5 text-blue-600" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <h4 class="text-sm font-semibold text-gray-900 truncate">
                            {{ material.original_name || material.originalName }}
                          </h4>
                          <p class="text-xs text-gray-600">
                            {{ material.sizeFormatted || formatFileSize(material.file_size) }}
                          </p>
                        </div>
                      </div>
                    </div>
                    <el-empty v-else description="Нет дополнительных материалов" :image-size="80" />
                  </div>
                </el-tab-pane>

                <el-tab-pane name="comments">
                  <template #label>
                    <span>Комментарии</span>
                    <el-badge :value="comments.length" class="ml-2" v-if="comments.length > 0" />
                  </template>
                  
                  <CommentsSection
                    :comments="comments"
                    :lesson-id="currentLessonId"
                    :topic-id="currentTopicId"
                    @add-comment="handleAddComment"
                    @reply-comment="handleReplyComment"
                  />
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ZoomIn, 
  ZoomOut, 
  Download, 
  Printer,
  Check,
  ArrowLeft,
  ArrowRight,
  FullScreen,
  Menu,
  Close
} from '@element-plus/icons-vue'
import { 
  ChevronRightIcon, 
  DocumentTextIcon,
  PlayCircleIcon
} from '@heroicons/vue/24/solid'
import LessonSidebar from '@/components/LessonSidebar.vue'
import CommentsSection from '@/components/CommentsSection.vue'
import TestQuiz from '@/components/TestQuiz.vue'
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

// IDs for comments
const currentLessonId = computed(() => `${stationId.value}-${currentLessonIndex.value}`)
const currentTopicId = computed(() => `${currentLessonId.value}-${currentTopicIndex.value}`)

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
const additionalMaterials = ref([])

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
  // Находим тест для текущего урока (с topicIndex === null)
  return testsData.tests.find(test => 
    test.lessonIndex === currentLessonIndex.value && 
    test.topicIndex === null
  )
})

const topicTestPassed = computed(() => {
  if (!currentTopicTest.value) return false
  return passedTests.value.has(currentTopicTest.value.id)
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

const progressColor = computed(() => {
  if (courseProgress.value < 30) return '#f56c6c'
  if (courseProgress.value < 70) return '#e6a23c'
  return '#67c23a'
})

// UI State
const activeTab = ref('materials')
const isFullscreen = ref(false)
const showSidebar = ref(false)
const isMobile = ref(window.innerWidth < 1024)

// Handle window resize
const handleResize = () => {
  isMobile.value = window.innerWidth < 1024
  if (!isMobile.value) {
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
        const fileUrl = await minioService.getPresignedDownloadUrl(
          fileConfig.objectName,
          7 * 24 * 60 * 60,
          fileConfig.fileType === 'pdf' ? 'application/pdf' : 
          fileConfig.fileType === 'video' ? 'video/mp4' : 'application/octet-stream'
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
          type: fileConfig.fileType === 'pdf' ? 'application/pdf' : 
                fileConfig.fileType === 'video' ? 'video/mp4' : 'application/octet-stream'
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

    // Load the first main file
    if (mainFiles.length > 0) {
      currentFile.value = mainFiles[0]
      if (currentFile.value.type?.includes('pdf')) {
        await loadPdfDocument(currentFile.value)
      }
    }

    additionalMaterials.value = additionals
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
      
      // Используем оптимальный масштаб для отрисовки
      const optimalScale = pdfService.calculateOptimalScale(page, 1000)
      await pdfService.renderPdfPage(page, canvas, optimalScale)
    } catch (error) {
      console.error(`Error rendering page ${pageNum}:`, error)
    }
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
      // Входим в полноэкранный режим
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
      // Выходим из полноэкранного режима
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
    // Fallback на CSS режим
    isFullscreen.value = !isFullscreen.value
    if (isFullscreen.value) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
}

// Обработчик выхода из полноэкранного режима через ESC
const handleFullscreenChange = () => {
  if (!document.fullscreenElement && 
      !document.webkitFullscreenElement && 
      !document.mozFullScreenElement && 
      !document.msFullscreenElement) {
    isFullscreen.value = false
    document.body.style.overflow = ''
  }
}

const downloadCurrentFile = () => {
  // Disabled for protection
  ElMessage.warning('Загрузка отключена для защиты контента')
}

const printCurrentFile = () => {
  // Disabled for protection
  ElMessage.warning('Печать отключена для защиты контента')
}

const openMaterial = (material) => {
  currentFile.value = material
  if (material.type?.includes('pdf')) {
    loadPdfDocument(material)
  }
  activeTab.value = 'materials'
}

const downloadMaterial = (material) => {
  // Disabled
  ElMessage.warning('Загрузка отключена для защиты контента')
}

const markAsCompleted = () => {
  completedTopics.value.add(currentTopicId.value)
  // Save to localStorage
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
  // Close sidebar on mobile after selection
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleSelectTest = ({ lessonIndex }) => {
  currentLessonIndex.value = lessonIndex
  isTestMode.value = true
  // Close sidebar on mobile after selection
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleAddComment = (commentData) => {
  const newComment = {
    id: Date.now(),
    author: authService.getCurrentUser()?.full_name || 'Anonymous',
    authorAvatar: authService.getCurrentUser()?.avatar_url || '',
    content: commentData.content,
    timestamp: new Date().toISOString(),
    replies: []
  }
  comments.value.unshift(newComment)
  // TODO: Save to backend
  ElMessage.success('Комментарий добавлен!')
}

const handleReplyComment = ({ commentId, content }) => {
  const comment = comments.value.find(c => c.id === commentId)
  if (comment) {
    const reply = {
      id: Date.now(),
      author: authService.getCurrentUser()?.full_name || 'Anonymous',
      authorAvatar: authService.getCurrentUser()?.avatar_url || '',
      content: content,
      timestamp: new Date().toISOString()
    }
    if (!comment.replies) {
      comment.replies = []
    }
    comment.replies.push(reply)
    // TODO: Save to backend
    ElMessage.success('Ответ добавлен!')
  }
}

// Test handlers
const handleTestCompleted = ({ score, isPassed }) => {
  const testToSave = isTestMode.value ? currentLessonTest.value : currentTopicTest.value
  
  if (isPassed && testToSave) {
    passedTests.value.add(testToSave.id)
    savePassedTests()
    ElMessage.success(`Поздравляем! Вы успешно прошли тест с результатом ${score}%`)
    
    // Автоматически отметить тему как завершенную (только для тестов топиков)
    if (!isTestMode.value && !isTopicCompleted.value) {
      markAsCompleted()
    }
  }
}

const handleTestStarted = () => {
  // Можно добавить аналитику или другие действия при начале теста
  console.log('Test started')
}

// Load completed topics from localStorage
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

// Load passed tests from localStorage
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

// Save passed tests to localStorage
const savePassedTests = () => {
  try {
    localStorage.setItem('passedTests', JSON.stringify([...passedTests.value]))
  } catch (error) {
    console.error('Error saving passed tests:', error)
  }
}

// Watch for route changes
watch(() => [currentLessonIndex.value, currentTopicIndex.value], () => {
  if (!isTestMode.value) {
    loadTopicMaterials()
  }
}, { immediate: true })

onMounted(async () => {
  // Check authentication
  const authResult = await authService.checkAuth()
  if (!authResult.isAuthenticated) {
    ElMessage.warning('Для доступа к уроку необходимо войти в систему')
    router.push(`/station/${stationId.value}/courses`)
    return
  }

  loadCompletedTopics()
  loadPassedTests()
  loadTopicMaterials()
  
  // Add resize listener
  window.addEventListener('resize', handleResize)
  
  // Add fullscreen event listeners
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
})

onUnmounted(() => {
  // Clean up
  window.removeEventListener('resize', handleResize)
  
  // Remove fullscreen event listeners
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  
  if (isFullscreen.value) {
    document.body.style.overflow = ''
    // Попытка выйти из полноэкранного режима при размонтировании
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
  /* Убеждаемся, что ориентация изображения берется из самого изображения */
  image-orientation: from-image;
  -webkit-image-orientation: from-image;
}

/* Плавная анимация масштабирования */
.pdf-content-viewer > div {
  transition: transform 0.2s ease-out;
}

.video-content-viewer video {
  transition: transform 0.2s ease-out;
}

/* Slide animation for mobile sidebar */
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

/* Mobile responsive */
@media (max-width: 768px) {
  :deep(.el-tabs__item) {
    font-size: 12px;
    padding: 0 8px;
  }
}

/* Fullscreen styles */
:deep(.fixed.inset-0) {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  background: #000;
}

:deep(.fixed.inset-0 .pdf-content-viewer) {
  height: 100vh !important;
  max-height: 100vh !important;
  overflow-y: auto;
  padding: 2rem;
}

:deep(.fixed.inset-0 .video-content-viewer) {
  height: 100vh !important;
  width: 100vw !important;
}

:deep(.fixed.inset-0 video) {
  max-width: 100vw;
  max-height: 100vh;
  width: auto;
  height: auto;
}

@media print {
  body * {
    visibility: hidden;
  }
}
</style>

