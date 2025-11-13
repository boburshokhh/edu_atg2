/**
 * Оптимизированный MinIO сервис с кэшированием и мемоизацией
 */

import { S3Client, PutObjectCommand, ListObjectsV2Command, DeleteObjectCommand, HeadObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'
import { LRUCache } from '@/utils/performance'

// Конфигурация
const MINIO_ENDPOINT_RAW = import.meta.env.VITE_MINIO_ENDPOINT || 'https://minio.dmed.gubkin.uz'
const MINIO_ENDPOINT = MINIO_ENDPOINT_RAW.replace(/\/+$/, '')
const MINIO_ACCESS_KEY = import.meta.env.VITE_MINIO_ACCESS_KEY || 'admin'
const MINIO_SECRET_KEY = import.meta.env.VITE_MINIO_SECRET_KEY || '1234bobur$'
const MINIO_BUCKET = import.meta.env.VITE_MINIO_BUCKET || 'atgedu'
const isHttps = MINIO_ENDPOINT.startsWith('https://')

const MINIO_CONFIG = {
  endpoint: MINIO_ENDPOINT,
  region: 'us-east-1',
  credentials: {
    accessKeyId: MINIO_ACCESS_KEY,
    secretAccessKey: MINIO_SECRET_KEY
  },
  forcePathStyle: true,
  tls: isHttps
}

const DEFAULT_BUCKET = MINIO_BUCKET

// Создание S3 клиента
const s3Client = new S3Client(MINIO_CONFIG)

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
const getFrontendUrl = (url) => {
  if (typeof window === 'undefined') return url
  
  const isDev = import.meta.env.DEV
  if (isDev && url.includes(MINIO_ENDPOINT)) {
    return url.replace(MINIO_ENDPOINT, '/api/minio')
  }
  
  return url
}

// Проверка валидности кэшированных данных
const isCacheValid = (cachedItem, ttl) => {
  if (!cachedItem) return false
  return Date.now() - cachedItem.timestamp < ttl
}

// Получение presigned URL с кэшированием
export const getPresignedDownloadUrl = async (objectName, expiresIn = 7 * 24 * 60 * 60, contentType = null) => {
  const cacheKey = `${objectName}:${contentType || 'default'}`
  const cached = urlCache.get(cacheKey)
  
  // Проверяем кэш (учитываем, что URL должен быть действителен еще минимум 1 час)
  if (cached && isCacheValid(cached, URL_CACHE_TTL - 60 * 60 * 1000)) {
    return cached.value
  }
  
  try {
    const commandParams = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }
    
    if (contentType && (contentType.startsWith('video/') || contentType.startsWith('audio/'))) {
      commandParams.ResponseContentType = contentType
      commandParams.ResponseContentDisposition = `inline; filename="${objectName.split('/').pop()}"`
    }

    const command = new GetObjectCommand(commandParams)
    const url = await getSignedUrl(s3Client, command, { expiresIn })
    const frontendUrl = getFrontendUrl(url)
    
    // Сохраняем в кэш
    urlCache.set(cacheKey, {
      value: frontendUrl,
      timestamp: Date.now()
    })
    
    return frontendUrl
  } catch (error) {
    console.error('Ошибка создания presigned URL:', error)
    throw error
  }
}

// Получение метаданных файла с кэшированием
export const getFileMetadata = async (objectName) => {
  const cached = metadataCache.get(objectName)
  
  if (cached && isCacheValid(cached, METADATA_CACHE_TTL)) {
    return cached.value
  }
  
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }

    const command = new HeadObjectCommand(params)
    const response = await s3Client.send(command)

    const metadata = {
      size: response.ContentLength,
      lastModified: response.LastModified,
      contentType: response.ContentType,
      etag: response.ETag
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

    const fileBuffer = await file.arrayBuffer()

    const uploadParams = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName,
      Body: new Uint8Array(fileBuffer),
      ContentType: file.type || 'application/octet-stream',
      ContentDisposition: `attachment; filename="${originalName}"`
    }

    const command = new PutObjectCommand(uploadParams)
    await s3Client.send(command)

    const fileUrl = await getPresignedDownloadUrl(objectName, 7 * 24 * 60 * 60)

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
    console.error('Ошибка загрузки файла:', error)
    throw new Error(`Не удалось загрузить файл: ${error.message}`)
  }
}

// Получение списка файлов с кэшированием
export const listFiles = async (folder = '') => {
  const cacheKey = `list:${folder}`
  const cached = listCache.get(cacheKey)
  
  if (cached && isCacheValid(cached, LIST_CACHE_TTL)) {
    return cached.value
  }
  
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Prefix: folder ? `${folder}/` : ''
    }

    const command = new ListObjectsV2Command(params)
    const response = await s3Client.send(command)

    if (!response.Contents || response.Contents.length === 0) {
      return []
    }

    // Используем Promise.allSettled для обработки ошибок отдельных файлов
    const filesPromises = response.Contents.map(async (item) => {
      const fileName = item.Key.split('/').pop()
      const contentType = detectContentType(fileName)
      
      let fileUrl
      try {
        fileUrl = await getPresignedDownloadUrl(item.Key, 7 * 24 * 60 * 60, contentType)
      } catch (urlError) {
        const directUrl = `${MINIO_CONFIG.endpoint}/${DEFAULT_BUCKET}/${item.Key}`
        fileUrl = getFrontendUrl(directUrl)
      }

      return {
        objectName: item.Key,
        fileName,
        originalName: fileName.replace(/^\d+-/, ''),
        size: item.Size,
        sizeFormatted: formatFileSize(item.Size),
        type: contentType,
        url: fileUrl,
        file_url: fileUrl,
        file_size: item.Size,
        original_name: fileName.replace(/^\d+-/, ''),
        lastModified: item.LastModified,
        uploaded_at: item.LastModified
      }
    })

    const results = await Promise.allSettled(filesPromises)
    const files = results
      .filter(r => r.status === 'fulfilled')
      .map(r => r.value)
    
    // Сохраняем в кэш
    listCache.set(cacheKey, {
      value: files,
      timestamp: Date.now()
    })

    return files
  } catch (error) {
    console.error('Ошибка получения списка файлов:', error)
    throw new Error(`Не удалось получить список файлов: ${error.message}`)
  }
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
    const params = {
      Bucket: DEFAULT_BUCKET,
      Prefix: cleanPath ? `${cleanPath}/` : '',
      Delimiter: '/'
    }

    const command = new ListObjectsV2Command(params)
    const response = await s3Client.send(command)

    const contents = {
      folders: [],
      files: []
    }

    // Обрабатываем папки
    if (response.CommonPrefixes && response.CommonPrefixes.length > 0) {
      contents.folders = response.CommonPrefixes.map(prefix => {
        const folderName = prefix.Prefix.replace(cleanPath ? `${cleanPath}/` : '', '').replace(/\/$/, '')
        return {
          name: folderName,
          path: prefix.Prefix.replace(/\/$/, ''),
          isFolder: true
        }
      })
    }

    // Обрабатываем файлы
    if (response.Contents && response.Contents.length > 0) {
      const filePromises = response.Contents
        .filter(item => item.Key !== `${cleanPath}/` && item.Key !== `${cleanPath}`)
        .map(async (item) => {
          const fileName = item.Key.split('/').pop()
          const contentType = detectContentType(fileName)
          
          let fileUrl
          try {
            fileUrl = await getPresignedDownloadUrl(item.Key, 7 * 24 * 60 * 60, contentType)
          } catch (urlError) {
            const directUrl = `${MINIO_CONFIG.endpoint}/${DEFAULT_BUCKET}/${item.Key}`
            fileUrl = getFrontendUrl(directUrl)
          }

          return {
            objectName: item.Key,
            fileName,
            originalName: fileName.replace(/^\d+-/, ''),
            size: item.Size,
            sizeFormatted: formatFileSize(item.Size),
            type: contentType,
            url: fileUrl,
            file_url: fileUrl,
            file_size: item.Size,
            original_name: fileName.replace(/^\d+-/, ''),
            lastModified: item.LastModified,
            uploaded_at: item.LastModified
          }
        })
      
      const results = await Promise.allSettled(filePromises)
      contents.files = results
        .filter(r => r.status === 'fulfilled')
        .map(r => r.value)
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
    const params = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }

    const command = new DeleteObjectCommand(params)
    await s3Client.send(command)
    
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
  const url = `${MINIO_CONFIG.endpoint}/${DEFAULT_BUCKET}/${objectName}`
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
  const cacheKey = 'structure:root'
  const cached = listCache.get(cacheKey)
  
  if (cached && isCacheValid(cached, LIST_CACHE_TTL)) {
    return cached.value
  }
  
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Delimiter: '/'
    }

    const command = new ListObjectsV2Command(params)
    const response = await s3Client.send(command)

    const structure = {
      folders: [],
      files: []
    }

    if (response.CommonPrefixes && response.CommonPrefixes.length > 0) {
      structure.folders = response.CommonPrefixes.map(prefix => ({
        name: prefix.Prefix.replace(/\/$/, ''),
        path: prefix.Prefix,
        isFolder: true
      }))
    }

    if (response.Contents && response.Contents.length > 0) {
      structure.files = response.Contents
        .filter(item => !item.Key.includes('/'))
        .map(item => ({
          objectName: item.Key,
          fileName: item.Key,
          originalName: item.Key.replace(/^\d+-/, ''),
          size: item.Size,
          sizeFormatted: formatFileSize(item.Size),
          type: 'application/octet-stream',
          lastModified: item.LastModified
        }))
    }
    
    listCache.set(cacheKey, {
      value: structure,
      timestamp: Date.now()
    })

    return structure
  } catch (error) {
    console.error('Ошибка получения структуры папок:', error)
    throw new Error(`Не удалось получить структуру папок: ${error.message}`)
  }
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
  formatFileSize,
  clearCache,
  getCacheStats
}

