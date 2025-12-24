<template>
  <div 
    ref="pdfViewerContainer" 
    class="pdf-viewer-container"
    :class="isFullscreen ? 'h-screen overflow-y-auto' : 'max-h-[70vh] overflow-y-auto'"
    @scroll="handleScroll"
  >
    <!-- Loading indicator -->
    <div
      v-if="isLoading"
      class="flex items-center justify-center min-h-[400px]"
    >
      <el-icon
        class="is-loading"
        :size="32"
      >
        <Loading />
      </el-icon>
    </div>

    <!-- Error state -->
    <div
      v-else-if="loadError"
      class="flex flex-col items-center justify-center min-h-[400px] p-6 text-center"
    >
      <div class="text-sm text-gray-600 mb-3">
        Не удалось загрузить PDF. Проверьте интернет и попробуйте ещё раз.
      </div>
      <div class="text-xs text-gray-500 mb-4 break-all max-w-[90%]">
        {{ loadError }}
      </div>
      <el-button
        type="primary"
        @click="retryLoad"
      >
        Повторить
      </el-button>
    </div>

    <!-- Virtual PDF Pages -->
    <div
      v-else
      class="pdf-pages-wrapper"
      :style="{ height: totalHeight + 'px' }"
    >
      <div 
        v-for="page in visiblePages" 
        :key="page.pageNumber"
        class="pdf-page-container"
        :style="{
          position: 'absolute',
          top: page.top + 'px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '100%',
          display: 'flex',
          justifyContent: 'center'
        }"
      >
        <canvas
          :ref="el => setCanvasRef(el, page.pageNumber)"
          class="pdf-canvas"
          :data-page="page.pageNumber"
          :style="{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'top center'
          }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick, shallowRef } from 'vue'
import { usePdf } from '@/composables/usePdf'
import { throttle } from '@/utils/performance'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  source: {
    type: String,
    required: true
  },
  zoom: {
    type: Number,
    default: 100
  },
  isFullscreen: {
    type: Boolean,
    default: false
  }
})

const pdfViewerContainer = ref(null)
const canvasRefs = shallowRef(new Map())
const visiblePages = ref([])
const totalHeight = ref(0)
const pageHeight = ref(0) // Будет вычисляться динамически
const pageHeights = ref(new Map()) // Высота каждой страницы
const isLoading = ref(true)
const loadError = ref(null)
const activeLoadId = ref(0)

const PAGE_GAP = 16 // px gap between pages (stable spacing, avoids overlap)

const {
  currentPdfDocument,
  totalPages,
  loadPdf,
  getPage,
  renderPage,
  preloadNearbyPages
} = usePdf()

const isSlowNetwork = () => {
  try {
    const c = navigator?.connection
    const effective = (c?.effectiveType || '').toLowerCase()
    return effective === 'slow-2g' || effective === '2g'
  } catch {
    return false
  }
}

const setCanvasRef = (el, pageNumber) => {
  if (el) {
    canvasRefs.value.set(pageNumber, el)
  }
}

// Вычисление позиции страницы с учетом реальных высот
const calculatePageTop = (pageNumber) => {
  let top = PAGE_GAP // Top padding
  for (let i = 1; i < pageNumber; i++) {
    const height = pageHeights.value.get(i) || pageHeight.value || 1100
    top += height + PAGE_GAP
  }
  return top
}

// Вычисление видимых страниц
const calculateVisiblePages = () => {
  if (!pdfViewerContainer.value || totalPages.value === 0) return

  const scrollTop = pdfViewerContainer.value.scrollTop
  const containerHeight = pdfViewerContainer.value.clientHeight
  const buffer = isSlowNetwork() ? 1 : 2 // On slow networks reduce work

  // Находим первую видимую страницу
  let firstVisible = 1
  for (let i = 1; i <= totalPages.value; i++) {
    const pageTop = calculatePageTop(i)
    const pageHeight = pageHeights.value.get(i) || 1100
    if (pageTop + pageHeight > scrollTop) {
      firstVisible = Math.max(1, i - buffer)
      break
    }
  }

  // Находим последнюю видимую страницу
  let lastVisible = totalPages.value
  for (let i = firstVisible; i <= totalPages.value; i++) {
    const pageTop = calculatePageTop(i)
    if (pageTop > scrollTop + containerHeight) {
      lastVisible = Math.min(totalPages.value, i + buffer)
      break
    }
  }

  const pages = []
  for (let i = firstVisible; i <= lastVisible; i++) {
    pages.push({
      pageNumber: i,
      top: calculatePageTop(i)
    })
  }

  visiblePages.value = pages

  // Предзагрузка соседних страниц
  const currentPage = Math.floor((scrollTop + containerHeight / 2) / (pageHeight.value || 1100)) + 1
  preloadNearbyPages(currentPage, isSlowNetwork() ? 1 : 3)
}

// Throttled scroll handler
const handleScroll = throttle(() => {
  calculateVisiblePages()
}, 100)

// Рендеринг видимых страниц
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const retry = async (fn, { retries = 2, baseDelay = 250, factor = 2 } = {}) => {
  let attempt = 0
   
  while (true) {
    try {
      return await fn()
    } catch (e) {
      if (attempt >= retries) throw e
      const delay = baseDelay * Math.pow(factor, attempt)
      attempt += 1
      await sleep(delay)
    }
  }
}

const renderVisiblePages = async (loadId) => {
  if (!currentPdfDocument.value) return

  for (const page of visiblePages.value) {
    if (loadId && loadId !== activeLoadId.value) return
    const canvas = canvasRefs.value.get(page.pageNumber)
    if (!canvas || canvas.dataset.rendered === 'true') continue

    try {
      const pdfPage = await retry(() => getPage(page.pageNumber), { retries: 2, baseDelay: 250 })
      if (pdfPage && canvas) {
        // Рендерим с базовым масштабом (100%), zoom применяется через CSS transform
        await retry(() => renderPage(pdfPage, canvas, 100), { retries: 1, baseDelay: 300 })
        canvas.dataset.rendered = 'true'
        
        // ✅ Save REAL rendered height (DOM-measured), avoids overlap in fullscreen / different DPR
        if (!pageHeights.value.has(page.pageNumber)) {
          await nextTick()
          const rect = canvas.getBoundingClientRect()
          const measuredHeight = Math.max(1, Math.ceil(rect.height))
          pageHeights.value.set(page.pageNumber, measuredHeight)

          // Update base height estimate from page 1
          if (page.pageNumber === 1) {
            pageHeight.value = measuredHeight
          }

          updateTotalHeight()
          nextTick(() => {
            calculateVisiblePages()
          })
        }
      }
    } catch (error) {
      console.error(`Ошибка рендеринга страницы ${page.pageNumber}:`, error)
    }
  }
}

// Обновление общей высоты контейнера
const updateTotalHeight = () => {
  if (totalPages.value === 0) return
  
  let total = PAGE_GAP
  for (let i = 1; i <= totalPages.value; i++) {
    const height = pageHeights.value.get(i) || pageHeight.value || 1100
    total += height + PAGE_GAP
  }
  totalHeight.value = total
}

// Загрузка PDF
const loadPdfDocument = async () => {
  if (!props.source) return

  const myLoadId = activeLoadId.value + 1
  activeLoadId.value = myLoadId
  isLoading.value = true
  loadError.value = null
  pageHeights.value.clear()
  pageHeight.value = 0

  try {
    await retry(() => loadPdf(props.source), { retries: 2, baseDelay: 400 })
    if (myLoadId !== activeLoadId.value) return

    // Устанавливаем начальную высоту (будет обновлена после рендеринга)
    if (totalPages.value > 0) {
      pageHeight.value = 1100 // Временная высота для расчета
      updateTotalHeight()
    }

    await nextTick()
    calculateVisiblePages()

    await nextTick()
    await renderVisiblePages(myLoadId)
    
    // Пересчитываем после первого рендеринга
    await nextTick()
    updateTotalHeight()
    calculateVisiblePages()
  } catch (error) {
    console.error('Ошибка загрузки PDF:', error)
    loadError.value = error?.message || String(error)
  } finally {
    if (myLoadId === activeLoadId.value) {
      isLoading.value = false
    }
  }
}

const retryLoad = () => {
  loadPdfDocument()
}

// Следим за изменением источника
watch(() => props.source, (newSource) => {
  if (newSource) {
    // Очищаем рендеренные страницы при смене документа
    canvasRefs.value.forEach(canvas => {
      canvas.dataset.rendered = 'false'
    })
    canvasRefs.value.clear()
    visiblePages.value = []
    loadPdfDocument()
  }
}, { immediate: true })

// Следим за изменением видимых страниц
watch(visiblePages, () => {
  nextTick(() => {
    renderVisiblePages(activeLoadId.value)
  })
}, { deep: true })

// Следим за изменением масштаба
watch(() => props.zoom, () => {
  // Очищаем сохраненные высоты при изменении zoom
  pageHeights.value.clear()
  
  // Помечаем все canvas как не отрендеренные для перерисовки
  canvasRefs.value.forEach(canvas => {
    canvas.dataset.rendered = 'false'
  })
  
  nextTick(() => {
    renderVisiblePages()
    updateTotalHeight()
    calculateVisiblePages()
  })
})

onMounted(() => {
  loadPdfDocument()
})

onUnmounted(() => {
  canvasRefs.value.clear()
})
</script>

<style scoped>
.pdf-viewer-container {
  position: relative;
  background: #f5f5f5;
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}

.pdf-viewer-container::-webkit-scrollbar {
  width: 8px;
}

.pdf-viewer-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.pdf-viewer-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.pdf-viewer-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.pdf-pages-wrapper {
  position: relative;
  width: 100%;
}

.pdf-page-container {
  margin: 0;
  margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: white;
  display: flex;
  justify-content: center;
}

.pdf-canvas {
  display: block;
  max-width: 100%;
  height: auto;
  width: auto;
}
</style>

