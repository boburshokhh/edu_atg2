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

    <!-- Content Area (separate chain; must NOT be tied to Controls Bar v-if) -->
    <template v-if="currentFile">
      <!-- PDF Viewer -->
      <SecurePDFViewer
        v-if="currentFileType === 'pdf'"
        :file="currentFile"
        :zoom="currentZoom"
        :is-fullscreen="isFullscreen"
        @zoom-in="$emit('zoom-in')"
        @zoom-out="$emit('zoom-out')"
      />

      <!-- Video Player -->
      <OptimizedVideoPlayer
        v-else-if="currentFileType === 'video'"
        :source="currentFile"
        :zoom="currentZoom"
        :is-fullscreen="isFullscreen"
        @fullscreen-change="handleFullscreenChange"
      />

      <!-- Unsupported File Type -->
      <DocumentErrorState
        v-else
        error="Неподдерживаемый формат файла"
        :file-type="currentFileType"
        :file-name="currentFile.original_name || currentFile.originalName || 'Файл'"
        :on-download="() => $emit('download-file', currentFile)"
      />
    </template>

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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { defineAsyncComponent } from 'vue'
import { ZoomIn, ZoomOut, FullScreen, Document } from '@element-plus/icons-vue'
import DocumentErrorState from './DocumentErrorState.vue'

// Lazy load viewers
const SecurePDFViewer = defineAsyncComponent(() => import('./SecurePDFViewer.vue'))
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

watch(
  () => [props.currentFileType, props.currentFile?.objectName || props.currentFile?.object_key || props.currentFile?.objectKey],
  ([type, key]) => {
    if (!props.currentFile) return
    console.log('[ContentViewer] Render target:', { type, key })
  },
  { immediate: true }
)

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

