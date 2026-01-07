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
              'flex items-start gap-3 p-2 rounded-lg border transition-all group',
              isActiveMaterial(material)
                ? isDark 
                  ? 'bg-blue-900/20 border-blue-800' 
                  : 'bg-blue-50 border-blue-100'
                : isDark
                  ? 'bg-gray-700/50 border-gray-600 hover:shadow-sm'
                  : 'bg-blue-50 border-blue-100 hover:shadow-sm'
            ]"
            @click.prevent="selectMaterial(material)"
          >
            <div 
              :class="[
                'p-1.5 rounded shadow-sm group-hover:text-blue-600 transition-colors',
                isDark 
                  ? 'bg-blue-800 text-primary' 
                  : 'bg-white text-primary'
              ]"
            >
              <span class="material-symbols-outlined text-xl">
                {{ getMaterialIcon(material) }}
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p 
                :class="[
                  'text-sm font-medium group-hover:underline truncate',
                  isDark ? 'text-blue-400' : 'text-primary'
                ]"
              >
                {{ cleanFileName(material.original_name || material.originalName) }}
              </p>
              <p 
                :class="[
                  'text-xs mt-0.5',
                  isDark ? 'text-gray-400' : 'text-gray-500'
                ]"
              >
                {{ formatFileSize(material.file_size) }} • {{ getMaterialType(material) }}
              </p>
            </div>
            <span 
              :class="[
                'material-symbols-outlined text-primary text-sm opacity-0 group-hover:opacity-100 transition-opacity',
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
              'group flex items-start gap-3 cursor-pointer',
              isActiveMaterial(material) ? 'opacity-100' : ''
            ]"
            @click="selectMaterial(material)"
          >
            <div 
              :class="[
                'mt-0.5 transition-colors',
                isVideoMaterial(material)
                  ? isDark 
                    ? 'text-gray-500 group-hover:text-red-400' 
                    : 'text-gray-400 group-hover:text-red-500'
                  : isDark
                    ? 'text-gray-500 group-hover:text-primary'
                    : 'text-gray-400 group-hover:text-primary'
              ]"
            >
              <span class="material-symbols-outlined text-xl">
                {{ getMaterialIcon(material) }}
              </span>
            </div>
            <div class="flex-1">
              <p 
                :class="[
                  'text-sm font-medium leading-tight transition-colors',
                  isVideoMaterial(material)
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
                  isDark ? 'text-gray-400' : 'text-gray-500'
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

// Функция для очистки названия файла от "_OUTLINE"
const cleanFileName = (fileName) => {
  if (!fileName) return 'Файл'
  // Убираем "_OUTLINE" из названия (может быть в начале или в конце)
  return fileName.replace(/^O_OUTLINE\s+/i, '').replace(/\s*_OUTLINE$/i, '').replace(/\s*OUTLINE$/i, '')
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
