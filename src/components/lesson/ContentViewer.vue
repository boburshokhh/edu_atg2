<template>
  <div 
    ref="fullscreenContainer"
    :class="[
      'flex-1 flex justify-center bg-[#525659] relative custom-scrollbar',
      currentFileType === 'pdf' ? 'overflow-auto h-full' : 'overflow-auto p-8'
    ]"
  >
      <!-- Video Player -->
      <OptimizedVideoPlayer
        v-if="currentFile && currentFileType === 'video'"
        :source="currentFile"
        :zoom="currentZoom"
        :is-fullscreen="isFullscreen"
        @fullscreen-change="handleFullscreenChange"
      />

      <!-- PDF Viewer -->
      <LessonPdfViewer
        v-else-if="currentFile && currentFileType === 'pdf'"
        :source="currentFile"
        :zoom="currentZoom"
        @zoom-in="$emit('zoom-in')"
        @zoom-out="$emit('zoom-out')"
      />

    <!-- Document Viewer (for unsupported files) -->
      <div 
      v-else-if="currentFile"
      class="w-full max-w-[800px] bg-white h-auto shadow-2xl relative transition-transform origin-top"
      :style="{ transform: `scale(${currentZoom / 100})` }"
    >
      <div class="w-full min-h-[1130px] p-12 flex flex-col gap-8 opacity-80">
        <!-- Header Skeleton -->
        <div class="w-3/4 h-8 bg-slate-200 rounded animate-pulse"></div>
        
        <!-- Text Skeletons -->
        <div class="space-y-3">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-2/3 h-4 bg-slate-100 rounded"></div>
        </div>

        <!-- Diagram Placeholder -->
        <div class="w-full h-64 bg-slate-50 rounded border border-dashed border-slate-200 flex items-center justify-center">
          <div class="text-slate-300 flex flex-col items-center gap-2">
            <span class="material-symbols-outlined text-4xl">image</span>
            <span class="text-sm">
          {{ currentFile.original_name || currentFile.originalName || 'Файл' }}
            </span>
          </div>
        </div>

        <!-- More Text -->
        <div class="space-y-3">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-1/2 h-4 bg-slate-100 rounded"></div>
        </div>

        <!-- Additional content sections for long scroll -->
        <div class="space-y-3 mt-8">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-3/4 h-4 bg-slate-100 rounded"></div>
        </div>

        <div class="space-y-3 mt-8">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
        </div>

        <div class="w-full h-48 bg-slate-50 rounded border border-dashed border-slate-200 flex items-center justify-center mt-8">
          <div class="text-slate-300 flex flex-col items-center gap-2">
            <span class="material-symbols-outlined text-4xl">description</span>
            <span class="text-sm">Content Section</span>
          </div>
        </div>

        <div class="space-y-3 mt-8">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-2/3 h-4 bg-slate-100 rounded"></div>
        </div>

        <!-- Footer -->
        <div class="mt-auto pt-8 border-t border-slate-100 flex flex-col gap-2">
          <div class="text-[10px] uppercase font-bold text-slate-400 tracking-widest">
            Confidential Training Material
          </div>
          <div class="text-xs text-slate-400">
            © 2024 Advanced UX Academy. All rights reserved.
          </div>
        </div>
      </div>

      <!-- Page Indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white px-4 py-2 rounded-full shadow-lg flex gap-4 text-sm font-medium opacity-0 hover:opacity-100 transition-opacity duration-300 cursor-default pointer-events-none">
        <span>Page 1 of 5</span>
      </div>
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
const LessonPdfViewer = defineAsyncComponent(() => import('./LessonPdfViewer.vue'))

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
/* Custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 12px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Firefox scrollbar */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) rgba(0, 0, 0, 0.1);
}
</style>
