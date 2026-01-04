<template>
  <header
    class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm z-10"
  >
    <div class="flex items-center gap-4">
      <button
        class="p-2 hover:bg-slate-100 rounded-full text-slate-500"
        @click="handleToggleSidebar"
      >
        <span class="material-symbols-outlined">menu</span>
      </button>
      <h2 class="font-medium text-slate-700">
        {{ currentFileName || 'Выберите материал' }}
      </h2>
    </div>
    <div class="flex items-center gap-4">
      <div class="flex items-center bg-slate-100 rounded-lg px-2 py-1 gap-2">
        <button
          class="p-1 hover:bg-white rounded text-slate-600"
          :disabled="currentZoom <= 50"
          @click="$emit('zoom-out')"
        >
          <span class="material-symbols-outlined text-[20px]">remove</span>
        </button>
        <span class="text-sm font-medium w-12 text-center text-slate-700">{{ currentZoom }}%</span>
        <button
          class="p-1 hover:bg-white rounded text-slate-600"
          :disabled="currentZoom >= 200"
          @click="$emit('zoom-in')"
        >
          <span class="material-symbols-outlined text-[20px]">add</span>
        </button>
      </div>
      <button
        v-if="!isTopicCompleted"
        class="bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        @click="$emit('mark-complete')"
      >
        Завершить
      </button>
      <div
        v-else
        class="bg-emerald-50 text-emerald-700 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2"
      >
        <span class="material-symbols-outlined text-[18px]">check</span>
        <span>Завершено</span>
      </div>
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
  }
})

const emit = defineEmits(['zoom-in', 'zoom-out', 'mark-complete', 'toggle-sidebar'])

const handleToggleSidebar = () => {
  emit('toggle-sidebar')
}
</script>

<style scoped>
/* No additional styles needed - using Tailwind */
</style>
