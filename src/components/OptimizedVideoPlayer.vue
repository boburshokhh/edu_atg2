<template>
  <div 
    :class="[
      'video-player-wrapper flex items-center justify-center',
      isFullscreen ? 'h-screen bg-black' : ''
    ]"
    :style="isFullscreen ? {} : { 
      transform: `scale(${zoom / 100})`,
      transformOrigin: 'center center'
    }"
  >
    <vue-plyr
      ref="videoPlayerRef"
      :class="isFullscreen ? 'w-full h-full' : 'w-full max-w-full'"
      :key="videoKey"
      :options="plyrOptions"
      @ready="onPlayerReady"
    >
      <video
        :src="videoSource"
        preload="metadata"
        playsinline
        crossorigin="anonymous"
      >
        Ваш браузер не поддерживает воспроизведение видео.
      </video>
    </vue-plyr>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useVideo } from '@/composables/useVideo'

const props = defineProps({
  source: {
    type: Object,
    required: true
  },
  zoom: {
    type: Number,
    default: 100
  },
  isFullscreen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['fullscreen-change'])

const videoPlayerRef = ref(null)
const videoKey = ref(0)

const {
  initPlayer,
  isFullscreen: videoFullscreen,
  cleanup
} = useVideo()

// Plyr конфигурация для оптимизации
const plyrOptions = {
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
  settings: ['quality', 'speed'],
  speed: { selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] },
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
  // Оптимизация для производительности
  storage: { enabled: true, key: 'plyr' },
  invertTime: false,
  toggleInvert: true,
  clickToPlay: true,
  keyboard: { focused: true, global: false }
}

const videoSource = computed(() => {
  return props.source?.url || props.source?.file_url || ''
})

const onPlayerReady = () => {
  if (videoPlayerRef.value) {
    initPlayer(videoPlayerRef.value)
    
    // Подписываемся на события fullscreen
    const player = videoPlayerRef.value.player
    
    if (player) {
      player.on('enterfullscreen', () => {
        emit('fullscreen-change', true)
      })
      
      player.on('exitfullscreen', () => {
        emit('fullscreen-change', false)
      })
    }
  }
}

// Следим за изменением источника
watch(() => props.source, (newSource, oldSource) => {
  if (newSource && newSource !== oldSource) {
    // Форсируем перерендер компонента при смене источника
    videoKey.value++
  }
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.video-player-wrapper {
  transition: transform 0.2s ease-out;
  will-change: transform;
  overflow: hidden;
}

:deep(.plyr) {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100vh;
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

/* Оптимизация для production */
:deep(.plyr__poster) {
  background-size: cover;
  background-position: center;
}

:deep(.plyr__progress__buffer) {
  will-change: width;
}
</style>

