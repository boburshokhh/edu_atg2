<template>
  <div class="course-materials-sidebar bg-white border-l border-gray-200 flex flex-col">
    <!-- Compact Header -->
    <div class="p-4 border-b border-gray-200 relative">
      <div class="flex items-center justify-between mb-1">
        <div class="flex-1 min-w-0">
          <h2 class="text-sm font-bold text-gray-900 uppercase tracking-wide mb-0.5">
            Материалы курса
          </h2>
          <div
            v-if="topicTitle"
            class="text-xs font-medium text-gray-500 truncate"
          >
            {{ topicTitle }}
          </div>
        </div>
        <el-button
          :icon="Fold"
          circle
          size="small"
          class="sidebar-toggle-btn"
          title="Свернуть сайдбар"
          @click="handleToggleSidebar"
        />
      </div>
    </div>

    <!-- Materials List -->
    <div class="materials-list-container">
      <!-- Основные материалы -->
      <div
        v-if="mainMaterials.length > 0"
        class="materials-section"
      >
        <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
          <div class="flex items-center gap-2">
            <el-icon
              class="text-blue-600"
              :size="14"
            >
              <Document />
            </el-icon>
            <span class="text-xs font-bold text-gray-700">Основные материалы</span>
          </div>
        </div>
        
        <div class="materials-items">
          <button
            v-for="(material, index) in mainMaterials"
            :key="`main-${index}`"
            :class="[
              'w-full px-4 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition-colors text-left border-l-3',
              isActiveMaterial(material)
                ? 'border-blue-600 bg-blue-50'
                : 'border-transparent'
            ]"
            @click="handleMaterialClick(material)"
          >
            <!-- Material Icon -->
            <div class="flex-shrink-0 mt-0.5">
              <div 
                v-if="isActiveMaterial(material)"
                class="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center"
              >
                <el-icon
                  class="text-white"
                  :size="12"
                >
                  <Check v-if="isActiveMaterial(material)" />
                  <Document v-else />
                </el-icon>
              </div>
              <div 
                v-else
                class="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center"
              >
                <el-icon
                  class="text-gray-400"
                  :size="12"
                >
                  <Document v-if="!isVideoFile(material)" />
                  <VideoPlay v-else />
                </el-icon>
              </div>
            </div>

            <!-- Material Info -->
            <div class="flex-1 min-w-0">
              <div 
                :class="[
                  'text-xs font-bold mb-0.5 leading-tight',
                  isActiveMaterial(material)
                    ? 'text-blue-600'
                    : 'text-gray-900'
                ]"
              >
                {{ material.original_name || material.originalName }}
              </div>
              <div class="text-xs font-medium text-gray-500">
                {{ material.sizeFormatted || formatFileSize(material.file_size) }}
              </div>
            </div>

            <!-- Active Icon -->
            <div
              v-if="isActiveMaterial(material)"
              class="flex-shrink-0"
            >
              <el-icon
                class="text-blue-600"
                :size="14"
              >
                <CaretRight />
              </el-icon>
            </div>
          </button>
        </div>
      </div>

      <!-- Дополнительные материалы -->
      <div
        v-if="additionalMaterials.length > 0"
        class="materials-section"
      >
        <div class="px-4 py-2 bg-gray-50 border-b border-gray-200 border-t border-gray-200">
          <div class="flex items-center gap-2">
            <el-icon
              class="text-purple-600"
              :size="14"
            >
              <Folder />
            </el-icon>
            <span class="text-xs font-semibold text-gray-700">Дополнительные материалы</span>
          </div>
        </div>
        
        <div class="materials-items">
          <button
            v-for="(material, index) in additionalMaterials"
            :key="`additional-${index}`"
            :class="[
              'w-full px-4 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition-colors text-left border-l-3',
              isActiveMaterial(material)
                ? 'border-purple-600 bg-purple-50'
                : 'border-transparent'
            ]"
            @click="handleMaterialClick(material)"
          >
            <!-- Material Icon -->
            <div class="flex-shrink-0 mt-0.5">
              <div 
                v-if="isActiveMaterial(material)"
                class="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center"
              >
                <el-icon
                  class="text-white"
                  :size="12"
                >
                  <Check />
                </el-icon>
              </div>
              <div 
                v-else
                class="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center"
              >
                <el-icon
                  class="text-gray-400"
                  :size="12"
                >
                  <Document v-if="!isVideoFile(material)" />
                  <VideoPlay v-else />
                </el-icon>
              </div>
            </div>

            <!-- Material Info -->
            <div class="flex-1 min-w-0">
              <div 
                :class="[
                  'text-xs font-bold mb-0.5 leading-tight',
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
            <div
              v-if="isActiveMaterial(material)"
              class="flex-shrink-0"
            >
              <el-icon
                class="text-purple-600"
                :size="14"
              >
                <CaretRight />
              </el-icon>
            </div>
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="mainMaterials.length === 0 && additionalMaterials.length === 0"
        class="px-4 py-8 text-center"
      >
        <el-empty
          description="Нет доступных материалов"
          :image-size="60"
        />
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
  width: 100%;
  max-width: 100%;
}

/* Desktop styles */
.materials-sidebar-desktop {
  position: sticky;
  top: clamp(3.5rem, 10vw, 4rem);
  height: calc(100vh - clamp(3.5rem, 10vw, 4rem));
  max-height: calc(100vh - clamp(3.5rem, 10vw, 4rem));
  overflow: hidden;
  width: clamp(16rem, 25vw, 20rem);
  min-width: clamp(16rem, 25vw, 20rem);
  max-width: clamp(16rem, 25vw, 20rem);
}

/* Mobile styles */
.materials-sidebar-mobile {
  position: fixed;
  right: 0;
  top: clamp(3.5rem, 10vw, 4rem);
  height: calc(100vh - clamp(3.5rem, 10vw, 4rem));
  z-index: 40;
  overflow: hidden;
  width: clamp(16rem, 80vw, 20rem);
  max-width: 85vw;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.materials-list-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  width: 100%;
}

.materials-section {
  border-b: 1px solid #f3f4f6;
  width: 100%;
}

.materials-items {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.sidebar-toggle-btn {
  flex-shrink: 0;
  margin-left: clamp(0.25rem, 1vw, 0.5rem);
  width: clamp(1.75rem, 4vw, 2rem);
  height: clamp(1.75rem, 4vw, 2rem);
}

/* Кастомный скроллбар для сайдбара */
/* Custom Scrollbar - Hidden by default, visible on hover */
.materials-list-container {
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.materials-list-container:hover {
  scrollbar-color: #c1c1c1 #f1f1f1;
}

.materials-list-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.materials-list-container::-webkit-scrollbar-track {
  background: transparent;
}

.materials-list-container::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 3px;
  transition: background 0.2s;
}

.materials-list-container:hover::-webkit-scrollbar-thumb {
  background: #c1c1c1;
}

.materials-list-container:hover::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Media Queries */
/* Mobile phones (max-width: 480px) */
@media (max-width: 480px) {
  .materials-sidebar-mobile {
    width: 85vw;
    max-width: 85vw;
  }

  .materials-sidebar-desktop {
    width: clamp(14rem, 30vw, 18rem);
    min-width: clamp(14rem, 30vw, 18rem);
    max-width: clamp(14rem, 30vw, 18rem);
  }
}

/* Tablets (max-width: 768px) */
@media (max-width: 768px) {
  .materials-sidebar-mobile {
    width: clamp(18rem, 75vw, 22rem);
    max-width: 80vw;
  }

  .materials-sidebar-desktop {
    width: clamp(16rem, 28vw, 20rem);
    min-width: clamp(16rem, 28vw, 20rem);
    max-width: clamp(16rem, 28vw, 20rem);
  }
}

/* Small laptops (max-width: 1024px) */
@media (max-width: 1024px) {
  .materials-sidebar-desktop {
    width: clamp(16rem, 30vw, 20rem);
    min-width: clamp(16rem, 30vw, 20rem);
    max-width: clamp(16rem, 30vw, 20rem);
  }
}

/* Desktop (min-width: 1025px) */
@media (min-width: 1025px) {
  .materials-sidebar-desktop {
    width: clamp(18rem, 22vw, 20rem);
    min-width: clamp(18rem, 22vw, 20rem);
    max-width: clamp(18rem, 22vw, 20rem);
  }
}

/* Wide monitors (min-width: 1440px) */
@media (min-width: 1440px) {
  .materials-sidebar-desktop {
    width: 20rem;
    min-width: 20rem;
    max-width: 20rem;
  }
}
</style>
