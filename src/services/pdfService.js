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
 * @returns {Promise<void>}
 */
export const renderPdfPage = async (page, canvas, scale = 2.0) => {
  try {
    const context = canvas.getContext('2d')
    
    // Явно устанавливаем rotation: 0, чтобы игнорировать любую ориентацию из метаданных PDF
    // Также используем offsetX: 0, offsetY: 0 для правильного позиционирования
    const viewport = page.getViewport({ 
      scale: scale, 
      rotation: 0,
      offsetX: 0,
      offsetY: 0
    })

    // Устанавливаем размеры canvas
    canvas.height = viewport.height
    canvas.width = viewport.width

    // Очищаем canvas перед отрисовкой (важно для правильного отображения)
    context.clearRect(0, 0, canvas.width, canvas.height)
    
    // Сбрасываем любые трансформации контекста
    context.setTransform(1, 0, 0, 1, 0, 0)

    // Отрисовываем страницу без дополнительных трансформаций
    const renderContext = {
      canvasContext: context,
      viewport: viewport
      // Не указываем transform, чтобы использовать стандартное поведение
    }

    await page.render(renderContext).promise
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
  // Используем rotation: 0 для правильного расчета размеров
  const viewport = page.getViewport({ scale: 1.0, rotation: 0 })
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

