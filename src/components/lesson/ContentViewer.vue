<template>
  <div 
    :class="[
      'flex-1 overflow-auto bg-[#525659] p-4 sm:p-6 md:p-8 flex justify-center items-start relative custom-scrollbar min-h-0'
    ]"
  >
    <!-- Loading State -->
    <transition name="fade">
      <div
        v-if="isLoading"
        class="w-full max-w-5xl bg-white rounded-lg shadow-2xl p-8 md:p-12 flex items-center justify-center min-h-[400px]"
      >
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p class="text-slate-500">{{ loadingText }}</p>
        </div>
      </div>
    </transition>

    <!-- Content with transitions -->
    <transition name="content-fade" mode="out-in">
      <!-- Video Player -->
      <div
        v-if="currentFile && currentFileType === 'video' && !isLoading"
        key="video"
        class="w-full max-w-5xl mx-auto"
      >
        <EducationalVideoPlayer
          :source="currentFile"
          :save-progress="true"
          :progress-key="`lesson_${currentFile.id || currentFile.objectKey}`"
          class="w-full"
          @ready="handleVideoReady"
          @error="handleVideoError"
        />
      </div>

      <!-- PDF Viewer -->
      <div
        v-else-if="currentFile && currentFileType === 'pdf' && !isLoading"
        key="pdf"
        class="w-full max-w-5xl mx-auto"
      >
        <LessonPdfViewer
          :source="currentFile"
          @page-loaded="handlePdfLoaded"
        />
      </div>

      <!-- Document Viewer (for unsupported files) -->
      <div 
        v-else-if="currentFile && !isLoading"
        key="document"
        class="w-full max-w-3xl bg-white h-auto min-h-[60vh] md:min-h-[80vh] shadow-2xl relative mb-8 md:mb-12 flex flex-col group"
      >
      <div class="w-full h-full p-6 sm:p-8 md:p-12 lg:p-16 flex flex-col gap-6 md:gap-8 lg:gap-10 opacity-80" aria-label="Simulated Document Page">
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
        v-else-if="!isLoading"
        key="empty"
        class="w-full max-w-3xl bg-white rounded-lg shadow-2xl p-8 md:p-12 flex items-center justify-center min-h-[400px]"
      >
        <div class="text-center">
          <span class="material-symbols-outlined text-6xl text-slate-400 mb-4 block">
            description
          </span>
          <p class="text-slate-500">Выберите материал для просмотра</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, defineAsyncComponent } from 'vue'

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
  }
})

const emit = defineEmits(['download-file'])

// Loading state
const isLoading = ref(false)
const loadingText = ref('Загрузка...')

// Watch for file changes to show loading
watch(() => [props.currentFile, props.currentFileType], ([newFile, newType], [oldFile, oldType]) => {
  if (newFile && newFile !== oldFile) {
    isLoading.value = true
    if (newType === 'video') {
      loadingText.value = 'Загрузка видео...'
    } else if (newType === 'pdf') {
      loadingText.value = 'Загрузка PDF...'
    } else {
      loadingText.value = 'Загрузка файла...'
    }
    
    // Hide loading after a short delay (content will handle its own loading)
    setTimeout(() => {
      isLoading.value = false
    }, 300)
  } else if (!newFile) {
    isLoading.value = false
  }
}, { immediate: false })

// Handlers
const handleVideoReady = () => {
  isLoading.value = false
}

const handleVideoError = () => {
  isLoading.value = false
  loadingText.value = 'Ошибка загрузки видео'
}

const handlePdfLoaded = () => {
  isLoading.value = false
}
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

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.content-fade-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.content-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.content-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.content-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .custom-scrollbar {
    padding: 1rem;
  }
}
</style>
