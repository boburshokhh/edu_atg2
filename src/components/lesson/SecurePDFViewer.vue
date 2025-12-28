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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ArrowLeft, ArrowRight, ZoomIn, ZoomOut, Document, Refresh } from '@element-plus/icons-vue'
import * as pdfjsLib from 'pdfjs-dist'

// Настройка worker для PDF.js
// Используем CDN для worker (можно также использовать локальный файл)
if (typeof window !== 'undefined') {
  pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`
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
    const httpHeaders = {}
    if (authToken) {
      httpHeaders['Authorization'] = authToken
    }

    // Загружаем PDF через streaming endpoint с поддержкой Range requests
    const loadingTask = pdfjsLib.getDocument({
      url: streamUrl,
      httpHeaders: httpHeaders,
      withCredentials: true,
      // Отключаем автоматическое скачивание всего файла
      disableAutoFetch: false,
      disableStream: false,
      // Оптимизация для больших файлов
      cMapUrl: `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/cmaps/`,
      cMapPacked: true,
    })

    pdfDoc.value = await loadingTask.promise
    totalPages.value = pdfDoc.value.numPages
    currentPage.value = 1

    console.log('[SecurePDFViewer] PDF loaded successfully:', {
      pages: totalPages.value,
      file: props.file.fileName || props.file.originalName
    })

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
  if (!pdfDoc.value || !pdfCanvas.value) return

  try {
    const page = await pdfDoc.value.getPage(pageNum)
    const viewport = page.getViewport({ scale: props.zoom / 100 })
    
    const canvas = pdfCanvas.value
    const context = canvas.getContext('2d')
    
    canvas.height = viewport.height
    canvas.width = viewport.width

    const renderContext = {
      canvasContext: context,
      viewport: viewport,
      // Отключаем текстовый слой для дополнительной защиты
      // (можно включить для поиска, но это упрощает копирование)
      textLayer: null,
    }

    await page.render(renderContext).promise
    currentPage.value = pageNum
  } catch (err) {
    console.error('[SecurePDFViewer] Error rendering page:', err)
    error.value = 'Ошибка отображения страницы'
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

