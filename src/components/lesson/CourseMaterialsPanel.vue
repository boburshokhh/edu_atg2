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
          <span class="material-symbols-outlined text-sm">menu</span>
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
          <span class="material-symbols-outlined text-lg">description</span>
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
              <span class="material-symbols-outlined text-xs">check_circle</span>
            </div>
            
            <div 
              class="p-1.5 rounded shadow-sm transition-all flex items-center justify-center"
              :class="[
                isActiveMaterial(material)
                  ? isDark
                    ? 'bg-blue-600'
                    : 'bg-blue-600'
                  : isDark
                    ? 'bg-gray-700/50 group-hover:bg-gray-700'
                    : 'bg-white group-hover:bg-gray-50'
              ]"
            >
              <component 
                :is="getMaterialIconComponent(material)" 
                class="w-6 h-6"
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
            <span 
              :class="[
                'material-symbols-outlined text-sm transition-opacity',
                isActiveMaterial(material)
                  ? 'opacity-100 text-primary'
                  : 'opacity-0 group-hover:opacity-100 text-primary',
                isDark ? 'text-blue-400' : ''
              ]"
            >
              download
            </span>
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
          <span class="material-symbols-outlined text-lg">folder_open</span>
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
              <span class="material-symbols-outlined text-xs">check_circle</span>
            </div>
            
            <div class="mt-0.5 flex items-center justify-center">
              <component 
                :is="getMaterialIconComponent(material)" 
                class="w-6 h-6"
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
import { h } from 'vue'

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

// Colorful icon components using h() function
const PdfIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', fill: '#DC2626' }),
  h('path', { d: 'M14 2V8H20', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('path', { d: 'M16 13H8V11H16V13Z', fill: 'white' }),
  h('path', { d: 'M16 17H8V15H16V17Z', fill: 'white' }),
  h('path', { d: 'M10 9H9V10H10V9Z', fill: 'white' })
])

const VideoIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M15 10L20.553 6.276C20.8334 6.10747 21.1786 6.02763 21.5248 6.05074C21.871 6.07385 22.2004 6.19866 22.4539 6.40424C22.7074 6.60982 22.8698 6.88377 22.9146 7.18282C22.9594 7.48187 22.8838 7.78719 22.701 8.044L19 13L22.701 17.956C22.8838 18.2128 22.9594 18.5181 22.9146 18.8172C22.8698 19.1162 22.7074 19.3902 22.4539 19.5958C22.2004 19.8013 21.871 19.9262 21.5248 19.9493C21.1786 19.9724 20.8334 19.8925 20.553 19.724L15 16V10Z', fill: '#EF4444' }),
  h('path', { d: 'M3 6C3 5.46957 3.21071 4.96086 3.58579 4.58579C3.96086 4.21071 4.46957 4 5 4H13C13.5304 4 14.0391 4.21071 14.4142 4.58579C14.7893 4.96086 15 5.46957 15 6V18C15 18.5304 14.7893 19.0391 14.4142 19.4142C14.0391 19.7893 13.5304 20 13 20H5C4.46957 20 3.96086 19.7893 3.58579 19.4142C3.21071 19.0391 3 18.5304 3 18V6Z', fill: '#EF4444' }),
  h('path', { d: 'M9 8L12 10L9 12V8Z', fill: 'white' })
])

const WordIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', fill: '#2563EB' }),
  h('path', { d: 'M14 2V8H20', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('path', { d: 'M8 12L9.5 16.5L11 12M13 12V16.5M15.5 12L17 16.5L18.5 12', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
])

const ExcelIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', fill: '#16A34A' }),
  h('path', { d: 'M14 2V8H20', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('path', { d: 'M8 12L10.5 15.5L8 19M16 12V19M16 12H10.5', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
])

const PowerPointIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', fill: '#EA580C' }),
  h('path', { d: 'M14 2V8H20', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('circle', { cx: '12', cy: '14', r: '3', fill: 'white' }),
  h('path', { d: 'M9 14H15', stroke: '#EA580C', 'stroke-width': '1.5', 'stroke-linecap': 'round' })
])

const DocumentIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', fill: '#6B7280' }),
  h('path', { d: 'M14 2V8H20', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('path', { d: 'M8 12H16M8 16H16M8 9H12', stroke: 'white', 'stroke-width': '1.5', 'stroke-linecap': 'round' })
])

const getMaterialIconComponent = (material) => {
  if (isVideoMaterial(material)) {
    return VideoIcon
  }
  const fileName = (material.original_name || material.originalName || '').toLowerCase()
  if (fileName.endsWith('.pdf')) {
    return PdfIcon
  }
  if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
    return WordIcon
  }
  if (fileName.endsWith('.xls') || fileName.endsWith('.xlsx')) {
    return ExcelIcon
  }
  if (fileName.endsWith('.ppt') || fileName.endsWith('.pptx')) {
    return PowerPointIcon
  }
  return DocumentIcon
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
