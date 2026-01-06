/**
 * Video Streaming Service
 * Сервис для работы с видео через streaming API с поддержкой Range Requests
 */

const API_BASE_URL = '/api'

/**
 * Получить streaming URL для видео
 * Использует новый streaming endpoint с поддержкой range requests
 * 
 * @param {string} objectKey - MinIO object key
 * @param {boolean} requireAuth - Требуется ли аутентификация (default: false для публичного видео)
 * @returns {string} Streaming URL
 */
export function getVideoStreamUrl(objectKey, requireAuth = false) {
  if (!objectKey) {
    return ''
  }

  // Убираем ведущие слэши
  const cleanKey = objectKey.replace(/^\/+/, '')
  
  // Кодируем ключ для URL (важно для специальных символов)
  const encodedKey = encodeURIComponent(cleanKey).replace(/%2F/g, '/')
  
  // Используем публичный endpoint для видео (без аутентификации)
  // или защищенный endpoint для приватного контента
  const endpoint = requireAuth ? 'stream' : 'video'
  
  return `${API_BASE_URL}/files/${endpoint}/${encodedKey}`
}

/**
 * Получить HLS streaming URL
 * 
 * @param {string} objectKey - MinIO object key (обычно .m3u8 файл)
 * @returns {string} HLS streaming URL
 */
export function getHlsStreamUrl(objectKey) {
  if (!objectKey) {
    return ''
  }

  const cleanKey = objectKey.replace(/^\/+/, '')
  const encodedKey = encodeURIComponent(cleanKey).replace(/%2F/g, '/')
  
  return `${API_BASE_URL}/files/hls/${encodedKey}`
}

/**
 * Проверить, является ли URL HLS плейлистом
 * 
 * @param {string} url - URL для проверки
 * @returns {boolean}
 */
export function isHlsUrl(url) {
  return url && (url.includes('.m3u8') || url.includes('application/vnd.apple.mpegurl'))
}

/**
 * Получить тип видео по URL или расширению
 * 
 * @param {string} url - URL видео
 * @param {string} mimeType - MIME type (опционально)
 * @returns {string} MIME type
 */
export function getVideoMimeType(url, mimeType = null) {
  if (mimeType && mimeType.startsWith('video/')) {
    return mimeType
  }

  if (!url) {
    return 'video/mp4'
  }

  const urlLower = url.toLowerCase()
  
  if (urlLower.includes('.webm')) {
    return 'video/webm'
  } else if (urlLower.includes('.ogg') || urlLower.includes('.ogv')) {
    return 'video/ogg'
  } else if (urlLower.includes('.mov')) {
    return 'video/quicktime'
  } else if (urlLower.includes('.m3u8')) {
    return 'application/vnd.apple.mpegurl'
  } else {
    return 'video/mp4' // Default
  }
}

/**
 * Конвертировать старый presigned URL в streaming URL
 * 
 * @param {string} presignedUrl - Presigned URL от MinIO
 * @param {string} objectKey - MinIO object key (если известен)
 * @returns {string} Streaming URL
 */
export function convertToStreamUrl(presignedUrl, objectKey = null) {
  if (!presignedUrl) {
    return ''
  }

  // Если уже streaming URL, возвращаем как есть
  if (presignedUrl.includes('/api/files/video/') || 
      presignedUrl.includes('/api/files/stream/') ||
      presignedUrl.includes('/api/files/hls/')) {
    return presignedUrl
  }

  // Если есть objectKey, используем его
  if (objectKey) {
    return getVideoStreamUrl(objectKey, false)
  }

  // Пытаемся извлечь key из presigned URL
  try {
    const url = new URL(presignedUrl)
    const pathParts = url.pathname.split('/')
    // MinIO presigned URLs обычно имеют формат: /bucket/key
    // Пропускаем bucket и берем остальное
    if (pathParts.length > 2) {
      const key = pathParts.slice(2).join('/')
      return getVideoStreamUrl(key, false)
    }
  } catch (e) {
    console.warn('[videoStreamService] Failed to parse presigned URL:', e)
  }

  // Fallback: возвращаем оригинальный URL
  return presignedUrl
}

/**
 * Создать источник видео для Plyr
 * 
 * @param {string|Object} source - URL или объект с информацией о видео
 * @param {boolean} requireAuth - Требуется ли аутентификация
 * @returns {Object} Plyr source object
 */
export function createVideoSource(source, requireAuth = false) {
  if (!source) {
    return null
  }

  // Если это уже объект с url
  if (typeof source === 'object') {
    const url = source.url || source.file_url || source.objectKey || ''
    const objectKey = source.objectKey || source.object_key || null
    const mimeType = source.mimeType || source.mime_type || source.type || null

    // Конвертируем в streaming URL
    let streamUrl = url
    if (objectKey) {
      streamUrl = getVideoStreamUrl(objectKey, requireAuth)
    } else if (url && !url.includes('/api/files/')) {
      streamUrl = convertToStreamUrl(url, objectKey)
    }

    // Проверяем на HLS
    if (isHlsUrl(url) || isHlsUrl(mimeType)) {
      return {
        type: 'video',
        title: source.title || source.originalName || '',
        sources: [{
          src: streamUrl,
          type: 'application/vnd.apple.mpegurl'
        }]
      }
    }

    return {
      type: 'video',
      title: source.title || source.originalName || '',
      sources: [{
        src: streamUrl,
        type: getVideoMimeType(streamUrl, mimeType)
      }]
    }
  }

  // Если это просто строка URL
  if (typeof source === 'string') {
    const streamUrl = convertToStreamUrl(source)
    
    return {
      type: 'video',
      sources: [{
        src: streamUrl,
        type: getVideoMimeType(streamUrl)
      }]
    }
  }

  return null
}

