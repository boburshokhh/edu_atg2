/**
 * Оптимизированный MinIO сервис с кэшированием и мемоизацией
 */

import { LRUCache } from '@/utils/performance'

// Конфигурация
// IMPORTANT:
// - Browser works with MinIO ONLY through frontend proxy (/api/minio) to avoid CORS
//   and to keep Host header stable for presigned URLs.
// - Backend talks to MinIO by container name: http://minio:9000
const MINIO_ENDPOINT_RAW =
  import.meta.env.VITE_MINIO_ENDPOINT ||
  'http://192.168.32.100:9000'
const MINIO_ENDPOINT = MINIO_ENDPOINT_RAW.replace(/\/+$/, '')
const MINIO_BUCKET = import.meta.env.VITE_MINIO_BUCKET || 'atgedu'
const DEFAULT_BUCKET = MINIO_BUCKET

// Unified API base - always use /api (frontend nginx proxies to backend)
const API_BASE_URL = '/api'

const encodeKeyPath = (key) => {
  const clean = (key || '').replace(/^\/+/, '')
  return clean
    .split('/')
    .map(seg => encodeURIComponent(seg))
    .join('/')
}

function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  if (typeof token === 'string' && token.trim()) {
    return `Bearer ${token.trim()}`
  }
  return null
}

async function apiRequest(url, options = {}) {
  const token = getAuthToken()
  const headers = {
    ...(options.headers || {}),
  }
  if (token) {
    headers.Authorization = token
    console.log('[apiRequest] Using auth token:', token.substring(0, 20) + '...')
  } else {
    console.warn('[apiRequest] No auth token found')
  }

  const fullUrl = `${API_BASE_URL}${url}`
  console.log('[apiRequest] Request:', options.method || 'GET', fullUrl)

  const res = await fetch(fullUrl, {
    ...options,
    headers,
  })

  const contentType = res.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const payload = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null)

  if (!res.ok) {
    console.error('[apiRequest] Error response:', res.status, res.statusText, payload)
    const msg =
      (payload && (payload.error || payload.message || payload.detail)) ||
      `HTTP ${res.status}: ${res.statusText}`
    throw new Error(msg)
  }

  return payload
}

// Кэши для разных типов данных
const urlCache = new LRUCache(100) // Кэш для presigned URLs
const metadataCache = new LRUCache(200) // Кэш для метаданных файлов
const listCache = new LRUCache(50) // Кэш для списков файлов

// TTL для кэшей (в миллисекундах)
const URL_CACHE_TTL = 6 * 60 * 60 * 1000 // 6 часов (presigned URLs живут 7 дней)
const METADATA_CACHE_TTL = 10 * 60 * 1000 // 10 минут
const LIST_CACHE_TTL = 5 * 60 * 1000 // 5 минут

// Форматирование размера файла (мемоизированная версия)
const sizeCache = new Map()
export const formatFileSize = (bytes) => {
  if (sizeCache.has(bytes)) {
    return sizeCache.get(bytes)
  }
  
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  const result = Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  
  sizeCache.set(bytes, result)
  return result
}

// Получение URL с кэшированием
// Простая замена MinIO endpoint на /api/minio, сохраняя весь путь и query параметры
// IMPORTANT: Presigned URLs are signed with hostname, so we must preserve the signature
// by using /api/minio/ proxy which sets Host header correctly (minio:9000)
const getFrontendUrl = (url) => {
  if (typeof window === 'undefined') return url
  if (!url || typeof url !== 'string') return url
  
  // Простая замена: заменяем MinIO endpoint на /api/minio
  // Presigned URL от MinIO уже содержит bucket в пути (например: http://minio:9000/atgedu/stations/WKC1.jpg)
  // Мы просто заменяем origin на /api/minio, сохраняя путь и query параметры (включая подпись)
  if (url.includes(MINIO_ENDPOINT)) {
    return url.replace(MINIO_ENDPOINT, '/api/minio')
  }
  
  // Если URL содержит minio:9000 или другой MinIO endpoint
  try {
    const urlObj = new URL(url)
    // Проверяем порт 9000 или hostname содержит "minio"
    if (urlObj.port === '9000' || urlObj.hostname.includes('minio')) {
      // Сохраняем путь и query параметры (включая подпись presigned URL)
      return `/api/minio${urlObj.pathname}${urlObj.search}`
    }
  } catch (e) {
    // Игнорируем ошибки парсинга
    console.warn('[getFrontendUrl] Failed to parse URL:', url, e)
  }
  
  return url
}

// Проверка валидности кэшированных данных
const isCacheValid = (cachedItem, ttl) => {
  if (!cachedItem) return false
  return Date.now() - cachedItem.timestamp < ttl
}

// ✅ Получение presigned URL с кэшированием и поддержкой Range requests
export const getPresignedDownloadUrl = async (
  objectName, 
  expiresIn = 7 * 24 * 60 * 60, 
  contentType = null,
  range = null  // ✅ Новый параметр для Range requests
) => {
  // Normalize object key: remove leading slashes to avoid "//tex_kart/..."
  const normalizedObjectName = (objectName || '').replace(/^\/+/, '')

  const cacheKey = `${normalizedObjectName}:${contentType || 'default'}:${range || 'full'}`
  const cached = urlCache.get(cacheKey)
  
  // Проверяем кэш (учитываем, что URL должен быть действителен еще минимум 1 час)
  if (cached && isCacheValid(cached, URL_CACHE_TTL - 60 * 60 * 1000)) {
    return cached.value
  }
  
  try {
    const q = new URLSearchParams()
    q.set('key', normalizedObjectName)
    q.set('expiresIn', String(expiresIn))
    if (contentType) q.set('contentType', contentType)

    const data = await apiRequest(`/files/presign?${q.toString()}`)
    const url = data?.url
    if (!url) {
      console.warn(`[MinIO] Invalid presign response for ${normalizedObjectName}, returning fallback`)
      // Return fallback URL instead of throwing
      return getFileUrl(normalizedObjectName)
    }

    console.log(`[MinIO] Got presigned URL from backend: ${url.substring(0, 150)}...`)
    const frontendUrl = getFrontendUrl(url)
    console.log(`[MinIO] Converted to frontend URL: ${frontendUrl.substring(0, 150)}...`)
    
    // Сохраняем в кэш
    urlCache.set(cacheKey, {
      value: frontendUrl,
      timestamp: Date.now()
    })
    
    return frontendUrl
  } catch (error) {
    console.warn(`[MinIO] Error creating presigned URL for ${normalizedObjectName}:`, error.message || error)
    // Return fallback URL instead of throwing to prevent breaking the UI
    return getFileUrl(normalizedObjectName)
  }
}

// ✅ Новая функция для получения URL с Range (для явного указания диапазона байтов)
export const getPresignedUrlWithRange = async (
  objectName,
  startByte = 0,
  endByte = null,
  contentType = null
) => {
  // Примечание: Range указывается в HTTP заголовке запроса, а не в presigned URL
  // Но мы можем вернуть URL с информацией о Range для использования в fetch
  const url = await getPresignedDownloadUrl(
    objectName,
    7 * 24 * 60 * 60,
    contentType
  )
  
  // Range будет добавлен в заголовки при запросе
  return { url, range: endByte !== null ? `bytes=${startByte}-${endByte}` : `bytes=${startByte}-` }
}

// Получение метаданных файла с кэшированием
export const getFileMetadata = async (objectName) => {
  const cached = metadataCache.get(objectName)
  
  if (cached && isCacheValid(cached, METADATA_CACHE_TTL)) {
    return cached.value
  }
  
  try {
    const key = (objectName || '').replace(/^\/+/, '')
    const data = await apiRequest(`/files/exists?key=${encodeURIComponent(key)}`)
    if (!data?.exists) throw new Error('Not found')

    const metadata = {
      size: data.size,
      lastModified: data.lastModified,
      contentType: data.contentType,
      etag: data.etag
    }
    
    // Сохраняем в кэш
    metadataCache.set(objectName, {
      value: metadata,
      timestamp: Date.now()
    })
    
    return metadata
  } catch (error) {
    console.error('Ошибка получения метаданных:', error)
    throw error
  }
}

// Определение ContentType по расширению
const detectContentType = (fileName) => {
  const name = fileName.toLowerCase()
  
  const typeMap = {
    'mp4': 'video/mp4',
    'webm': 'video/webm',
    'ogg': 'video/ogg',
    'ogv': 'video/ogg',
    'mov': 'video/quicktime',
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'svg': 'image/svg+xml'
  }
  
  const ext = name.split('.').pop()
  return typeMap[ext] || 'application/octet-stream'
}

// Загрузка файла
export const uploadFile = async (file, folder = '') => {
  try {
    const timestamp = Date.now()
    const originalName = file.name
    const fileName = `${timestamp}-${originalName.replace(/[^a-zA-Z0-9.-]/g, '_')}`
    const objectName = folder ? `${folder}/${fileName}` : fileName

    console.log('[uploadFile] Requesting presigned PUT for:', objectName)
    
    // 1) Ask backend for presigned PUT
    const presign = await apiRequest('/files/presign-upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        key: objectName,
        contentType: file.type || 'application/octet-stream',
        expiresIn: 900
      }),
    })
    const putUrl = presign?.url
    if (!putUrl) {
      console.error('[uploadFile] Invalid presign response:', presign)
      throw new Error('Invalid presign-upload response')
    }

    console.log('[uploadFile] Got presigned URL, uploading...')

    // 2) Upload to MinIO via Vite proxy (keeps same-origin and preserves signature via proxy host)
    const uploadUrl = getFrontendUrl(putUrl)
    console.log('[uploadFile] Upload URL:', uploadUrl)
    
    const putRes = await fetch(uploadUrl, {
      method: 'PUT',
      headers: { 'Content-Type': file.type || 'application/octet-stream' },
      body: file
    })
    
    if (!putRes.ok) {
      const errorText = await putRes.text().catch(() => '')
      console.error('[uploadFile] Upload failed:', putRes.status, putRes.statusText, errorText)
      throw new Error(`Upload failed: HTTP ${putRes.status} ${putRes.statusText}`)
    }

    console.log('[uploadFile] Upload successful, getting download URL...')
    const fileUrl = await getPresignedDownloadUrl(objectName, 7 * 24 * 60 * 60, file.type || null)

    return {
      success: true,
      url: fileUrl,
      objectName,
      fileName,
      originalName,
      size: file.size,
      type: file.type || 'application/octet-stream',
      sizeFormatted: formatFileSize(file.size)
    }
  } catch (error) {
    console.error('[uploadFile] Error:', error)
    throw new Error(`Не удалось загрузить файл: ${error.message}`)
  }
}

// Получение списка файлов с кэшированием
export const listFiles = async (folder = '') => {
  const contents = await getFolderContents(folder)
  return contents.files || []
}

// Получение содержимого папки с кэшированием
export const getFolderContents = async (folderPath = '') => {
  let cleanPath = folderPath.replace(/\/$/, '').replace(/^\/+/, '')
  if (!cleanPath || cleanPath === '/') cleanPath = ''
  
  const cacheKey = `folder:${cleanPath}`
  const cached = listCache.get(cacheKey)
  
  if (cached && isCacheValid(cached, LIST_CACHE_TTL)) {
    return cached.value
  }
  
  try {
    const q = new URLSearchParams()
    if (cleanPath) q.set('prefix', cleanPath)
    const data = await apiRequest(`/files/folder-contents?${q.toString()}`)

    const contents = {
      folders: (data?.folders || []).map((f) => ({
        ...f,
      })),
      files: (data?.files || []).map((file) => {
        const url = file.url || file.file_url
        return {
          ...file,
          url: url ? getFrontendUrl(url) : url,
          file_url: url ? getFrontendUrl(url) : url,
        }
      }),
    }
    
    // Сохраняем в кэш
    listCache.set(cacheKey, {
      value: contents,
      timestamp: Date.now()
    })

    return contents
  } catch (error) {
    console.error('Ошибка получения содержимого папки:', error)
    throw new Error(`Не удалось получить содержимое папки: ${error.message}`)
  }
}

// Удаление файла (инвалидация кэша)
export const deleteFile = async (objectName) => {
  try {
    const key = (objectName || '').replace(/^\/+/, '')
    await apiRequest(`/files/object?key=${encodeURIComponent(key)}`, {
      method: 'DELETE'
    })
    
    // Очищаем связанные кэши
    urlCache.clear()
    metadataCache.delete(objectName)
    listCache.clear()

    return { success: true }
  } catch (error) {
    console.error('Ошибка удаления файла:', error)
    throw new Error(`Не удалось удалить файл: ${error.message}`)
  }
}

// Получение URL файла (синхронная версия)
export const getFileUrl = (objectName) => {
  const url = `${MINIO_ENDPOINT}/${DEFAULT_BUCKET}/${objectName}`
  return getFrontendUrl(url)
}

// Получение безопасного URL
export const getSecureFileUrl = async (objectName, expiresIn = 3600) => {
  try {
    return await getPresignedDownloadUrl(objectName, expiresIn)
  } catch (error) {
    console.error('Ошибка получения secure URL:', error)
    return getFileUrl(objectName)
  }
}

// Проверка существования файла
export const fileExists = async (objectName) => {
  try {
    await getFileMetadata(objectName)
    return true
  } catch (error) {
    return false
  }
}

// Получение структуры папок
export const getFolderStructure = async () => {
  const contents = await getFolderContents('')
  return { folders: contents.folders || [], files: contents.files || [] }
}

// Очистка кэша (полезно для отладки)
export const clearCache = () => {
  urlCache.clear()
  metadataCache.clear()
  listCache.clear()
  sizeCache.clear()
}

// Получение статистики кэша
export const getCacheStats = () => {
  return {
    urlCache: urlCache.size,
    metadataCache: metadataCache.size,
    listCache: listCache.size,
    sizeCache: sizeCache.size
  }
}

// Алиас для обратной совместимости
export const getPresignedUrl = getPresignedDownloadUrl

export default {
  uploadFile,
  getFileUrl,
  getSecureFileUrl,
  listFiles,
  getFolderStructure,
  getFolderContents,
  deleteFile,
  fileExists,
  getFileMetadata,
  getPresignedUrl,
  getPresignedDownloadUrl,
  getPresignedUrlWithRange,  // ✅ Новая функция для Range requests
  formatFileSize,
  clearCache,
  getCacheStats
}

