<template>
  <div class="flex-1 flex flex-col min-h-0 overflow-hidden">
    <!-- Top Toolbar (only for non-PDF content) -->
    <div 
      v-if="currentFileType !== 'pdf'"
      :class="[
        'p-2 border-b flex items-center justify-between shadow-sm z-10 transition-colors duration-200',
        isDark 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      ]"
    >
      <div class="flex items-center gap-2">
        <button
          :class="[
            'p-1.5 rounded transition-colors',
            isDark 
              ? 'hover:bg-gray-700 text-gray-400' 
              : 'hover:bg-gray-100 text-gray-500'
          ]"
          title="Уменьшить"
          @click="zoomOut"
        >
          <span class="material-symbols-outlined text-sm">remove_circle_outline</span>
        </button>
        <span 
          :class="[
            'text-sm font-mono min-w-[3rem] text-center',
            isDark ? 'text-gray-400' : 'text-gray-500'
          ]"
        >
          {{ zoom }}%
        </span>
        <button
          :class="[
            'p-1.5 rounded transition-colors',
            isDark 
              ? 'hover:bg-gray-700 text-gray-400' 
              : 'hover:bg-gray-100 text-gray-500'
          ]"
          title="Увеличить"
          @click="zoomIn"
        >
          <span class="material-symbols-outlined text-sm">add_circle_outline</span>
        </button>
      </div>
      <button
        :class="[
          'p-1.5 rounded transition-colors',
          isDark 
            ? 'hover:bg-gray-700 text-gray-400' 
            : 'hover:bg-gray-100 text-gray-500'
        ]"
        title="Полноэкранный режим"
        @click="toggleViewerFullscreen"
      >
        <span class="material-symbols-outlined text-sm">
          {{ isViewerFullscreen ? 'fullscreen_exit' : 'fullscreen' }}
        </span>
      </button>
    </div>

    <!-- Content Area -->
    <div 
      ref="contentContainer"
      :class="[
        'flex-1 min-h-0',
        currentFileType === 'pdf' 
          ? 'overflow-hidden' 
          : 'overflow-auto custom-scrollbar p-2 sm:p-4 md:p-8 flex items-center justify-center',
        isDark ? 'bg-black/40' : 'bg-gray-100'
      ]"
    >
      <!-- Video Player -->
      <div
        v-if="currentFile && currentFileType === 'video'"
        class="w-full max-w-5xl mx-auto"
        :style="{ transform: `scale(${zoom / 100})`, transformOrigin: 'center' }"
      >
        <EducationalVideoPlayer
          :source="currentFile"
          :save-progress="true"
          :progress-key="`lesson_${currentFile.id || currentFile.objectKey}`"
          class="w-full"
        />
      </div>

      <!-- PDF Viewer - No CSS transform, component handles zoom internally -->
      <LessonPdfViewer
        v-else-if="currentFile && currentFileType === 'pdf'"
        ref="pdfViewerRef"
        :source="currentFile"
        :is-dark="isDark"
        class="w-full h-full"
        @page-change="handlePdfPageChange"
        @scale-change="handlePdfScaleChange"
        @loaded="handlePdfLoaded"
        @error="handlePdfError"
      />

      <!-- Document Viewer (for unsupported files) -->
      <div 
        v-else-if="currentFile"
        :class="[
          'w-full max-w-5xl aspect-[16/9] shadow-2xl rounded-sm p-8 md:p-16 flex flex-col justify-between relative border transition-transform duration-200',
          isDark 
            ? 'bg-gray-800 text-gray-100 border-gray-700' 
            : 'bg-white text-gray-900 border-gray-200'
        ]"
        :style="{ transform: `scale(${zoom / 100})`, transformOrigin: 'center' }"
      >
        <div class="flex flex-col items-center justify-center flex-1 space-y-10 text-center">
          <!-- ATG Logo placeholder -->
          <div class="flex flex-col items-center">
            <div class="relative">
              <svg class="w-32 h-20 text-blue-700" fill="currentColor" viewBox="0 0 100 60">
                <path 
                  d="M10,50 L25,10 L40,50 M35,50 L50,10 L80,10 L80,20 L65,20 L65,50 L90,50 L90,30" 
                  fill="none" 
                  stroke="currentColor" 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="6"
                />
                <path d="M15,5 L60,5 M20,0 L50,0" stroke="#9CA3AF" stroke-linecap="round" stroke-width="3" />
              </svg>
            </div>
          </div>

          <div class="space-y-4 w-full">
            <h1 class="text-3xl md:text-5xl font-bold text-blue-900">
              <span :class="isDark ? 'text-gray-100' : 'text-gray-900'">Файл:</span>
              {{ currentFile.original_name || currentFile.originalName || 'Документ' }}
            </h1>
            <div class="h-1 w-full bg-blue-900 rounded-full"></div>
            <h2 class="text-xl md:text-2xl font-semibold text-blue-600">
              Предварительный просмотр недоступен
            </h2>
          </div>

          <div class="mt-8">
            <el-button 
              type="primary" 
              size="large"
              @click="$emit('download-file', currentFile)"
            >
              <span class="material-symbols-outlined mr-2">download</span>
              Скачать файл
            </el-button>
          </div>
        </div>
      </div>

      <!-- No Content Placeholder -->
      <div
        v-else
        :class="[
          'w-full max-w-3xl rounded-lg shadow-2xl p-8 md:p-12 flex items-center justify-center min-h-[400px]',
          isDark ? 'bg-gray-800' : 'bg-white'
        ]"
      >
        <div class="text-center">
          <span 
            :class="[
              'material-symbols-outlined text-6xl mb-4 block',
              isDark ? 'text-gray-600' : 'text-slate-400'
            ]"
          >
            description
          </span>
          <p :class="isDark ? 'text-gray-400' : 'text-slate-500'">
            Выберите материал для просмотра
          </p>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <div 
      :class="[
        'p-2 sm:p-4 flex justify-between items-center shrink-0 z-20 border-t transition-colors duration-200 gap-2',
        isDark 
          ? 'bg-gray-800 border-gray-700 shadow-[0_-2px_10px_rgba(0,0,0,0.2)]' 
          : 'bg-white border-gray-200 shadow-[0_-2px_10px_rgba(0,0,0,0.05)]'
      ]"
    >
      <!-- Previous Button -->
      <button
        :class="[
          'flex items-center px-2 sm:px-4 py-2 text-sm font-medium rounded-md border transition-colors',
          !hasPrevious 
            ? 'opacity-50 cursor-not-allowed' 
            : '',
          isDark 
            ? 'text-gray-300 bg-gray-800 border-gray-600 hover:bg-gray-700' 
            : 'text-gray-500 bg-white border-gray-200 hover:bg-gray-50'
        ]"
        :disabled="!hasPrevious"
        @click="$emit('previous')"
      >
        <span class="material-symbols-outlined text-sm sm:mr-1">arrow_back_ios</span>
        <span class="hidden sm:inline">Назад</span>
      </button>

      <!-- Complete Button - visible on all sizes, compact on mobile -->
      <button
        v-if="!isTopicCompleted"
        class="flex items-center justify-center px-2 sm:px-6 py-2 text-sm font-bold text-white bg-green-500 rounded-md hover:bg-green-600 shadow-sm transition-all transform active:scale-95"
        @click="$emit('mark-complete')"
      >
        <span class="material-symbols-outlined text-sm sm:mr-2">check</span>
        <span class="hidden sm:inline">Завершить</span>
      </button>
      <button
        v-else
        class="flex items-center justify-center px-2 sm:px-6 py-2 text-sm font-bold text-white bg-green-600 rounded-md cursor-default opacity-80"
        disabled
      >
        <span class="material-symbols-outlined text-sm sm:mr-2">check_circle</span>
        <span class="hidden sm:inline">Завершено</span>
      </button>

      <!-- Next Button -->
      <button
        :class="[
          'flex items-center px-2 sm:px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-blue-600 shadow-sm transition-colors',
          !hasNext ? 'opacity-50 cursor-not-allowed' : ''
        ]"
        :disabled="!hasNext"
        @click="$emit('next')"
      >
        <span class="hidden sm:inline">Далее</span>
        <span class="material-symbols-outlined text-sm sm:ml-1">arrow_forward_ios</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineAsyncComponent } from 'vue'

// Lazy load viewers
const EducationalVideoPlayer = defineAsyncComponent(() => import('../video/EducationalVideoPlayer.vue'))
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
  isDark: {
    type: Boolean,
    default: false
  },
  isTopicCompleted: {
    type: Boolean,
    default: false
  },
  hasPrevious: {
    type: Boolean,
    default: false
  },
  hasNext: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['download-file', 'previous', 'next', 'mark-complete'])

// Refs
const contentContainer = ref(null)
const pdfViewerRef = ref(null)
const isViewerFullscreen = ref(false)

// Zoom state (for non-PDF content)
const zoom = ref(100)

const zoomIn = () => {
  zoom.value = Math.min(200, zoom.value + 10)
}

const zoomOut = () => {
  zoom.value = Math.max(50, zoom.value - 10)
}

const toggleViewerFullscreen = () => {
  if (!contentContainer.value) return
  
  if (!isViewerFullscreen.value) {
    if (contentContainer.value.requestFullscreen) {
      contentContainer.value.requestFullscreen()
    } else if (contentContainer.value.webkitRequestFullscreen) {
      contentContainer.value.webkitRequestFullscreen()
    }
    isViewerFullscreen.value = true
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen()
    }
    isViewerFullscreen.value = false
  }
}

// PDF event handlers
const handlePdfPageChange = (page) => {
  // Can be used for analytics or progress tracking
  console.log('[ContentViewer] PDF page changed to:', page)
}

const handlePdfScaleChange = (scale) => {
  // Can be used for analytics or state sync
  console.log('[ContentViewer] PDF scale changed to:', scale)
}

const handlePdfLoaded = (info) => {
  console.log('[ContentViewer] PDF loaded:', info)
}

const handlePdfError = (error) => {
  console.error('[ContentViewer] PDF error:', error)
}

// Listen for fullscreen changes
if (typeof document !== 'undefined') {
  document.addEventListener('fullscreenchange', () => {
    isViewerFullscreen.value = !!document.fullscreenElement
  })
}
</script>

<style scoped>
/* Custom scrollbar */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
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

/* Dark mode scrollbar */
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(75, 85, 99, 0.5);
}
</style>
