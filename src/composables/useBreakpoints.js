import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable for responsive breakpoints
 * Provides mobile/tablet/desktop detection with resize handling
 */
export function useBreakpoints() {
  const isMobile = ref(window.innerWidth < 768)
  const isTablet = ref(window.innerWidth >= 768 && window.innerWidth < 1024)
  const isDesktop = ref(window.innerWidth >= 1024)

  const updateBreakpoints = () => {
    const width = window.innerWidth
    isMobile.value = width < 768
    isTablet.value = width >= 768 && width < 1024
    isDesktop.value = width >= 1024
  }

  onMounted(() => {
    window.addEventListener('resize', updateBreakpoints)
    updateBreakpoints() // Initial check
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateBreakpoints)
  })

  return {
    isMobile,
    isTablet,
    isDesktop,
    updateBreakpoints
  }
}

