import { ref, computed, watch, onUnmounted, shallowRef } from 'vue'
import pdfService from '@/services/pdfService.optimized'

/**
 * Composable для работы с PDF документами
 */
export function usePdf() {
  // Используем shallowRef для больших объектов
  const currentPdfDocument = shallowRef(null)
  const totalPages = ref(0)
  const currentZoom = ref(100)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Загрузка PDF документа
  const loadPdf = async (url) => {
    if (!url) return
    
    isLoading.value = true
    error.value = null
    
    try {
      const pdf = await pdfService.loadPdfDocument(url)
      currentPdfDocument.value = pdf
      totalPages.value = pdf.numPages
    } catch (err) {
      error.value = err.message
      console.error('Ошибка загрузки PDF:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // Управление масштабом
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
  
  const resetZoom = () => {
    currentZoom.value = 100
  }
  
  const setZoom = (zoom) => {
    currentZoom.value = Math.max(50, Math.min(200, zoom))
  }
  
  // Получение страницы
  const getPage = async (pageNumber) => {
    if (!currentPdfDocument.value) return null
    
    try {
      return await pdfService.getPdfPage(currentPdfDocument.value, pageNumber)
    } catch (err) {
      console.error(`Ошибка получения страницы ${pageNumber}:`, err)
      return null
    }
  }
  
  // Рендеринг страницы
  const renderPage = async (page, canvas, zoom = currentZoom.value) => {
    if (!page || !canvas) return
    
    try {
      const scale = zoom / 100
      return await pdfService.renderPdfPage(page, canvas, scale * 2) // *2 для retina displays
    } catch (err) {
      console.error('Ошибка рендеринга страницы:', err)
      return null
    }
  }
  
  // Предзагрузка соседних страниц
  const preloadNearbyPages = (currentPage, range = 2) => {
    if (!currentPdfDocument.value) return
    pdfService.preloadNearbyPages(currentPdfDocument.value, currentPage, range)
  }
  
  // Очистка ресурсов
  const cleanup = () => {
    if (currentPdfDocument.value) {
      currentPdfDocument.value.destroy()
      currentPdfDocument.value = null
    }
    totalPages.value = 0
    error.value = null
  }
  
  // Автоочистка при размонтировании
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    currentPdfDocument,
    totalPages,
    currentZoom,
    isLoading,
    error,
    loadPdf,
    zoomIn,
    zoomOut,
    resetZoom,
    setZoom,
    getPage,
    renderPage,
    preloadNearbyPages,
    cleanup
  }
}

