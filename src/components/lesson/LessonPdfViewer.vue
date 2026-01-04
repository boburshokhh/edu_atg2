<template>
  <div class="relative mb-12 flex flex-col items-center group w-full">
    <!-- PDF Container -->
    <div
      v-if="pdfData && !isRendering"
      class="bg-white shadow-2xl transition-all duration-200 ease-out origin-top"
      :style="{ width: zoom + '%' }"
    >
      <VuePdfEmbed
        :key="pdfKey"
        :source="pdfData"
        :scale="zoom / 100"
        text-layer
        annotation-layer
        class="w-full h-auto"
        @loaded="handlePdfLoaded"
        @rendered="handlePdfRendered"
        @loading-failed="handlePdfError"
      />
    </div>

    <!-- Rendering State (during zoom change) -->
    <div
      v-if="isRendering && pdfData"
      class="w-full bg-white rounded-lg shadow-2xl p-12 flex items-center justify-center min-h-[400px]"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-6xl text-slate-400 mb-4 block animate-pulse">
          description
        </span>
        <p class="text-slate-500">Обновление масштаба...</p>
      </div>
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
import { ref, computed, watch, nextTick } from 'vue'
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
const isRendering = ref(false)
const zoomUpdateTimeout = ref(null)

// Computed key for VuePdfEmbed to force re-render on zoom change
const pdfKey = computed(() => {
  const sourceKey = props.source?.objectName || props.source?.object_key || props.source?.objectKey || ''
  return `pdf-${sourceKey}-${props.zoom}`
})

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
  isRendering.value = false
}

const handlePdfError = (err) => {
  console.error('[LessonPdfViewer] PDF rendering error:', err)
  error.value = err?.message || 'Ошибка отображения PDF'
  isRendering.value = false
  
  // Try to recover - reset to previous state
  if (pdfData.value) {
    // PDF data exists, just rendering failed - try to continue
    setTimeout(() => {
      isRendering.value = false
    }, 500)
  }
}

// Watch for zoom changes
watch(() => props.zoom, async (newZoom, oldZoom) => {
  // Only trigger if PDF is already loaded and zoom actually changed
  if (!pdfData.value || newZoom === oldZoom) {
    return
  }

  // Clear any pending timeout
  if (zoomUpdateTimeout.value) {
    clearTimeout(zoomUpdateTimeout.value)
  }

  // Set rendering state
  isRendering.value = true

  // Use debounce to avoid too frequent updates
  zoomUpdateTimeout.value = setTimeout(async () => {
    try {
      // Wait for next tick to ensure DOM is ready
      await nextTick()
      
      // Small delay to allow smooth transition
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // The key change will force VuePdfEmbed to re-render
      // isRendering will be set to false in handlePdfRendered
    } catch (err) {
      console.error('[LessonPdfViewer] Error updating zoom:', err)
      isRendering.value = false
      error.value = 'Ошибка при изменении масштаба'
    }
  }, 150)
}, { immediate: false })

// Watch for source changes
watch(() => props.source, () => {
  currentPage.value = 1
  totalPages.value = 0
  isRendering.value = false
  
  // Clear any pending zoom updates
  if (zoomUpdateTimeout.value) {
    clearTimeout(zoomUpdateTimeout.value)
    zoomUpdateTimeout.value = null
  }
  
  loadPdf()
}, { immediate: true })
</script>

<style scoped>
/* No additional styles needed - scrolling handled by parent ContentViewer */
</style>

