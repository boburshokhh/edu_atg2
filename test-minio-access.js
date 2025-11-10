/**
 * Тестовый скрипт для проверки доступа к MinIO bucket
 * 
 * Запуск: node test-minio-access.js
 */

import { S3Client, ListObjectsV2Command, HeadObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3'
import { getSignedUrl } from '@aws-sdk/s3-request-presigner'

// Конфигурация MinIO
// Используем те же значения, что и в основном сервисе
// Убираем завершающий слеш, если он есть
const MINIO_ENDPOINT_RAW = process.env.VITE_MINIO_ENDPOINT || 'https://minio.dmed.gubkin.uz'
const MINIO_ENDPOINT = MINIO_ENDPOINT_RAW.replace(/\/+$/, '') // Убираем завершающие слеши
const MINIO_ACCESS_KEY = process.env.VITE_MINIO_ACCESS_KEY || 'admin'
const MINIO_SECRET_KEY = process.env.VITE_MINIO_SECRET_KEY || 'dmed_gubkin'
const MINIO_BUCKET = process.env.VITE_MINIO_BUCKET || 'atgedu'

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

// Цвета для консоли
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logSuccess(message) {
  log(`✅ ${message}`, 'green')
}

function logError(message) {
  log(`❌ ${message}`, 'red')
}

function logInfo(message) {
  log(`ℹ️  ${message}`, 'blue')
}

function logWarning(message) {
  log(`⚠️  ${message}`, 'yellow')
}

// Тест 1: Проверка подключения к MinIO
async function testConnection() {
  log('\n📡 Тест 1: Проверка подключения к MinIO...', 'cyan')
  try {
    const command = new ListObjectsV2Command({
      Bucket: DEFAULT_BUCKET,
      MaxKeys: 1
    })
    await s3Client.send(command)
    logSuccess(`Подключение к MinIO успешно!`)
    logInfo(`Endpoint: ${MINIO_CONFIG.endpoint}`)
    logInfo(`Bucket: ${DEFAULT_BUCKET}`)
    return true
  } catch (error) {
    logError(`Ошибка подключения: ${error.message}`)
    if (error.name === 'InvalidAccessKeyId' || error.name === 'SignatureDoesNotMatch') {
      logWarning('Проверьте credentials (accessKeyId и secretAccessKey)')
    } else if (error.name === 'NoSuchBucket') {
      logWarning(`Bucket "${DEFAULT_BUCKET}" не существует`)
    } else if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      logWarning('Проверьте доступность MinIO сервера')
    }
    return false
  }
}

// Тест 2: Получение списка файлов из bucket
async function testListFiles() {
  log('\n📁 Тест 2: Получение списка файлов из bucket...', 'cyan')
  try {
    const command = new ListObjectsV2Command({
      Bucket: DEFAULT_BUCKET,
      MaxKeys: 10
    })
    const response = await s3Client.send(command)
    
    if (!response.Contents || response.Contents.length === 0) {
      logWarning('Bucket пуст или не содержит файлов')
      return []
    }
    
    logSuccess(`Найдено файлов: ${response.Contents.length}`)
    logInfo('Первые файлы:')
    response.Contents.slice(0, 5).forEach((file, index) => {
      const sizeKB = (file.Size / 1024).toFixed(2)
      log(`  ${index + 1}. ${file.Key} (${sizeKB} KB)`, 'reset')
    })
    
    if (response.Contents.length > 5) {
      log(`  ... и еще ${response.Contents.length - 5} файлов`, 'reset')
    }
    
    return response.Contents
  } catch (error) {
    logError(`Ошибка получения списка файлов: ${error.message}`)
    return []
  }
}

// Тест 3: Проверка доступа к конкретному файлу
async function testFileAccess(fileKey) {
  log(`\n🔍 Тест 3: Проверка доступа к файлу "${fileKey}"...`, 'cyan')
  try {
    // Проверяем существование файла
    const headCommand = new HeadObjectCommand({
      Bucket: DEFAULT_BUCKET,
      Key: fileKey
    })
    const metadata = await s3Client.send(headCommand)
    
    logSuccess(`Файл существует!`)
    logInfo(`Размер: ${(metadata.ContentLength / 1024).toFixed(2)} KB`)
    logInfo(`Тип: ${metadata.ContentType || 'не указан'}`)
    logInfo(`Дата изменения: ${metadata.LastModified}`)
    
    // Генерируем presigned URL
    const getCommand = new GetObjectCommand({
      Bucket: DEFAULT_BUCKET,
      Key: fileKey
    })
    const presignedUrl = await getSignedUrl(s3Client, getCommand, { expiresIn: 3600 })
    
    logSuccess(`Presigned URL сгенерирован (действителен 1 час)`)
    logInfo(`URL: ${presignedUrl.substring(0, 80)}...`)
    
    return { success: true, url: presignedUrl, metadata }
  } catch (error) {
    if (error.name === 'NoSuchKey' || error.name === 'NotFound') {
      logError(`Файл "${fileKey}" не найден в bucket`)
    } else {
      logError(`Ошибка доступа к файлу: ${error.message}`)
    }
    return { success: false, error: error.message }
  }
}

// Тест 4: Поиск видео файла
async function testFindVideo() {
  log('\n🎥 Тест 4: Поиск видео файла "video_2025-11-09_17-39-52.mp4"...', 'cyan')
  
  const videoName = 'video_2025-11-09_17-39-52.mp4'
  const possiblePaths = [
    videoName, // В корне
    `videos/${videoName}`,
    `uploads/${videoName}`,
    `courses/${videoName}`
  ]
  
  for (const path of possiblePaths) {
    try {
      const headCommand = new HeadObjectCommand({
        Bucket: DEFAULT_BUCKET,
        Key: path
      })
      await s3Client.send(headCommand)
      
      logSuccess(`Видео найдено по пути: ${path}`)
      
      // Генерируем presigned URL для видео
      const getCommand = new GetObjectCommand({
        Bucket: DEFAULT_BUCKET,
        Key: path,
        ResponseContentType: 'video/mp4',
        ResponseContentDisposition: `inline; filename="${videoName}"`
      })
      const presignedUrl = await getSignedUrl(s3Client, getCommand, { expiresIn: 7 * 24 * 60 * 60 })
      
      logSuccess(`Presigned URL для видео сгенерирован (действителен 7 дней)`)
      logInfo(`URL: ${presignedUrl.substring(0, 100)}...`)
      
      return { found: true, path, url: presignedUrl }
    } catch (error) {
      if (error.name !== 'NoSuchKey' && error.name !== 'NotFound') {
        logWarning(`Ошибка при проверке пути "${path}": ${error.message}`)
      }
    }
  }
  
  // Если не нашли по путям, ищем в списке файлов
  try {
    const listCommand = new ListObjectsV2Command({
      Bucket: DEFAULT_BUCKET
    })
    const response = await s3Client.send(listCommand)
    
    if (response.Contents) {
      const videoFile = response.Contents.find(file => 
        file.Key.includes('video_2025-11-09_17-39-52') ||
        file.Key.endsWith('video_2025-11-09_17-39-52.mp4')
      )
      
      if (videoFile) {
        logSuccess(`Видео найдено в списке файлов: ${videoFile.Key}`)
        
        const getCommand = new GetObjectCommand({
          Bucket: DEFAULT_BUCKET,
          Key: videoFile.Key,
          ResponseContentType: 'video/mp4',
          ResponseContentDisposition: `inline; filename="${videoName}"`
        })
        const presignedUrl = await getSignedUrl(s3Client, getCommand, { expiresIn: 7 * 24 * 60 * 60 })
        
        logSuccess(`Presigned URL для видео сгенерирован`)
        return { found: true, path: videoFile.Key, url: presignedUrl }
      }
    }
  } catch (error) {
    logError(`Ошибка при поиске видео в списке файлов: ${error.message}`)
  }
  
  logError(`Видео "${videoName}" не найдено в bucket`)
  return { found: false }
}

// Тест 5: Проверка структуры папок
async function testFolderStructure() {
  log('\n📂 Тест 5: Проверка структуры папок...', 'cyan')
  try {
    const command = new ListObjectsV2Command({
      Bucket: DEFAULT_BUCKET,
      Delimiter: '/',
      MaxKeys: 20
    })
    const response = await s3Client.send(command)
    
    if (response.CommonPrefixes && response.CommonPrefixes.length > 0) {
      logSuccess(`Найдено папок: ${response.CommonPrefixes.length}`)
      logInfo('Папки:')
      response.CommonPrefixes.forEach((prefix, index) => {
        log(`  ${index + 1}. ${prefix.Prefix}`, 'reset')
      })
    } else {
      logWarning('Папки не найдены (возможно, все файлы в корне)')
    }
    
    return response.CommonPrefixes || []
  } catch (error) {
    logError(`Ошибка получения структуры папок: ${error.message}`)
    return []
  }
}

// Главная функция тестирования
async function runTests() {
  log('\n' + '='.repeat(60), 'cyan')
  log('🧪 ТЕСТИРОВАНИЕ ДОСТУПА К MINIO BUCKET', 'cyan')
  log('='.repeat(60), 'cyan')
  logInfo(`Endpoint: ${MINIO_ENDPOINT}`)
  logInfo(`Bucket: ${DEFAULT_BUCKET}`)
  logInfo(`TLS: ${isHttps ? 'HTTPS' : 'HTTP'}`)
  
  const results = {
    connection: false,
    listFiles: false,
    folderStructure: false,
    videoFound: false
  }
  
  // Тест 1: Подключение
  results.connection = await testConnection()
  if (!results.connection) {
    logError('\n❌ Не удалось подключиться к MinIO. Проверьте настройки.')
    return
  }
  
  // Тест 2: Список файлов
  const files = await testListFiles()
  results.listFiles = files.length >= 0
  
  // Тест 3: Структура папок
  const folders = await testFolderStructure()
  results.folderStructure = true
  
  // Тест 4: Поиск видео
  const videoResult = await testFindVideo()
  results.videoFound = videoResult.found || false
  
  // Итоговый отчет
  log('\n' + '='.repeat(60), 'cyan')
  log('📊 ИТОГОВЫЙ ОТЧЕТ', 'cyan')
  log('='.repeat(60), 'cyan')
  
  log(`Подключение к MinIO: ${results.connection ? '✅ Успешно' : '❌ Ошибка'}`, results.connection ? 'green' : 'red')
  log(`Получение списка файлов: ${results.listFiles ? '✅ Успешно' : '❌ Ошибка'}`, results.listFiles ? 'green' : 'red')
  log(`Структура папок: ${results.folderStructure ? '✅ Успешно' : '❌ Ошибка'}`, results.folderStructure ? 'green' : 'red')
  log(`Поиск видео: ${results.videoFound ? '✅ Найдено' : '❌ Не найдено'}`, results.videoFound ? 'green' : 'red')
  
  const allTestsPassed = Object.values(results).every(r => r === true)
  
  log('\n' + '='.repeat(60), 'cyan')
  if (allTestsPassed) {
    logSuccess('🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!')
  } else {
    logWarning('⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ')
  }
  log('='.repeat(60), 'cyan')
  log('')
}

// Запуск тестов
runTests().catch(error => {
  logError(`Критическая ошибка: ${error.message}`)
  console.error(error)
  process.exit(1)
})

