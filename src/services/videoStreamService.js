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
 * @param {string} presignedUrl - Presigned URL от MinIO или относительный путь
 * @param {string} objectKey - MinIO object key (если известен)
 * @returns {string} Streaming URL
 */
export function convertToStreamUrl(presignedUrl, objectKey = null) {
  if (!presignedUrl || typeof presignedUrl !== 'string') {
    return ''
  }

  // Если уже streaming URL, возвращаем как есть
  if (presignedUrl.includes('/api/files/video/') || 
      presignedUrl.includes('/api/files/stream/') ||
      presignedUrl.includes('/api/files/hls/')) {
    return presignedUrl
  }

  // Если есть objectKey, используем его (приоритет)
  if (objectKey && typeof objectKey === 'string') {
    return getVideoStreamUrl(objectKey, false)
  }

  // Если это относительный путь (начинается с /), проверяем, не является ли он уже streaming URL
  if (presignedUrl.startsWith('/')) {
    // Если это уже наш streaming endpoint, возвращаем как есть
    if (presignedUrl.startsWith('/api/files/')) {
      return presignedUrl
    }
    // Если это относительный путь к файлу, пытаемся извлечь objectKey
    // Например: /videos/course/lesson1.mp4
    const cleanPath = presignedUrl.replace(/^\/+/, '')
    if (cleanPath) {
      return getVideoStreamUrl(cleanPath, false)
    }
  }

  // Пытаемся извлечь key из абсолютного presigned URL
  // Проверяем, является ли это абсолютным URL (начинается с http:// или https://)
  if (presignedUrl.startsWith('http://') || presignedUrl.startsWith('https://')) {
    try {
      const url = new URL(presignedUrl)
      const pathParts = url.pathname.split('/').filter(part => part.length > 0)
      
      // MinIO presigned URLs обычно имеют формат: /bucket/key или /api/minio/bucket/key
      // Ищем bucket и key
      if (pathParts.length >= 2) {
        // Пропускаем первый элемент (bucket или 'api' или 'minio')
        // Если путь содержит 'minio', пропускаем 'api' и 'minio'
        let startIndex = 0
        if (pathParts[0] === 'api' && pathParts[1] === 'minio') {
          startIndex = 3 // Пропускаем 'api', 'minio', и bucket
        } else if (pathParts[0] === 'minio') {
          startIndex = 2 // Пропускаем 'minio' и bucket
        } else {
          startIndex = 1 // Пропускаем только bucket
        }
        
        if (pathParts.length > startIndex) {
          const key = pathParts.slice(startIndex).join('/')
          if (key) {
            return getVideoStreamUrl(key, false)
          }
        }
      }
    } catch (e) {
      // Если не удалось распарсить как URL, это может быть просто objectKey
      // Попробуем использовать как objectKey напрямую
      const cleanKey = presignedUrl.replace(/^\/+/, '').replace(/^https?:\/\/[^\/]+\//, '')
      if (cleanKey && cleanKey !== presignedUrl) {
        return getVideoStreamUrl(cleanKey, false)
      }
    }
  } else {
    // Если это не абсолютный URL и не относительный путь, возможно это objectKey
    // Убираем ведущие слэши и используем как objectKey
    const cleanKey = presignedUrl.replace(/^\/+/, '')
    if (cleanKey) {
      return getVideoStreamUrl(cleanKey, false)
    }
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
    const url = source.url || source.file_url || ''
    const objectKey = source.objectKey || source.object_key || source.objectName || source.object_name || null
    const mimeType = source.mimeType || source.mime_type || source.type || null

    // Приоритет: objectKey > url
    // Если есть objectKey, используем его напрямую
    let streamUrl = ''
    if (objectKey && typeof objectKey === 'string') {
      streamUrl = getVideoStreamUrl(objectKey, requireAuth)
    } else if (url && typeof url === 'string') {
      // Если objectKey нет, но есть url, пытаемся конвертировать
      if (url.includes('/api/files/')) {
        // Уже streaming URL
        streamUrl = url
      } else {
        // Пытаемся конвертировать presigned URL или извлечь objectKey
        streamUrl = convertToStreamUrl(url, objectKey)
      }
    } else {
      // Нет ни objectKey, ни url
      console.warn('[videoStreamService] No valid source found in object:', source)
      return null
    }

    if (!streamUrl) {
      console.warn('[videoStreamService] Failed to create stream URL from:', source)
      return null
    }

    // Проверяем на HLS
    const checkUrl = objectKey || url || streamUrl
    if (isHlsUrl(checkUrl) || isHlsUrl(mimeType)) {
      return {
        type: 'video',
        title: source.title || source.originalName || source.original_name || '',
        sources: [{
          src: streamUrl,
          type: 'application/vnd.apple.mpegurl'
        }]
      }
    }

    return {
      type: 'video',
      title: source.title || source.originalName || source.original_name || '',
      sources: [{
        src: streamUrl,
        type: getVideoMimeType(streamUrl, mimeType)
      }]
    }
  }

  // Если это просто строка URL или objectKey
  if (typeof source === 'string') {
    // Проверяем, является ли это уже streaming URL
    if (source.includes('/api/files/')) {
      return {
        type: 'video',
        sources: [{
          src: source,
          type: getVideoMimeType(source)
        }]
      }
    }
    
    // Пытаемся конвертировать
    const streamUrl = convertToStreamUrl(source)
    
    if (!streamUrl) {
      console.warn('[videoStreamService] Failed to convert source to stream URL:', source)
      return null
    }
    
    return {
      type: 'video',
      sources: [{
        src: streamUrl,
        type: getVideoMimeType(streamUrl)
      }]
    }
  }

  console.warn('[videoStreamService] Invalid source type:', typeof source, source)
  return null
}

