<template>
  <div 
    :class="[
      'educational-video-player relative w-full bg-black rounded-lg overflow-hidden shadow-2xl',
      isFullscreen ? 'fullscreen' : '',
      containerClass
    ]"
  >
    <div 
      ref="playerContainer"
      class="plyr-container relative w-full aspect-video"
      :style="containerStyle"
    >
      <video
        ref="videoElement"
        :key="videoKey"
        :poster="poster"
        :preload="preload"
        playsinline
        crossorigin="anonymous"
        class="video-element w-full h-full object-contain"
      >
        <p>Ваш браузер не поддерживает воспроизведение видео.</p>
      </video>
    </div>

    <!-- Loading overlay -->
    <div
      v-if="isLoading"
      class="absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-10"
    >
      <div class="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin" />
      <p class="mt-4 text-white text-sm">{{ loadingText }}</p>
    </div>

    <!-- Error overlay -->
    <div
      v-if="error"
      class="absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-10"
    >
      <div class="text-center text-white p-6">
        <svg
          class="w-12 h-12 mx-auto mb-4 text-red-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p class="mb-4 text-base">{{ error }}</p>
        <button
          class="px-4 py-2 bg-primary text-white rounded hover:bg-blue-600 transition-colors text-sm font-medium"
          @click="retry"
        >
          Повторить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import { createVideoSource } from '@/services/videoStreamService'

const props = defineProps({
  // Источник видео: может быть URL (string) или объект с информацией
  source: {
    type: [String, Object],
    required: true
  },
  // Постер (превью изображение)
  poster: {
    type: String,
    default: null
  },
  // Требуется ли аутентификация
  requireAuth: {
    type: Boolean,
    default: false
  },
  // Preload стратегия
  preload: {
    type: String,
    default: 'metadata',
    validator: (value) => ['none', 'metadata', 'auto'].includes(value)
  },
  // Автовоспроизведение
  autoplay: {
    type: Boolean,
    default: false
  },
  // Начальное время (для возобновления просмотра)
  startTime: {
    type: Number,
    default: 0
  },
  // Дополнительные CSS классы для контейнера
  containerClass: {
    type: String,
    default: ''
  },
  // Стили контейнера
  containerStyle: {
    type: Object,
    default: () => ({})
  },
  // Показывать ли настройки качества (для HLS)
  showQuality: {
    type: Boolean,
    default: true
  },
  // Показывать ли настройки скорости
  showSpeed: {
    type: Boolean,
    default: true
  },
  // Опции скорости воспроизведения
  speedOptions: {
    type: Array,
    default: () => [0.5, 0.75, 1, 1.25, 1.5, 2]
  },
  // Сохранять ли прогресс в localStorage
  saveProgress: {
    type: Boolean,
    default: true
  },
  // Ключ для сохранения прогресса (если не указан, используется source)
  progressKey: {
    type: String,
    default: null
  }
})

const emit = defineEmits([
  'ready',
  'play',
  'pause',
  'ended',
  'timeupdate',
  'progress',
  'error',
  'fullscreen-change',
  'quality-change',
  'speed-change'
])

const videoElement = ref(null)
const playerContainer = ref(null)
const videoKey = ref(0)
const player = ref(null)
const isLoading = ref(false)
const loadingText = ref('Загрузка видео...')
const error = ref(null)
const isFullscreen = ref(false)

// Вычисляемые свойства
const progressStorageKey = computed(() => {
  if (props.progressKey) {
    return `video_progress_${props.progressKey}`
  }
  const sourceKey = typeof props.source === 'string' 
    ? props.source 
    : props.source?.objectKey || props.source?.url || 'default'
  return `video_progress_${sourceKey}`
})

// Конфигурация Plyr для образовательных платформ
const plyrConfig = computed(() => {
  const controls = [
    'play-large',
    'play',
    'progress',
    'current-time',
    'duration',
    'mute',
    'volume',
    'settings',
    'fullscreen'
  ]

  const settings = []
  if (props.showSpeed) {
    settings.push('speed')
  }
  if (props.showQuality) {
    settings.push('quality')
  }

  return {
    controls,
    settings: settings.length > 0 ? settings : undefined,
    speed: {
      selected: 1,
      options: props.speedOptions
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
    iconUrl: 'https://cdn.plyr.io/3.7.8/plyr.svg',
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
    },
    previewThumbnails: {
      enabled: false
    },
    captions: {
      active: false,
      language: 'ru',
      update: false
    }
  }
})

// Инициализация плеера
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
    isLoading.value = true
    loadingText.value = 'Инициализация плеера...'
    error.value = null

    // Создаем источник видео через наш streaming service
    const videoSource = createVideoSource(props.source, props.requireAuth)
    
    if (!videoSource || !videoSource.sources || videoSource.sources.length === 0) {
      throw new Error('Не удалось создать источник видео')
    }

    // Устанавливаем источник
    if (videoElement.value) {
      const source = videoSource.sources[0]
      videoElement.value.src = source.src
      videoElement.value.type = source.type
      
      // Устанавливаем постер, если есть
      if (props.poster) {
        videoElement.value.poster = props.poster
      }
    }

    // Ждем, пока элемент будет готов
    await nextTick()

    // Создаем Plyr плеер
    player.value = new Plyr(videoElement.value, plyrConfig.value)

    // Подписываемся на события
    setupPlayerEvents()

    // Загружаем сохраненный прогресс
    if (props.saveProgress && props.startTime > 0) {
      const savedProgress = loadProgress()
      if (savedProgress > 0) {
        player.value.currentTime = savedProgress
      }
    } else if (props.startTime > 0) {
      player.value.currentTime = props.startTime
    }

    // Автовоспроизведение
    if (props.autoplay) {
      try {
        await player.value.play()
      } catch (e) {
        console.warn('Autoplay blocked:', e)
      }
    }

    isLoading.value = false
    emit('ready', player.value)
  } catch (err) {
    console.error('Error initializing player:', err)
    error.value = err.message || 'Ошибка инициализации видеоплеера'
    isLoading.value = false
    emit('error', err)
  }
}

// Настройка событий плеера
const setupPlayerEvents = () => {
  if (!player.value) return

  player.value.on('ready', () => {
    isLoading.value = false
    loadingText.value = ''
  })

  player.value.on('loadstart', () => {
    isLoading.value = true
    loadingText.value = 'Подключение к серверу...'
  })

  player.value.on('loadedmetadata', () => {
    isLoading.value = false
    loadingText.value = ''
  })

  player.value.on('canplay', () => {
    isLoading.value = false
    loadingText.value = ''
  })

  player.value.on('waiting', () => {
    isLoading.value = true
    loadingText.value = 'Буферизация...'
  })

  player.value.on('playing', () => {
    isLoading.value = false
    loadingText.value = ''
  })

  player.value.on('play', () => {
    emit('play')
  })

  player.value.on('pause', () => {
    emit('pause')
  })

  player.value.on('ended', () => {
    // Очищаем сохраненный прогресс при завершении
    if (props.saveProgress) {
      clearProgress()
    }
    emit('ended')
  })

  player.value.on('timeupdate', () => {
    const currentTime = player.value.currentTime
    emit('timeupdate', currentTime)
    
    // Сохраняем прогресс каждые 5 секунд
    if (props.saveProgress && currentTime > 0) {
      saveProgress(currentTime)
    }
  })

  player.value.on('progress', () => {
    if (player.value && videoElement.value) {
      const buffered = videoElement.value.buffered
      if (buffered.length > 0) {
        const bufferedEnd = buffered.end(buffered.length - 1)
        const duration = player.value.duration || 0
        const progress = duration > 0 ? (bufferedEnd / duration) * 100 : 0
        emit('progress', progress)
      }
    }
  })

  player.value.on('enterfullscreen', () => {
    isFullscreen.value = true
    emit('fullscreen-change', true)
  })

  player.value.on('exitfullscreen', () => {
    isFullscreen.value = false
    emit('fullscreen-change', false)
  })

  player.value.on('qualitychange', (event) => {
    emit('quality-change', event.detail.quality)
  })

  player.value.on('ratechange', (event) => {
    emit('speed-change', event.detail.rate)
  })

  player.value.on('error', (event) => {
    const errorMsg = event.detail?.plyr?.message || 'Ошибка воспроизведения видео'
    error.value = errorMsg
    isLoading.value = false
    emit('error', new Error(errorMsg))
  })
}

// Сохранение прогресса
const saveProgress = (time) => {
  try {
    localStorage.setItem(progressStorageKey.value, String(time))
  } catch (e) {
    console.warn('Failed to save progress:', e)
  }
}

// Загрузка прогресса
const loadProgress = () => {
  try {
    const saved = localStorage.getItem(progressStorageKey.value)
    return saved ? parseFloat(saved) : 0
  } catch (e) {
    console.warn('Failed to load progress:', e)
    return 0
  }
}

// Очистка прогресса
const clearProgress = () => {
  try {
    localStorage.removeItem(progressStorageKey.value)
  } catch (e) {
    // Ignore
  }
}

// Повторная попытка загрузки
const retry = () => {
  error.value = null
  videoKey.value++
  nextTick(() => {
    initPlayer()
  })
}

// Публичные методы
const play = () => {
  if (player.value) {
    player.value.play()
  }
}

const pause = () => {
  if (player.value) {
    player.value.pause()
  }
}

const stop = () => {
  if (player.value) {
    player.value.stop()
  }
}

const seek = (time) => {
  if (player.value) {
    player.value.currentTime = time
  }
}

const setVolume = (volume) => {
  if (player.value) {
    player.value.volume = Math.max(0, Math.min(1, volume))
  }
}

const toggleMute = () => {
  if (player.value) {
    player.value.muted = !player.value.muted
  }
}

const enterFullscreen = () => {
  if (player.value) {
    player.value.fullscreen.enter()
  }
}

const exitFullscreen = () => {
  if (player.value) {
    player.value.fullscreen.exit()
  }
}

// Отслеживание изменений источника
watch(() => props.source, (newSource, oldSource) => {
  if (newSource && newSource !== oldSource) {
    videoKey.value++
    nextTick(() => {
      initPlayer()
    })
  }
}, { deep: true })

// Lifecycle hooks
onMounted(() => {
  initPlayer()
})

onBeforeUnmount(() => {
  if (player.value) {
    try {
      player.value.destroy()
    } catch (e) {
      console.warn('Error destroying player:', e)
    }
    player.value = null
  }
})

// Expose public methods
defineExpose({
  player,
  play,
  pause,
  stop,
  seek,
  setVolume,
  toggleMute,
  enterFullscreen,
  exitFullscreen,
  loadProgress,
  clearProgress
})
</script>

<style scoped>
.educational-video-player.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  border-radius: 0;
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

/* Dark mode styles */
.dark :deep(.plyr__controls) {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
}
</style>
