<template>
  <div 
    ref="pdfContainer"
    class="pdf-viewer-container relative w-full h-full flex flex-col"
  >
    <!-- PDF Toolbar -->
    <div 
      :class="[
        'pdf-toolbar flex items-center justify-between px-4 py-2 border-b sticky top-0 z-20',
        isDark 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      ]"
    >
      <!-- Zoom Controls -->
      <div class="flex items-center gap-2">
        <button
          :class="[
            'p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="isRendering || scale <= 0.5"
          title="Уменьшить"
          @click="zoomOut"
        >
          <span class="material-symbols-outlined text-lg">remove</span>
        </button>
        <span 
          :class="[
            'text-sm font-mono min-w-[4rem] text-center',
            isDark ? 'text-gray-400' : 'text-gray-600'
          ]"
        >
          {{ Math.round(scale * 100) }}%
        </span>
        <button
          :class="[
            'p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="isRendering || scale >= 3"
          title="Увеличить"
          @click="zoomIn"
        >
          <span class="material-symbols-outlined text-lg">add</span>
        </button>
        
        <!-- Fit width button -->
        <button
          :class="[
            'p-1.5 rounded transition-colors ml-2',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          title="По ширине"
          @click="fitToWidth"
        >
          <span class="material-symbols-outlined text-lg">fit_width</span>
        </button>
      </div>

      <!-- Page Navigation -->
      <div class="flex items-center gap-2">
        <button
          :class="[
            'p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="currentPage <= 1"
          title="Предыдущая страница"
          @click="goToPrevPage"
        >
          <span class="material-symbols-outlined text-lg">chevron_left</span>
        </button>
        
        <div class="flex items-center gap-1">
          <input
            v-model.number="pageInput"
            type="number"
            :min="1"
            :max="totalPages"
            :class="[
              'w-12 text-center text-sm rounded border px-1 py-0.5',
              isDark 
                ? 'bg-gray-700 border-gray-600 text-gray-200' 
                : 'bg-white border-gray-300 text-gray-700'
            ]"
            @change="goToPage(pageInput)"
            @keyup.enter="goToPage(pageInput)"
          />
          <span :class="isDark ? 'text-gray-400' : 'text-gray-500'" class="text-sm">
            / {{ totalPages }}
          </span>
        </div>
        
        <button
          :class="[
            'p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="currentPage >= totalPages"
          title="Следующая страница"
          @click="goToNextPage"
        >
          <span class="material-symbols-outlined text-lg">chevron_right</span>
        </button>
      </div>

      <!-- Loading indicator -->
      <div class="flex items-center gap-2 min-w-[100px] justify-end">
        <div 
          v-if="isRendering"
          class="flex items-center gap-2"
        >
          <div class="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span :class="['text-xs', isDark ? 'text-gray-400' : 'text-gray-500']">
            Рендеринг...
          </span>
        </div>
      </div>
    </div>

    <!-- PDF Scroll Container -->
    <div 
      ref="scrollContainer"
      :class="[
        'pdf-scroll-container flex-1 overflow-auto',
        isDark ? 'bg-gray-900' : 'bg-[#525659]',
        isDragging ? 'cursor-grabbing' : (scale > 1 ? 'cursor-grab' : '')
      ]"
      @scroll="handleScroll"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
    >
      <!-- Pages Wrapper -->
      <div 
        ref="pagesWrapper"
        class="pdf-pages-wrapper flex flex-col items-center py-4 min-h-full"
        :style="{ minWidth: containerWidth + 'px' }"
      >
        <!-- Virtual Pages -->
        <div
          v-for="pageNum in totalPages"
          :key="pageNum"
          :ref="el => setPageRef(el, pageNum)"
          :data-page="pageNum"
          class="pdf-page-container mb-4 shadow-xl bg-white relative"
          :style="{
            width: pageWidth + 'px',
            height: pageHeights[pageNum] || estimatedPageHeight + 'px'
          }"
        >
          <!-- Canvas for rendered page -->
          <canvas
            v-if="renderedPages.has(pageNum)"
            :ref="el => setCanvasRef(el, pageNum)"
            class="pdf-canvas block"
          />
          
          <!-- Placeholder for unrendered page -->
          <div 
            v-else
            class="absolute inset-0 flex items-center justify-center bg-gray-100"
          >
            <div class="text-center text-gray-400">
              <span class="material-symbols-outlined text-4xl mb-2 block">description</span>
              <span class="text-sm">Страница {{ pageNum }}</span>
            </div>
          </div>

          <!-- Page number overlay -->
          <div 
            class="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded"
          >
            {{ pageNum }}
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="isLoading"
      class="absolute inset-0 bg-black/50 flex items-center justify-center z-30"
    >
      <div class="text-center text-white">
        <div class="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4" />
        <p class="text-sm">Загрузка PDF...</p>
        <p v-if="loadingProgress > 0" class="text-xs mt-1 opacity-70">
          {{ loadingProgress }}%
        </p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-if="error && !isLoading"
      class="absolute inset-0 bg-white flex items-center justify-center z-30"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-6xl text-red-400 mb-4 block">error</span>
        <p class="text-red-500 mb-2">Ошибка загрузки PDF</p>
        <p class="text-sm text-gray-500 mb-4">{{ error }}</p>
        <button
          class="px-4 py-2 bg-primary text-white rounded hover:bg-blue-600 transition-colors"
          @click="loadPdf"
        >
          Повторить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`

const props = defineProps({
  source: {
    type: Object,
    default: null
  },
  initialScale: {
    type: Number,
    default: 1
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['page-change', 'scale-change', 'loaded', 'error'])

// Refs
const pdfContainer = ref(null)
const scrollContainer = ref(null)
const pagesWrapper = ref(null)
const pageRefs = ref({})
const canvasRefs = ref({})

// State
const pdfDoc = ref(null)
const totalPages = ref(0)
const currentPage = ref(1)
const pageInput = ref(1)
const scale = ref(props.initialScale)
const isLoading = ref(false)
const loadingProgress = ref(0)
const isRendering = ref(false)
const error = ref(null)

// Page dimensions
const pageWidth = ref(800)
const pageHeights = ref({})
const estimatedPageHeight = ref(1130) // A4 ratio estimation
const containerWidth = ref(0)

// Virtualization
const renderedPages = ref(new Set())
const renderQueue = ref([])
const visiblePages = ref(new Set())
const BUFFER_PAGES = 2 // Render 2 pages before/after visible

// Drag to pan
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, scrollLeft: 0, scrollTop: 0 })

// Render cache
const renderCache = new Map()

// Debounce timer
let zoomDebounceTimer = null
let scrollDebounceTimer = null

// API base URL
const API_BASE_URL = '/api'

// Get auth token
function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  return token ? `Bearer ${token.trim()}` : null
}

// Set refs
const setPageRef = (el, pageNum) => {
  if (el) pageRefs.value[pageNum] = el
}

const setCanvasRef = (el, pageNum) => {
  if (el) canvasRefs.value[pageNum] = el
}

// Load PDF
async function loadPdf() {
  if (!props.source) {
    pdfDoc.value = null
    return
  }

  const key = props.source.objectName || props.source.object_key || props.source.objectKey
  if (!key) {
    pdfDoc.value = null
    return
  }

  isLoading.value = true
  loadingProgress.value = 0
  error.value = null
  renderedPages.value.clear()
  renderCache.clear()

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

    const arrayBuffer = await response.arrayBuffer()
    
    // Load PDF document
    const loadingTask = pdfjsLib.getDocument({
      data: arrayBuffer,
      cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/',
      cMapPacked: true
    })

    loadingTask.onProgress = (progress) => {
      if (progress.total > 0) {
        loadingProgress.value = Math.round((progress.loaded / progress.total) * 100)
      }
    }

    pdfDoc.value = await loadingTask.promise
    totalPages.value = pdfDoc.value.numPages
    pageInput.value = 1
    currentPage.value = 1

    // Get first page dimensions to calculate initial scale
    const firstPage = await pdfDoc.value.getPage(1)
    const viewport = firstPage.getViewport({ scale: 1 })
    
    // Calculate fit-to-width scale
    await nextTick()
    calculateOptimalScale(viewport.width)
    
    // Store page heights
    for (let i = 1; i <= totalPages.value; i++) {
      const page = await pdfDoc.value.getPage(i)
      const vp = page.getViewport({ scale: scale.value })
      pageHeights.value[i] = vp.height
    }
    
    estimatedPageHeight.value = pageHeights.value[1] || 1130

    emit('loaded', { totalPages: totalPages.value })
    
    // Initial render of visible pages
    await nextTick()
    updateVisiblePages()
    
  } catch (err) {
    console.error('[LessonPdfViewer] Error loading PDF:', err)
    error.value = err.message || 'Не удалось загрузить PDF файл'
    emit('error', err)
  } finally {
    isLoading.value = false
  }
}

// Calculate optimal scale to fit container width
function calculateOptimalScale(originalWidth) {
  if (!scrollContainer.value) return
  
  const containerW = scrollContainer.value.clientWidth - 48 // padding
  containerWidth.value = containerW
  
  // Calculate scale to fit width
  const optimalScale = containerW / originalWidth
  scale.value = Math.min(Math.max(optimalScale, 0.5), 2)
  pageWidth.value = originalWidth * scale.value
}

// Fit to width
async function fitToWidth() {
  if (!pdfDoc.value) return
  
  const firstPage = await pdfDoc.value.getPage(1)
  const viewport = firstPage.getViewport({ scale: 1 })
  
  const containerW = scrollContainer.value.clientWidth - 48
  scale.value = containerW / viewport.width
  
  debouncedRender()
}

// Zoom functions
function zoomIn() {
  const newScale = Math.min(3, scale.value + 0.25)
  if (newScale !== scale.value) {
    scale.value = newScale
    debouncedRender()
  }
}

function zoomOut() {
  const newScale = Math.max(0.5, scale.value - 0.25)
  if (newScale !== scale.value) {
    scale.value = newScale
    debouncedRender()
  }
}

// Debounced render after zoom
function debouncedRender() {
  isRendering.value = true
  
  clearTimeout(zoomDebounceTimer)
  zoomDebounceTimer = setTimeout(async () => {
    // Clear cache and re-render at new scale
    renderedPages.value.clear()
    renderCache.clear()
    
    // Update page dimensions
    if (pdfDoc.value) {
      for (let i = 1; i <= totalPages.value; i++) {
        const page = await pdfDoc.value.getPage(i)
        const vp = page.getViewport({ scale: scale.value })
        pageHeights.value[i] = vp.height
        if (i === 1) pageWidth.value = vp.width
      }
    }
    
    await nextTick()
    updateVisiblePages()
    emit('scale-change', scale.value)
  }, 150)
}

// Update visible pages based on scroll position
function updateVisiblePages() {
  if (!scrollContainer.value || !pdfDoc.value) return
  
  const container = scrollContainer.value
  const scrollTop = container.scrollTop
  const viewportHeight = container.clientHeight
  const scrollBottom = scrollTop + viewportHeight
  
  const newVisiblePages = new Set()
  let accumulatedHeight = 16 // Initial padding
  
  for (let i = 1; i <= totalPages.value; i++) {
    const pageHeight = pageHeights.value[i] || estimatedPageHeight.value
    const pageTop = accumulatedHeight
    const pageBottom = pageTop + pageHeight
    
    // Check if page is in viewport (with buffer)
    const bufferTop = scrollTop - (viewportHeight * BUFFER_PAGES)
    const bufferBottom = scrollBottom + (viewportHeight * BUFFER_PAGES)
    
    if (pageBottom >= bufferTop && pageTop <= bufferBottom) {
      newVisiblePages.add(i)
    }
    
    // Update current page
    if (pageTop <= scrollTop + viewportHeight / 2 && pageBottom >= scrollTop + viewportHeight / 2) {
      if (currentPage.value !== i) {
        currentPage.value = i
        pageInput.value = i
        emit('page-change', i)
      }
    }
    
    accumulatedHeight = pageBottom + 16 // Gap between pages
  }
  
  visiblePages.value = newVisiblePages
  
  // Render visible pages
  renderVisiblePages()
}

// Render visible pages
async function renderVisiblePages() {
  if (!pdfDoc.value) return
  
  const pagesToRender = [...visiblePages.value].filter(p => !renderedPages.value.has(p))
  
  if (pagesToRender.length === 0) {
    isRendering.value = false
    return
  }
  
  isRendering.value = true
  
  // Sort by distance from current page
  pagesToRender.sort((a, b) => Math.abs(a - currentPage.value) - Math.abs(b - currentPage.value))
  
  for (const pageNum of pagesToRender) {
    if (!visiblePages.value.has(pageNum)) continue // Skip if no longer visible
    await renderPage(pageNum)
  }
  
  isRendering.value = false
  
  // Clean up pages that are far from viewport
  cleanupDistantPages()
}

// Render single page
async function renderPage(pageNum) {
  if (!pdfDoc.value || renderedPages.value.has(pageNum)) return
  
  const cacheKey = `${pageNum}-${scale.value}`
  
  try {
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: scale.value })
    
    // Mark as rendered to prevent duplicate renders
    renderedPages.value.add(pageNum)
    
    await nextTick()
    
    const canvas = canvasRefs.value[pageNum]
    if (!canvas) return
    
    // High DPI support
    const dpr = window.devicePixelRatio || 1
    canvas.width = viewport.width * dpr
    canvas.height = viewport.height * dpr
    canvas.style.width = viewport.width + 'px'
    canvas.style.height = viewport.height + 'px'
    
    const ctx = canvas.getContext('2d')
    ctx.scale(dpr, dpr)
    
    // Check cache
    if (renderCache.has(cacheKey)) {
      const imageData = renderCache.get(cacheKey)
      ctx.putImageData(imageData, 0, 0)
      return
    }
    
    // Render page
    await page.render({
      canvasContext: ctx,
      viewport: viewport
    }).promise
    
    // Cache the result (only for reasonable sizes)
    if (canvas.width * canvas.height < 4000000) { // ~2000x2000
      try {
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
        renderCache.set(cacheKey, imageData)
      } catch (e) {
        // Canvas might be tainted, skip caching
      }
    }
    
  } catch (err) {
    console.error(`[LessonPdfViewer] Error rendering page ${pageNum}:`, err)
    renderedPages.value.delete(pageNum)
  }
}

// Cleanup pages far from viewport to save memory
function cleanupDistantPages() {
  const MAX_CACHED_PAGES = 10
  
  if (renderedPages.value.size <= MAX_CACHED_PAGES) return
  
  const sortedPages = [...renderedPages.value].sort(
    (a, b) => Math.abs(a - currentPage.value) - Math.abs(b - currentPage.value)
  )
  
  // Remove pages that are far from current
  const pagesToRemove = sortedPages.slice(MAX_CACHED_PAGES)
  
  for (const pageNum of pagesToRemove) {
    if (!visiblePages.value.has(pageNum)) {
      renderedPages.value.delete(pageNum)
      
      // Clear canvas
      const canvas = canvasRefs.value[pageNum]
      if (canvas) {
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
    }
  }
}

// Handle scroll
function handleScroll() {
  clearTimeout(scrollDebounceTimer)
  scrollDebounceTimer = setTimeout(() => {
    updateVisiblePages()
  }, 50)
}

// Page navigation
function goToPage(pageNum) {
  const num = Math.max(1, Math.min(totalPages.value, parseInt(pageNum) || 1))
  pageInput.value = num
  
  // Scroll to page
  const pageEl = pageRefs.value[num]
  if (pageEl && scrollContainer.value) {
    pageEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

function goToPrevPage() {
  if (currentPage.value > 1) {
    goToPage(currentPage.value - 1)
  }
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) {
    goToPage(currentPage.value + 1)
  }
}

// Drag to pan
function startDrag(e) {
  if (scale.value <= 1 || e.button !== 0) return
  
  isDragging.value = true
  dragStart.value = {
    x: e.clientX,
    y: e.clientY,
    scrollLeft: scrollContainer.value.scrollLeft,
    scrollTop: scrollContainer.value.scrollTop
  }
  
  e.preventDefault()
}

function onDrag(e) {
  if (!isDragging.value) return
  
  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y
  
  scrollContainer.value.scrollLeft = dragStart.value.scrollLeft - dx
  scrollContainer.value.scrollTop = dragStart.value.scrollTop - dy
}

function endDrag() {
  isDragging.value = false
}

// Keyboard navigation
function handleKeydown(e) {
  if (!pdfDoc.value) return
  
  switch (e.key) {
    case 'ArrowLeft':
    case 'PageUp':
      e.preventDefault()
      goToPrevPage()
      break
    case 'ArrowRight':
    case 'PageDown':
      e.preventDefault()
      goToNextPage()
      break
    case '+':
    case '=':
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        zoomIn()
      }
      break
    case '-':
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        zoomOut()
      }
      break
    case '0':
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        fitToWidth()
      }
      break
  }
}

// Watch for source changes
watch(() => props.source, () => {
  currentPage.value = 1
  pageInput.value = 1
  totalPages.value = 0
  loadPdf()
}, { immediate: true })

// Watch for initial scale changes
watch(() => props.initialScale, (newScale) => {
  if (newScale && newScale !== scale.value) {
    scale.value = newScale
    debouncedRender()
  }
})

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  
  // Handle resize
  const resizeObserver = new ResizeObserver(() => {
    if (pdfDoc.value && scrollContainer.value) {
      containerWidth.value = scrollContainer.value.clientWidth - 48
    }
  })
  
  if (scrollContainer.value) {
    resizeObserver.observe(scrollContainer.value)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearTimeout(zoomDebounceTimer)
  clearTimeout(scrollDebounceTimer)
  renderCache.clear()
  
  if (pdfDoc.value) {
    pdfDoc.value.destroy()
  }
})

// Expose methods
defineExpose({
  zoomIn,
  zoomOut,
  fitToWidth,
  goToPage,
  goToPrevPage,
  goToNextPage,
  currentPage,
  totalPages,
  scale
})
</script>

<style scoped>
.pdf-viewer-container {
  min-height: 400px;
}

.pdf-scroll-container {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.pdf-scroll-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.pdf-scroll-container::-webkit-scrollbar-track {
  background: transparent;
}

.pdf-scroll-container::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 4px;
}

.pdf-scroll-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(107, 114, 128, 0.8);
}

.pdf-page-container {
  transition: box-shadow 0.2s;
}

.pdf-page-container:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.pdf-canvas {
  display: block;
}

/* Hide number input spinners */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}

/* Dark mode scrollbar */
.dark .pdf-scroll-container::-webkit-scrollbar-thumb {
  background-color: rgba(75, 85, 99, 0.5);
}
</style>
