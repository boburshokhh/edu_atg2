<template>
  <header
    class="h-14 md:h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 md:px-8 shadow-sm z-10 transition-all duration-300"
  >
    <div class="flex items-center gap-2 md:gap-4 min-w-0">
      <IconButton
        icon="menu"
        variant="default"
        aria-label="Меню"
        @click="handleToggleSidebar"
      />
      <h2 class="font-medium text-slate-700 text-sm md:text-base lg:text-lg truncate max-w-[150px] md:max-w-md min-w-0">
        {{ currentFileName || 'Выберите материал' }}
      </h2>
    </div>
    <div class="flex items-center gap-2 md:gap-4">
      <IconButton
        :icon="isFullscreen ? 'fullscreen_exit' : 'fullscreen'"
        variant="default"
        :title="isFullscreen ? 'Выйти из полноэкранного режима' : 'На весь экран'"
        @click="$emit('toggle-fullscreen')"
      />

      <AppButton
        v-if="!isTopicCompleted"
        variant="primary"
        @click="$emit('mark-complete')"
      >
        <span class="hidden md:inline">Завершить</span>
        <span class="md:hidden">
          <span class="material-symbols-outlined text-[18px] align-middle">check</span>
        </span>
      </AppButton>
      <AppButton
        v-else
        variant="success"
        disabled
      >
        <span class="material-symbols-outlined text-[16px] md:text-[18px]">check</span>
        <span class="hidden md:inline ml-2">Завершено</span>
      </AppButton>
      <IconButton
        icon="chat_bubble"
        :variant="isCommentsOpen ? 'primary' : 'default'"
        title="Комментарии"
        @click="$emit('toggle-comments')"
      />
    </div>
  </header>
</template>

<script setup>
import IconButton from '@/components/ui/IconButton.vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  currentFileName: {
    type: String,
    default: ''
  },
  isTopicCompleted: {
    type: Boolean,
    default: false
  },
  isCommentsOpen: {
    type: Boolean,
    default: false
  },
  isFullscreen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['mark-complete', 'toggle-sidebar', 'toggle-comments', 'toggle-fullscreen'])

const handleToggleSidebar = () => {
  emit('toggle-sidebar')
}
</script>

<style scoped>
/* No additional styles needed - using Tailwind */
</style>
