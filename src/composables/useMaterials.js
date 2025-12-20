import { ref, computed } from 'vue'
import minioService from '@/services/minioService'
import courseMaterials from '@/data/courseMaterials.json'
import { debounce } from '@/utils/performance'

/**
 * Composable для работы с учебными материалами
 */
export function useMaterials() {
  const mainMaterials = ref([])
  const additionalMaterials = ref([])
  const currentFile = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Определение типа файла
  const detectFileType = (file) => {
    if (!file) return 'unknown'
    
    const fileName = (file.original_name || file.originalName || file.fileName || '').toLowerCase()
    const fileType = (file.type || '').toLowerCase()
    const url = (file.url || file.file_url || '').toLowerCase()
    
    // MIME type
    if (fileType.includes('pdf') || fileType === 'application/pdf') {
      return 'pdf'
    }
    
    if (fileType.includes('video')) {
      return 'video'
    }
    
    // Расширения
    const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v', '.3gp']
    const pdfExtensions = ['.pdf']
    
    const checkExtension = (str, extensions) => {
      return extensions.some(ext => str.includes(ext))
    }
    
    if (url && checkExtension(url, pdfExtensions)) return 'pdf'
    if (url && checkExtension(url, videoExtensions)) return 'video'
    if (fileName && checkExtension(fileName, pdfExtensions)) return 'pdf'
    if (fileName && checkExtension(fileName, videoExtensions)) return 'video'
    
    const objectName = (file.objectName || '').toLowerCase()
    if (objectName && checkExtension(objectName, pdfExtensions)) return 'pdf'
    if (objectName && checkExtension(objectName, videoExtensions)) return 'video'
    
    return 'unknown'
  }
  
  // Текущий тип файла
  const currentFileType = computed(() => {
    if (!currentFile.value) return 'unknown'
    return detectFileType(currentFile.value)
  })
  
  // Загрузка материалов для урока
  const loadTopicMaterials = async (lessonTitle, topicCode) => {
    if (!lessonTitle || !topicCode) {
      console.warn('loadTopicMaterials: missing lessonTitle or topicCode', { lessonTitle, topicCode })
      return
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      // Нормализация названия урока (убираем различия в форматировании)
      const normalizeLessonTitle = (title) => {
        if (!title) return ''
        return title
          .replace(/:/g, '.')
          .replace(/\s+/g, ' ')
          .trim()
      }
      
      const normalizedLessonTitle = normalizeLessonTitle(lessonTitle)
      
      const lessonData = courseMaterials.lessons.find(l => {
        const normalized = normalizeLessonTitle(l.lessonTitle)
        return normalized === normalizedLessonTitle || 
               l.lessonTitle === lessonTitle ||
               l.lessonTitle.replace(':', '.') === lessonTitle.replace(':', '.')
      })

      if (!lessonData) {
        console.warn('Lesson data not found for:', { 
          lessonTitle, 
          normalizedLessonTitle,
          availableLessons: courseMaterials.lessons.map(l => l.lessonTitle)
        })
        isLoading.value = false
        return
      }

      // Нормализация кода темы
      const normalizeTopicCode = (code) => {
        if (!code) return ''
        return code
          .replace(/\.$/, '')
          .replace(/\s+/g, ' ')
          .trim()
      }
      
      const normalizedTopicCode = normalizeTopicCode(topicCode)
      
      const topicData = lessonData.topics.find(t => {
        const normalized = normalizeTopicCode(t.topicCode)
        return normalized === normalizedTopicCode ||
               (t.topicCode || '').replace(/\.$/, '').trim() === (topicCode || '').replace(/\.$/, '').trim()
      })

      if (!topicData || !topicData.files) {
        console.warn('Topic data not found for:', {
          topicCode,
          normalizedTopicCode,
          lessonTitle: lessonData.lessonTitle,
          availableTopics: lessonData.topics.map(t => t.topicCode)
        })
        isLoading.value = false
        return
      }

      const mainFiles = []
      const additionals = []

      // Параллельная загрузка URL для всех файлов
      const filePromises = topicData.files.map(async (fileConfig) => {
        try {
          const fileName = (fileConfig.fileName || fileConfig.objectName || '').toLowerCase()
          let mimeType = 'application/octet-stream'
          
          // Определение MIME type
          if (fileConfig.fileType === 'pdf') {
            mimeType = 'application/pdf'
          } else if (fileConfig.fileType === 'video') {
            if (fileName.endsWith('.webm')) {
              mimeType = 'video/webm'
            } else if (fileName.endsWith('.ogg')) {
              mimeType = 'video/ogg'
            } else if (fileName.endsWith('.mov')) {
              mimeType = 'video/quicktime'
            } else {
              mimeType = 'video/mp4'
            }
          } else {
            // Автоопределение
            if (fileName.endsWith('.pdf')) {
              mimeType = 'application/pdf'
            } else if (fileName.endsWith('.mp4')) {
              mimeType = 'video/mp4'
            } else if (fileName.endsWith('.webm')) {
              mimeType = 'video/webm'
            } else if (fileName.endsWith('.ogg')) {
              mimeType = 'video/ogg'
            } else if (fileName.endsWith('.mov')) {
              mimeType = 'video/quicktime'
            }
          }
          
          const fileUrl = await minioService.getPresignedDownloadUrl(
            fileConfig.objectName,
            7 * 24 * 60 * 60,
            mimeType
          )

          const fileObject = {
            objectName: fileConfig.objectName,
            fileName: fileConfig.fileName,
            original_name: fileConfig.fileName,
            originalName: fileConfig.fileName,
            file_size: fileConfig.fileSize,
            sizeFormatted: fileConfig.sizeFormatted,
            url: fileUrl,
            file_url: fileUrl,
            type: mimeType,
            isMainFile: fileConfig.is_main_file
          }

          return fileObject
        } catch (err) {
          console.error('Error loading file:', err)
          return null
        }
      })

      const results = await Promise.allSettled(filePromises)
      
      results.forEach(result => {
        if (result.status === 'fulfilled' && result.value) {
          if (result.value.isMainFile) {
            mainFiles.push(result.value)
          } else {
            additionals.push(result.value)
          }
        }
      })

      mainMaterials.value = mainFiles
      additionalMaterials.value = additionals

      console.log('Materials loaded:', {
        mainFiles: mainFiles.length,
        additionalFiles: additionals.length,
        totalFiles: mainFiles.length + additionals.length
      })

      // Автоматически выбираем первый основной файл
      if (mainFiles.length > 0) {
        currentFile.value = mainFiles[0]
        console.log('Current file set to:', {
          fileName: mainFiles[0].original_name || mainFiles[0].fileName,
          url: mainFiles[0].url ? 'present' : 'missing',
          type: detectFileType(mainFiles[0])
        })
      } else if (additionals.length > 0) {
        // Если нет основных файлов, выбираем первый дополнительный
        currentFile.value = additionals[0]
        console.log('Current file set to (additional):', {
          fileName: additionals[0].original_name || additionals[0].fileName,
          url: additionals[0].url ? 'present' : 'missing',
          type: detectFileType(additionals[0])
        })
      } else {
        console.warn('No files loaded for topic')
        currentFile.value = null
      }
    } catch (err) {
      error.value = err.message
      console.error('Error loading topic materials:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // Debounced версия для избежания частых перезагрузок
  const loadTopicMaterialsDebounced = debounce(loadTopicMaterials, 300)
  
  // Открытие материала
  const openMaterial = (material) => {
    currentFile.value = material
  }
  
  // Скачивание файла
  const downloadFile = (file) => {
    if (!file || (!file.url && !file.file_url)) {
      console.error('URL файла недоступен')
      return
    }
    
    const url = file.url || file.file_url
    const link = document.createElement('a')
    link.href = url
    link.download = file.original_name || file.originalName || file.fileName || 'download'
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
  
  // Очистка
  const cleanup = () => {
    mainMaterials.value = []
    additionalMaterials.value = []
    currentFile.value = null
    error.value = null
  }
  
  return {
    mainMaterials,
    additionalMaterials,
    currentFile,
    currentFileType,
    isLoading,
    error,
    loadTopicMaterials,
    loadTopicMaterialsDebounced,
    openMaterial,
    downloadFile,
    detectFileType,
    cleanup
  }
}

