<template>
  <div class="flex-1 overflow-auto flex justify-center bg-[#525659] relative">
    <!-- Control Panel -->
    <div class="absolute top-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-2 bg-white/90 backdrop-blur rounded-lg shadow-lg px-4 py-2">
      <!-- Zoom Out -->
      <button
        class="p-1 hover:bg-slate-100 rounded text-slate-600 transition-colors"
        @click="$emit('zoom-out')"
        :disabled="zoom <= 50"
      >
        <ZoomOut :size="20" />
      </button>
      
      <!-- Zoom Display -->
      <span class="text-sm font-medium w-12 text-center text-slate-700">{{ zoom }}%</span>
      
      <!-- Zoom In -->
      <button
        class="p-1 hover:bg-slate-100 rounded text-slate-600 transition-colors"
        @click="$emit('zoom-in')"
        :disabled="zoom >= 200"
      >
        <ZoomIn :size="20" />
      </button>
      
      <!-- Page Indicator -->
      <div class="h-6 w-px bg-slate-300 mx-1"></div>
      <span class="text-sm font-medium text-slate-700">
        {{ currentPage }} / {{ totalPages }}
      </span>
    </div>

    <!-- PDF Container -->
    <div
      v-if="pdfSource"
      class="w-full max-w-[800px] py-8 px-4 flex justify-center"
    >
      <VuePdfEmbed
        :source="pdfSource"
        :scale="zoom / 100"
        text-layer
        annotation-layer
        class="w-full"
        @loaded="handlePdfLoaded"
        @rendered="handlePdfRendered"
      />
    </div>

    <!-- Loading State -->
    <div
      v-else
      class="w-full max-w-[800px] bg-white rounded-lg shadow-2xl p-12 flex items-center justify-center min-h-[400px]"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-6xl text-slate-400 mb-4 block animate-pulse">
          description
        </span>
        <p class="text-slate-500">Загрузка PDF...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import { ZoomIn, ZoomOut } from 'lucide-vue-next'
// Import required styles for PDF viewer
import 'vue-pdf-embed/dist/styles/annotationLayer.css'
import 'vue-pdf-embed/dist/styles/textLayer.css'

const props = defineProps({
  source: {
    type: Object,
    default: null
  },
  zoom: {
    type: Number,
    default: 100
  }
})

const emit = defineEmits(['zoom-in', 'zoom-out', 'page-loaded'])

const currentPage = ref(1)
const totalPages = ref(0)

const pdfSource = computed(() => {
  if (!props.source) return null
  const key = props.source.objectName || props.source.object_key || props.source.objectKey
  if (!key) return null
  
  // Use backend streaming endpoint
  return `/api/files/stream/${encodeURIComponent(key)}`
})

const handlePdfLoaded = (pdfDoc) => {
  if (pdfDoc && pdfDoc.numPages) {
    totalPages.value = pdfDoc.numPages
    currentPage.value = 1
    emit('page-loaded', { currentPage: 1, totalPages: totalPages.value })
  }
}

const handlePdfRendered = () => {
  // Document rendered successfully
}

watch(() => props.source, () => {
  currentPage.value = 1
  totalPages.value = 0
}, { immediate: true })
</script>

