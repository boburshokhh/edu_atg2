<template>
  <div 
    ref="pdfViewerContainer" 
    class="pdf-viewer-container"
    :class="isFullscreen ? 'h-screen overflow-y-auto' : 'max-h-[70vh] overflow-y-auto'"
    @scroll="handleScroll"
  >
    <!-- Loading indicator -->
    <div v-if="isLoading" class="flex items-center justify-center min-h-[400px]">
      <el-icon class="is-loading" :size="32">
        <Loading />
      </el-icon>
    </div>

    <!-- Virtual PDF Pages -->
    <div v-else class="pdf-pages-wrapper" :style="{ height: totalHeight + 'px' }">
      <div 
        v-for="page in visiblePages" 
        :key="page.pageNumber"
        class="pdf-page-container"
        :style="{
          position: 'absolute',
          top: page.top + 'px',
          left: '50%',
          transform: `translateX(-50%) scale(${zoom / 100})`,
          transformOrigin: 'top center',
        }"
      >
        <canvas
          :ref="el => setCanvasRef(el, page.pageNumber)"
          class="pdf-canvas"
          :data-page="page.pageNumber"
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
const pageHeight = ref(800) // Средняя высота страницы
const isLoading = ref(true)

const {
  currentPdfDocument,
  totalPages,
  loadPdf,
  getPage,
  renderPage,
  preloadNearbyPages
} = usePdf()

const setCanvasRef = (el, pageNumber) => {
  if (el) {
    canvasRefs.value.set(pageNumber, el)
  }
}

// Вычисление видимых страниц
const calculateVisiblePages = () => {
  if (!pdfViewerContainer.value || totalPages.value === 0) return

  const scrollTop = pdfViewerContainer.value.scrollTop
  const containerHeight = pdfViewerContainer.value.clientHeight
  const buffer = 2 // Загружаем 2 страницы сверху и снизу от видимых

  const firstVisible = Math.floor(scrollTop / pageHeight.value)
  const lastVisible = Math.ceil((scrollTop + containerHeight) / pageHeight.value)

  const start = Math.max(0, firstVisible - buffer)
  const end = Math.min(totalPages.value, lastVisible + buffer + 1)

  const pages = []
  for (let i = start; i < end; i++) {
    pages.push({
      pageNumber: i + 1,
      top: i * pageHeight.value
    })
  }

  visiblePages.value = pages

  // Предзагрузка соседних страниц
  const currentPage = Math.floor(scrollTop / pageHeight.value) + 1
  preloadNearbyPages(currentPage, 3)
}

// Throttled scroll handler
const handleScroll = throttle(() => {
  calculateVisiblePages()
}, 100)

// Рендеринг видимых страниц
const renderVisiblePages = async () => {
  if (!currentPdfDocument.value) return

  for (const page of visiblePages.value) {
    const canvas = canvasRefs.value.get(page.pageNumber)
    if (!canvas || canvas.dataset.rendered === 'true') continue

    try {
      const pdfPage = await getPage(page.pageNumber)
      if (pdfPage && canvas) {
        await renderPage(pdfPage, canvas, props.zoom)
        canvas.dataset.rendered = 'true'
      }
    } catch (error) {
      console.error(`Ошибка рендеринга страницы ${page.pageNumber}:`, error)
    }
  }
}

// Загрузка PDF
const loadPdfDocument = async () => {
  if (!props.source) return

  isLoading.value = true

  try {
    await loadPdf(props.source)

    // Вычисляем общую высоту
    if (totalPages.value > 0) {
      totalHeight.value = totalPages.value * pageHeight.value
    }

    await nextTick()
    calculateVisiblePages()

    await nextTick()
    await renderVisiblePages()
  } catch (error) {
    console.error('Ошибка загрузки PDF:', error)
  } finally {
    isLoading.value = false
  }
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
    renderVisiblePages()
  })
}, { deep: true })

// Следим за изменением масштаба
watch(() => props.zoom, () => {
  // Помечаем все canvas как не отрендеренные для перерисовки
  canvasRefs.value.forEach(canvas => {
    canvas.dataset.rendered = 'false'
  })
  
  nextTick(() => {
    renderVisiblePages()
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
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: white;
}

.pdf-canvas {
  display: block;
  max-width: 100%;
  height: auto;
}
</style>

