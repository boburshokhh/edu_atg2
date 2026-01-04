<template>
  <div class="relative mb-12 flex flex-col items-center group w-full">
    <!-- PDF Container -->
    <div
      v-if="pdfData"
      class="pdf-container bg-white shadow-2xl"
      :style="{ transform: `scale(${effectiveZoom / 100})`, transformOrigin: 'top center' }"
    >
      <VuePdfEmbed
        :key="`pdf-${effectiveZoom}-${pdfKey}`"
        :source="pdfData"
        :scale="1"
        text-layer
        annotation-layer
        class="w-full h-auto"
        @loaded="handlePdfLoaded"
        @rendered="handlePdfRendered"
        @loading-failed="handlePdfError"
      />
    </div>
    
    <!-- Rendering State (for large zoom changes) -->
    <div
      v-if="isRendering && pdfData"
      class="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-10"
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
const effectiveZoom = ref(props.zoom || 100)
const pdfKey = ref(0)

// Debounce timer for zoom changes
const zoomDebounceTimer = ref(null)

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
}

// Watch for source changes
watch(() => props.source, () => {
  currentPage.value = 1
  totalPages.value = 0
  loadPdf()
}, { immediate: true })

// Watch for zoom changes with debounce and rendering state
watch(() => props.zoom, (newZoom, oldZoom) => {
  // Clear existing debounce timer
  if (zoomDebounceTimer.value) {
    clearTimeout(zoomDebounceTimer.value)
  }
  
  // Get previous zoom value (use effectiveZoom if oldZoom is undefined on first call)
  const previousZoom = oldZoom !== undefined ? oldZoom : effectiveZoom.value
  
  // For large zoom changes (>150%), show rendering state
  const zoomDiff = Math.abs(newZoom - previousZoom)
  if (zoomDiff > 50 || newZoom > 150) {
    isRendering.value = true
  }
  
  // Debounce zoom changes to avoid excessive re-renders
  zoomDebounceTimer.value = setTimeout(async () => {
    effectiveZoom.value = newZoom
    
    // Force re-render by updating key for large changes
    if (zoomDiff > 30) {
      pdfKey.value += 1
    }
    
    // Wait for next tick to ensure DOM is updated
    await nextTick()
    
    // Clear rendering state after a short delay
    if (isRendering.value) {
      setTimeout(() => {
        isRendering.value = false
      }, 300)
    }
  }, 100) // 100ms debounce
}, { immediate: true })
</script>

<style scoped>
.pdf-container {
  will-change: transform;
  transition: transform 0.2s ease-out;
}

/* Optimize GPU rendering */
.pdf-container {
  backface-visibility: hidden;
  perspective: 1000px;
}
</style>

