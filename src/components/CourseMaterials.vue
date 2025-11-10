<template>
  <div v-if="isAuthenticated" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Header -->
    <div class="p-6 border-b border-gray-100">
      <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
        <DocumentTextIcon class="w-5 h-5 text-blue-600" />
        Материалы курса
      </h3>
      <p class="text-sm text-gray-600 mt-1">Доступны только для авторизованных пользователей</p>
    </div>
    
    <!-- Materials Content -->
    <div class="p-6">
      <div class="space-y-4">
        <div 
          v-for="(lesson, lessonIndex) in curriculum" 
          :key="lessonIndex"
          class="border border-gray-200 rounded-xl overflow-hidden"
        >
          <!-- Lesson Header -->
          <div class="p-4 bg-gray-50 border-b border-gray-200">
            <h4 class="font-bold text-gray-900">{{ lesson.title }}</h4>
          </div>
          
          <!-- Topics and Materials -->
          <div class="p-4 space-y-3">
            <div v-for="(topic, topicIndex) in lesson.topics" :key="topicIndex" class="space-y-2">
              <!-- Topic Title -->
              <div class="font-semibold text-gray-700 text-sm">
                <span v-if="topic.code" class="text-blue-600 mr-2">{{ topic.code }}</span>
                {{ topic.title }}
              </div>
              
              <!-- Основные материалы (PDF) -->
              <div v-if="(topic.mainPdfs && topic.mainPdfs.length > 0) || topic.mainPdf" class="ml-4 space-y-2">
                <div 
                  v-for="(mainFile, mainFileIndex) in (topic.mainPdfs || (topic.mainPdf ? [topic.mainPdf] : []))" 
                  :key="mainFileIndex"
                  class="flex items-center justify-between p-3 bg-amber-50 rounded-lg border border-amber-200 hover:bg-amber-100 transition-colors"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <DocumentTextIcon class="w-5 h-5 text-amber-600 flex-shrink-0" />
                    <span class="text-sm font-medium text-gray-900 truncate">
                      {{ mainFile.original_name || mainFile.originalName }}
                    </span>
                    <span v-if="mainFile.sizeFormatted" class="text-xs text-gray-500 ml-2">
                      ({{ mainFile.sizeFormatted }})
                    </span>
                  </div>
                  <button
                    v-if="mainFile.url || mainFile.file_url"
                    class="ml-3 px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-500 text-white hover:bg-amber-600 transition-all flex-shrink-0"
                    @click="handlePdfClick(mainFile)"
                  >
                    Просмотр
                  </button>
                  <span v-else class="ml-3 text-xs text-red-500 italic flex-shrink-0">
                    Недоступен
                  </span>
                </div>
              </div>
              
              <!-- Дополнительные материалы (PDF и видео) -->
              <div v-if="(topic.additionals || []).length > 0" class="ml-4 space-y-2">
                <div 
                  v-for="(file, fileIndex) in topic.additionals" 
                  :key="fileIndex"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-all cursor-pointer"
                  @click="handleFileClick(file, topic.additionals, fileIndex)"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <PlayCircleIcon v-if="isVideoFile(file)" class="w-5 h-5 text-purple-600 flex-shrink-0" />
                    <DocumentTextIcon v-else class="w-5 h-5 text-blue-600 flex-shrink-0" />
                    <span class="text-sm font-medium text-gray-900 truncate">
                      {{ file.original_name || file.originalName }}
                    </span>
                    <span v-if="file.sizeFormatted" class="text-xs text-gray-500 ml-2">
                      ({{ file.sizeFormatted }})
                    </span>
                    <span v-if="isVideoFile(file)" class="text-[9px] px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded font-semibold flex-shrink-0 ml-2">
                      ВИДЕО
                    </span>
                    <span v-else class="text-[9px] px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded font-semibold flex-shrink-0 ml-2">
                      ДОКУМЕНТ
                    </span>
                    <span v-if="file.error" class="text-[9px] px-1.5 py-0.5 bg-red-100 text-red-700 rounded font-semibold flex-shrink-0 ml-2">
                      ОШИБКА
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { DocumentTextIcon, PlayCircleIcon } from '@heroicons/vue/24/solid'

export default {
  name: 'CourseMaterials',
  components: {
    DocumentTextIcon,
    PlayCircleIcon
  },
  props: {
    // Структура курса с материалами
    curriculum: {
      type: Array,
      required: true,
      default: () => []
    },
    // Флаг авторизации
    isAuthenticated: {
      type: Boolean,
      default: false
    }
  },
  emits: ['open-pdf', 'play-video', 'file-click'],
  setup(props, { emit }) {
    // Проверка, является ли файл видео
    const isVideoFile = (file) => {
      if (!file) return false
      const fileName = (file.original_name || file.originalName || '').toLowerCase()
      const fileType = (file.type || '').toLowerCase()
      return fileName.endsWith('.mp4') || 
             fileName.endsWith('.webm') || 
             fileName.endsWith('.ogg') ||
             fileName.endsWith('.mov') ||
             fileType.includes('video')
    }

    // Обработка клика на PDF
    const handlePdfClick = (file) => {
      if (!file.url && !file.file_url) {
        return
      }
      emit('open-pdf', file)
    }

    // Обработка клика на файл (PDF или видео)
    const handleFileClick = (file, allFiles, fileIndex) => {
      if (isVideoFile(file)) {
        // Получаем все видео из списка файлов
        const videos = allFiles.filter(f => isVideoFile(f))
        emit('play-video', {
          videos,
          startIndex: videos.findIndex(v => (v.objectName || v.id) === (file.objectName || file.id))
        })
      } else {
        // Для PDF открываем в просмотрщике
        emit('open-pdf', file)
      }
    }

    return {
      isVideoFile,
      handlePdfClick,
      handleFileClick
    }
  }
}
</script>

<style scoped>
/* Дополнительные стили при необходимости */
</style>

