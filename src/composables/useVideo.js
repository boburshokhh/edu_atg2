import { ref, shallowRef, onUnmounted } from 'vue'

/**
 * Composable для работы с видео плеером
 */
export function useVideo() {
  const videoPlayer = shallowRef(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const volume = ref(1)
  const isMuted = ref(false)
  const isFullscreen = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Инициализация плеера
  const initPlayer = (playerRef) => {
    videoPlayer.value = playerRef
    
    if (playerRef && playerRef.player) {
      const player = playerRef.player
      
      // Подписка на события
      player.on('play', () => {
        isPlaying.value = true
      })
      
      player.on('pause', () => {
        isPlaying.value = false
      })
      
      player.on('timeupdate', () => {
        currentTime.value = player.currentTime
      })
      
      player.on('loadedmetadata', () => {
        duration.value = player.duration
      })
      
      player.on('volumechange', () => {
        volume.value = player.volume
        isMuted.value = player.muted
      })
      
      player.on('enterfullscreen', () => {
        isFullscreen.value = true
      })
      
      player.on('exitfullscreen', () => {
        isFullscreen.value = false
      })
      
      player.on('waiting', () => {
        isLoading.value = true
      })
      
      player.on('canplay', () => {
        isLoading.value = false
      })
      
      player.on('error', (event) => {
        error.value = event.detail?.plyr?.message || 'Ошибка воспроизведения'
        isLoading.value = false
      })
    }
  }
  
  // Управление воспроизведением
  const play = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.play()
    }
  }
  
  const pause = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.pause()
    }
  }
  
  const togglePlay = () => {
    if (isPlaying.value) {
      pause()
    } else {
      play()
    }
  }
  
  const stop = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.stop()
    }
  }
  
  // Управление временем
  const seek = (time) => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.currentTime = time
    }
  }
  
  const forward = (seconds = 10) => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.forward(seconds)
    }
  }
  
  const rewind = (seconds = 10) => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.rewind(seconds)
    }
  }
  
  // Управление громкостью
  const setVolume = (vol) => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.volume = Math.max(0, Math.min(1, vol))
    }
  }
  
  const toggleMute = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.muted = !videoPlayer.value.player.muted
    }
  }
  
  // Полноэкранный режим
  const enterFullscreen = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.fullscreen.enter()
    }
  }
  
  const exitFullscreen = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.fullscreen.exit()
    }
  }
  
  const toggleFullscreen = () => {
    if (isFullscreen.value) {
      exitFullscreen()
    } else {
      enterFullscreen()
    }
  }
  
  // Смена источника
  const changeSource = (source) => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.source = {
        type: 'video',
        sources: [{
          src: source.url || source.file_url,
          type: source.type || 'video/mp4'
        }]
      }
    }
  }
  
  // Очистка
  const cleanup = () => {
    if (videoPlayer.value && videoPlayer.value.player) {
      videoPlayer.value.player.destroy()
    }
    videoPlayer.value = null
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    error.value = null
  }
  
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    videoPlayer,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    isFullscreen,
    isLoading,
    error,
    initPlayer,
    play,
    pause,
    togglePlay,
    stop,
    seek,
    forward,
    rewind,
    setVolume,
    toggleMute,
    enterFullscreen,
    exitFullscreen,
    toggleFullscreen,
    changeSource,
    cleanup
  }
}

