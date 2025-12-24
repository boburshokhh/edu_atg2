<template>
  <div 
    ref="fullscreenContainer"
    class="content-viewer relative bg-gray-100" 
    :class="isFullscreen ? 'fixed inset-0 z-50' : ''"
  >
    <!-- Controls Bar -->
    <div 
      v-if="!isFullscreen || currentFileType !== 'video'"
      class="absolute top-2 left-2 right-2 z-10 flex items-center justify-between"
    >
      <div class="flex items-center gap-1.5">
        <el-button 
          :icon="ZoomOut" 
          circle 
          size="small"
          class="bg-white/90 backdrop-blur-sm"
          :disabled="currentFileType === 'video' && isFullscreen"
          @click="$emit('zoom-out')"
        />
        <el-button 
          :icon="ZoomIn" 
          circle 
          size="small"
          class="bg-white/90 backdrop-blur-sm"
          :disabled="currentFileType === 'video' && isFullscreen"
          @click="$emit('zoom-in')"
        />
        <el-tag class="bg-white/90 backdrop-blur-sm">
          {{ currentZoom }}%
        </el-tag>
      </div>
      <div class="flex items-center gap-1.5">
        <el-button 
          :icon="FullScreen" 
          circle 
          size="small"
          class="bg-white/90 backdrop-blur-sm"
          title="Полный экран"
          @click="toggleFullscreen"
        />
      </div>
    </div>

    <!-- PDF Viewer -->
    <VirtualizedPdfViewer
      v-if="currentFile && currentFileType === 'pdf' && (currentFile.url || currentFile.file_url)"
      :source="currentFile.url || currentFile.file_url"
      :zoom="currentZoom"
      :is-fullscreen="isFullscreen"
    />
    
    <!-- Loading PDF URL -->
    <div 
      v-else-if="currentFile && currentFileType === 'pdf' && !(currentFile.url || currentFile.file_url)"
      class="flex items-center justify-center min-h-[400px]"
    >
      <el-icon
        class="is-loading"
        :size="32"
      >
        <Loading />
      </el-icon>
      <span class="ml-2">Загрузка файла...</span>
    </div>

    <!-- Video Player -->
    <OptimizedVideoPlayer
      v-else-if="currentFile && currentFileType === 'video'"
      :source="currentFile"
      :zoom="currentZoom"
      :is-fullscreen="isFullscreen"
      @fullscreen-change="handleFullscreenChange"
    />

    <!-- Unsupported File Type -->
    <div 
      v-else-if="currentFile && currentFileType === 'unknown'"
      class="flex flex-col items-center justify-center min-h-[400px] p-8"
    >
      <el-icon
        :size="64"
        class="text-gray-400 mb-4"
      >
        <Document />
      </el-icon>
      <h3 class="text-lg font-semibold text-gray-700 mb-2">
        Неподдерживаемый формат файла
      </h3>
      <p class="text-sm text-gray-500 mb-4">
        {{ currentFile.original_name || currentFile.originalName || 'Файл' }}
      </p>
      <el-button 
        type="primary" 
        @click="$emit('download-file', currentFile)"
      >
        Скачать файл
      </el-button>
    </div>

    <!-- No Content Placeholder -->
    <div
      v-else
      class="flex items-center justify-center min-h-[400px]"
    >
      <el-empty
        description="Выберите материал для просмотра"
        :image-size="80"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { defineAsyncComponent } from 'vue'
import { ZoomIn, ZoomOut, FullScreen, Document, Loading } from '@element-plus/icons-vue'

// Lazy load viewers
const VirtualizedPdfViewer = defineAsyncComponent(() => import('./VirtualizedPdfViewer.vue'))
const OptimizedVideoPlayer = defineAsyncComponent(() => import('./OptimizedVideoPlayer.vue'))

const props = defineProps({
  currentFile: {
    type: Object,
    default: null
  },
  currentFileType: {
    type: String,
    default: 'unknown'
  },
  currentZoom: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits(['zoom-in', 'zoom-out', 'toggle-fullscreen', 'download-file'])

const fullscreenContainer = ref(null)
const isFullscreen = ref(false)

const toggleFullscreen = async () => {
  if (!fullscreenContainer.value) return
  
  try {
    if (!isFullscreen.value) {
      if (fullscreenContainer.value.requestFullscreen) {
        await fullscreenContainer.value.requestFullscreen()
      } else if (fullscreenContainer.value.webkitRequestFullscreen) {
        await fullscreenContainer.value.webkitRequestFullscreen()
      } else if (fullscreenContainer.value.mozRequestFullScreen) {
        await fullscreenContainer.value.mozRequestFullScreen()
      } else if (fullscreenContainer.value.msRequestFullscreen) {
        await fullscreenContainer.value.msRequestFullscreen()
      }
      
      isFullscreen.value = true
      document.body.style.overflow = 'hidden'
    } else {
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        await document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        await document.msExitFullscreen()
      }
      
      isFullscreen.value = false
      document.body.style.overflow = ''
    }
  } catch (error) {
    console.error('Error toggling fullscreen:', error)
  }
}

const handleFullscreenChange = (value) => {
  isFullscreen.value = value
}

const handleDocumentFullscreenChange = () => {
  if (!document.fullscreenElement && 
      !document.webkitFullscreenElement && 
      !document.mozFullScreenElement && 
      !document.msFullscreenElement) {
    isFullscreen.value = false
    document.body.style.overflow = ''
  }
}

const addFullscreenListeners = () => {
  if (typeof document === 'undefined') return
  document.addEventListener('fullscreenchange', handleDocumentFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleDocumentFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleDocumentFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleDocumentFullscreenChange)
}

const removeFullscreenListeners = () => {
  if (typeof document === 'undefined') return
  document.removeEventListener('fullscreenchange', handleDocumentFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleDocumentFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleDocumentFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleDocumentFullscreenChange)
}

onMounted(() => {
  addFullscreenListeners()
})

onUnmounted(() => {
  removeFullscreenListeners()
})
</script>

<style scoped>
.content-viewer {
  min-height: 400px;
  transition: all 0.3s ease;
}
</style>

