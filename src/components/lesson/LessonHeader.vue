<template>
  <header
    :class="[
      'h-16 border-b flex items-center justify-between px-6 shrink-0 z-20 transition-colors duration-200',
      isDark 
        ? 'bg-gray-800 border-gray-700' 
        : 'bg-white border-gray-200'
    ]"
  >
    <!-- Left section: Menu & Breadcrumbs -->
    <div class="flex items-center gap-4">
      <button
        :class="[
          'p-2 rounded-full transition-colors',
          isDark 
            ? 'hover:bg-gray-700 text-gray-400' 
            : 'hover:bg-gray-100 text-gray-500'
        ]"
        @click="$emit('toggle-sidebar')"
      >
        <span class="material-symbols-outlined text-xl">menu</span>
      </button>

      <!-- Breadcrumbs -->
      <nav class="hidden md:flex items-center text-sm">
        <router-link
          to="/"
          :class="[
            'hover:text-primary cursor-pointer transition-colors',
            isDark ? 'text-gray-400' : 'text-gray-500'
          ]"
        >
          Главная
        </router-link>
        <span 
          :class="[
            'material-symbols-outlined text-base mx-2',
            isDark ? 'text-gray-600' : 'text-gray-400'
          ]"
        >
          chevron_right
        </span>
        <span
          :class="[
            'hover:text-primary cursor-pointer transition-colors',
            isDark ? 'text-gray-400' : 'text-gray-500'
          ]"
        >
          Программы
        </span>
        <span 
          :class="[
            'material-symbols-outlined text-base mx-2',
            isDark ? 'text-gray-600' : 'text-gray-400'
          ]"
        >
          chevron_right
        </span>
        <span
          :class="[
            'font-medium',
            isDark ? 'text-gray-100' : 'text-gray-900'
          ]"
        >
          Модуль {{ currentLessonIndex + 1 }}
        </span>
      </nav>

      <!-- Mobile: File name -->
      <h2 
        class="md:hidden font-medium text-sm truncate max-w-[150px]"
        :class="isDark ? 'text-gray-100' : 'text-gray-700'"
      >
        {{ currentFileName || 'Выберите материал' }}
      </h2>
    </div>

    <!-- Right section: Actions & Profile -->
    <div class="flex items-center gap-4">
      <!-- Dark mode toggle -->
      <button
        :class="[
          'p-2 rounded-full transition-colors',
          isDark 
            ? 'hover:bg-gray-700 text-gray-400' 
            : 'hover:bg-gray-100 text-gray-500'
        ]"
        title="Переключить тему"
        @click="$emit('toggle-dark-mode')"
      >
        <span class="material-symbols-outlined text-xl">
          {{ isDark ? 'light_mode' : 'dark_mode' }}
        </span>
      </button>

      <!-- Fullscreen toggle -->
      <button
        :class="[
          'p-2 rounded-full transition-colors',
          isDark 
            ? 'hover:bg-gray-700 text-gray-400' 
            : 'hover:bg-gray-100 text-gray-500'
        ]"
        :title="isFullscreen ? 'Выйти из полноэкранного режима' : 'На весь экран'"
        @click="$emit('toggle-fullscreen')"
      >
        <span class="material-symbols-outlined text-xl">
          {{ isFullscreen ? 'fullscreen_exit' : 'fullscreen' }}
        </span>
      </button>

      <!-- Materials toggle -->
      <button
        :class="[
          'p-2 rounded-full transition-colors',
          isMaterialsSidebarOpen 
            ? 'bg-primary text-white' 
            : isDark 
              ? 'hover:bg-gray-700 text-gray-400' 
              : 'hover:bg-gray-100 text-gray-500'
        ]"
        title="Материалы курса"
        @click="$emit('toggle-materials-sidebar')"
      >
        <span class="material-symbols-outlined text-xl">folder</span>
      </button>

      <!-- Comments toggle -->
      <button
        :class="[
          'p-2 rounded-full transition-colors',
          isCommentsOpen 
            ? 'bg-primary text-white' 
            : isDark 
              ? 'hover:bg-gray-700 text-gray-400' 
              : 'hover:bg-gray-100 text-gray-500'
        ]"
        title="Комментарии"
        @click="$emit('toggle-comments')"
      >
        <span class="material-symbols-outlined text-xl">chat_bubble</span>
      </button>

      <!-- User profile section -->
      <div 
        :class="[
          'flex items-center gap-3 pl-4 border-l',
          isDark ? 'border-gray-700' : 'border-gray-200'
        ]"
      >
        <div class="text-right hidden sm:block">
          <p 
            :class="[
              'text-sm font-medium',
              isDark ? 'text-gray-100' : 'text-gray-900'
            ]"
          >
            {{ userName }}
          </p>
          <p 
            :class="[
              'text-xs',
              isDark ? 'text-gray-400' : 'text-gray-500'
            ]"
          >
            {{ userRole }}
          </p>
        </div>
        <div 
          :class="[
            'h-10 w-10 rounded-full flex items-center justify-center overflow-hidden border',
            isDark 
              ? 'bg-gray-600 border-gray-500' 
              : 'bg-gray-200 border-gray-300'
          ]"
        >
          <span 
            :class="[
              'material-symbols-outlined text-xl',
              isDark ? 'text-gray-300' : 'text-gray-400'
            ]"
          >
            person
          </span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import authService from '@/services/auth'

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
  isMaterialsSidebarOpen: {
    type: Boolean,
    default: false
  },
  isFullscreen: {
    type: Boolean,
    default: false
  },
  isDark: {
    type: Boolean,
    default: false
  },
  currentLessonIndex: {
    type: Number,
    default: 0
  },
  courseTitle: {
    type: String,
    default: ''
  }
})

defineEmits([
  'mark-complete', 
  'toggle-sidebar', 
  'toggle-comments',
  'toggle-materials-sidebar',
  'toggle-fullscreen',
  'toggle-dark-mode'
])

// User data
const userName = computed(() => {
  const user = authService.getCurrentUser()
  if (user) {
    return user.full_name || user.username || 'Пользователь'
  }
  return 'Пользователь'
})

const userRole = computed(() => {
  const user = authService.getCurrentUser()
  const role = user ? user.role : 'user'
  const roles = {
    admin: 'Администратор',
    instructor: 'Преподаватель',
    user: 'Студент'
  }
  return roles[role] || 'Студент'
})
</script>

<style scoped>
/* Google Material Symbols font should be loaded in index.html */
</style>
