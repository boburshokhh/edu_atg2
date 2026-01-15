<template>
  <aside
    :class="[
      'w-80 flex flex-col shrink-0 overflow-y-auto transition-colors duration-200 border-l hidden xl:flex',
      isDark 
        ? 'bg-gray-800 border-gray-700' 
        : 'bg-white border-gray-200'
    ]"
  >
    <!-- Header -->
    <div 
      :class="[
        'p-4 border-b sticky top-0 z-10 transition-colors duration-200',
        isDark 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      ]"
    >
      <div class="flex items-center justify-between">
        <h2 
          :class="[
            'font-bold text-lg tracking-tight uppercase',
            isDark ? 'text-gray-100' : 'text-gray-900'
          ]"
        >
          Материалы курса
        </h2>
        <button 
          :class="[
            'p-1 rounded transition-colors',
            isDark 
              ? 'hover:bg-gray-700 text-gray-500' 
              : 'hover:bg-gray-100 text-gray-500'
          ]"
          @click="$emit('toggle-sidebar')"
        >
          <Menu :size="16" />
        </button>
      </div>
      <p 
        v-if="topicTitle"
        :class="[
          'text-xs mt-1',
          isDark ? 'text-gray-400' : 'text-gray-500'
        ]"
      >
        {{ topicTitle }}
      </p>
    </div>

    <!-- Materials Content -->
    <div class="p-4 space-y-6">
      <!-- Main Materials -->
      <div v-if="mainMaterials.length > 0">
        <div class="flex items-center gap-2 text-primary mb-3">
          <FileText :size="18" />
          <h3 class="text-sm font-semibold uppercase tracking-wider">Основные материалы</h3>
        </div>
        <div class="space-y-3 pl-2">
          <a
            v-for="material in mainMaterials"
            :key="material.id || material.objectName"
            href="#"
            :class="[
              'flex items-start gap-3 p-2.5 rounded-lg border-2 transition-all group relative',
              isActiveMaterial(material)
                ? isDark 
                  ? 'bg-blue-900/40 border-blue-500 shadow-lg shadow-blue-900/20' 
                  : 'bg-blue-100 border-blue-500 shadow-md shadow-blue-200/50'
                : isDark
                  ? 'bg-gray-700/50 border-gray-600 hover:shadow-sm hover:border-gray-500'
                  : 'bg-blue-50 border-blue-100 hover:shadow-sm hover:border-blue-200'
            ]"
            @click.prevent="selectMaterial(material)"
          >
            <!-- Active indicator bar -->
            <div 
              v-if="isActiveMaterial(material)"
              :class="[
                'absolute left-0 top-0 bottom-0 w-1 rounded-l-lg',
                isDark ? 'bg-blue-400' : 'bg-blue-600'
              ]"
            />
            
            <!-- Checkmark icon for active material -->
            <div 
              v-if="isActiveMaterial(material)"
              :class="[
                'absolute top-1 right-1 p-0.5 rounded-full',
                isDark ? 'bg-blue-500 text-white' : 'bg-blue-600 text-white'
              ]"
            >
              <CheckCircle2 :size="12" />
            </div>
            
            <div 
              :class="[
                'p-1.5 rounded shadow-sm transition-colors flex items-center justify-center',
                isActiveMaterial(material)
                  ? isDark
                    ? 'bg-blue-600'
                    : 'bg-blue-600'
                  : isDark
                    ? 'bg-gray-700/50 group-hover:bg-gray-700'
                    : 'bg-white group-hover:bg-gray-50'
              ]"
            >
              <FileTypeIcon 
                :file-type="getFileType(material)" 
                size="md"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p 
                :class="[
                  'text-sm font-medium truncate transition-colors',
                  isActiveMaterial(material)
                    ? isDark
                      ? 'text-blue-300 font-semibold'
                      : 'text-blue-700 font-semibold'
                    : isDark
                      ? 'text-blue-400 group-hover:text-blue-300 group-hover:underline'
                      : 'text-primary group-hover:text-blue-600 group-hover:underline'
                ]"
              >
                {{ cleanFileName(material.original_name || material.originalName) }}
              </p>
              <p 
                :class="[
                  'text-xs mt-0.5',
                  isActiveMaterial(material)
                    ? isDark
                      ? 'text-blue-400'
                      : 'text-blue-600'
                    : isDark
                      ? 'text-gray-400'
                      : 'text-gray-500'
                ]"
              >
                {{ formatFileSize(material.file_size) }} • {{ getMaterialType(material) }}
              </p>
            </div>
            <Download 
              :size="16"
              :class="[
                'transition-opacity',
                isActiveMaterial(material)
                  ? 'opacity-100 text-primary'
                  : 'opacity-0 group-hover:opacity-100 text-primary',
                isDark ? 'text-blue-400' : ''
              ]"
            />
          </a>
        </div>
      </div>

      <!-- Additional Materials -->
      <div v-if="additionalMaterials.length > 0">
        <div 
          :class="[
            'flex items-center gap-2 mb-3',
            isDark ? 'text-gray-400' : 'text-gray-500'
          ]"
        >
          <FolderOpen :size="18" />
          <h3 class="text-sm font-semibold uppercase tracking-wider">Дополнительные материалы</h3>
        </div>
        <div class="space-y-4 pl-2">
          <div
            v-for="material in additionalMaterials"
            :key="material.id || material.objectName"
            :class="[
              'group flex items-start gap-3 cursor-pointer p-2 rounded-lg border-2 transition-all relative',
              isActiveMaterial(material)
                ? isDark
                  ? 'bg-blue-900/30 border-blue-500 shadow-md shadow-blue-900/20'
                  : 'bg-blue-50 border-blue-500 shadow-sm shadow-blue-200/30'
                : isDark
                  ? 'border-transparent hover:border-gray-600 hover:bg-gray-700/30'
                  : 'border-transparent hover:border-blue-200 hover:bg-blue-50/50'
            ]"
            @click="selectMaterial(material)"
          >
            <!-- Active indicator bar -->
            <div 
              v-if="isActiveMaterial(material)"
              :class="[
                'absolute left-0 top-0 bottom-0 w-1 rounded-l-lg',
                isDark ? 'bg-blue-400' : 'bg-blue-600'
              ]"
            />
            
            <!-- Checkmark icon for active material -->
            <div 
              v-if="isActiveMaterial(material)"
              :class="[
                'absolute top-1.5 right-1.5 p-0.5 rounded-full',
                isDark ? 'bg-blue-500 text-white' : 'bg-blue-600 text-white'
              ]"
            >
              <CheckCircle2 :size="12" />
            </div>
            
            <div class="mt-0.5 flex items-center justify-center">
              <FileTypeIcon 
                :file-type="getFileType(material)" 
                size="md"
              />
            </div>
            <div class="flex-1">
              <p 
                :class="[
                  'text-sm font-medium leading-tight transition-colors',
                  isActiveMaterial(material)
                    ? isVideoMaterial(material)
                      ? isDark
                        ? 'text-red-300 font-semibold'
                        : 'text-red-700 font-semibold'
                      : isDark
                        ? 'text-blue-300 font-semibold'
                        : 'text-blue-700 font-semibold'
                    : isVideoMaterial(material)
                      ? 'group-hover:text-red-500'
                      : 'group-hover:text-primary',
                  isDark ? 'text-gray-100' : 'text-gray-900'
                ]"
              >
                {{ cleanFileName(material.original_name || material.originalName) }}
              </p>
              <p 
                :class="[
                  'text-xs mt-1',
                  isActiveMaterial(material)
                    ? isDark
                      ? 'text-blue-400'
                      : 'text-blue-600'
                    : isDark
                      ? 'text-gray-400'
                      : 'text-gray-500'
                ]"
              >
                {{ formatFileSize(material.file_size) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="mainMaterials.length === 0 && additionalMaterials.length === 0"
        class="py-8 text-center"
      >
        <el-empty
          description="Нет доступных материалов"
          :image-size="60"
        />
      </div>
    </div>
  </aside>
</template>

<script setup>
import { Menu, FileText, CheckCircle2, FolderOpen, Download } from 'lucide-vue-next'
import FileTypeIcon from '@/components/ui/FileTypeIcon.vue'

const props = defineProps({
  mainMaterials: {
    type: Array,
    default: () => []
  },
  additionalMaterials: {
    type: Array,
    default: () => []
  },
  currentFile: {
    type: Object,
    default: null
  },
  topicTitle: {
    type: String,
    default: ''
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-material', 'toggle-sidebar'])

const isVideoMaterial = (material) => {
  if (!material) return false
  const fileName = (material.original_name || material.originalName || '').toLowerCase()
  const fileType = (material.type || '').toLowerCase()
  return fileName.endsWith('.mp4') || 
         fileName.endsWith('.webm') || 
         fileName.endsWith('.ogg') ||
         fileName.endsWith('.mov') ||
         fileType.includes('video')
}

const getMaterialIcon = (material) => {
  if (isVideoMaterial(material)) {
    return 'play_circle_outline'
  }
  const fileName = (material.original_name || material.originalName || '').toLowerCase()
  if (fileName.endsWith('.pdf')) {
    return 'picture_as_pdf'
  }
  return 'description'
}

const getFileType = (material) => {
  if (isVideoMaterial(material)) {
    return 'video'
  }
  const fileName = (material.original_name || material.originalName || '').toLowerCase()
  if (fileName.endsWith('.pdf')) {
    return 'pdf'
  }
  if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
    return 'word'
  }
  if (fileName.endsWith('.xls') || fileName.endsWith('.xlsx')) {
    return 'excel'
  }
  if (fileName.endsWith('.ppt') || fileName.endsWith('.pptx')) {
    return 'powerpoint'
  }
  return 'document'
}

const getMaterialType = (material) => {
  if (isVideoMaterial(material)) {
    return 'Видео'
  }
  const fileName = (material.original_name || material.originalName || '').toLowerCase()
  if (fileName.endsWith('.pdf')) {
    return 'PDF'
  }
  if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
    return 'Word'
  }
  if (fileName.endsWith('.xls') || fileName.endsWith('.xlsx')) {
    return 'Excel'
  }
  if (fileName.endsWith('.ppt') || fileName.endsWith('.pptx')) {
    return 'PowerPoint'
  }
  return 'Файл'
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const isActiveMaterial = (material) => {
  if (!props.currentFile || !material) return false
  return (material.url === props.currentFile.url) || 
         (material.file_url === props.currentFile.file_url) ||
         (material.objectName === props.currentFile.objectName)
}

const selectMaterial = (material) => {
  emit('select-material', material)
}

// Функция для очистки названия файла от "_OUTLINE" или "_outline"
const cleanFileName = (fileName) => {
  if (!fileName) return 'Файл'
  // Убираем "_OUTLINE" или "_outline" из названия (может быть в начале или в конце)
  // Обрабатываем различные варианты: O_OUTLINE, _OUTLINE, OUTLINE, _outline, outline
  return fileName
    .replace(/^O_OUTLINE\s+/i, '')  // Убираем "O_OUTLINE " в начале
    .replace(/^O_outline\s+/i, '')  // Убираем "O_outline " в начале
    .replace(/\s*_OUTLINE$/i, '')    // Убираем " _OUTLINE" в конце
    .replace(/\s*_outline$/i, '')    // Убираем " _outline" в конце
    .replace(/\s*OUTLINE$/i, '')     // Убираем " OUTLINE" в конце
    .replace(/\s*outline$/i, '')     // Убираем " outline" в конце
    .trim()                           // Убираем лишние пробелы
}
</script>

<style scoped>
/* Custom scrollbar */
aside::-webkit-scrollbar {
  width: 6px;
}

aside::-webkit-scrollbar-track {
  background: transparent;
}

aside::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

aside::-webkit-scrollbar-thumb:hover {
  background-color: rgba(107, 114, 128, 0.8);
}
</style>
