<template>
  <header
    class="h-16 bg-white dark:bg-[#1a2632] border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-8 shadow-sm z-10"
  >
    <div class="flex items-center gap-4">
      <button
        class="p-2 hover:bg-slate-100 dark:hover:bg-white/5 rounded-full text-slate-500 dark:text-slate-400"
        @click="$emit('toggle-menu')"
      >
        <span class="material-symbols-outlined">menu</span>
      </button>
      <h2 class="font-medium text-slate-700 dark:text-slate-200">
        {{ currentFileName }}
      </h2>
    </div>
    <div class="flex items-center gap-4">
      <!-- Zoom Controls -->
      <div class="flex items-center bg-slate-100 dark:bg-slate-700 rounded-lg px-2 py-1 gap-2">
        <button
          class="p-1 hover:bg-white dark:hover:bg-slate-600 rounded text-slate-600 dark:text-slate-300"
          @click="$emit('zoom-out')"
        >
          <span class="material-symbols-outlined text-[20px]">remove</span>
        </button>
        <span class="text-sm font-medium w-12 text-center text-slate-700 dark:text-slate-200">
          {{ currentZoom }}%
        </span>
        <button
          class="p-1 hover:bg-white dark:hover:bg-slate-600 rounded text-slate-600 dark:text-slate-300"
          @click="$emit('zoom-in')"
        >
          <span class="material-symbols-outlined text-[20px]">add</span>
        </button>
      </div>
      <!-- Mark Complete Button -->
      <button
        v-if="!isTopicCompleted"
        class="bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        @click="$emit('mark-complete')"
      >
        Завершить
      </button>
      <div
        v-else
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400"
      >
        <span class="material-symbols-outlined text-[18px]">check</span>
        <span>Завершено</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stationId: {
    type: Number,
    required: true
  },
  station: {
    type: Object,
    default: () => ({})
  },
  currentLesson: {
    type: Object,
    default: () => ({})
  },
  currentFile: {
    type: Object,
    default: null
  },
  currentZoom: {
    type: Number,
    default: 100
  },
  isTopicCompleted: {
    type: Boolean,
    default: false
  }
})

defineEmits(['zoom-in', 'zoom-out', 'mark-complete', 'toggle-menu'])

const currentFileName = computed(() => {
  if (props.currentFile) {
    return (
      props.currentFile.originalName ||
      props.currentFile.original_name ||
      props.currentFile.fileName ||
      'Файл'
    )
  }
  if (props.currentLesson) {
    return props.currentLesson.title || 'Урок'
  }
  return 'Выберите материал'
})
</script>

<style scoped>
/* No additional styles needed - using Tailwind classes */
</style>
