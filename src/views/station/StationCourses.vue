<template>
  <!-- Hero Section с фото станции -->
  <StationHero
    :station="station"
    :station-id="stationId"
    :station-image-src="stationImageSrc"
    :course-program="courseProgram"
    :course-stats="courseStats"
  />

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
                <CourseAboutTab 
                  v-show="activeTab === 'about'"
                  :course-program="courseProgram"
                />

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
            <CourseSidebar
              :sidebar-video-url="sidebarVideoUrl"
              :loading-sidebar-video="loadingSidebarVideo"
              @start-learning="startLearning"
              @video-error="handleVideoError"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Video Player -->
    <VideoPlayer
      v-model="showVideoPlayer"
      :video-url="currentVideo?.file_url || currentVideo?.url || ''"
      :video-title="currentVideo?.original_name || currentVideo?.originalName || 'Видеоурок'"
      :video-description="currentVideo?.original_name || ''"
      :video-id="currentVideo?.objectName"
      :lessons="allVideos"
      :current-index="currentVideoIndex"
      @video-end="handleVideoEnd"
      @close="handleVideoClose"
      @next="playNextVideo"
      @previous="playPreviousVideo"
    />
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import useNotify from '@/composables/useNotify'
import VideoPlayer from '@/components/course/VideoPlayer.vue'
import CourseCurriculum from '@/components/course/CourseCurriculum.vue'
import StationHero from '@/components/course/StationHero.vue'
import CourseAboutTab from '@/components/course/CourseAboutTab.vue'
import CourseSidebar from '@/components/course/CourseSidebar.vue'
import courseMaterials from '@/data/courseMaterials.json'
import minioService from '@/services/minioService'
import authService from '@/services/auth'
import stationService from '@/services/stationService'
import { ElMessage } from 'element-plus'

export default {
  name: 'StationCourses',
  components: {
    VideoPlayer,
    CourseCurriculum,
    StationHero,
    CourseAboutTab,
    CourseSidebar
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const notify = useNotify()
    const stationId = computed(() => parseInt(route.params.id))
    const station = ref(null)
    const courseProgramData = ref(null)
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

    // Получить все видео из списка файлов
    const getVideoFiles = (files) => {
      if (!files) return []
      return files.filter(file => isVideoFile(file))
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

    // Обработчики для тестов из компоненты CourseCurriculum
    const handleStartTest = (test) => {
      ElMessage.info(`Запуск теста: ${test.title}`)
      // TODO: Реализовать логику запуска теста
    }

    const handleStartFinalTest = (finalTest) => {
      ElMessage.info(`Запуск итогового теста: ${finalTest?.title || 'Итоговый тест'}`)
      // TODO: Реализовать логику запуска итогового теста
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
      activeTab,
      loadingLessons,
      isAuthenticated,
      // Video Player
      showVideoPlayer,
      currentVideo,
      currentVideoIndex,
      allVideos,
      playVideos,
      playNextVideo,
      playPreviousVideo,
      handleVideoEnd,
      handleVideoClose,
      // Test handlers
      handleStartTest,
      handleStartFinalTest,
      // Start learning
      startLearning,
      // Sidebar video
      sidebarVideoUrl,
      loadingSidebarVideo,
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

</style>

