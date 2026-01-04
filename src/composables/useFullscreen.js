import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable for managing fullscreen state
 * Provides unified fullscreen API across different browsers
 */
export function useFullscreen(containerRef) {
  const isFullscreen = ref(false)

  const enterFullscreen = async () => {
    if (!containerRef.value) return

    try {
      const element = containerRef.value
      
      if (element.requestFullscreen) {
        await element.requestFullscreen()
      } else if (element.webkitRequestFullscreen) {
        await element.webkitRequestFullscreen()
      } else if (element.mozRequestFullScreen) {
        await element.mozRequestFullScreen()
      } else if (element.msRequestFullscreen) {
        await element.msRequestFullscreen()
      }
      
      isFullscreen.value = true
      document.body.style.overflow = 'hidden'
    } catch (error) {
      console.error('[useFullscreen] Error entering fullscreen:', error)
      throw error
    }
  }

  const exitFullscreen = async () => {
    try {
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
    } catch (error) {
      console.error('[useFullscreen] Error exiting fullscreen:', error)
      throw error
    }
  }

  const toggleFullscreen = async () => {
    if (isFullscreen.value) {
      await exitFullscreen()
    } else {
      await enterFullscreen()
    }
  }

  const handleFullscreenChange = () => {
    const isCurrentlyFullscreen = !!(
      document.fullscreenElement || 
      document.webkitFullscreenElement || 
      document.mozFullScreenElement || 
      document.msFullscreenElement
    )
    
    if (!isCurrentlyFullscreen) {
      isFullscreen.value = false
      document.body.style.overflow = ''
    } else {
      isFullscreen.value = true
      document.body.style.overflow = 'hidden'
    }
  }

  onMounted(() => {
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('MSFullscreenChange', handleFullscreenChange)
  })

  onUnmounted(() => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
    document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
    
    // Cleanup on unmount
    if (isFullscreen.value) {
      document.body.style.overflow = ''
      exitFullscreen().catch(() => {
        // Ignore errors during cleanup
      })
    }
  })

  return {
    isFullscreen,
    enterFullscreen,
    exitFullscreen,
    toggleFullscreen
  }
}

