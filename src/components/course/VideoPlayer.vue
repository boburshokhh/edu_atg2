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
        ref="playerContainer"
        class="video-wrapper relative bg-black rounded-lg overflow-hidden" 
        @contextmenu.prevent
        @dragstart.prevent
        @selectstart.prevent
      >
        <!-- Plyr Video Player -->
        <video
          ref="videoElement"
          :key="videoKey"
          class="w-full h-full"
          preload="metadata"
          :playsinline="true"
          crossorigin="anonymous"
          @contextmenu.prevent
          @dragstart.prevent
        />

        <!-- Loading Overlay -->
        <div
          v-if="loading"
          class="absolute inset-0 bg-black/50 flex items-center justify-center z-10 pointer-events-none"
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
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'

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
    const playerContainer = ref(null)
    const player = ref(null)
    const videoKey = ref(0)
    const visible = ref(props.modelValue)
    const loading = ref(true)
    const loadingText = ref('Загрузка видео...')
    const currentTime = ref(0)
    const duration = ref(0)

    // Конфигурация Plyr
    const plyrConfig = {
      controls: [
        'play-large',
        'play',
        'progress',
        'current-time',
        'duration',
        'mute',
        'volume',
        'settings',
        'fullscreen'
      ],
      settings: ['speed', 'quality'],
      speed: {
        selected: 1,
        options: [0.5, 0.75, 1, 1.25, 1.5, 2]
      },
      quality: {
        default: 720,
        options: [1080, 720, 480, 360]
      },
      ratio: '16:9',
      autopause: true,
      resetOnEnd: false,
      hideControls: true,
      loadSprite: true,
      iconUrl: null,
      blankVideo: null,
      storage: {
        enabled: true,
        key: 'plyr'
      },
      invertTime: false,
      toggleInvert: true,
      clickToPlay: true,
      keyboard: {
        focused: true,
        global: false
      },
      tooltips: {
        controls: true,
        seek: true
      }
    }

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

    // Инициализация Plyr плеера
    const initPlayer = async () => {
      if (!videoElement.value || !playerContainer.value) {
        return
      }

      // Уничтожаем старый плеер, если есть
      if (player.value) {
        try {
          player.value.destroy()
        } catch (e) {
          console.warn('Error destroying old player:', e)
        }
        player.value = null
      }

      try {
        loading.value = true
        loadingText.value = 'Инициализация плеера...'

        // Ждем, пока элемент будет готов
        await nextTick()

        // Создаем Plyr плеер
        player.value = new Plyr(videoElement.value, plyrConfig)

        // Подписываемся на события Plyr
        setupPlayerEvents()

        loading.value = false
      } catch (error) {
        console.error('Error initializing player:', error)
        loading.value = false
        loadingText.value = 'Ошибка инициализации видеоплеера'
      }
    }

    // Настройка событий Plyr
    const setupPlayerEvents = () => {
      if (!player.value) return

      player.value.on('ready', () => {
        loading.value = false
        loadingText.value = ''
      })

      player.value.on('loadstart', () => {
        loading.value = true
        loadingText.value = 'Подключение к серверу...'
      })

      player.value.on('loadedmetadata', () => {
        if (player.value) {
          duration.value = player.value.duration || 0
        }
        loading.value = false
        loadingText.value = ''
      })

      player.value.on('canplay', () => {
        loading.value = false
        loadingText.value = ''
      })

      player.value.on('canplaythrough', () => {
        loading.value = false
        loadingText.value = ''
      })

      player.value.on('waiting', () => {
        loading.value = true
        loadingText.value = 'Буферизация...'
      })

      player.value.on('playing', () => {
        loading.value = false
        loadingText.value = ''
      })

      player.value.on('ended', () => {
        emit('video-end', props.videoId)
      })

      player.value.on('timeupdate', () => {
        if (player.value) {
          currentTime.value = player.value.currentTime || 0
        }
      })

      player.value.on('progress', () => {
        // Видео загружает данные
        if (player.value && videoElement.value) {
          const buffered = videoElement.value.buffered
          if (buffered.length > 0 && duration.value > 0) {
            const bufferedEnd = buffered.end(buffered.length - 1)
            const bufferedPercent = (bufferedEnd / duration.value) * 100
            // Можно использовать для показа прогресса загрузки
          }
        }
      })

      player.value.on('error', (event) => {
        console.error('Video error:', event)
        loading.value = false
        loadingText.value = 'Ошибка воспроизведения видео'
      })
    }

    // Загрузка видео с поддержкой streaming
    const loadVideo = async (url) => {
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
            videoKey.value++
            await nextTick()
            await initPlayer()
          } else {
            // Для браузеров без нативной поддержки HLS показываем ошибку
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

          // Устанавливаем источник
          video.src = url
          
          // Обновляем ключ для пересоздания элемента
          videoKey.value++
          await nextTick()
          await initPlayer()
        }
      } catch (error) {
        console.error('Error loading video:', error)
        loading.value = false
        loadingText.value = 'Ошибка загрузки видео'
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
      // Уничтожаем Plyr плеер
      if (player.value) {
        try {
          player.value.destroy()
          player.value = null
        } catch (e) {
          console.warn('Error destroying player:', e)
        }
      }

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
      // Уничтожаем Plyr плеер
      if (player.value) {
        try {
          player.value.destroy()
          player.value = null
        } catch (e) {
          console.warn('Error destroying player:', e)
        }
      }

      if (videoElement.value) {
        videoElement.value.pause()
        videoElement.value.src = ''
      }
    })

    return {
      videoElement,
      playerContainer,
      videoKey,
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
  -webkit-touch-callout: none;
  -khtml-user-select: none;
  pointer-events: auto;
}

/* Plyr стилизация */
:deep(.plyr) {
  width: 100%;
  height: 100%;
}

:deep(.plyr__video-wrapper) {
  width: 100%;
  height: 100%;
}

:deep(.plyr__video) {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

:deep(.plyr__controls) {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
}

:deep(.plyr__control--overlaid) {
  background: rgba(59, 130, 246, 0.9);
  border-radius: 50%;
}

:deep(.plyr__control--overlaid:hover) {
  background: rgba(37, 99, 235, 1);
}

:deep(.plyr--full-ui input[type=range]) {
  color: #3B82F6;
}

:deep(.plyr__control.plyr__tab-focus) {
  box-shadow: 0 0 0 5px rgba(59, 130, 246, 0.5);
}

:deep(.plyr__menu__container .plyr__control[role=menuitemradio][aria-checked=true]::before) {
  background: #3B82F6;
}
</style>
