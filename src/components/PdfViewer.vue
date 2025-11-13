<template>
  <div class="pdf-viewer-wrapper">
    <div 
      v-if="pdfSource"
      :class="[
        'pdf-viewer-container',
        isFullscreen ? 'fullscreen' : ''
      ]"
      @contextmenu.prevent
    >
      <div 
        class="pdf-pages-wrapper"
        :style="{
          transform: `scale(${zoom / 100})`,
          transformOrigin: 'top center'
        }"
      >
        <vue-pdf-embed
          v-for="pageNum in totalPages"
          :key="pageNum"
          :source="pdfSource"
          :page="pageNum"
          :class="[
            'pdf-page',
            `page-${pageNum}`
          ]"
          @rendered="handlePageRendered"
          @loading-failed="handleLoadingFailed"
        />
      </div>
    </div>
    <div v-else class="pdf-viewer-empty">
      <el-empty description="PDF не загружен" :image-size="80" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import * as pdfjsLib from 'pdfjs-dist'

const props = defineProps({
  source: {
    type: String,
    default: ''
  },
  zoom: {
    type: Number,
    default: 100
  },
  isFullscreen: {
    type: Boolean,
    default: false
  }
})

const pdfSource = computed(() => props.source)
const totalPages = ref(1)

// Загружаем PDF для определения количества страниц
const loadPdfInfo = async (url) => {
  if (!url) return
  
  try {
    const loadingTask = pdfjsLib.getDocument({
      url: url,
      withCredentials: false,
      isEvalSupported: false,
      verbosity: 0
    })
    
    const pdf = await loadingTask.promise
    totalPages.value = pdf.numPages
  } catch (error) {
    console.error('Ошибка загрузки информации о PDF:', error)
    totalPages.value = 1
  }
}

const handlePageRendered = () => {
  // Страница успешно отрендерена
}

const handleLoadingFailed = (error) => {
  console.error('Ошибка рендеринга страницы:', error)
}

watch(() => props.source, (newSource) => {
  if (newSource) {
    loadPdfInfo(newSource)
  }
}, { immediate: true })

onMounted(() => {
  if (props.source) {
    loadPdfInfo(props.source)
  }
})
</script>

<style scoped>
.pdf-viewer-wrapper {
  width: 100%;
  height: 100%;
}

.pdf-viewer-container {
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  min-height: 400px;
  max-height: 500px;
  background: #f3f4f6;
}

.pdf-viewer-container.fullscreen {
  height: 100vh;
  max-height: 100vh;
  padding: 32px;
}

.pdf-pages-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  transition: transform 0.2s ease-out;
}

.pdf-page {
  margin-bottom: 16px;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  display: block;
  width: 100%;
  max-width: 100%;
}

.pdf-viewer-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

:deep(.vue-pdf-embed) {
  display: block;
  width: 100%;
}

:deep(.vue-pdf-embed canvas) {
  display: block;
  width: 100% !important;
  height: auto !important;
  max-width: 100% !important;
  /* Исправление ориентации через CSS */
  image-orientation: from-image;
  -webkit-image-orientation: from-image;
}

/* Убираем любые трансформации, которые могут переворачивать страницу */
:deep(.vue-pdf-embed) {
  transform: none !important;
}
</style>

