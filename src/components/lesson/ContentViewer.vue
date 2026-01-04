<template>
  <div class="content-viewer-wrapper">
    <!-- Content Area -->
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
      <div 
        v-else
        class="flex flex-col items-center justify-center min-h-[400px] p-8"
      >
        <span class="material-symbols-outlined text-6xl text-slate-600 dark:text-slate-400 mb-4">
          description
        </span>
        <h3 class="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-2">
          Неподдерживаемый формат файла
        </h3>
        <p class="text-sm text-slate-600 dark:text-slate-400 mb-4">
          {{ currentFile.original_name || currentFile.originalName || 'Файл' }}
        </p>
        <el-button 
          v-if="currentFileType !== 'pdf'"
          type="primary" 
          @click="$emit('download-file', currentFile)"
        >
          Скачать файл
        </el-button>
        <el-alert
          v-else
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            <span>Скачивание конфиденциальных документов запрещено</span>
          </template>
        </el-alert>
      </div>
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

const isFullscreen = ref(false)

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

watch(
  () => [props.currentFileType, props.currentFile?.objectName || props.currentFile?.object_key || props.currentFile?.objectKey],
  ([type, key]) => {
    if (!props.currentFile) return
    console.log('[ContentViewer] Render target:', { type, key })
  },
  { immediate: true }
)

onMounted(() => {
  addFullscreenListeners()
})

onUnmounted(() => {
  removeFullscreenListeners()
})
</script>

<style scoped>
.content-viewer-wrapper {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>
