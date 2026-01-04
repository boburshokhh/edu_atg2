<template>
  <div 
    ref="fullscreenContainer"
    :class="[
      'flex-1 overflow-auto bg-[#525659] p-4 sm:p-8 flex justify-center items-start relative custom-scrollbar'
    ]"
    style="min-height: 0;"
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
      class="w-full max-w-[800px] bg-white h-auto min-h-[60vh] md:min-h-[1130px] shadow-2xl relative mb-12 flex flex-col group"
      :style="{ transform: `scale(${currentZoom / 100})` }"
    >
      <div class="w-full h-full p-8 sm:p-16 flex flex-col gap-10 opacity-80" aria-label="Simulated Document Page">
        <!-- Title Skeleton -->
        <div class="w-3/4 h-10 bg-slate-200 rounded animate-pulse"></div>

        <!-- Text Paragraph Skeleton -->
        <div class="space-y-4">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-11/12 h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-2/3 h-4 bg-slate-100 rounded"></div>
        </div>

        <!-- Diagram Area -->
        <div class="w-full h-72 bg-slate-50 rounded-xl border border-dashed border-slate-200 flex items-center justify-center transition-colors group-hover:bg-slate-100/50">
          <div class="text-slate-300 flex flex-col items-center gap-3">
            <span class="material-symbols-outlined text-5xl">image</span>
            <span class="text-sm font-medium">
              {{ currentFile.original_name || currentFile.originalName || 'Файл' }}
            </span>
          </div>
        </div>

        <!-- More Text Skeletons -->
        <div class="space-y-4">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-1/2 h-4 bg-slate-100 rounded"></div>
        </div>

        <!-- Second Diagram/Image Area -->
        <div class="w-full h-56 bg-slate-50 rounded-xl border border-dashed border-slate-200 flex items-center justify-center transition-colors group-hover:bg-slate-100/50">
          <div class="text-slate-300 flex flex-col items-center gap-3">
            <span class="material-symbols-outlined text-5xl">bar_chart</span>
            <span class="text-sm font-medium">Content Section</span>
          </div>
        </div>

        <!-- Final Text Block -->
        <div class="space-y-4 mt-auto">
          <div class="w-full h-4 bg-slate-100 rounded"></div>
          <div class="w-5/6 h-4 bg-slate-100 rounded"></div>
        </div>
      </div>

      <!-- Floating Page Indicator - visible on hover of container -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white px-5 py-2.5 rounded-full shadow-2xl flex gap-4 text-sm font-semibold z-10 cursor-default select-none opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
        <span class="flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px]">description</span>
          Page 1 of 5
        </span>
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
/* Custom scrollbar - matching advanced-course-viewer */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
  /* Ensure scrolling works in flex containers */
  min-height: 0;
  /* Smooth scrolling */
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
