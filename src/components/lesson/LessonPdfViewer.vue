<template>
  <div 
    ref="pdfContainer"
    class="pdf-viewer-container relative w-full h-full flex flex-col"
  >
    <!-- PDF Toolbar -->
    <div 
      :class="[
        'pdf-toolbar flex items-center justify-between px-2 sm:px-4 py-1.5 sm:py-2 border-b sticky top-0 z-20 gap-1 sm:gap-2',
        isDark 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      ]"
    >
      <!-- Zoom Controls -->
      <div class="flex items-center gap-1 sm:gap-2 shrink-0">
        <button
          :class="[
            'p-1 sm:p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="isRendering || scale <= 0.5"
          title="Уменьшить"
          @click="zoomOut"
        >
          <span class="material-symbols-outlined text-base sm:text-lg">remove</span>
        </button>
        <span 
          :class="[
            'text-xs sm:text-sm font-mono min-w-[2.5rem] sm:min-w-[4rem] text-center',
            isDark ? 'text-gray-400' : 'text-gray-600'
          ]"
        >
          {{ Math.round(scale * 100) }}%
        </span>
        <button
          :class="[
            'p-1 sm:p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="isRendering || scale >= 3"
          title="Увеличить"
          @click="zoomIn"
        >
          <span class="material-symbols-outlined text-base sm:text-lg">add</span>
        </button>
        
        <!-- Fit width button - hidden on xs -->
        <button
          :class="[
            'hidden sm:flex p-1.5 rounded transition-colors ml-1 sm:ml-2',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          title="По ширине"
          @click="fitToWidth"
        >
          <span class="material-symbols-outlined text-lg">fit_width</span>
        </button>
      </div>

      <!-- Page Navigation -->
      <div class="flex items-center gap-1 sm:gap-2 shrink-0">
        <button
          :class="[
            'p-1 sm:p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="currentPage <= 1"
          title="Предыдущая страница"
          @click="goToPrevPage"
        >
          <span class="material-symbols-outlined text-base sm:text-lg">chevron_left</span>
        </button>
        
        <div class="flex items-center gap-0.5 sm:gap-1">
          <input
            v-model.number="pageInput"
            type="number"
            :min="1"
            :max="totalPages"
            :class="[
              'w-10 sm:w-12 text-center text-xs sm:text-sm rounded border px-0.5 sm:px-1 py-0.5',
              isDark 
                ? 'bg-gray-700 border-gray-600 text-gray-200' 
                : 'bg-white border-gray-300 text-gray-700'
            ]"
            @change="goToPage(pageInput)"
            @keyup.enter="goToPage(pageInput)"
          />
          <span :class="isDark ? 'text-gray-400' : 'text-gray-500'" class="text-xs sm:text-sm whitespace-nowrap">
            / {{ totalPages }}
          </span>
        </div>
        
        <button
          :class="[
            'p-1 sm:p-1.5 rounded transition-colors',
            isDark ? 'hover:bg-gray-700 text-gray-400' : 'hover:bg-gray-100 text-gray-500'
          ]"
          :disabled="currentPage >= totalPages"
          title="Следующая страница"
          @click="goToNextPage"
        >
          <span class="material-symbols-outlined text-base sm:text-lg">chevron_right</span>
        </button>
      </div>

      <!-- Loading indicator - hidden on xs, icon only on sm -->
      <div class="hidden sm:flex items-center gap-2 min-w-[40px] md:min-w-[100px] justify-end shrink-0">
        <div 
          v-if="isRendering"
          class="flex items-center gap-1 sm:gap-2"
        >
          <div class="w-3 h-3 sm:w-4 sm:h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span :class="['text-xs hidden md:inline', isDark ? 'text-gray-400' : 'text-gray-500']">
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
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
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
          class="pdf-page-container mb-4 shadow-xl relative overflow-hidden"
          :style="{
            width: pageWidths[pageNum] + 'px',
            height: pageHeights[pageNum] + 'px',
            backgroundColor: '#ffffff'
          }"
        >
          <!-- Canvas for rendered page -->
          <canvas
            v-if="renderedPages.has(pageNum)"
            :ref="el => setCanvasRef(el, pageNum)"
            class="pdf-canvas block absolute top-0 left-0"
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
            class="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded pointer-events-none"
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
import { ref, shallowRef, watch, onMounted, onBeforeUnmount, nextTick, markRaw } from 'vue'
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
const pdfDoc = shallowRef(null)
const totalPages = ref(0)
const currentPage = ref(1)
const pageInput = ref(1)
const scale = ref(props.initialScale)
const isLoading = ref(false)
const loadingProgress = ref(0)
const isRendering = ref(false)
const error = ref(null)

// Page dimensions (viewport dimensions, not canvas)
const pageWidths = ref({})
const pageHeights = ref({})
const estimatedPageHeight = ref(1130)
const containerWidth = ref(0)

// Virtualization
const renderedPages = ref(new Set())
const renderingPages = ref(new Set()) // Track pages currently being rendered
const visiblePages = ref(new Set())
const BUFFER_PAGES = 2

// Drag to pan
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, scrollLeft: 0, scrollTop: 0 })

// Pinch to zoom
const isPinching = ref(false)
const pinchStartDistance = ref(0)
const pinchStartScale = ref(1)
let pinchRafId = null

// Debounce timers
let zoomDebounceTimer = null
let scrollDebounceTimer = null

// API base URL
const API_BASE_URL = '/api'

// Device pixel ratio for high DPI displays
const DPR = window.devicePixelRatio || 1

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
  renderingPages.value.clear()

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

    pdfDoc.value = markRaw(await loadingTask.promise)
    totalPages.value = pdfDoc.value.numPages
    pageInput.value = 1
    currentPage.value = 1

    // Get first page to calculate scale
    const firstPage = await pdfDoc.value.getPage(1)
    const viewport = firstPage.getViewport({ scale: 1 })
    
    // Calculate fit-to-width scale
    await nextTick()
    calculateOptimalScale(viewport.width)
    
    // Pre-calculate all page dimensions at current scale
    await calculateAllPageDimensions()

    emit('loaded', { totalPages: totalPages.value })
    
    // Initial render of visible pages
    await nextTick()
    updateVisiblePages()
    
  } catch (err) {
    console.error('[PDFViewer] Error loading PDF:', err)
    error.value = err.message || 'Не удалось загрузить PDF файл'
    emit('error', err)
  } finally {
    isLoading.value = false
  }
}

// Calculate all page dimensions
async function calculateAllPageDimensions() {
  if (!pdfDoc.value) return
  
  for (let i = 1; i <= totalPages.value; i++) {
    const page = await pdfDoc.value.getPage(i)
    const viewport = page.getViewport({ scale: scale.value })
    
    // Store VIEWPORT dimensions (not canvas dimensions)
    pageWidths.value[i] = viewport.width
    pageHeights.value[i] = viewport.height
  }
  
  estimatedPageHeight.value = pageHeights.value[1] || 1130
}

// Calculate optimal scale to fit container width
function calculateOptimalScale(originalWidth) {
  if (!scrollContainer.value) return
  
  const containerW = scrollContainer.value.clientWidth - 48
  containerWidth.value = containerW
  
  const optimalScale = containerW / originalWidth
  scale.value = Math.min(Math.max(optimalScale, 0.5), 2)
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
    // Clear rendered pages
    renderedPages.value.clear()
    renderingPages.value.clear()
    
    // Recalculate dimensions at new scale
    await calculateAllPageDimensions()
    
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
    
    // Check if page is in viewport with buffer
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
    
    accumulatedHeight = pageBottom + 16
  }
  
  visiblePages.value = newVisiblePages
  renderVisiblePages()
}

// Render visible pages
async function renderVisiblePages() {
  if (!pdfDoc.value) return
  
  const pagesToRender = [...visiblePages.value].filter(
    p => !renderedPages.value.has(p) && !renderingPages.value.has(p)
  )
  
  if (pagesToRender.length === 0) {
    isRendering.value = false
    return
  }
  
  isRendering.value = true
  
  // Sort by distance from current page
  pagesToRender.sort((a, b) => 
    Math.abs(a - currentPage.value) - Math.abs(b - currentPage.value)
  )
  
  // Render pages in parallel (but limit concurrency)
  const CONCURRENT_RENDERS = 3
  for (let i = 0; i < pagesToRender.length; i += CONCURRENT_RENDERS) {
    const batch = pagesToRender.slice(i, i + CONCURRENT_RENDERS)
    await Promise.all(batch.map(pageNum => renderPage(pageNum)))
  }
  
  isRendering.value = false
  cleanupDistantPages()
}

// Render single page
async function renderPage(pageNum) {
  if (!pdfDoc.value || renderedPages.value.has(pageNum) || renderingPages.value.has(pageNum)) {
    return
  }
  
  // Mark as rendering to prevent duplicates
  renderingPages.value.add(pageNum)
  
  try {
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: scale.value })
    
    // Mark as rendered BEFORE nextTick so v-if shows canvas
    renderedPages.value.add(pageNum)
    
    await nextTick()
    
    const canvas = canvasRefs.value[pageNum]
    if (!canvas) {
      renderingPages.value.delete(pageNum)
      renderedPages.value.delete(pageNum)
      return
    }
    
    // Set canvas size with DPR for sharp rendering
    canvas.width = viewport.width * DPR
    canvas.height = viewport.height * DPR
    
    // Set CSS size to viewport dimensions (not DPR-scaled)
    canvas.style.width = viewport.width + 'px'
    canvas.style.height = viewport.height + 'px'
    
    const ctx = canvas.getContext('2d')
    
    // Clear canvas first
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Create render context with DPR-scaled viewport
    const renderContext = {
      canvasContext: ctx,
      viewport: viewport,
      transform: DPR !== 1 ? [DPR, 0, 0, DPR, 0, 0] : null
    }
    
    // Render page
    await page.render(renderContext).promise
    
    renderingPages.value.delete(pageNum)
    
  } catch (err) {
    console.error(`[PDFViewer] Error rendering page ${pageNum}:`, err)
    renderingPages.value.delete(pageNum)
    renderedPages.value.delete(pageNum)
  }
}

// Cleanup pages far from viewport
function cleanupDistantPages() {
  const MAX_CACHED_PAGES = 10
  
  if (renderedPages.value.size <= MAX_CACHED_PAGES) return
  
  const sortedPages = [...renderedPages.value].sort(
    (a, b) => Math.abs(a - currentPage.value) - Math.abs(b - currentPage.value)
  )
  
  const pagesToRemove = sortedPages.slice(MAX_CACHED_PAGES)
  
  for (const pageNum of pagesToRemove) {
    if (!visiblePages.value.has(pageNum)) {
      renderedPages.value.delete(pageNum)
      
      // Clear canvas properly
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

// Touch handlers for pinch-to-zoom
function getTouchDistance(touches) {
  if (touches.length < 2) return 0
  const dx = touches[0].clientX - touches[1].clientX
  const dy = touches[0].clientY - touches[1].clientY
  return Math.sqrt(dx * dx + dy * dy)
}

function handleTouchStart(e) {
  if (e.touches.length === 2) {
    e.preventDefault()
    isPinching.value = true
    pinchStartDistance.value = getTouchDistance(e.touches)
    pinchStartScale.value = scale.value
  }
}

function handleTouchMove(e) {
  if (!isPinching.value || e.touches.length !== 2) return
  
  e.preventDefault()
  
  // Throttle with requestAnimationFrame
  if (pinchRafId) return
  
  pinchRafId = requestAnimationFrame(() => {
    const currentDistance = getTouchDistance(e.touches)
    const pinchRatio = currentDistance / pinchStartDistance.value
    const newScale = Math.min(3, Math.max(0.5, pinchStartScale.value * pinchRatio))
    
    if (Math.abs(newScale - scale.value) > 0.02) {
      scale.value = newScale
      // Don't debounce during active pinch - wait for touchend
    }
    
    pinchRafId = null
  })
}

function handleTouchEnd(e) {
  if (isPinching.value && e.touches.length < 2) {
    isPinching.value = false
    if (pinchRafId) {
      cancelAnimationFrame(pinchRafId)
      pinchRafId = null
    }
    // Trigger debounced render after pinch ends
    debouncedRender()
  }
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
  renderedPages.value.clear()
  renderingPages.value.clear()
  pageWidths.value = {}
  pageHeights.value = {}
  loadPdf()
}, { immediate: true })

// Watch for initial scale changes
watch(() => props.initialScale, (newScale) => {
  if (newScale && newScale !== scale.value) {
    scale.value = newScale
    debouncedRender()
  }
})

// Track previous width for significant resize detection
let previousContainerWidth = 0
let resizeDebounceTimer = null

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  
  const resizeObserver = new ResizeObserver((entries) => {
    if (!pdfDoc.value || !scrollContainer.value) return
    
    const newWidth = scrollContainer.value.clientWidth - 48
    containerWidth.value = newWidth
    
    // Check if this is a significant resize (e.g., orientation change)
    // Threshold: > 20% width change
    const widthChange = Math.abs(newWidth - previousContainerWidth)
    const isSignificantResize = previousContainerWidth > 0 && widthChange / previousContainerWidth > 0.2
    
    if (isSignificantResize) {
      // Debounce fitToWidth to avoid rapid re-renders during animation
      clearTimeout(resizeDebounceTimer)
      resizeDebounceTimer = setTimeout(() => {
        fitToWidth()
      }, 200)
    }
    
    previousContainerWidth = newWidth
  })
  
  if (scrollContainer.value) {
    resizeObserver.observe(scrollContainer.value)
    previousContainerWidth = scrollContainer.value.clientWidth - 48
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearTimeout(zoomDebounceTimer)
  clearTimeout(scrollDebounceTimer)
  clearTimeout(resizeDebounceTimer)
  
  if (pinchRafId) {
    cancelAnimationFrame(pinchRafId)
  }
  
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
  touch-action: pan-x pan-y;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
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

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}

.dark .pdf-scroll-container::-webkit-scrollbar-thumb {
  background-color: rgba(75, 85, 99, 0.5);
}
</style>