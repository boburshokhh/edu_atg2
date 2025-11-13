<template>
  <div class="course-materials-sidebar bg-white border-l border-gray-200 flex flex-col w-72 lg:w-80">
    <!-- Compact Header -->
    <div class="p-4 border-b border-gray-200 relative">
      <div class="flex items-center justify-between mb-1">
        <div class="flex-1 min-w-0">
          <h2 class="text-sm font-bold text-gray-900 uppercase tracking-wide mb-0.5">Материалы курса</h2>
          <div v-if="topicTitle" class="text-xs font-medium text-gray-600 truncate">
            {{ topicTitle }}
          </div>
        </div>
        <el-button
          @click="handleToggleSidebar"
          :icon="Fold"
          circle
          size="small"
          class="sidebar-toggle-btn"
          title="Свернуть сайдбар"
        />
      </div>
    </div>

    <!-- Materials List -->
    <div class="materials-list-container">
      <!-- Основные материалы -->
      <div v-if="mainMaterials.length > 0" class="materials-section">
        <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
          <div class="flex items-center gap-2">
            <el-icon class="text-blue-600" :size="14"><Document /></el-icon>
            <span class="text-xs font-semibold text-gray-700">Основные материалы</span>
          </div>
        </div>
        
        <div class="materials-items">
          <button
            v-for="(material, index) in mainMaterials"
            :key="`main-${index}`"
            @click="handleMaterialClick(material)"
            :class="[
              'w-full px-4 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition-colors text-left border-l-3',
              isActiveMaterial(material)
                ? 'border-blue-600 bg-blue-50'
                : 'border-transparent'
            ]"
          >
            <!-- Material Icon -->
            <div class="flex-shrink-0 mt-0.5">
              <div 
                v-if="isActiveMaterial(material)"
                class="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center"
              >
                <el-icon class="text-white" :size="12">
                  <Check v-if="isActiveMaterial(material)" />
                  <Document v-else />
                </el-icon>
              </div>
              <div 
                v-else
                class="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center"
              >
                <el-icon class="text-gray-400" :size="12">
                  <Document v-if="!isVideoFile(material)" />
                  <VideoPlay v-else />
                </el-icon>
              </div>
            </div>

            <!-- Material Info -->
            <div class="flex-1 min-w-0">
              <div 
                :class="[
                  'text-xs font-medium mb-0.5 leading-tight',
                  isActiveMaterial(material)
                    ? 'text-blue-600'
                    : 'text-gray-900'
                ]"
              >
                {{ material.original_name || material.originalName }}
              </div>
              <div class="text-xs text-gray-500">
                {{ material.sizeFormatted || formatFileSize(material.file_size) }}
              </div>
            </div>

            <!-- Active Icon -->
            <div v-if="isActiveMaterial(material)" class="flex-shrink-0">
              <el-icon class="text-blue-600" :size="14">
                <CaretRight />
              </el-icon>
            </div>
          </button>
        </div>
      </div>

      <!-- Дополнительные материалы -->
      <div v-if="additionalMaterials.length > 0" class="materials-section">
        <div class="px-4 py-2 bg-gray-50 border-b border-gray-200 border-t border-gray-200">
          <div class="flex items-center gap-2">
            <el-icon class="text-purple-600" :size="14"><Folder /></el-icon>
            <span class="text-xs font-semibold text-gray-700">Дополнительные материалы</span>
          </div>
        </div>
        
        <div class="materials-items">
          <button
            v-for="(material, index) in additionalMaterials"
            :key="`additional-${index}`"
            @click="handleMaterialClick(material)"
            :class="[
              'w-full px-4 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition-colors text-left border-l-3',
              isActiveMaterial(material)
                ? 'border-purple-600 bg-purple-50'
                : 'border-transparent'
            ]"
          >
            <!-- Material Icon -->
            <div class="flex-shrink-0 mt-0.5">
              <div 
                v-if="isActiveMaterial(material)"
                class="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center"
              >
                <el-icon class="text-white" :size="12">
                  <Check />
                </el-icon>
              </div>
              <div 
                v-else
                class="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center"
              >
                <el-icon class="text-gray-400" :size="12">
                  <Document v-if="!isVideoFile(material)" />
                  <VideoPlay v-else />
                </el-icon>
              </div>
            </div>

            <!-- Material Info -->
            <div class="flex-1 min-w-0">
              <div 
                :class="[
                  'text-xs font-medium mb-0.5 leading-tight',
                  isActiveMaterial(material)
                    ? 'text-purple-600'
                    : 'text-gray-900'
                ]"
              >
                {{ material.original_name || material.originalName }}
              </div>
              <div class="text-xs text-gray-500">
                {{ material.sizeFormatted || formatFileSize(material.file_size) }}
              </div>
            </div>

            <!-- Active Icon -->
            <div v-if="isActiveMaterial(material)" class="flex-shrink-0">
              <el-icon class="text-purple-600" :size="14">
                <CaretRight />
              </el-icon>
            </div>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="mainMaterials.length === 0 && additionalMaterials.length === 0" class="px-4 py-8 text-center">
        <el-empty description="Нет доступных материалов" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { Document, VideoPlay, Check, CaretRight, Folder, Fold } from '@element-plus/icons-vue'

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
  }
})

const emit = defineEmits(['select-material', 'toggle-sidebar'])

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

const handleMaterialClick = (material) => {
  emit('select-material', material)
}

const handleToggleSidebar = () => {
  emit('toggle-sidebar')
}
</script>

<style scoped>
.course-materials-sidebar {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
}

/* Desktop styles */
.materials-sidebar-desktop {
  position: sticky;
  top: 64px; /* Высота LessonHeader */
  height: calc(100vh - 64px);
  max-height: calc(100vh - 64px);
  overflow: hidden;
}

/* Mobile styles */
.materials-sidebar-mobile {
  position: fixed;
  right: 0;
  top: 64px;
  height: calc(100vh - 64px);
  z-index: 40;
  overflow: hidden;
}

.materials-list-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0; /* Важно для правильной работы flex с overflow */
}

.materials-section {
  border-b: 1px solid #f3f4f6;
}

.materials-items {
  display: flex;
  flex-direction: column;
}

.sidebar-toggle-btn {
  flex-shrink: 0;
  margin-left: 8px;
}

/* Кастомный скроллбар для сайдбара */
.materials-list-container::-webkit-scrollbar {
  width: 6px;
}

.materials-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.materials-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.materials-list-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
