// Сервис для работы с MinIO через AWS S3 SDK
// MinIO совместим с AWS S3 API

import { S3Client, PutObjectCommand, ListObjectsV2Command, DeleteObjectCommand, HeadObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// Конфигурация MinIO
// Поддержка переменных окружения для гибкости (продакшен/локально)
// Убираем завершающий слеш, если он есть
const MINIO_ENDPOINT_RAW = import.meta.env.VITE_MINIO_ENDPOINT || 'https://minio.dmed.gubkin.uz'
const MINIO_ENDPOINT = MINIO_ENDPOINT_RAW.replace(/\/+$/, '') // Убираем завершающие слеши
const MINIO_ACCESS_KEY = import.meta.env.VITE_MINIO_ACCESS_KEY || 'admin'
const MINIO_SECRET_KEY = import.meta.env.VITE_MINIO_SECRET_KEY || '1234bobur$'
const MINIO_BUCKET = import.meta.env.VITE_MINIO_BUCKET || 'atgedu'

// Определяем, используется ли HTTPS
const isHttps = MINIO_ENDPOINT.startsWith('https://')

const MINIO_CONFIG = {
  endpoint: MINIO_ENDPOINT,
  region: 'us-east-1',
  credentials: {
    accessKeyId: MINIO_ACCESS_KEY,
    secretAccessKey: MINIO_SECRET_KEY
  },
  forcePathStyle: true, // Важно для MinIO
  tls: isHttps // Автоматически определяется по протоколу endpoint
}

const DEFAULT_BUCKET = MINIO_BUCKET

// Создание S3 клиента для MinIO
const s3Client = new S3Client(MINIO_CONFIG)

// Форматирование размера файла
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// Загрузка файла
export const uploadFile = async (file, folder = '') => {
  try {
    // Генерируем уникальное имя файла
    const timestamp = Date.now()
    const originalName = file.name
    const fileName = `${timestamp}-${originalName.replace(/[^a-zA-Z0-9.-]/g, '_')}`
    const objectName = folder ? `${folder}/${fileName}` : fileName

    // Читаем файл как ArrayBuffer
    const fileBuffer = await file.arrayBuffer()

    // Параметры для загрузки
    const uploadParams = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName,
      Body: new Uint8Array(fileBuffer),
      ContentType: file.type || 'application/octet-stream',
      ContentDisposition: `attachment; filename="${originalName}"`
    }

    // Загружаем файл
    const command = new PutObjectCommand(uploadParams)
    await s3Client.send(command)

    // Генерируем presigned URL для просмотра (действителен 7 дней)
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

// Получение списка файлов
export const listFiles = async (folder = '') => {
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

    // Преобразуем список файлов в нужный формат
    const files = await Promise.all(
      response.Contents.map(async (item) => {
        // Генерируем presigned URL для просмотра (действителен 7 дней)
        let fileUrl
        try {
          fileUrl = await getPresignedDownloadUrl(item.Key, 7 * 24 * 60 * 60)
        } catch (urlError) {
          console.warn('Не удалось сгенерировать presigned URL для', item.Key)
          // Используем прямой URL и заменяем на прокси путь для фронтенда
          const directUrl = `${MINIO_CONFIG.endpoint}/${DEFAULT_BUCKET}/${item.Key}`
          fileUrl = getFrontendUrl(directUrl)
        }
        
        // Пытаемся получить metadata
        let contentType = 'application/octet-stream'
        try {
          const getCommand = new HeadObjectCommand({
            Bucket: DEFAULT_BUCKET,
            Key: item.Key
          })
          const metadata = await s3Client.send(getCommand)
          contentType = metadata.ContentType || contentType
        } catch (e) {
          console.warn('Не удалось получить метаданные для', item.Key)
        }

        return {
          objectName: item.Key,
          fileName: item.Key.split('/').pop(),
          originalName: item.Key.split('/').pop().replace(/^\d+-/, ''), // Убираем timestamp
          size: item.Size,
          sizeFormatted: formatFileSize(item.Size),
          type: contentType,
          url: fileUrl,
          file_url: fileUrl,
          file_size: item.Size,
          original_name: item.Key.split('/').pop().replace(/^\d+-/, ''),
          lastModified: item.LastModified,
          uploaded_at: item.LastModified
        }
      })
    )

    return files
  } catch (error) {
    console.error('Ошибка получения списка файлов:', error)
    throw new Error(`Не удалось получить список файлов: ${error.message}`)
  }
}

// Получение структуры папок (дерево папок)
export const getFolderStructure = async () => {
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Delimiter: '/' // Разделитель для папок
    }

    const command = new ListObjectsV2Command(params)
    const response = await s3Client.send(command)

    const structure = {
      folders: [],
      files: []
    }

    // Получаем папки (CommonPrefixes)
    if (response.CommonPrefixes && response.CommonPrefixes.length > 0) {
      structure.folders = response.CommonPrefixes.map(prefix => ({
        name: prefix.Prefix.replace(/\/$/, ''), // Убираем завершающий слеш
        path: prefix.Prefix,
        isFolder: true
      }))
    }

    // Получаем файлы в корне
    if (response.Contents && response.Contents.length > 0) {
      structure.files = response.Contents
        .filter(item => !item.Key.includes('/')) // Только корневые файлы
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

    return structure
  } catch (error) {
    console.error('Ошибка получения структуры папок:', error)
    throw new Error(`Не удалось получить структуру папок: ${error.message}`)
  }
}

// Получение содержимого конкретной папки
export const getFolderContents = async (folderPath = '') => {
  try {
    // Убираем завершающие слеши и очищаем путь
    let cleanPath = folderPath.replace(/\/$/, '').replace(/^\/+/, '')
    
    // Если путь пустой или содержит только слеши, сбрасываем в корень
    if (!cleanPath || cleanPath === '/') {
      cleanPath = ''
    }
    
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

    // Получаем подпапки
    if (response.CommonPrefixes && response.CommonPrefixes.length > 0) {
      contents.folders = response.CommonPrefixes.map(prefix => {
        const folderName = prefix.Prefix.replace(cleanPath ? `${cleanPath}/` : '', '').replace(/\/$/, '')
        return {
          name: folderName,
          path: prefix.Prefix.replace(/\/$/, ''), // Убираем завершающий слеш
          isFolder: true
        }
      })
    }

    // Получаем файлы в папке
    if (response.Contents && response.Contents.length > 0) {
      const files = await Promise.all(
        response.Contents
          .filter(item => item.Key !== `${cleanPath}/` && item.Key !== `${cleanPath}`)
          .map(async (item) => {
            let contentType = 'application/octet-stream'
            
            // Определяем ContentType по расширению файла, если не указан в метаданных
            const fileName = item.Key.split('/').pop().toLowerCase()
            if (fileName.endsWith('.mp4')) {
              contentType = 'video/mp4'
            } else if (fileName.endsWith('.webm')) {
              contentType = 'video/webm'
            } else if (fileName.endsWith('.ogg') || fileName.endsWith('.ogv')) {
              contentType = 'video/ogg'
            } else if (fileName.endsWith('.mov')) {
              contentType = 'video/quicktime'
            } else if (fileName.endsWith('.pdf')) {
              contentType = 'application/pdf'
            } else if (fileName.endsWith('.jpg') || fileName.endsWith('.jpeg')) {
              contentType = 'image/jpeg'
            } else if (fileName.endsWith('.png')) {
              contentType = 'image/png'
            }
            
            // Пытаемся получить метаданные из MinIO
            try {
              const getCommand = new HeadObjectCommand({
                Bucket: DEFAULT_BUCKET,
                Key: item.Key
              })
              const metadata = await s3Client.send(getCommand)
              contentType = metadata.ContentType || contentType
            } catch (e) {
              console.warn('Не удалось получить метаданные для', item.Key, 'используем определенный тип:', contentType)
            }

            let fileUrl
            try {
              // Используем правильный ContentType при генерации presigned URL
              fileUrl = await getPresignedDownloadUrl(item.Key, 7 * 24 * 60 * 60, contentType)
            } catch (urlError) {
              console.warn('Ошибка генерации presigned URL, используем прямую ссылку:', urlError)
              // Используем прямой URL и заменяем на прокси путь для фронтенда
              const directUrl = `${MINIO_CONFIG.endpoint}/${DEFAULT_BUCKET}/${item.Key}`
              fileUrl = getFrontendUrl(directUrl)
            }

            return {
              objectName: item.Key,
              fileName: item.Key.split('/').pop(),
              originalName: item.Key.split('/').pop().replace(/^\d+-/, ''),
              size: item.Size,
              sizeFormatted: formatFileSize(item.Size),
              type: contentType,
              url: fileUrl,
              file_url: fileUrl,
              file_size: item.Size,
              original_name: item.Key.split('/').pop().replace(/^\d+-/, ''),
              lastModified: item.LastModified,
              uploaded_at: item.LastModified
            }
          })
      )
      
      contents.files = files
    }

    return contents
  } catch (error) {
    console.error('Ошибка получения содержимого папки:', error)
    throw new Error(`Не удалось получить содержимое папки: ${error.message}`)
  }
}

// Удаление файла
export const deleteFile = async (objectName) => {
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }

    const command = new DeleteObjectCommand(params)
    await s3Client.send(command)

    return { success: true }
  } catch (error) {
    console.error('Ошибка удаления файла:', error)
    throw new Error(`Не удалось удалить файл: ${error.message}`)
  }
}

// Замена URL на фронтенде для использования прокси
// В dev режиме используем относительные пути через Vite proxy
// В production используем прямой endpoint
const getFrontendUrl = (url) => {
  if (typeof window === 'undefined') {
    return url // На сервере оставляем как есть
  }
  
  // Проверяем, находимся ли мы в dev режиме
  const isDev = import.meta.env.DEV
  
  // Если это dev режим и URL содержит наш MinIO endpoint, заменяем на прокси
  if (isDev && url.includes(MINIO_ENDPOINT)) {
    // Заменяем https://minio.dmed.gubkin.uz/atgedu/... на /api/minio/atgedu/...
    return url.replace(MINIO_ENDPOINT, '/api/minio')
  }
  
  // В production или если URL не содержит endpoint, возвращаем как есть
  return url
}

// Получение URL файла (синхронная версия - возвращает прямой URL)
export const getFileUrl = (objectName) => {
  // Формируем URL
  const url = `${MINIO_CONFIG.endpoint}/${DEFAULT_BUCKET}/${objectName}`
  // На фронтенде заменяем на прокси путь
  return getFrontendUrl(url)
}

// Получение безопасного URL файла (асинхронная версия - возвращает presigned URL)
export const getSecureFileUrl = async (objectName, expiresIn = 3600) => {
  try {
    return await getPresignedDownloadUrl(objectName, expiresIn)
  } catch (error) {
    console.error('Ошибка получения secure URL:', error)
    return getFileUrl(objectName) // Fallback к прямому URL
  }
}

// Проверка существования файла
export const fileExists = async (objectName) => {
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }

    const command = new HeadObjectCommand(params)
    await s3Client.send(command)
    return true
  } catch (error) {
    return false
  }
}

// Получение метаданных файла
export const getFileMetadata = async (objectName) => {
  try {
    const params = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }

    const command = new HeadObjectCommand(params)
    const response = await s3Client.send(command)

    return {
      size: response.ContentLength,
      lastModified: response.LastModified,
      contentType: response.ContentType,
      etag: response.ETag
    }
  } catch (error) {
    console.error('Ошибка получения метаданных:', error)
    throw error
  }
}

// Получение presigned URL для безопасного скачивания/стриминга
export const getPresignedDownloadUrl = async (objectName, expiresIn = 3600, contentType = null) => {
  try {
    const commandParams = {
      Bucket: DEFAULT_BUCKET,
      Key: objectName
    }
    
    // Для видео и аудио настраиваем правильные заголовки для стриминга
    if (contentType && (contentType.startsWith('video/') || contentType.startsWith('audio/'))) {
      commandParams.ResponseContentType = contentType
      // inline = воспроизведение в браузере (не скачивание)
      commandParams.ResponseContentDisposition = `inline; filename="${objectName.split('/').pop()}"`
      // Важно: НЕ добавляем Range в presigned URL, так как Range устанавливается в заголовках запроса
      // Браузер автоматически будет использовать Range requests для стриминга
    }

    const command = new GetObjectCommand(commandParams)
    const url = await getSignedUrl(s3Client, command, { expiresIn })
    
    // На фронтенде заменяем на прокси путь для избежания CORS
    return getFrontendUrl(url)
  } catch (error) {
    console.error('Ошибка создания presigned URL:', error)
    throw error
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
  formatFileSize
}
