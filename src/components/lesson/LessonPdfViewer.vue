<template>
  <div class="w-full max-w-[800px] relative mb-12 flex flex-col group">
    <!-- Control Panel -->
    <div class="sticky top-4 z-10 flex items-center justify-center mb-4 px-4">
      <div class="flex items-center gap-2 bg-white/90 backdrop-blur rounded-lg shadow-lg px-3 py-1.5 md:px-4 md:py-2">
        <!-- Zoom Out -->
        <button
          class="p-1 hover:bg-slate-100 rounded text-slate-600 transition-colors"
          @click="$emit('zoom-out')"
          :disabled="zoom <= 50"
        >
          <ZoomOut :size="18" class="md:w-5 md:h-5" />
        </button>
        
        <!-- Zoom Display -->
        <span class="text-xs md:text-sm font-medium w-10 md:w-12 text-center text-slate-700">{{ zoom }}%</span>
        
        <!-- Zoom In -->
        <button
          class="p-1 hover:bg-slate-100 rounded text-slate-600 transition-colors"
          @click="$emit('zoom-in')"
          :disabled="zoom >= 200"
        >
          <ZoomIn :size="18" class="md:w-5 md:h-5" />
        </button>
        
        <!-- Page Indicator -->
        <div class="h-4 md:h-6 w-px bg-slate-300 mx-1"></div>
        <span class="text-xs md:text-sm font-medium text-slate-700 whitespace-nowrap">
          {{ currentPage }} / {{ totalPages }}
        </span>
      </div>
    </div>

    <!-- PDF Container -->
    <div
      v-if="pdfData"
      class="w-full bg-white shadow-2xl"
    >
      <VuePdfEmbed
        :source="pdfData"
        :scale="zoom / 100"
        text-layer
        annotation-layer
        class="w-full"
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
import { ref, computed, watch } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import { ZoomIn, ZoomOut } from 'lucide-vue-next'
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

const emit = defineEmits(['zoom-in', 'zoom-out', 'page-loaded'])

const currentPage = ref(1)
const totalPages = ref(0)
const pdfData = ref(null)
const isLoading = ref(false)
const error = ref(null)

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

watch(() => props.source, () => {
  currentPage.value = 1
  totalPages.value = 0
  loadPdf()
}, { immediate: true })
</script>

<style scoped>
/* No additional styles needed - scrolling handled by parent ContentViewer */
</style>

