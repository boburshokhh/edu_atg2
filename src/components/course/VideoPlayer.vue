<template>
  <div class="video-player-container">
    <!-- Модальное окно -->
    <el-dialog
      v-model="visible"
      :title="videoTitle"
      width="90%"
      class="video-dialog"
      :before-close="handleClose"
      @close="handleClose"
    >
      <div
        class="video-wrapper relative bg-black rounded-lg overflow-hidden" 
        @contextmenu.prevent
        @dragstart.prevent
        @selectstart.prevent
      >
        <!-- Native HTML5 Video Player -->
        <video
          ref="videoElement"
          class="w-full h-full"
          :controls="true"
          preload="metadata"
          :playsinline="true"
          crossorigin="anonymous"
          @loadedmetadata="handleLoadedMetadata"
          @loadstart="handleLoadStart"
          @canplay="handleCanPlay"
          @canplaythrough="handleCanPlayThrough"
          @waiting="handleWaiting"
          @playing="handlePlaying"
          @ended="handleEnded"
          @error="handleError"
          @timeupdate="handleTimeUpdate"
          @progress="handleProgress"
          @contextmenu.prevent
          @dragstart.prevent
        />

        <!-- Loading Overlay -->
        <div
          v-if="loading"
          class="absolute inset-0 bg-black/50 flex items-center justify-center z-50 pointer-events-none"
        >
          <div class="text-white text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4" />
            <p>{{ loadingText }}</p>
          </div>
        </div>
      </div>

      <!-- Video Info -->
      <div class="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 class="text-lg font-semibold mb-2">
          {{ videoTitle }}
        </h3>
        <p class="text-gray-600">
          {{ videoDescription }}
        </p>
        
        <!-- Progress Info -->
        <div class="mt-4">
          <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Прогресс воспроизведения</span>
            <span>{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-between w-full">
          <el-button
            :disabled="currentIndex === 0"
            @click="emit('previous')"
          >
            <el-icon class="mr-2">
              <ArrowLeft />
            </el-icon>
            Предыдущий урок
          </el-button>
          <el-button
            type="primary"
            :disabled="currentIndex >= lessons.length - 1"
            @click="emit('next')"
          >
            Следующий урок
            <el-icon class="ml-2">
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

export default {
  name: 'VideoPlayer',
  components: {
    ArrowLeft,
    ArrowRight
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    videoUrl: {
      type: String,
      required: true
    },
    videoTitle: {
      type: String,
      default: 'Видеоурок'
    },
    videoDescription: {
      type: String,
      default: ''
    },
    videoId: {
      type: [String, Number],
      default: null
    },
    lessons: {
      type: Array,
      default: () => []
    },
    currentIndex: {
      type: Number,
      default: 0
    }
  },
  emits: ['update:modelValue', 'close', 'video-end', 'next', 'previous'],
  setup(props, { emit }) {
    const videoElement = ref(null)
    const visible = ref(props.modelValue)
    const loading = ref(true)
    const loadingText = ref('Загрузка видео...')
    const currentTime = ref(0)
    const duration = ref(0)

    // Видимость модального окна
    watch(() => props.modelValue, (val) => {
      visible.value = val
      if (val && videoElement.value && props.videoUrl) {
        loadVideo(props.videoUrl)
      }
    })

    watch(visible, (val) => {
      emit('update:modelValue', val)
      if (!val && videoElement.value) {
        handleClose()
      }
    })

    // Отслеживание изменений URL видео
    watch(() => props.videoUrl, (newUrl, oldUrl) => {
      if (newUrl && newUrl !== oldUrl && videoElement.value && visible.value) {
        loadVideo(newUrl)
      }
    })

    // Загрузка видео с поддержкой streaming
    const loadVideo = (url) => {
      if (!videoElement.value || !url) return

      try {
        loading.value = true
        loadingText.value = 'Подключение к видео...'

        const video = videoElement.value

        // Если это HLS (.m3u8) - используем нативную поддержку браузера
        if (url.includes('.m3u8') || url.includes('application/x-mpegURL')) {
          const isNativeHlsSupported = video.canPlayType('application/vnd.apple.mpegurl')
          
          if (isNativeHlsSupported) {
            // Используем нативную поддержку HLS (Safari, Chrome на Android)
            video.src = url
            loading.value = false
            loadingText.value = ''
          } else {
            // Для браузеров без нативной поддержки HLS показываем ошибку
            // В будущем можно использовать vue-plyr, который поддерживает HLS
            loading.value = false
            loadingText.value = 'HLS не поддерживается в вашем браузере. Используйте Safari или Chrome на Android.'
            console.warn('HLS not supported in this browser')
          }
        } else {
          // Обычное MP4/WebM видео с HTTP Range requests (стриминг по частям)
          // HTML5 video автоматически использует Range requests для стриминга
          // Это позволяет воспроизводить видео без полной загрузки
          
          // Определяем тип контента по расширению
          if (url.includes('.webm')) {
            video.type = 'video/webm'
          } else if (url.includes('.ogg')) {
            video.type = 'video/ogg'
          } else if (url.includes('.mov')) {
            video.type = 'video/quicktime'
          } else {
            video.type = 'video/mp4'
          }

          // Используем preload="metadata" для оптимизации
          // Видео будет загружаться только по мере необходимости
          video.preload = 'metadata'
          
          // Устанавливаем источник
          video.src = url
          
          // Важно: не вызываем load() явно - браузер сам начнет загрузку metadata
          // Это позволяет начать воспроизведение сразу после загрузки metadata,
          // а остальное будет загружаться по мере необходимости (Range requests)
          
          loading.value = false
          loadingText.value = ''
        }
      } catch (error) {
        console.error('Error loading video:', error)
        loading.value = false
        loadingText.value = 'Ошибка загрузки видео'
      }
    }

    // Обработчики событий видео
    const handleLoadedMetadata = () => {
      if (videoElement.value) {
        duration.value = videoElement.value.duration || 0
      loading.value = false
        loadingText.value = ''
      }
    }

    const handleLoadStart = () => {
      loadingText.value = 'Подключение к серверу...'
    }

    const handleCanPlay = () => {
      // Видео готово к воспроизведению (достаточно данных для начала)
      loading.value = false
      loadingText.value = ''
    }

    const handleCanPlayThrough = () => {
      // Весь контент загружен или загрузится без остановок
      loading.value = false
      loadingText.value = ''
    }

    const handleProgress = () => {
      // Видео загружает данные (Range requests работают)
      // Можно показать прогресс загрузки буфера
      if (videoElement.value) {
        const buffered = videoElement.value.buffered
        if (buffered.length > 0 && duration.value > 0) {
          const bufferedEnd = buffered.end(buffered.length - 1)
          const bufferedPercent = (bufferedEnd / duration.value) * 100
          // Можно использовать для показа прогресса загрузки
        }
      }
    }

    const handleWaiting = () => {
      loading.value = true
      loadingText.value = 'Буферизация...'
    }

    const handlePlaying = () => {
      loading.value = false
      loadingText.value = ''
    }

    const handleEnded = () => {
      emit('video-end', props.videoId)
    }

    const handleError = (event) => {
      console.error('Video error:', event)
      loading.value = false
      loadingText.value = 'Ошибка воспроизведения видео'
    }

    const handleTimeUpdate = () => {
      if (videoElement.value) {
        currentTime.value = videoElement.value.currentTime || 0
      }
    }

    // Форматирование времени
    const formatTime = (seconds) => {
      if (!seconds || isNaN(seconds)) return '00:00'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      }
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }

    // Закрытие плеера
    const handleClose = () => {
      if (videoElement.value) {
        try {
          videoElement.value.pause()
          videoElement.value.src = ''
          videoElement.value.load()
        } catch (e) {
          console.warn('Error stopping video:', e)
        }
      }

      loading.value = true
      loadingText.value = 'Загрузка видео...'
      currentTime.value = 0
      duration.value = 0

      emit('close')
      emit('update:modelValue', false)
    }

    onMounted(() => {
      if (visible.value && props.videoUrl && videoElement.value) {
        loadVideo(props.videoUrl)
      }
    })

    onBeforeUnmount(() => {
      if (videoElement.value) {
        videoElement.value.pause()
        videoElement.value.src = ''
      }
    })

    return {
      videoElement,
      visible,
      loading,
      loadingText,
      currentTime,
      duration,
      handleClose,
      formatTime
    }
  }
}
</script>

<style scoped>
.video-player-container {
  position: relative;
  user-select: none;
}

.video-wrapper {
  position: relative;
  aspect-ratio: 16/9;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  user-select: none;
}

.video-wrapper video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  pointer-events: auto;
}

.video-wrapper video::-webkit-media-controls-panel {
  background-color: rgba(0, 0, 0, 0.8);
}

/* Защита от скачивания */
.video-wrapper video {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
</style>
