<template>
  <div 
    ref="pdfContainer"
    class="secure-pdf-viewer"
    :class="{ 'fullscreen-mode': isFullscreen }"
  >
    <!-- Loading State -->
    <div 
      v-if="loading"
      class="pdf-loading"
    >
      <el-icon class="is-loading rotating" :size="48">
        <Refresh />
      </el-icon>
      <p class="loading-text">Загрузка документа...</p>
    </div>

    <!-- Error State -->
    <div 
      v-else-if="error"
      class="pdf-error"
    >
      <el-icon :size="64" class="error-icon">
        <Document />
      </el-icon>
      <h3 class="error-title">Ошибка загрузки документа</h3>
      <p class="error-message">{{ error }}</p>
      <el-button 
        type="primary" 
        @click="loadPdf"
      >
        Попробовать снова
      </el-button>
    </div>

    <!-- PDF Canvas Container -->
    <div 
      v-else
      ref="pdfCanvasContainer"
      class="pdf-canvas-container"
      :style="{ transform: `scale(${zoom / 100})`, transformOrigin: 'top left' }"
    >
      <canvas 
        ref="pdfCanvas"
        class="pdf-canvas"
      />
    </div>

    <!-- PDF Controls -->
    <div 
      v-if="!loading && !error && totalPages > 0"
      class="pdf-controls"
    >
      <div class="controls-left">
        <el-button 
          :icon="ArrowLeft" 
          :disabled="currentPage <= 1"
          size="small"
          @click="previousPage"
        >
          Назад
        </el-button>
        <span class="page-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>
        <el-button 
          :icon="ArrowRight" 
          :disabled="currentPage >= totalPages"
          size="small"
          @click="nextPage"
        >
          Вперед
        </el-button>
      </div>
      <div class="controls-right">
        <el-button 
          :icon="ZoomOut" 
          :disabled="zoom <= 50"
          size="small"
          @click="zoomOut"
        />
        <el-tag class="zoom-tag">{{ zoom }}%</el-tag>
        <el-button 
          :icon="ZoomIn" 
          :disabled="zoom >= 200"
          size="small"
          @click="zoomIn"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ArrowLeft, ArrowRight, ZoomIn, ZoomOut, Document, Refresh } from '@element-plus/icons-vue'
import * as pdfjsLib from 'pdfjs-dist'

// Настройка worker для PDF.js
// КРИТИЧЕСКИ ВАЖНО: Worker должен точно соответствовать версии библиотеки
if (typeof window !== 'undefined') {
  // Для PDF.js 5.x используем worker из node_modules через правильный путь
  // Это гарантирует совместимость версий и решает проблему с приватными полями
  try {
    // Пробуем использовать worker из node_modules (правильный путь для Vite)
    // В production Vite соберет worker правильно
    const workerPath = `pdfjs-dist/build/pdf.worker.min.mjs`
    pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
      workerPath,
      import.meta.url
    ).toString()
    
    console.log('[SecurePDFViewer] Using worker from node_modules:', pdfjsLib.GlobalWorkerOptions.workerSrc)
  } catch (e) {
    // Fallback: используем CDN worker с той же версией
    const pdfjsVersion = pdfjsLib.version || '5.4.449'
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsVersion}/pdf.worker.min.mjs`
    console.warn('[SecurePDFViewer] Using CDN worker as fallback:', pdfjsLib.GlobalWorkerOptions.workerSrc)
  }
  
  // Проверяем версию PDF.js для совместимости
  const pdfjsVersion = pdfjsLib.version || 'unknown'
  console.log('[SecurePDFViewer] PDF.js configured:', {
    version: pdfjsVersion,
    workerSrc: pdfjsLib.GlobalWorkerOptions.workerSrc
  })
}

const props = defineProps({
  file: {
    type: Object,
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

const emit = defineEmits(['zoom-in', 'zoom-out', 'fullscreen-change'])

// State
const loading = ref(true)
const error = ref(null)
const pdfDoc = ref(null)
const currentPage = ref(1)
const totalPages = ref(0)
const pdfContainer = ref(null)
const pdfCanvasContainer = ref(null)
const pdfCanvas = ref(null)

// Загрузка PDF через streaming endpoint
const loadPdf = async () => {
  if (!props.file) {
    error.value = 'Файл не указан'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    // Используем streaming endpoint вместо presigned URL
    // Формат: /api/files/stream/{objectKey}
    const objectKey = props.file.objectName || props.file.object_key || props.file.objectKey
    
    if (!objectKey) {
      throw new Error('Не указан ключ объекта для загрузки')
    }

    // Нормализуем ключ: убираем ведущие слэши
    const normalizedKey = String(objectKey).replace(/^\/+/, '')
    
    if (!normalizedKey) {
      throw new Error('Некорректный ключ объекта')
    }

    // Кодируем ключ для URL (encodeURIComponent правильно обрабатывает все специальные символы)
    const encodedKey = encodeURIComponent(normalizedKey)
    const streamUrl = `/api/files/stream/${encodedKey}`
    
    console.log('[SecurePDFViewer] Loading PDF:', {
      originalKey: objectKey,
      normalizedKey: normalizedKey,
      streamUrl: streamUrl
    })

    // Получаем токен авторизации из localStorage
    const getAuthToken = () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        return `Bearer ${token.trim()}`
      }
      return null
    }

    const authToken = getAuthToken()
    
    // РЕШЕНИЕ: Загружаем PDF как ArrayBuffer вместо streaming URL
    // Это решает проблему "Cannot read from private field" в PDF.js 5.x
    console.log('[SecurePDFViewer] Fetching PDF as ArrayBuffer...')
    
    const fetchOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/pdf',
      },
      credentials: 'include',
    }
    
    if (authToken) {
      fetchOptions.headers['Authorization'] = authToken
    }

    // Загружаем весь PDF файл как ArrayBuffer
    const response = await fetch(streamUrl, fetchOptions)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch PDF: ${response.status} ${response.statusText}`)
    }

    // Преобразуем ответ в ArrayBuffer
    const arrayBuffer = await response.arrayBuffer()
    
    if (!arrayBuffer || arrayBuffer.byteLength === 0) {
      throw new Error('PDF file is empty')
    }

    console.log('[SecurePDFViewer] PDF fetched as ArrayBuffer:', {
      size: arrayBuffer.byteLength,
      sizeMB: (arrayBuffer.byteLength / 1024 / 1024).toFixed(2)
    })

    // Загружаем PDF из ArrayBuffer (это решает проблему с приватными полями)
    const loadingTask = pdfjsLib.getDocument({
      data: arrayBuffer, // Используем data вместо url
      // Используем стандартные настройки для стабильности
      useSystemFonts: false,
      // Оптимизация для больших файлов
      cMapUrl: `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/cmaps/`,
      cMapPacked: true,
      // Дополнительные настройки для совместимости
      verbosity: 0, // Уменьшаем логирование
      stopAtErrors: false, // Продолжаем при ошибках
    })

    // Ждем полной загрузки документа
    const pdfDocument = await loadingTask.promise
    
    if (!pdfDocument) {
      throw new Error('Failed to load PDF document')
    }

    // Проверяем, что документ полностью готов
    if (typeof pdfDocument.numPages !== 'number' || pdfDocument.numPages <= 0) {
      throw new Error('PDF document is not properly loaded')
    }

    pdfDoc.value = pdfDocument
    totalPages.value = pdfDocument.numPages
    currentPage.value = 1

    console.log('[SecurePDFViewer] PDF loaded successfully:', {
      pages: totalPages.value,
      file: props.file.fileName || props.file.originalName,
      documentReady: !!pdfDocument,
      hasGetPage: typeof pdfDocument.getPage === 'function'
    })

    // Ждем следующего тика для гарантии, что canvas готов
    await nextTick()
    
    // Дополнительная задержка для гарантии, что DOM и worker полностью готовы
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // Проверяем готовность перед рендерингом
    if (!pdfDoc.value || typeof pdfDoc.value.getPage !== 'function') {
      throw new Error('PDF document is not ready for rendering')
    }
    
    // Рендерим первую страницу
    await renderPage(1)
    loading.value = false
  } catch (err) {
    console.error('[SecurePDFViewer] Error loading PDF:', err)
    
    // Детальная обработка ошибок
    let errorMessage = 'Не удалось загрузить документ'
    if (err.name === 'MissingPDFException') {
      errorMessage = 'PDF файл поврежден или не найден'
    } else if (err.name === 'UnexpectedResponseException') {
      errorMessage = 'Ошибка сервера при загрузке документа. Проверьте авторизацию.'
    } else if (err.message) {
      errorMessage = err.message
    }
    
    error.value = errorMessage
    loading.value = false
  }
}

// Рендеринг страницы
const renderPage = async (pageNum) => {
  if (!pdfDoc.value || !pdfCanvas.value) {
    console.warn('[SecurePDFViewer] Cannot render: missing pdfDoc or canvas')
    return
  }

  try {
    // Проверяем, что документ полностью загружен
    if (!pdfDoc.value || typeof pdfDoc.value.getPage !== 'function') {
      throw new Error('PDF document is not ready')
    }

    // Получаем страницу с дополнительной проверкой
    let page
    try {
      // Проверяем, что метод getPage доступен
      if (typeof pdfDoc.value.getPage !== 'function') {
        throw new Error('getPage method is not available on PDF document')
      }
      
      // Получаем страницу
      const pagePromise = pdfDoc.value.getPage(pageNum)
      if (!pagePromise || typeof pagePromise.then !== 'function') {
        throw new Error('getPage did not return a promise')
      }
      
      page = await pagePromise
      
      // Дополнительная проверка после получения страницы
      if (!page) {
        throw new Error(`Page ${pageNum} returned null`)
      }
      
      // Проверяем, что страница имеет необходимые методы
      if (typeof page.getViewport !== 'function') {
        throw new Error('Page object is missing getViewport method')
      }
    } catch (getPageError) {
      // Если ошибка при получении страницы, пробуем перезагрузить документ
      console.error('[SecurePDFViewer] Error getting page:', getPageError)
      console.error('[SecurePDFViewer] PDF document state:', {
        hasPdfDoc: !!pdfDoc.value,
        numPages: pdfDoc.value?.numPages,
        getPageType: typeof pdfDoc.value?.getPage
      })
      throw new Error(`Не удалось получить страницу ${pageNum}: ${getPageError.message || 'Неизвестная ошибка'}`)
    }
    
    if (!page) {
      throw new Error(`Page ${pageNum} not found`)
    }

    // Проверяем, что страница валидна
    if (typeof page.getViewport !== 'function') {
      throw new Error('Page object is invalid')
    }

    // Вычисляем viewport с учетом zoom
    const scale = props.zoom / 100
    let viewport
    try {
      viewport = page.getViewport({ scale })
    } catch (viewportError) {
      console.error('[SecurePDFViewer] Error getting viewport:', viewportError)
      throw new Error('Не удалось создать viewport для страницы')
    }
    
    const canvas = pdfCanvas.value
    if (!canvas) {
      throw new Error('Canvas element not found')
    }

    const context = canvas.getContext('2d')
    if (!context) {
      throw new Error('Canvas context not available')
    }
    
    // Устанавливаем размеры canvas
    canvas.height = viewport.height
    canvas.width = viewport.width

    // Очищаем canvas перед рендерингом
    context.clearRect(0, 0, canvas.width, canvas.height)

    // Создаем контекст рендеринга
    const renderContext = {
      canvasContext: context,
      viewport: viewport,
    }

    // Рендерим страницу с обработкой ошибок
    let renderTask
    try {
      renderTask = page.render(renderContext)
      if (!renderTask || typeof renderTask.promise !== 'function') {
        throw new Error('Render task is invalid')
      }
      await renderTask.promise
    } catch (renderError) {
      console.error('[SecurePDFViewer] Error during render:', renderError)
      // Если ошибка рендеринга, пробуем отменить задачу
      if (renderTask && typeof renderTask.cancel === 'function') {
        try {
          renderTask.cancel()
        } catch (cancelError) {
          console.warn('[SecurePDFViewer] Error canceling render task:', cancelError)
        }
      }
      throw new Error(`Ошибка рендеринга страницы: ${renderError.message || 'Неизвестная ошибка'}`)
    }
    
    currentPage.value = pageNum
    
    console.log('[SecurePDFViewer] Page rendered successfully:', {
      page: pageNum,
      width: canvas.width,
      height: canvas.height,
      zoom: props.zoom
    })
  } catch (err) {
    console.error('[SecurePDFViewer] Error rendering page:', err)
    console.error('[SecurePDFViewer] Error details:', {
      pageNum,
      hasPdfDoc: !!pdfDoc.value,
      hasCanvas: !!pdfCanvas.value,
      pdfDocType: pdfDoc.value ? typeof pdfDoc.value : 'null',
      hasGetPage: pdfDoc.value ? typeof pdfDoc.value.getPage : 'null',
      errorName: err.name,
      errorMessage: err.message,
      errorStack: err.stack
    })
    
    // Более понятное сообщение об ошибке
    let errorMessage = 'Ошибка отображения страницы'
    if (err.message && (err.message.includes('private field') || err.message.includes('Cannot read'))) {
      errorMessage = 'Ошибка совместимости с PDF.js. Требуется полная перезагрузка документа.'
      console.error('[SecurePDFViewer] Private field error detected - document needs to be reloaded')
      
      // Очищаем состояние документа для полной перезагрузки
      pdfDoc.value = null
      totalPages.value = 0
      currentPage.value = 0
      
      // Устанавливаем ошибку и предлагаем перезагрузить
      error.value = errorMessage
      loading.value = false
      
      return
    } else if (err.message) {
      errorMessage = err.message
    }
    
    error.value = errorMessage
  }
}

// Навигация по страницам
const nextPage = async () => {
  if (currentPage.value < totalPages.value) {
    await renderPage(currentPage.value + 1)
    scrollToTop()
  }
}

const previousPage = async () => {
  if (currentPage.value > 1) {
    await renderPage(currentPage.value - 1)
    scrollToTop()
  }
}

const scrollToTop = () => {
  if (pdfContainer.value) {
    pdfContainer.value.scrollTop = 0
  }
}

// Zoom
const zoomIn = () => {
  emit('zoom-in')
}

const zoomOut = () => {
  emit('zoom-out')
}

// Перерисовка при изменении zoom
watch(() => props.zoom, async (newZoom) => {
  if (pdfDoc.value && currentPage.value > 0) {
    await renderPage(currentPage.value)
  }
})

// Перезагрузка при изменении objectKey (устойчивее, чем watch на весь объект)
watch(
  () => props.file?.objectName || props.file?.object_key || props.file?.objectKey,
  (newKey, oldKey) => {
    if (!newKey) return
    if (newKey !== oldKey) {
      console.log('[SecurePDFViewer] objectKey changed:', { oldKey, newKey })
    }
    loadPdf()
  },
  { immediate: true }
)

// Защита от контекстного меню и горячих клавиш
const preventContextMenu = (e) => {
  e.preventDefault()
  return false
}

const preventKeyShortcuts = (e) => {
  // Блокируем Ctrl+S, Ctrl+P, F12, Print Screen
  if (
    (e.ctrlKey && (e.key === 's' || e.key === 'S' || e.key === 'p' || e.key === 'P')) ||
    e.key === 'F12' ||
    (e.key === 'PrintScreen' || e.key === 'Print')
  ) {
    e.preventDefault()
    return false
  }
}

onMounted(() => {
  if (props.file) {
    loadPdf()
  }

  // Защита от контекстного меню
  if (pdfContainer.value) {
    pdfContainer.value.addEventListener('contextmenu', preventContextMenu)
    pdfContainer.value.addEventListener('keydown', preventKeyShortcuts)
  }
})

onUnmounted(() => {
  if (pdfContainer.value) {
    pdfContainer.value.removeEventListener('contextmenu', preventContextMenu)
    pdfContainer.value.removeEventListener('keydown', preventKeyShortcuts)
  }
})
</script>

<style scoped>
.secure-pdf-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  overflow: auto;
  background: #f3f4f6;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
}

.secure-pdf-viewer.fullscreen-mode {
  position: fixed;
  inset: 0;
  z-index: 50;
  min-height: 100vh;
}

.pdf-loading,
.pdf-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  width: 100%;
  gap: 1rem;
}

.loading-text {
  color: #6b7280;
  font-size: 0.875rem;
}

.error-icon {
  color: #ef4444;
}

.error-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.error-message {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.pdf-canvas-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
  padding: 1rem 0;
}

.pdf-canvas {
  display: block;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  background: white;
  /* Защита от выделения */
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  /* Защита от перетаскивания */
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
}

.pdf-controls {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  border-top: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  z-index: 10;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

.controls-left,
.controls-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
  padding: 0 0.5rem;
}

.zoom-tag {
  min-width: 3rem;
  text-align: center;
  font-size: 0.875rem;
}

/* Защита от печати */
@media print {
  .secure-pdf-viewer {
    display: none !important;
  }
}

/* Анимация вращения для иконки загрузки */
.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .pdf-controls {
    flex-direction: column;
    gap: 0.5rem;
  }

  .controls-left,
  .controls-right {
    width: 100%;
    justify-content: center;
  }

  .pdf-canvas-container {
    padding: 0.5rem 0;
  }
}
</style>

