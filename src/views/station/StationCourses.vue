<template>
  <!-- Hero Section с фото станции -->
    <div class="relative h-[80vh] min-h-[700px] overflow-hidden">
      <!-- Изображение станции -->
      <div class="absolute inset-0">
        <img 
          :src="stationImageSrc" 
          :alt="station?.name"
          class="w-full h-full object-cover"
        >
        <!-- Градиентный оверлей -->
        <div class="absolute inset-0 bg-gradient-to-r from-black/80 via-black/60 to-transparent" />
        <!-- Дополнительный вертикальный градиент для читаемости текста -->
        <div class="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-transparent" />
      </div>

      <!-- Контент хедера -->
      <div class="relative h-full page-container flex flex-col gap-6 md:gap-10 pt-28 pb-16">
        <!-- Навигация -->
        <div>
          <button 
            class="inline-flex items-center bg-white/10 backdrop-blur-md text-white hover:bg-white/20 transition-all duration-300 group px-4 py-2.5 rounded-xl border border-white/20 hover:border-white/40"
            @click="$router.push('/stations')"
          >
            <ChevronLeftIcon class="w-5 h-5 mr-2 transition-transform group-hover:-translate-x-1" />
            <span class="text-sm font-semibold">Все станции</span>
          </button>

          <!-- Breadcrumb сразу под кнопкой -->
          <nav class="mt-4 flex items-center space-x-2 text-sm text-white/70">
            <a
              href="/stations"
              class="hover:text-white transition-colors"
            >Станции</a>
            <ChevronRightIcon class="w-4 h-4" />
            <a
              :href="`/station/${stationId}`"
              class="hover:text-white transition-colors"
            >{{ station?.short_name || station?.shortName }}</a>
            <ChevronRightIcon class="w-4 h-4" />
            <span class="text-white font-medium">Обучающая программа</span>
          </nav>
        </div>

        <!-- Основная информация -->
        <div class="max-w-4xl">
          <div class="inline-flex items-center bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-md px-3.5 py-1.5 rounded-full mb-3 border border-white/20">
            <BookOpenIcon class="w-4 h-4 mr-2 text-white" />
            <span class="text-sm font-semibold text-white">Онлайн-тренинг</span>
          </div>

          <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-3 leading-tight">
            {{ courseProgram?.title }}
          </h1>
          
          <p class="text-base md:text-lg text-white/90 mb-6 max-w-3xl leading-relaxed">
            {{ courseProgram?.description }}
          </p>

          <!-- Статистика курса -->
          <div class="flex flex-wrap gap-4">
            <div class="flex items-center gap-2">
              <div class="w-9 h-9 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center">
                <ClockIcon class="w-5 h-5 text-white" />
              </div>
              <div>
                <div class="text-white/70 text-xs">
                  Длительность
                </div>
                <div class="text-white font-bold">
                  {{ courseStats.duration }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-9 h-9 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center">
                <PlayCircleIcon class="w-5 h-5 text-white" />
              </div>
              <div>
                <div class="text-white/70 text-xs">
                  Видеоуроков
                </div>
                <div class="text-white font-bold">
                  {{ courseStats.videos }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-9 h-9 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center">
                <DocumentTextIcon class="w-5 h-5 text-white" />
              </div>
              <div>
                <div class="text-white/70 text-xs">
                  Материалов
                </div>
                <div class="text-white font-bold">
                  {{ courseStats.materials }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="bg-gray-50">
      <div class="page-container py-12">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left Column - Course Content -->
          <div class="lg:col-span-2">
            <!-- Modern Tabs -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
              <div class="border-b border-gray-100">
                <nav class="flex">
                  <button 
                    :class="[
                      'flex-1 py-3 px-4 font-semibold text-sm transition-all relative',
                      activeTab === 'about' 
                        ? 'text-blue-600 bg-blue-50/50' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    ]"
                    @click="activeTab = 'about'"
                  >
                    О программе
                    <div
                      v-if="activeTab === 'about'"
                      class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
                    />
                  </button>
                  <button 
                    :class="[
                      'flex-1 py-3 px-4 font-semibold text-sm transition-all relative',
                      activeTab === 'curriculum' 
                        ? 'text-blue-600 bg-blue-50/50' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    ]"
                    @click="activeTab = 'curriculum'"
                  >
                    Программа тренинга
                    <div
                      v-if="activeTab === 'curriculum'"
                      class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
                    />
                  </button>
                </nav>
              </div>

              <!-- Tab Content -->
              <div class="p-8">
                <!-- About Tab -->
                <div v-show="activeTab === 'about'">
                  <h2 class="text-3xl font-bold text-gray-900 mb-6">
                    О программе
                  </h2>
                  
                  <!-- Learning Outcomes -->
                  <div class="mb-10">
                    <h3 class="text-xl font-bold text-gray-900 mb-5 flex items-center">
                      <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                        <svg
                          class="w-5 h-5 text-green-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </div>
                      Что вы изучите
                    </h3>
                    <div class="grid md:grid-cols-2 gap-4">
                      <div
                        v-for="(item, index) in courseProgram?.learningOutcomes"
                        :key="index" 
                        class="flex items-start p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                      >
                        <svg
                          class="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-gray-700">{{ item }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Requirements -->
                  <div class="mb-10">
                    <h3 class="text-xl font-bold text-gray-900 mb-5 flex items-center">
                      <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                        <svg
                          class="w-5 h-5 text-blue-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </div>
                      Требования
                    </h3>
                    <ul class="space-y-3">
                      <li
                        v-for="(req, index) in courseProgram?.requirements"
                        :key="index" 
                        class="flex items-start p-4 bg-blue-50 rounded-xl"
                      >
                        <svg
                          class="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-gray-700">{{ req }}</span>
                      </li>
                    </ul>
                  </div>

                  <!-- Target Audience -->
                  <div>
                    <h3 class="text-xl font-bold text-gray-900 mb-5 flex items-center">
                      <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                        <svg
                          class="w-5 h-5 text-purple-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </div>
                      Целевая аудитория
                    </h3>
                    <div class="grid md:grid-cols-2 gap-4">
                      <div
                        v-for="(audience, index) in courseProgram?.targetAudience"
                        :key="index" 
                        class="flex items-center space-x-3 p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors"
                      >
                        <div class="w-10 h-10 bg-purple-200 rounded-full flex items-center justify-center flex-shrink-0">
                          <svg
                            class="w-5 h-5 text-purple-700"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fill-rule="evenodd"
                              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                              clip-rule="evenodd"
                            />
                          </svg>
                        </div>
                        <span class="font-medium text-gray-900">{{ audience }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Curriculum Tab -->
                <div v-show="activeTab === 'curriculum'">
                  <!-- Используем компоненту CourseCurriculum для отображения структуры курса -->
                  <CourseCurriculum 
                    :lessons="courseProgram?.lessons || []"
                    :final-test="courseProgram?.finalTest"
                    @start-test="handleStartTest"
                    @start-final-test="handleStartFinalTest"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column - Sidebar -->
          <div class="lg:col-span-1">
            <div class="sticky top-28 space-y-6">
              <!-- Video Player Card -->
              <div
                v-if="sidebarVideoUrl"
                class="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 overflow-hidden"
              >
                <h3 class="text-sm font-bold text-gray-900 mb-3 uppercase tracking-wide">
                  Видео
                </h3>
                <div
                  class="relative w-full rounded-lg overflow-hidden bg-black"
                  style="aspect-ratio: 16/9;"
                >
                  <video
                    ref="sidebarVideoPlayer"
                    class="w-full h-full"
                    :src="sidebarVideoUrl"
                    controls
                    preload="metadata"
                    playsinline
                    crossorigin="anonymous"
                    @error="handleVideoError"
                  >
                    Ваш браузер не поддерживает воспроизведение видео.
                  </video>
                  <div
                    v-if="loadingSidebarVideo"
                    class="absolute inset-0 bg-black/50 flex items-center justify-center"
                  >
                    <div class="text-white text-center">
                      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2" />
                      <p class="text-xs">
                        Загрузка видео...
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Enrollment Card -->
              <el-card
                class="enrollment-card"
                shadow="always"
              >
                <div class="enrollment-card-content">
                  <el-button 
                    type="primary"
                    size="large"
                    class="start-learning-btn"
                    @click="startLearning"
                  >
                    <template #icon>
                      <PlayCircleIcon class="w-5 h-5" />
                    </template>
                    Начать обучение
                  </el-button>

                  <el-divider />
                  
                  <div class="enrollment-info">
                    <div class="enrollment-info-item">
                      <div class="enrollment-info-label">
                        <ClockIcon class="w-4 h-4" />
                        <span>Формат</span>
                      </div>
                      <span class="enrollment-info-value">Онлайн</span>
                    </div>
                    
                    <el-divider />
                    
                    <div class="enrollment-info-item">
                      <div class="enrollment-info-label">
                        <BookOpenIcon class="w-4 h-4" />
                        <span>Доступ</span>
                      </div>
                      <span class="enrollment-info-value">Навсегда</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Video Player -->
    <el-dialog
      v-model="showVideoPlayer"
      :title="currentVideo?.original_name || currentVideo?.originalName || 'Видеоурок'"
      width="90%"
      :before-close="handleVideoClose"
      @close="handleVideoClose"
    >
      <EducationalVideoPlayer
        v-if="currentVideo"
        :source="currentVideo"
        :require-auth="false"
        :save-progress="true"
        :progress-key="`video_${currentVideo.objectName || currentVideo.id}`"
        @ended="handleVideoEnd"
      />
      <template #footer>
        <div class="flex items-center justify-between w-full">
          <el-button
            :disabled="currentVideoIndex === 0"
            @click="playPreviousVideo"
          >
            <el-icon class="mr-2">
              <ArrowLeft />
            </el-icon>
            Предыдущее видео
          </el-button>
          <el-button
            type="primary"
            :disabled="currentVideoIndex >= allVideos.length - 1"
            @click="playNextVideo"
          >
            Следующее видео
            <el-icon class="ml-2">
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </template>
    </el-dialog>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import useNotify from '@/composables/useNotify'
import EducationalVideoPlayer from '@/components/video/EducationalVideoPlayer.vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import CourseCurriculum from '@/components/course/CourseCurriculum.vue'
import courseMaterials from '@/data/courseMaterials.json'
import minioService from '@/services/minioService'
import authService from '@/services/auth'
import stationService from '@/services/stationService'
import { ElMessage } from 'element-plus'
import { ClockIcon, PlayCircleIcon, DocumentTextIcon, BookOpenIcon, ChevronRightIcon, ChevronLeftIcon, TrophyIcon, ArrowDownTrayIcon } from '@heroicons/vue/24/solid'

export default {
  name: 'StationCourses',
  components: {
    EducationalVideoPlayer,
    CourseCurriculum,
    ArrowLeft,
    ArrowRight,
    ClockIcon,
    PlayCircleIcon,
    DocumentTextIcon,
    BookOpenIcon,
    ChevronRightIcon,
    ChevronLeftIcon,
    TrophyIcon,
    ArrowDownTrayIcon
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const notify = useNotify()
    const stationId = computed(() => parseInt(route.params.id))
    const station = ref(null)
    const courseProgramData = ref(null)
    const expandedLessons = ref([]) // Все уроки закрыты по умолчанию
    const activeTab = ref('curriculum') // Программа тренинга по умолчанию
    
    // Проверка авторизации
    const isAuthenticated = computed(() => {
      return authService.getCurrentUser() !== null
    })
    // Материалы из MinIO для каждой темы
    const topicMaterials = ref({}) // { 'lessonIndex-topicIndex': { mainPdf: {...}, additionals: [...] } }
    const loadingLessons = ref(false)

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
        console.warn('[StationCourses] Failed to build materialsByTopicKey index', e)
      }
      return m
    })
    
    // Изображение станции из MinIO
    const stationImageUrl = ref(null)
    
    // Sidebar Video Player State
    const sidebarVideoUrl = ref(null)
    const loadingSidebarVideo = ref(false)
    const sidebarVideoPlayer = ref(null)
    
    // Video Player State
    const showVideoPlayer = ref(false)
    const currentVideo = ref(null)
    const currentVideoIndex = ref(0)
    const allVideos = ref([]) // Все видео из текущего урока/темы


    const courseProgram = computed(() => courseProgramData.value)

    // Computed для URL изображения станции
    const stationImageSrc = computed(() => {
      const imageName = station.value?.image
      if (!imageName) {
        return ''
      }
      // Если уже загружен presigned URL, используем его
      if (stationImageUrl.value) {
        return stationImageUrl.value
      }
      // Иначе возвращаем прямой URL как fallback
      try {
        const objectName = imageName.includes('/') ? imageName : `stations/${imageName}`
        return minioService.getFileUrl(objectName)
      } catch (error) {
        console.error('Ошибка получения URL изображения:', error)
        return ''
      }
    })

    // Загрузить изображение станции из MinIO
    const loadStationImage = async () => {
      if (!station.value?.image) return
      try {
        // station.image can be either "WKC1.jpg" or "stations/WKC1.jpg"
        const objectName = station.value.image.includes('/') ? station.value.image : `stations/${station.value.image}`
        const url = await minioService.getPresignedDownloadUrl(
          objectName,
          7 * 24 * 60 * 60,
          'image/jpeg'
        )
        stationImageUrl.value = url
      } catch (error) {
        console.error('Ошибка загрузки изображения станции:', error)
      }
    }

    // Загрузить короткое видео о станции (promo video)
    const loadSidebarVideo = async () => {
      try {
        loadingSidebarVideo.value = true
        const promo = await stationService.getStationPromoVideo(stationId.value)
        if (!promo?.objectKey) {
          sidebarVideoUrl.value = null
          return
        }

        sidebarVideoUrl.value = await minioService.getPresignedDownloadUrl(
          promo.objectKey,
          7 * 24 * 60 * 60, // 7 дней
          'video/mp4'
        )
      } catch (error) {
        console.error('Ошибка загрузки видео для бокового меню:', error)
      } finally {
        loadingSidebarVideo.value = false
      }
    }

    // Обработчик ошибки видео
    const handleVideoError = (event) => {
      console.error('Ошибка воспроизведения видео:', event)
      loadingSidebarVideo.value = false
    }

    // Гибкое определение основного материала (оставлено для совместимости, если нужно)
    const isMainMaterial = (fileName, topicCode, topicTitle) => {
      if (!fileName || !topicCode) return false
      
      const normalizedFileName = fileName.toLowerCase().trim()
      const normalizedTopicCode = topicCode.toLowerCase().trim()
      
      // Извлекаем код темы (например, "1.2" из "Тема 1.2")
      const codeMatch = normalizedTopicCode.match(/тема\s*(\d+\.\d+)/i)
      if (codeMatch) {
        const fullCode = codeMatch[1] // Например, "1.2"
        
        // Вариант 1: Файл начинается с "Тема X.Y " (с пробелом после кода)
        // Например: "Тема 1.2 Вычислители расхода газа.pdf"
        const patternWithSpace = new RegExp(`^тема\\s*${fullCode.replace('.', '\\.')}\\s+`, 'i')
        if (patternWithSpace.test(normalizedFileName)) {
          return true
        }
        
        // Вариант 2: Файл начинается с "Тема X.Y." (с точкой после кода)
        // Например: "Тема 1.2. Вычислители расхода газа.pdf"
        const patternWithDot = new RegExp(`^тема\\s*${fullCode.replace('.', '\\.')}\\.`, 'i')
        if (patternWithDot.test(normalizedFileName)) {
          return true
        }
      }
      
      // Вариант 3: Файл начинается с "Тема X." где X - номер урока
      const topicMatch = normalizedTopicCode.match(/тема\s*(\d+)\.\d+/i)
      if (topicMatch) {
        const lessonNumber = topicMatch[1]
        // Проверяем "Тема 1.", "Тема 1.1.", "Тема1." и т.д.
        const patterns = [
          new RegExp(`^тема\\s*${lessonNumber}\\.`, 'i'),
          new RegExp(`^тема\\s*${lessonNumber}\\.\\d+\\.`, 'i')
        ]
        if (patterns.some(pattern => pattern.test(normalizedFileName))) {
          return true
        }
      }
      
      // Вариант 4: Файл содержит полный код темы (например, "Тема 1.1")
      if (normalizedFileName.includes(normalizedTopicCode.replace(/тема\s*/i, 'тема '))) {
        return true
      }
      
      // Вариант 5: Файл начинается с кода темы и содержит название темы
      // Например: "Тема 1.2 Вычислители" содержит "Тема 1.2" и часть названия
      if (codeMatch && topicTitle) {
        const fullCode = codeMatch[1]
        const startsWithCode = normalizedFileName.startsWith(`тема ${fullCode}`) || 
                               normalizedFileName.startsWith(`тема${fullCode}`)
        const containsTitle = normalizedFileName.includes(topicTitle.toLowerCase().substring(0, 10))
        if (startsWithCode && containsTitle) {
          return true
        }
      }
      
      // Вариант 6: Файл содержит название темы и ключевые слова "основной", "главный"
      const mainKeywords = ['основной', 'главный', 'main', 'primary']
      const hasMainKeyword = mainKeywords.some(keyword => normalizedFileName.includes(keyword))
      if (topicTitle && normalizedFileName.includes(topicTitle.toLowerCase()) && hasMainKeyword) {
        return true
      }
      
      return false
    }

    // Загрузка материалов темы из JSON конфигурации
    const loadTopicMaterials = async (lessonIndex, lesson, topicIndex, topic) => {
      const key = `${lessonIndex}-${topicIndex}`
      
      try {
        // 1) Prefer DB-backed topic files (course_program_topic_files)
        const dbFiles = Array.isArray(topic?.files) ? topic.files : []
        if (dbFiles.length > 0) {
          const mainPdfs = []
          const additionals = []

          for (const f of dbFiles) {
            try {
              const contentType =
                f.fileType === 'pdf'
                  ? 'application/pdf'
                  : f.fileType === 'video'
                    ? 'video/mp4'
                    : f.mimeType || 'application/octet-stream'

              const fileUrl = await minioService.getPresignedDownloadUrl(
                f.objectKey,
                7 * 24 * 60 * 60,
                contentType
              )

              const fileObject = {
                id: f.id,
                objectName: f.objectKey,
                fileName: f.originalName,
                original_name: f.originalName,
                originalName: f.originalName,
                file_size: f.fileSize,
                sizeFormatted: f.fileSize ? minioService.formatFileSize?.(f.fileSize) : undefined,
                url: fileUrl,
                file_url: fileUrl,
                type: contentType,
                is_main_file: !!(f.isMain && f.fileType === 'pdf'),
              }

              if (fileObject.is_main_file) {
                mainPdfs.push(fileObject)
              } else {
                additionals.push(fileObject)
              }
            } catch (e) {
              console.error('[StationCourses] Failed to presign topic file:', f, e)
            }
          }

          topicMaterials.value[key] = {
            mainPdf: mainPdfs.length === 1 ? mainPdfs[0] : null,
            mainPdfs,
            additionals,
          }
          return
        }

        // Prefer stable key lookup (topic.topicKey from DB + topicKey in courseMaterials.json)
        let topicData = null
        const stableKey = topic?.topicKey || topic?.topic_key
        if (stableKey && materialsByTopicKey.value.has(stableKey)) {
          topicData = materialsByTopicKey.value.get(stableKey)
        } else {
          // Fallback: legacy lookup by lesson title + topic code/title
          const lessonData = courseMaterials.lessons.find(l => 
            l.lessonTitle === lesson.title || 
            l.lessonTitle.replace(':', '.') === lesson.title.replace(':', '.')
          )
          
          if (!lessonData) {
            console.warn(`Не найдены материалы для урока: ${lesson.title}`)
            topicMaterials.value[key] = {
              mainPdf: null,
              additionals: []
            }
            return
          }

          // Ищем материалы для темы
          topicData = lessonData.topics.find(t => {
            // Сравнение кода темы (гибкое, игнорирует точки в конце)
            const topicCodeNormalized = (t.topicCode || '').replace(/\.$/, '').trim()
            const topicCodeFromData = (topic.code || '').replace(/\.$/, '').trim()
            const topicCodeMatch = topicCodeNormalized === topicCodeFromData
            
            // Сравнение названия темы (гибкое, учитывает CBM/СВМ)
            const titleNormalized = (t.topicTitle || '').toLowerCase().trim()
            const titleFromData = (topic.title || '').toLowerCase().trim()
            
            // Нормализуем CBM/СВМ для сравнения
            const titleNormalizedFixed = titleNormalized.replace(/свм/g, 'cbm').replace(/cbm/g, 'cbm')
            const titleFromDataFixed = titleFromData.replace(/свм/g, 'cbm').replace(/cbm/g, 'cbm')
            
            const topicTitleMatch = titleNormalizedFixed === titleFromDataFixed || 
                                    titleNormalized === titleFromData ||
                                    (titleNormalized.includes('система') && titleFromData.includes('система') && 
                                     titleNormalized.includes('cbm') && titleFromData.includes('cbm'))
            
            console.log(`Поиск темы: код "${topic.code}" vs "${t.topicCode}" = ${topicCodeMatch}, название "${topic.title}" vs "${t.topicTitle}" = ${topicTitleMatch}`)
            
            return topicCodeMatch && topicTitleMatch
          })
        }

        if (!topicData || !topicData.files || topicData.files.length === 0) {
          console.warn(`Не найдены материалы для темы: ${topic.code} - ${topic.title}`)
          topicMaterials.value[key] = {
            mainPdf: null,
            additionals: []
          }
          return
        }

        console.log(`Найдено ${topicData.files.length} файлов для темы ${topic.code}`)

        const mainPdfs = [] // Массив для нескольких основных файлов
        const additionals = []

        // Обрабатываем каждый файл из JSON
        for (const fileConfig of topicData.files) {
          try {
            // Генерируем presigned URL для файла
            const fileUrl = await minioService.getPresignedDownloadUrl(
              fileConfig.objectName,
              7 * 24 * 60 * 60, // 7 дней
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
              mainPdfs.push(fileObject)
              console.log(`Найден основной PDF: ${fileConfig.fileName}`)
            } else {
              additionals.push(fileObject)
              console.log(`Добавлен дополнительный материал: ${fileConfig.fileName} (${fileConfig.fileType})`)
            }
          } catch (urlError) {
            console.error(`Ошибка генерации URL для файла ${fileConfig.fileName}:`, urlError)
            console.error(`Путь к файлу: ${fileConfig.objectName}`)
            // Продолжаем обработку других файлов даже при ошибке
            // Но добавляем файл с пустым URL, чтобы пользователь видел, что файл должен быть
            const fileObjectWithError = {
              objectName: fileConfig.objectName,
              fileName: fileConfig.fileName,
              original_name: fileConfig.fileName,
              originalName: fileConfig.fileName,
              file_size: fileConfig.fileSize,
              sizeFormatted: fileConfig.sizeFormatted || 'Неизвестен',
              url: null,
              file_url: null,
              type: fileConfig.fileType === 'pdf' ? 'application/pdf' : 
                    fileConfig.fileType === 'video' ? 'video/mp4' : 'application/octet-stream',
              error: true,
              errorMessage: urlError.message
            }
            if (fileConfig.is_main_file) {
              mainPdfs.push(fileObjectWithError)
            } else {
              additionals.push(fileObjectWithError)
            }
          }
        }

        console.log(`Результат для темы ${topic.code}:`, {
          mainPdfsCount: mainPdfs.length,
          mainPdfs: mainPdfs.map(f => f.original_name),
          additionalsCount: additionals.length
        })

        // Для обратной совместимости: если один основной файл, сохраняем в mainPdf
        // Если несколько - используем mainPdfs массив
        topicMaterials.value[key] = {
          mainPdf: mainPdfs.length === 1 ? mainPdfs[0] : null, // Один файл для обратной совместимости
          mainPdfs: mainPdfs, // Массив всех основных файлов
          additionals
        }
      } catch (error) {
        console.error(`Ошибка загрузки материалов для темы ${topic.code}:`, error)
        console.error('Детали ошибки:', {
          lessonTitle: lesson.title,
          topicCode: topic.code,
          topicTitle: topic.title,
          errorMessage: error.message,
          errorStack: error.stack
        })
        // При ошибке оставляем пустые значения
        topicMaterials.value[key] = {
          mainPdf: null,
          mainPdfs: [],
          additionals: []
        }
      }
    }

    // Загрузка всех материалов из MinIO (только для авторизованных)
    const loadAllMaterials = async () => {
      // Проверяем авторизацию перед загрузкой материалов
      const authResult = await authService.checkAuth()
      if (!authResult.isAuthenticated) {
        // Для неавторизованных не загружаем материалы
        loadingLessons.value = false
        return
      }
      
      loadingLessons.value = true
      try {
        const lessons = courseProgram.value?.lessons || []
        const promises = []

        lessons.forEach((lesson, lessonIndex) => {
          (lesson.topics || []).forEach((topic, topicIndex) => {
            promises.push(loadTopicMaterials(lessonIndex, lesson, topicIndex, topic))
          })
        })

        await Promise.all(promises)
      } catch (error) {
        console.error('Ошибка загрузки материалов из MinIO:', error)
        ElMessage.error('Не удалось загрузить материалы курса')
      } finally {
        loadingLessons.value = false
      }
    }

    // Структура контента с материалами из MinIO
    const curriculum = computed(() => {
      const lessons = courseProgram.value?.lessons || []
      return lessons.map((lesson, lessonIndex) => ({
        ...lesson,
        topics: (lesson.topics || []).map((topic, topicIndex) => {
          const key = `${lessonIndex}-${topicIndex}`
          const materials = topicMaterials.value[key] || { mainPdf: null, mainPdfs: [], additionals: [] }
          return {
            ...topic,
            mainPdf: materials.mainPdf, // Для обратной совместимости
            mainPdfs: materials.mainPdfs || (materials.mainPdf ? [materials.mainPdf] : []), // Массив основных файлов
            additionals: materials.additionals
          }
        })
      }))
    })
    
    // Статистика курса
    const courseStats = computed(() => {
      let totalVideos = 0
      let totalMaterials = 0
      const lessonsArr = curriculum.value || []
      lessonsArr.forEach(lesson => {
        (lesson.topics || []).forEach(topic => {
          // Учитываем все основные файлы (может быть несколько)
          const mainFiles = topic.mainPdfs || (topic.mainPdf ? [topic.mainPdf] : [])
          totalMaterials += mainFiles.length
          const adds = topic.additionals || []
          totalMaterials += adds.length
          totalVideos += adds.filter(f => isVideoFile(f)).length
        })
      })
      return {
        lessons: lessonsArr.length || courseProgram.value?.lessonsCount || 0,
        videos: totalVideos,
        materials: totalMaterials,
        duration: courseProgram.value?.duration || '4 недели'
      }
    })

    // Больше не загружаем из БД/MinIO

    // Удалены функции выборки файлов из MinIO

    // Проверка, является ли файл видео
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

    // Проверка наличия видео в теме (по additionals)
    const hasVideoFiles = (topic) => {
      return (topic.additionals || []).some(file => isVideoFile(file))
    }

    // Получить все видео из списка файлов
    const getVideoFiles = (files) => {
      if (!files) return []
      return files.filter(file => isVideoFile(file))
    }

    // Обработка клика на файл
    const handleFileClick = (file, allFiles, fileIndex) => {
      if (!isAuthenticated.value) {
        ElMessage.warning('Для просмотра файлов необходимо войти в систему')
        return
      }
      if (isVideoFile(file)) {
        const videos = getVideoFiles(allFiles)
        playVideos(videos, videos.findIndex(v => (v.objectName || v.id) === (file.objectName || file.id)))
      } else {
        // Для всех остальных файлов (включая PDF) - скачиваем
        downloadFile(file)
      }
    }

    // Воспроизвести все видео из темы
    const playTopicVideos = (topic) => {
      if (!isAuthenticated.value) {
        ElMessage.warning('Для просмотра видео необходимо войти в систему')
        return
      }
      const videos = getVideoFiles(topic.additionals)
      if (videos.length > 0) {
        playVideos(videos, 0)
      }
    }

    // Воспроизвести видео
    const playVideos = (videos, startIndex = 0) => {
      if (!isAuthenticated.value) {
        ElMessage.warning('Для просмотра видео необходимо войти в систему')
        return
      }
      if (!videos || videos.length === 0) {
        ElMessage.warning('Видео не найдено')
        return
      }

      allVideos.value = videos.map((video, index) => ({
        id: video.objectName,
        title: video.original_name || video.originalName,
        url: video.file_url || video.url
      }))

      currentVideoIndex.value = startIndex
      currentVideo.value = videos[startIndex]
      showVideoPlayer.value = true
    }

    // Воспроизвести следующее видео
    const playNextVideo = () => {
      if (currentVideoIndex.value < allVideos.value.length - 1) {
        currentVideoIndex.value++
        const nextVideo = allVideos.value[currentVideoIndex.value]
        const allFiles = [...getAllFilesFromLessons()]
        const video = allFiles.find(f => 
          (f.file_url || f.url) === nextVideo.url || 
          f.objectName === nextVideo.id
        )
        if (video) {
          currentVideo.value = video
        }
      }
    }

    // Воспроизвести предыдущее видео
    const playPreviousVideo = () => {
      if (currentVideoIndex.value > 0) {
        currentVideoIndex.value--
        const prevVideo = allVideos.value[currentVideoIndex.value]
        const allFiles = [...getAllFilesFromLessons()]
        const video = allFiles.find(f => 
          (f.file_url || f.url) === prevVideo.url || 
          f.objectName === prevVideo.id
        )
        if (video) {
          currentVideo.value = video
        }
      }
    }

    // Получить все файлы из всех уроков
    const getAllFilesFromLessons = () => {
      const allFiles = []
      curriculum.value.forEach(lesson => {
        (lesson.topics || []).forEach(topic => {
          if (topic.mainPdf) allFiles.push(topic.mainPdf)
          if (topic.additionals) allFiles.push(...topic.additionals)
        })
      })
      return allFiles
    }

    // Обработчики видеоплеера
    const handleVideoEnd = () => {
      // Автоматически переходим к следующему видео
      if (currentVideoIndex.value < allVideos.value.length - 1) {
        playNextVideo()
      } else {
        ElMessage.success('Все видео просмотрены')
      }
    }

    const handleVideoClose = () => {
      showVideoPlayer.value = false
      currentVideo.value = null
      allVideos.value = []
      currentVideoIndex.value = 0
    }

    // Скачать материал (теперь не используется для PDF, только для других файлов)
    const downloadMaterial = (file) => {
      if (file.file_url || file.url) {
        const link = document.createElement('a')
        link.href = file.file_url || file.url
        link.download = file.original_name || file.originalName
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }

    const toggleLesson = (index) => {
      const idx = expandedLessons.value.indexOf(index)
      if (idx > -1) {
        expandedLessons.value.splice(idx, 1)
      } else {
        expandedLessons.value.push(index)
      }
    }

    // Обработчики для тестов из компоненты CourseCurriculum
    const handleStartTest = (test) => {
      ElMessage.info(`Запуск теста: ${test.title}`)
      // TODO: Реализовать логику запуска теста
    }

    const handleStartFinalTest = (finalTest) => {
      ElMessage.info(`Запуск итогового теста: ${finalTest?.title || 'Итоговый тест'}`)
      // TODO: Реализовать логику запуска итогового теста
    }

    // Обработчик для воспроизведения видео из компоненты CourseMaterials
    const handlePlayVideos = ({ videos, startIndex }) => {
      playVideos(videos, startIndex)
    }

    // Начать обучение
    const startLearning = () => {
      if (!isAuthenticated.value) {
        notify.warning({
          title: 'Доступ ограничен',
          message: 'Для доступа к урокам необходимо войти в систему',
          duration: 6000,
          actions: [
            {
              label: 'Войти',
              onClick: () => router.push('/login')
            },
            {
              label: 'Отмена',
              variant: 'outline'
            }
          ]
        })
        return
      }
      // Переходим к первому уроку и первой теме
      router.push({
        name: 'lesson-viewer',
        params: {
          id: stationId.value,
          lessonIndex: 0,
          topicIndex: 0
        }
      })
    }

    const loadStationAndProgram = async () => {
      try {
        const stationResp = await stationService.getStation(stationId.value)
        station.value = stationResp?.station || null
      } catch (e) {
        console.error('[StationCourses] Failed to load station:', e)
        station.value = null
      }

      try {
        courseProgramData.value = await stationService.getStationCourseProgram(stationId.value)
      } catch (e) {
        console.error('[StationCourses] Failed to load course program:', e)
        courseProgramData.value = null
      }
    }

    onMounted(async () => {
      await loadStationAndProgram()
      await loadStationImage()
      // Проверяем авторизацию при монтировании
      await authService.checkAuth()
      loadAllMaterials()
      // Загружаем видео для бокового меню
      loadSidebarVideo()
    })

    return {
      stationId,
      station,
      stationImageSrc,
      courseProgram,
      courseStats,
      expandedLessons,
      activeTab,
      loadingLessons,
      curriculum,
      toggleLesson,
      downloadMaterial,
      isAuthenticated,
      // Video Player
      showVideoPlayer,
      currentVideo,
      currentVideoIndex,
      allVideos,
      isVideoFile,
      hasVideoFiles,
      handleFileClick,
      playTopicVideos,
      playVideos,
      playNextVideo,
      playPreviousVideo,
      handleVideoEnd,
      handleVideoClose,
      // Test handlers
      handleStartTest,
      handleStartFinalTest,
      // Materials handlers
      handlePlayVideos,
      // Start learning
      startLearning,
      // Sidebar video
      sidebarVideoUrl,
      loadingSidebarVideo,
      sidebarVideoPlayer,
      handleVideoError
    }
  }
}
</script>

<style scoped>
/* Expand Animation */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 3000px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

/* Защита от печати PDF */
@media print {
  body * {
    visibility: hidden;
  }
}
</style>

<style>
/* Глобальные стили для защиты PDF от скачивания и копирования */
.pdf-viewer-container {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: transparent;
  scroll-behavior: smooth;
}


.pdf-viewer-container img,
.pdf-viewer-container canvas {
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  display: block;
  width: 100%;
  height: auto;
  /* Явно запрещаем любые трансформации (перевороты) */
  transform: none !important;
  -webkit-transform: none !important;
  -moz-transform: none !important;
  -ms-transform: none !important;
  -o-transform: none !important;
  /* Убеждаемся, что ориентация изображения берется из самого изображения */
  image-orientation: from-image;
  -webkit-image-orientation: from-image;
}

/* Блокировка печати через Ctrl+P */
@media print {
  body {
    display: none !important;
  }
}

/* Enrollment Card Styles */
.enrollment-card {
  border: 2px solid #3b82f6;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
}

.enrollment-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 128px;
  height: 128px;
  background: #3b82f6;
  opacity: 0.1;
  border-radius: 50%;
  transform: translate(50%, -50%);
}

.enrollment-card-content {
  position: relative;
  z-index: 1;
}

.start-learning-btn {
  width: 100%;
  margin-bottom: 24px;
  font-weight: 700;
  font-size: 16px;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.start-learning-btn:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.enrollment-info {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.enrollment-info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.enrollment-info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

.enrollment-info-value {
  font-weight: 700;
  color: #111827;
  font-size: 14px;
}

:deep(.el-divider) {
  margin: 12px 0;
}
</style>

