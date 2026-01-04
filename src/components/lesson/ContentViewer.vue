<template>
  <div 
    ref="fullscreenContainer"
    class="flex-1 overflow-auto p-8 flex justify-center bg-[#525659] relative"
  >
    <!-- Video Player -->
    <OptimizedVideoPlayer
      v-if="currentFile && currentFileType === 'video'"
      :source="currentFile"
      :zoom="currentZoom"
      :is-fullscreen="isFullscreen"
      @fullscreen-change="handleFullscreenChange"
    />

    <!-- Unsupported File Type -->
    <div 
      v-else-if="currentFile"
      class="w-full max-w-[800px] bg-white rounded-lg shadow-2xl p-12 flex flex-col items-center justify-center min-h-[400px]"
    >
      <span class="material-symbols-outlined text-6xl text-slate-400 mb-4">
        description
      </span>
      <h3 class="text-lg font-semibold text-slate-700 mb-2">
        Неподдерживаемый формат файла
      </h3>
      <p class="text-sm text-slate-500 mb-4">
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
      class="w-full max-w-[800px] bg-white rounded-lg shadow-2xl p-12 flex items-center justify-center min-h-[400px]"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-6xl text-slate-400 mb-4 block">
          description
        </span>
        <p class="text-slate-500">Выберите материал для просмотра</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { defineAsyncComponent } from 'vue'

// Lazy load viewers
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
/* No additional styles needed - using Tailwind */
</style>
