/**
 * PDF.js Service
 * Сервис для работы с PDF.js библиотекой
 */
import * as pdfjsLib from 'pdfjs-dist'

// Настройка worker для PDF.js
// В версии 5.x worker файлы имеют расширение .mjs
if (typeof window !== 'undefined' && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
  const version = pdfjsLib.version || '5.4.296'
  
  // Используем unpkg CDN с правильным расширением .mjs
  // unpkg обычно более надежен чем jsdelivr для последних версий
  pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${version}/build/pdf.worker.min.mjs`
  
  // Проверяем доступность worker при первой загрузке
  if (import.meta.env.DEV) {
    console.log(`PDF.js worker: ${pdfjsLib.GlobalWorkerOptions.workerSrc}`)
  }
}

/**
 * Загружает PDF документ из URL
 * @param {string} url - URL PDF файла
 * @returns {Promise<Object>} PDF документ
 */
export const loadPdfDocument = async (url) => {
  try {
    const loadingTask = pdfjsLib.getDocument({
      url: url,
      withCredentials: false,
      isEvalSupported: false,
      verbosity: 0
    })

    const pdf = await loadingTask.promise
    return pdf
  } catch (error) {
    console.error('Ошибка загрузки PDF:', error)
    throw error
  }
}

/**
 * Получает страницу PDF документа
 * @param {Object} pdf - PDF документ
 * @param {number} pageNumber - Номер страницы (начиная с 1)
 * @returns {Promise<Object>} Объект страницы PDF
 */
export const getPdfPage = async (pdf, pageNumber) => {
  try {
    const page = await pdf.getPage(pageNumber)
    return page
  } catch (error) {
    console.error(`Ошибка загрузки страницы ${pageNumber}:`, error)
    throw error
  }
}

/**
 * Отрисовывает страницу PDF на canvas
 * @param {Object} page - Объект страницы PDF
 * @param {HTMLCanvasElement} canvas - Canvas элемент для отрисовки
 * @param {number} scale - Масштаб отрисовки (по умолчанию 2.0)
 * @returns {Promise<{rotation: number, needsTransform: boolean}>} Информация о повороте
 */
export const renderPdfPage = async (page, canvas, scale = 2.0) => {
  try {
    const context = canvas.getContext('2d')
    
    // Получаем оригинальную ориентацию страницы
    const originalRotation = page.rotate || 0
    
    // Всегда используем rotation: 0 в viewport, но сохраняем информацию о повороте
    // для применения CSS transform
    const viewport = page.getViewport({ 
      scale: scale, 
      rotation: 0, // Всегда 0 для правильных размеров canvas
      offsetX: 0,
      offsetY: 0
    })

    // Устанавливаем размеры canvas на основе viewport без поворота
    canvas.height = viewport.height
    canvas.width = viewport.width

    // Очищаем canvas перед отрисовкой
    context.clearRect(0, 0, canvas.width, canvas.height)
    
    // Сбрасываем любые трансформации контекста
    context.setTransform(1, 0, 0, 1, 0, 0)

    // Если страница повернута, применяем трансформацию через canvas context
    if (originalRotation !== 0) {
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2
      
      // Перемещаем в центр
      context.translate(centerX, centerY)
      
      // Поворачиваем на нужный угол (в радианах)
      const rotationRad = (originalRotation * Math.PI) / 180
      context.rotate(rotationRad)
      
      // Возвращаем обратно
      context.translate(-centerX, -centerY)
      
      // Если поворот 90 или 270, нужно поменять местами ширину и высоту viewport
      if (originalRotation === 90 || originalRotation === 270) {
        // Используем viewport с поворотом для правильных размеров
        const rotatedViewport = page.getViewport({ scale: scale, rotation: originalRotation })
        canvas.width = rotatedViewport.width
        canvas.height = rotatedViewport.height
        context.clearRect(0, 0, canvas.width, canvas.height)
        context.setTransform(1, 0, 0, 1, 0, 0)
        context.translate(canvas.width / 2, canvas.height / 2)
        context.rotate(rotationRad)
        context.translate(-canvas.width / 2, -canvas.height / 2)
      }
    }

    // Отрисовываем страницу
    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }

    await page.render(renderContext).promise
    
    return {
      rotation: originalRotation,
      needsTransform: originalRotation !== 0
    }
  } catch (error) {
    console.error('Ошибка отрисовки страницы:', error)
    throw error
  }
}

/**
 * Вычисляет оптимальный масштаб для canvas на основе ширины контейнера
 * @param {Object} page - Объект страницы PDF
 * @param {number} containerWidth - Ширина контейнера в пикселях
 * @returns {number} Оптимальный масштаб
 */
export const calculateOptimalScale = (page, containerWidth = 1200) => {
  // Автоопределение и исправление ориентации для правильного расчета размеров
  const originalRotation = page.rotate || 0
  const rotation = (originalRotation === 180 || originalRotation === 90 || originalRotation === 270)
    ? 0
    : originalRotation
  
  // Используем исправленную rotation для правильного расчета размеров
  const viewport = page.getViewport({ scale: 1.0, rotation: rotation })
  const scale = containerWidth / viewport.width
  // Ограничиваем масштаб для производительности
  return Math.min(Math.max(scale, 1.0), 3.0)
}

export default {
  loadPdfDocument,
  getPdfPage,
  renderPdfPage,
  calculateOptimalScale
}

