/**
 * PDF.js Service с виртуализацией и кэшированием
 */
import * as pdfjsLib from 'pdfjs-dist'
import { LRUCache } from '@/utils/performance'

// Vite-friendly worker URL: ensures the worker is emitted into /assets/ on build.
// pdfjs-dist v5 ships workers as .mjs.
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

// Кэш для загруженных PDF документов
// Keep smaller caches to reduce memory pressure on low-end devices / long sessions.
const documentCache = new LRUCache(6)
// Кэш для отрендеренных страниц (ImageData is heavy)
const pageCache = new LRUCache(20)
// Кэш для объектов страниц PDF
const pageObjectCache = new LRUCache(12)

// Настройка worker (prefer bundled worker; fallback to CDN)
if (typeof window !== 'undefined' && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
  try {
    pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl
  } catch (e) {
    const version = pdfjsLib.version || '5.4.296'
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${version}/build/pdf.worker.min.mjs`
  }
}

/**
 * Загружает PDF документ с кэшированием
 */
export const loadPdfDocument = async (url) => {
  // Проверяем кэш
  const cached = documentCache.get(url)
  if (cached) {
    return cached.value
  }
  
  try {
    const loadingTask = pdfjsLib.getDocument({
      url: url,
      withCredentials: false,
      isEvalSupported: false,
      verbosity: 0,
      // Оптимизация: загружаем только метаданные, страницы - по требованию
      disableRange: false,
      disableStream: false,
      disableAutoFetch: true, // Отключаем предзагрузку всех страниц
      // Используем меньший размер кэша для экономии памяти
      // ✅ Local CMaps to avoid CDN dependency (important for slow/unstable networks)
      cMapUrl: `/cmaps/`,
      cMapPacked: true
    })

    const pdf = await loadingTask.promise
    
    // Сохраняем в кэш
    documentCache.set(url, {
      value: pdf,
      timestamp: Date.now()
    })
    
    return pdf
  } catch (error) {
    console.error('Ошибка загрузки PDF:', error)
    throw error
  }
}

/**
 * Получает страницу PDF с кэшированием
 */
export const getPdfPage = async (pdf, pageNumber) => {
  const cacheKey = `${pdf.fingerprints[0]}_${pageNumber}`
  const cached = pageObjectCache.get(cacheKey)
  
  if (cached) {
    return cached.value
  }
  
  try {
    const page = await pdf.getPage(pageNumber)
    
    pageObjectCache.set(cacheKey, {
      value: page,
      timestamp: Date.now()
    })
    
    return page
  } catch (error) {
    console.error(`Ошибка загрузки страницы ${pageNumber}:`, error)
    throw error
  }
}

/**
 * Отрисовывает страницу PDF с кэшированием результата
 */
export const renderPdfPage = async (page, canvas, scale = 2.0) => {
  try {
    const context = canvas.getContext('2d', {
      alpha: false, // Отключаем альфа-канал для лучшей производительности
      willReadFrequently: false
    })
    
    const originalRotation = page.rotate || 0
    
    const viewport = page.getViewport({ 
      scale: scale, 
      rotation: 0,
      offsetX: 0,
      offsetY: 0
    })

    canvas.height = viewport.height
    canvas.width = viewport.width

    // ✅ IMPORTANT: cache key must be computed AFTER canvas is resized
    const cacheKey = `page_${page._pageIndex}_${scale}_${canvas.width}_${canvas.height}`
    const cached = pageCache.get(cacheKey)
    if (cached && cached.value?.imageData) {
      // Guard against size mismatch (can happen if canvas was resized differently)
      if (cached.value.width === canvas.width && cached.value.height === canvas.height) {
        context.putImageData(cached.value.imageData, 0, 0)
        return cached.value.metadata
      }
    }

    // Оптимизация: отрисовка с использованием OffscreenCanvas, если доступно
    const useOffscreen = typeof OffscreenCanvas !== 'undefined'
    const renderCanvas = useOffscreen ? new OffscreenCanvas(canvas.width, canvas.height) : canvas
    const renderContext = useOffscreen ? renderCanvas.getContext('2d', { alpha: false }) : context

    if (originalRotation !== 0) {
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2
      const rotationRad = (originalRotation * Math.PI) / 180
      
      renderContext.translate(centerX, centerY)
      renderContext.rotate(rotationRad)
      renderContext.translate(-centerX, -centerY)
      
      if (originalRotation === 90 || originalRotation === 270) {
        const rotatedViewport = page.getViewport({ scale: scale, rotation: originalRotation })
        canvas.width = rotatedViewport.width
        canvas.height = rotatedViewport.height
        renderCanvas.width = canvas.width
        renderCanvas.height = canvas.height
        renderContext.clearRect(0, 0, canvas.width, canvas.height)
        renderContext.setTransform(1, 0, 0, 1, 0, 0)
        renderContext.translate(canvas.width / 2, canvas.height / 2)
        renderContext.rotate(rotationRad)
        renderContext.translate(-canvas.width / 2, -canvas.height / 2)
      }
    }

    const renderTask = page.render({
      canvasContext: renderContext,
      viewport: viewport,
      // Оптимизация: указываем, что не нужно масштабировать изображения
      intent: 'display'
    })

    await renderTask.promise
    
    // Если использовали OffscreenCanvas, копируем результат
    if (useOffscreen) {
      context.drawImage(renderCanvas, 0, 0)
    }
    
    const metadata = {
      rotation: originalRotation,
      needsTransform: originalRotation !== 0
    }
    
    // Сохраняем в кэш только если размер разумный (не сохраняем огромные страницы)
    // ImageData can be huge and slow, especially on low-memory devices.
    if (canvas.width * canvas.height < 1400 * 1400) {
      try {
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height)
        pageCache.set(cacheKey, {
          value: {
            width: canvas.width,
            height: canvas.height,
            imageData,
            metadata
          },
          timestamp: Date.now()
        })
      } catch (e) {
        // Some browsers/devices may fail to allocate ImageData; skip caching.
      }
    }
    
    return metadata
  } catch (error) {
    console.error('Ошибка отрисовки страницы:', error)
    throw error
  }
}

/**
 * Вычисляет оптимальный масштаб
 */
export const calculateOptimalScale = (page, containerWidth = 1200) => {
  const originalRotation = page.rotate || 0
  const rotation = (originalRotation === 180 || originalRotation === 90 || originalRotation === 270)
    ? 0
    : originalRotation
  
  const viewport = page.getViewport({ scale: 1.0, rotation: rotation })
  const scale = containerWidth / viewport.width
  
  // Ограничиваем масштаб
  return Math.min(Math.max(scale, 0.5), 3.0)
}

/**
 * Предзагрузка соседних страниц (для более плавной прокрутки)
 */
export const preloadNearbyPages = async (pdf, currentPage, range = 2) => {
  const totalPages = pdf.numPages
  const pagesToPreload = []
  
  // Определяем диапазон страниц для предзагрузки
  for (let i = currentPage - range; i <= currentPage + range; i++) {
    if (i > 0 && i <= totalPages && i !== currentPage) {
      pagesToPreload.push(i)
    }
  }
  
  // Загружаем страницы асинхронно (не ждем завершения)
  Promise.all(
    pagesToPreload.map(pageNum => 
      getPdfPage(pdf, pageNum).catch(err => {
        console.warn(`Не удалось предзагрузить страницу ${pageNum}:`, err)
      })
    )
  )
}

/**
 * Виртуализированный рендеринг страниц
 * Возвращает только те страницы, которые видны в viewport
 */
export const getVisiblePages = (scrollTop, containerHeight, pageHeight, totalPages) => {
  const firstVisible = Math.floor(scrollTop / pageHeight)
  const lastVisible = Math.ceil((scrollTop + containerHeight) / pageHeight)
  
  // Добавляем buffer для более плавной прокрутки
  const buffer = 2
  const start = Math.max(0, firstVisible - buffer)
  const end = Math.min(totalPages, lastVisible + buffer)
  
  return {
    start,
    end,
    visible: Array.from({ length: end - start }, (_, i) => start + i + 1)
  }
}

/**
 * Очистка кэша (полезно для освобождения памяти)
 */
export const clearPdfCache = () => {
  documentCache.clear()
  pageCache.clear()
  pageObjectCache.clear()
}

/**
 * Получение статистики кэша
 */
export const getCacheStats = () => {
  return {
    documents: documentCache.size,
    pages: pageCache.size,
    pageObjects: pageObjectCache.size
  }
}

/**
 * Извлечение текста со страницы (для поиска)
 */
export const extractPageText = async (page) => {
  try {
    const textContent = await page.getTextContent()
    const text = textContent.items.map(item => item.str).join(' ')
    return text
  } catch (error) {
    console.error('Ошибка извлечения текста:', error)
    return ''
  }
}

/**
 * Batch рендеринг страниц (для оптимизации)
 */
export const batchRenderPages = async (pdf, pageNumbers, canvases, scale = 2.0) => {
  const renderPromises = pageNumbers.map(async (pageNum, index) => {
    try {
      const page = await getPdfPage(pdf, pageNum)
      const canvas = canvases[index]
      if (canvas) {
        return await renderPdfPage(page, canvas, scale)
      }
    } catch (error) {
      console.error(`Ошибка рендеринга страницы ${pageNum}:`, error)
      return null
    }
  })
  
  return await Promise.allSettled(renderPromises)
}

export default {
  loadPdfDocument,
  getPdfPage,
  renderPdfPage,
  calculateOptimalScale,
  preloadNearbyPages,
  getVisiblePages,
  clearPdfCache,
  getCacheStats,
  extractPageText,
  batchRenderPages
}

