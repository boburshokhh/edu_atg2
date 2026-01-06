<template>
  <header
    class="h-14 md:h-16 bg-white border-b border-slate-200 flex flex-col shadow-sm z-10 transition-all duration-300"
  >
    <!-- Main header row -->
    <div class="flex items-center justify-between px-4 md:px-8 h-full">
      <div class="flex items-center gap-2 md:gap-4 min-w-0 flex-1">
        <IconButton
          icon="menu"
          variant="default"
          aria-label="Меню"
          @click="handleToggleSidebar"
        />
        
        <!-- Breadcrumbs -->
        <nav v-if="breadcrumbs.length > 0" class="hidden md:flex items-center gap-1.5 text-xs text-slate-500">
          <template v-for="(crumb, index) in breadcrumbs" :key="index">
            <span
              v-if="index > 0"
              class="material-symbols-outlined text-[16px] text-slate-400"
            >
              chevron_right
            </span>
            <span
              :class="[
                'truncate max-w-[120px]',
                index === breadcrumbs.length - 1 ? 'text-slate-700 font-medium' : 'hover:text-slate-700 cursor-pointer'
              ]"
              @click="index < breadcrumbs.length - 1 && $emit('navigate', crumb.path)"
            >
              {{ crumb.label }}
            </span>
          </template>
        </nav>
        
        <!-- File name (fallback if no breadcrumbs) -->
        <h2
          v-if="breadcrumbs.length === 0"
          class="font-medium text-slate-700 text-sm md:text-base lg:text-lg truncate max-w-[150px] md:max-w-md min-w-0"
        >
          {{ currentFileName || 'Выберите материал' }}
        </h2>
        <h2
          v-else
          class="font-medium text-slate-700 text-sm md:text-base lg:text-lg truncate max-w-[150px] md:max-w-md min-w-0"
        >
          {{ currentFileName || 'Выберите материал' }}
        </h2>
      </div>
      
      <!-- Progress indicator -->
      <div
        v-if="showProgress && lessonProgress > 0"
        class="hidden md:flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg mr-4"
      >
        <div class="w-24 h-1.5 bg-slate-200 rounded-full overflow-hidden">
          <div
            class="h-full bg-primary rounded-full transition-all duration-300"
            :style="{ width: `${lessonProgress}%` }"
          />
        </div>
        <span class="text-xs font-medium text-slate-600">{{ Math.round(lessonProgress) }}%</span>
      </div>
      
      <div class="flex items-center gap-2 md:gap-4">
    <div class="flex items-center gap-2 md:gap-4">
      <IconButton
        :icon="isFullscreen ? 'fullscreen_exit' : 'fullscreen'"
        variant="default"
        :title="isFullscreen ? 'Выйти из полноэкранного режима' : 'На весь экран'"
        @click="$emit('toggle-fullscreen')"
      />

        <transition name="button-fade" mode="out-in">
          <AppButton
            v-if="!isTopicCompleted"
            key="complete"
            variant="primary"
            class="transition-all duration-200 hover:scale-105 active:scale-95"
            @click="handleMarkComplete"
          >
            <span class="hidden md:inline">Завершить</span>
            <span class="md:hidden">
              <span class="material-symbols-outlined text-[18px] align-middle">check</span>
            </span>
          </AppButton>
          <AppButton
            v-else
            key="completed"
            variant="success"
            disabled
            class="transition-all duration-200"
          >
            <span class="material-symbols-outlined text-[16px] md:text-[18px]">check_circle</span>
            <span class="hidden md:inline ml-2">Завершено</span>
          </AppButton>
        </transition>
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
import { computed } from 'vue'
import IconButton from '@/components/ui/IconButton.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { ElMessage } from 'element-plus'

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
  },
  // Breadcrumbs for navigation
  breadcrumbs: {
    type: Array,
    default: () => []
  },
  // Lesson progress (0-100)
  lessonProgress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  // Show progress indicator
  showProgress: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['mark-complete', 'toggle-sidebar', 'toggle-comments', 'toggle-fullscreen', 'navigate'])

const handleToggleSidebar = () => {
  emit('toggle-sidebar')
}

const handleMarkComplete = () => {
  emit('mark-complete')
  // Visual feedback
  ElMessage.success('Урок отмечен как завершенный!')
}
</script>

<style scoped>
/* Button transition */
.button-fade-enter-active,
.button-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.button-fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.button-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Progress bar animation */
@keyframes progress-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  header {
    padding: 0.5rem;
  }
}
</style>
