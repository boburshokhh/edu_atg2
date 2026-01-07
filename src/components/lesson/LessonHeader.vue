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

      <!-- User profile section with dropdown -->
      <div class="relative">
        <button
          :class="[
            'flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-opacity-80',
            isDark 
              ? 'text-gray-300 hover:bg-gray-700' 
              : 'text-gray-700 hover:bg-gray-100'
          ]"
          @click="userDropdownOpen = !userDropdownOpen"
        >
          <div 
            class="w-10 h-10 rounded-full overflow-hidden ring-2 ring-offset-2 transition-all hover:ring-offset-4 cursor-pointer"
            :class="userAvatar 
              ? (isDark ? 'ring-blue-500' : 'ring-blue-500') 
              : (isDark 
                ? 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-500' 
                : 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-300')"
            @mouseenter="hoveringAvatar = true"
            @mouseleave="hoveringAvatar = false"
            @click.stop="showAvatarPreview = true"
          >
            <img 
              v-if="userAvatar" 
              :src="userAvatar" 
              :alt="userName"
              class="w-full h-full object-cover transition-transform duration-300"
              :class="hoveringAvatar ? 'scale-110' : ''"
            >
            <div
              v-else-if="userName"
              class="w-full h-full flex items-center justify-center text-white text-sm font-semibold"
            >
              {{ userName.charAt(0).toUpperCase() }}
            </div>
            <div
              v-else
              class="w-full h-full flex items-center justify-center text-white text-sm font-semibold"
            >
              ?
            </div>
          </div>
          <div
            v-if="userName"
            class="flex flex-col items-start hidden sm:block"
          >
            <span 
              :class="[
                'text-sm font-medium',
                isDark ? 'text-gray-100' : 'text-gray-900'
              ]"
            >
              {{ userName }}
            </span>
            <span 
              :class="[
                'text-xs opacity-70',
                isDark ? 'text-gray-400' : 'text-gray-500'
              ]"
            >
              {{ userRole }}
            </span>
          </div>
          <svg
            class="w-4 h-4 transition-transform duration-200 hidden sm:block"
            :class="[
              userDropdownOpen ? 'rotate-180' : '',
              isDark ? 'text-gray-400' : 'text-gray-500'
            ]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>
        
        <!-- User Dropdown -->
        <transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div 
            v-if="userDropdownOpen"
            :class="[
              'absolute right-0 mt-2 w-48 rounded-lg shadow-lg py-1 border z-50',
              isDark 
                ? 'bg-gray-800 border-gray-700' 
                : 'bg-white border-gray-100'
            ]"
            @click.stop
          >
            <router-link
              to="/profile"
              :class="[
                'block px-4 py-2 text-sm transition-colors',
                isDark 
                  ? 'text-gray-300 hover:bg-gray-700' 
                  : 'text-gray-700 hover:bg-gray-50'
              ]"
              @click="userDropdownOpen = false"
            >
              Профиль
            </router-link>
            <router-link
              to="/dashboard"
              :class="[
                'block px-4 py-2 text-sm transition-colors',
                isDark 
                  ? 'text-gray-300 hover:bg-gray-700' 
                  : 'text-gray-700 hover:bg-gray-50'
              ]"
              @click="userDropdownOpen = false"
            >
              Dashboard
            </router-link>
            <router-link
              v-if="isAdminUser"
              to="/admin"
              :class="[
                'block px-4 py-2 text-sm transition-colors font-medium',
                isDark 
                  ? 'text-blue-400 hover:bg-gray-700' 
                  : 'text-blue-600 hover:bg-blue-50'
              ]"
              @click="userDropdownOpen = false"
            >
              Админ-панель
            </router-link>
            <hr 
              :class="[
                'my-1',
                isDark ? 'border-gray-700' : 'border-gray-100'
              ]"
            >
            <button
              :class="[
                'w-full text-left px-4 py-2 text-sm transition-colors',
                isDark 
                  ? 'text-red-400 hover:bg-gray-700' 
                  : 'text-red-600 hover:bg-red-50'
              ]"
              @click="handleLogout"
            >
              Выйти
            </button>
          </div>
        </transition>
      </div>
    </div>

    <!-- Avatar Preview Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div 
          v-if="showAvatarPreview && isAuthenticated && userName"
          class="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-sm flex items-center justify-center"
          @click="showAvatarPreview = false; resetZoom()"
        >
          <div
            class="relative max-w-4xl max-h-[90vh] p-8"
            @click.stop
          >
            <!-- Close Button -->
            <button
              class="absolute -top-2 -right-2 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all z-10"
              @click="showAvatarPreview = false; resetZoom()"
            >
              <svg
                class="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>

            <!-- Avatar Image -->
            <div class="flex items-center justify-center bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
              <img 
                v-if="userAvatar"
                :src="userAvatar"
                :alt="userName || 'Пользователь'"
                class="rounded-full shadow-2xl transition-transform duration-300"
                :style="{ transform: `scale(${avatarScale})` }"
                style="max-width: 500px; max-height: 500px; object-fit: cover;"
              >
              <div
                v-else-if="userName"
                class="w-64 h-64 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-6xl font-bold"
                :style="{ transform: `scale(${avatarScale})` }"
              >
                {{ userName.charAt(0).toUpperCase() }}
              </div>
              <div
                v-else
                class="w-64 h-64 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-6xl font-bold"
                :style="{ transform: `scale(${avatarScale})` }"
              >
                ?
              </div>
            </div>

            <!-- User Info -->
            <div
              v-if="userName"
              class="mt-6 text-center text-white"
            >
              <h3 class="text-2xl font-bold mb-2">
                {{ userName }}
              </h3>
              <p class="text-blue-300 mb-4">
                {{ userRole }}
              </p>
            </div>

            <!-- Zoom Controls -->
            <div class="flex items-center justify-center gap-4 mt-6 bg-white/10 backdrop-blur-md rounded-xl px-6 py-3 border border-white/20">
              <button
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="avatarScale <= 0.5"
                @click="zoomOut"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
                  />
                </svg>
              </button>
              
              <span class="text-white text-sm font-medium px-4">{{ Math.round(avatarScale * 100) }}%</span>
              
              <button
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="avatarScale >= 3"
                @click="zoomIn"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"
                  />
                </svg>
              </button>

              <button
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all ml-4"
                @click="resetZoom"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
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

const emit = defineEmits([
  'mark-complete', 
  'toggle-sidebar', 
  'toggle-comments',
  'toggle-materials-sidebar',
  'toggle-fullscreen',
  'toggle-dark-mode'
])

const router = useRouter()

// State
const userDropdownOpen = ref(false)
const hoveringAvatar = ref(false)
const showAvatarPreview = ref(false)
const avatarScale = ref(1)

// User data
const isAuthenticated = computed(() => {
  return authService.getCurrentUser() !== null
})

const userName = computed(() => {
  const user = authService.getCurrentUser()
  if (user) {
    return user.full_name || user.username || 'Пользователь'
  }
  return 'Пользователь'
})

const userAvatar = computed(() => {
  const user = authService.getCurrentUser()
  if (user) {
    return user.avatar_url || user.avatar || null
  }
  return null
})

const userRole = computed(() => {
  const user = authService.getCurrentUser()
  if (!user) {
    return 'Студент'
  }
  const roles = {
    admin: 'Администратор',
    instructor: 'Преподаватель',
    user: 'Студент'
  }
  return roles[user.role] || 'Студент'
})

const isAdminUser = computed(() => {
  return authService.isAdmin()
})

// Zoom functions
const zoomIn = () => {
  if (avatarScale.value < 3) {
    avatarScale.value += 0.2
  }
}

const zoomOut = () => {
  if (avatarScale.value > 0.5) {
    avatarScale.value -= 0.2
  }
}

const resetZoom = () => {
  avatarScale.value = 1
}

// Logout function
const handleLogout = async () => {
  try {
    userDropdownOpen.value = false
    
    // Очищаем кеш аватарки
    localStorage.removeItem('avatar_key')
    localStorage.removeItem('avatar_url_cached')
    localStorage.removeItem('avatar_url_expires')
    
    // Выполняем выход
    const result = await authService.logout()
    
    if (result.success) {
      // Перенаправляем на главную
      router.push('/').then(() => {
        // Обновляем страницу для полной очистки состояния
        window.location.href = '/'
      })
    } else {
      // Даже если logout не удался на сервере, очищаем локально и перенаправляем
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
  } catch (error) {
    console.error('Logout error:', error)
    // В случае ошибки очищаем локально и перенаправляем
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    // Очищаем кеш аватарки
    localStorage.removeItem('avatar_key')
    localStorage.removeItem('avatar_url_cached')
    localStorage.removeItem('avatar_url_expires')
    window.location.href = '/'
  }
}

// Close dropdowns when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    userDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Google Material Symbols font should be loaded in index.html */

/* Fade animation for avatar preview modal */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
