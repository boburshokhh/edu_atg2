<template>
  <div class="relative mb-12 flex flex-col items-center group w-full">
    <!-- PDF Container -->
    <div
      v-if="pdfData"
      class="bg-white shadow-2xl origin-top transition-all duration-200 ease-out"
      :style="{ width: zoom + '%' }"
    >
      <VuePdfEmbed
        :source="pdfData"
        :scale="debouncedZoom / 100"
        :text-layer="!isZooming"
        :annotation-layer="!isZooming"
        class="w-full h-auto"
        @loaded="handlePdfLoaded"
        @rendered="handlePdfRendered"
        @loading-failed="handlePdfError"
      />
    </div>

    <!-- Loading State -->
    <div
      v-else-if="isLoading"
      class="w-full bg-white rounded-lg shadow-2xl p-12 flex items-center justify-center min-h-[400px]"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-6xl text-slate-400 mb-4 block animate-pulse">
          description
        </span>
        <p class="text-slate-500">Загрузка PDF...</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="w-full bg-white rounded-lg shadow-2xl p-12 flex items-center justify-center min-h-[400px]"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-6xl text-red-400 mb-4 block">
          error
        </span>
        <p class="text-red-500 mb-2">Ошибка загрузки PDF</p>
        <p class="text-sm text-slate-500">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
// Import required styles for PDF viewer
import 'vue-pdf-embed/dist/styles/annotationLayer.css'
import 'vue-pdf-embed/dist/styles/textLayer.css'

const props = defineProps({
  source: {
    type: Object,
    default: null
  },
  zoom: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits(['page-loaded'])

const currentPage = ref(1)
const totalPages = ref(0)
const pdfData = ref(null)
const isLoading = ref(false)
const error = ref(null)

// Debounced zoom для стабильности рендеринга
const debouncedZoom = ref(props.zoom)
const isZooming = ref(false)
let zoomTimeout = null

// API base URL
const API_BASE_URL = '/api'

// Get auth token from localStorage
function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  if (token) {
    return `Bearer ${token.trim()}`
  }
  return null
}

// Load PDF with authentication
async function loadPdf() {
  if (!props.source) {
    pdfData.value = null
    return
  }

  const key = props.source.objectName || props.source.object_key || props.source.objectKey
  if (!key) {
    pdfData.value = null
    return
  }

  isLoading.value = true
  error.value = null
  pdfData.value = null

  try {
    const token = getAuthToken()
    const url = `${API_BASE_URL}/files/stream/${encodeURIComponent(key)}`
    
    const headers = {}
    if (token) {
      headers['Authorization'] = token
    }

    const response = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    // Convert response to ArrayBuffer for vue-pdf-embed
    const arrayBuffer = await response.arrayBuffer()
    pdfData.value = arrayBuffer
  } catch (err) {
    console.error('[LessonPdfViewer] Error loading PDF:', err)
    error.value = err.message || 'Не удалось загрузить PDF файл'
    pdfData.value = null
  } finally {
    isLoading.value = false
  }
}

const handlePdfLoaded = (pdfDoc) => {
  if (pdfDoc && pdfDoc.numPages) {
    totalPages.value = pdfDoc.numPages
    currentPage.value = 1
    emit('page-loaded', { currentPage: 1, totalPages: totalPages.value })
  }
}

const handlePdfRendered = () => {
  // Document rendered successfully
}

const handlePdfError = (err) => {
  console.error('[LessonPdfViewer] PDF rendering error:', err)
  error.value = err?.message || 'Ошибка отображения PDF'
}

// Watch zoom changes with debounce
watch(() => props.zoom, (newZoom) => {
  // Отключаем text/annotation layers во время зума для производительности
  isZooming.value = true
  
  // Очищаем предыдущий таймер
  if (zoomTimeout) {
    clearTimeout(zoomTimeout)
  }
  
  // Если это первое значение (инициализация), применяем сразу
  if (debouncedZoom.value === 0 || Math.abs(debouncedZoom.value - newZoom) > 50) {
     debouncedZoom.value = newZoom
     isZooming.value = false
     return
  }

  // Для обычного зума ждем окончания ввода
  zoomTimeout = setTimeout(() => {
    debouncedZoom.value = newZoom
    isZooming.value = false
    zoomTimeout = null
  }, 300) // 300ms debounce для плавности (CSS transition обработает визуальную часть)
}, { immediate: true })

watch(() => props.source, () => {
  currentPage.value = 1
  totalPages.value = 0
  loadPdf()
}, { immediate: true })

// Cleanup таймера при размонтировании
onUnmounted(() => {
  if (zoomTimeout) {
    clearTimeout(zoomTimeout)
    zoomTimeout = null
  }
})
</script>

<style scoped>
/* No additional styles needed - scrolling handled by parent ContentViewer */
</style>

