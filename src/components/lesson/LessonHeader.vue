<template>
  <header
    class="h-14 md:h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 md:px-8 shadow-sm z-10 transition-all duration-300"
  >
    <div class="flex items-center gap-2 md:gap-4">
      <button
        class="p-2 hover:bg-slate-100 rounded-full text-slate-500 transition-colors"
        @click="handleToggleSidebar"
      >
        <span class="material-symbols-outlined text-[20px] md:text-[24px]">menu</span>
      </button>
      <h2 class="font-medium text-slate-700 text-sm md:text-base lg:text-lg truncate max-w-[150px] md:max-w-md">
        {{ currentFileName || 'Выберите материал' }}
      </h2>
    </div>
    <div class="flex items-center gap-2 md:gap-4">
      <div class="hidden sm:flex items-center bg-slate-100 rounded-lg px-2 py-1 gap-2">
        <button
          class="p-1 hover:bg-white rounded text-slate-600 transition-colors"
          :disabled="currentZoom <= 50"
          @click="$emit('zoom-out')"
        >
          <span class="material-symbols-outlined text-[18px] md:text-[20px]">remove</span>
        </button>
        <span class="text-xs md:text-sm font-medium w-8 md:w-12 text-center text-slate-700">{{ currentZoom }}%</span>
        <button
          class="p-1 hover:bg-white rounded text-slate-600 transition-colors"
          :disabled="currentZoom >= 200"
          @click="$emit('zoom-in')"
        >
          <span class="material-symbols-outlined text-[18px] md:text-[20px]">add</span>
        </button>
      </div>
      
      <!-- Mobile Zoom Controls (Simplified) -->
      <div class="flex sm:hidden items-center gap-1">
         <button
          class="p-2 hover:bg-slate-100 rounded-full text-slate-600"
          @click="$emit('zoom-out')"
        >
          <span class="material-symbols-outlined text-[20px]">remove</span>
        </button>
        <button
          class="p-2 hover:bg-slate-100 rounded-full text-slate-600"
          @click="$emit('zoom-in')"
        >
          <span class="material-symbols-outlined text-[20px]">add</span>
        </button>
      </div>

      <button
        v-if="!isTopicCompleted"
        class="bg-primary hover:bg-blue-600 text-white px-3 py-1.5 md:px-4 md:py-2 rounded-lg text-xs md:text-sm font-medium transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100"
        @click="$emit('mark-complete')"
      >
        <span class="hidden md:inline">Завершить</span>
        <span class="md:hidden"><span class="material-symbols-outlined text-[18px] align-middle">check</span></span>
      </button>
      <div
        v-else
        class="bg-emerald-50 text-emerald-700 px-3 py-1.5 md:px-4 md:py-2 rounded-lg text-xs md:text-sm font-medium flex items-center gap-2 border border-emerald-100"
      >
        <span class="material-symbols-outlined text-[16px] md:text-[18px]">check</span>
        <span class="hidden md:inline">Завершено</span>
      </div>
      <button
        :class="[
          'p-2 rounded-lg transition-colors',
          isCommentsOpen ? 'bg-primary/10 text-primary' : 'text-slate-500 hover:bg-slate-100'
        ]"
        @click="$emit('toggle-comments')"
        title="Комментарии"
      >
        <span
          class="material-symbols-outlined text-[20px] md:text-[24px]"
          :style="isCommentsOpen ? { fontVariationSettings: '\'FILL\' 1' } : {}"
        >
          chat_bubble
        </span>
      </button>
    </div>
  </header>
</template>

<script setup>
const props = defineProps({
  currentFileName: {
    type: String,
    default: ''
  },
  currentZoom: {
    type: Number,
    default: 100
  },
  isTopicCompleted: {
    type: Boolean,
    default: false
  },
  isCommentsOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['zoom-in', 'zoom-out', 'mark-complete', 'toggle-sidebar', 'toggle-comments'])

const handleToggleSidebar = () => {
  emit('toggle-sidebar')
}
</script>

<style scoped>
/* No additional styles needed - using Tailwind */
</style>
