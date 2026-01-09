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
        aria-label="Открыть меню"
        @click="$emit('toggle-sidebar')"
      >
        <span class="material-symbols-outlined text-xl">menu</span>
      </button>

      <!-- Breadcrumbs -->
      <nav 
        class="hidden md:flex items-center text-sm" 
        aria-label="Навигационная цепочка"
      >
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
          aria-hidden="true"
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
          aria-hidden="true"
        >
          chevron_right
        </span>
        <span
          :class="[
            'font-medium',
            isDark ? 'text-gray-100' : 'text-gray-900'
          ]"
          aria-current="page"
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
        :aria-label="isDark ? 'Включить светлую тему' : 'Включить темную тему'"
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
        :aria-label="isFullscreen ? 'Выйти из полноэкранного режима' : 'Полноэкранный режим'"
        :aria-pressed="isFullscreen"
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
        aria-label="Материалы курса"
        :aria-pressed="isMaterialsSidebarOpen"
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
        aria-label="Комментарии"
        :aria-pressed="isCommentsOpen"
        @click="$emit('toggle-comments')"
      >
        <span class="material-symbols-outlined text-xl">chat_bubble</span>
      </button>

      <!-- User profile section with dropdown -->
      <div class="relative" ref="dropdownRef">
        <button
          :class="[
            'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
            isDark 
              ? 'text-gray-300 hover:bg-gray-700/50' 
              : 'text-gray-700 hover:bg-gray-100'
          ]"
          aria-label="Меню пользователя"
          :aria-expanded="userDropdownOpen"
          aria-haspopup="true"
          @click="toggleDropdown"
        >
          <!-- Avatar -->
          <div 
            class="w-10 h-10 rounded-full overflow-hidden ring-2 ring-offset-2 transition-all hover:ring-offset-4 cursor-pointer shrink-0"
            :class="userAvatar 
              ? (isDark ? 'ring-blue-500' : 'ring-blue-500') 
              : (isDark 
                ? 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-500' 
                : 'bg-gradient-to-br from-blue-600 to-blue-700 ring-gray-300')"
            @mouseenter="hoveringAvatar = true"
            @mouseleave="hoveringAvatar = false"
            @click.stop="openAvatarPreview"
          >
            <img 
              v-if="userAvatar && !imageError" 
              :src="userAvatar" 
              :alt="`Аватар ${userName}`"
              class="w-full h-full object-cover transition-transform duration-300"
              :class="hoveringAvatar ? 'scale-110' : ''"
              @error="handleImageError"
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
          
          <!-- User Info - Always visible on md+ -->
          <div
            v-if="userName"
            class="flex flex-col items-start min-w-0 hidden md:block"
          >
            <!-- ФИО сверху -->
            <span 
              :class="[
                'text-sm font-semibold truncate max-w-[120px] leading-tight',
                isDark ? 'text-gray-100' : 'text-gray-900'
              ]"
              :title="userName"
            >
              {{ userName }}
            </span>
            <!-- Роль снизу маленьким шрифтом -->
            <span 
              :class="[
                'text-[10px] font-normal mt-0.5 leading-tight',
                isDark ? 'text-blue-400' : 'text-blue-600'
              ]"
            >
              {{ userRole }}
            </span>
          </div>
          
          <!-- Mobile: Show only role badge -->
          <div
            v-if="userName"
            class="md:hidden"
          >
            <span 
              :class="[
                'text-xs font-medium px-2 py-1 rounded-full',
                isDark ? 'bg-blue-900/50 text-blue-300' : 'bg-blue-100 text-blue-700'
              ]"
            >
              {{ userRole }}
            </span>
          </div>
          
          <!-- Dropdown arrow -->
          <svg
            class="w-4 h-4 transition-transform duration-200 shrink-0 hidden md:block"
            :class="[
              userDropdownOpen ? 'rotate-180' : '',
              isDark ? 'text-gray-400' : 'text-gray-500'
            ]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
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
            role="menu"
            aria-orientation="vertical"
          >
            <router-link
              to="/profile"
              :class="[
                'block px-4 py-2 text-sm transition-colors',
                isDark 
                  ? 'text-gray-300 hover:bg-gray-700' 
                  : 'text-gray-700 hover:bg-gray-50'
              ]"
              role="menuitem"
              @click="closeDropdown"
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
              role="menuitem"
              @click="closeDropdown"
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
              role="menuitem"
              @click="closeDropdown"
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
              role="menuitem"
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
          role="dialog"
          aria-modal="true"
          aria-labelledby="avatar-preview-title"
          @click="closeAvatarPreview"
          @keydown.esc="closeAvatarPreview"
        >
          <div
            class="relative max-w-4xl max-h-[90vh] p-8"
            @click.stop
            ref="modalRef"
          >
            <!-- Close Button -->
            <button
              class="absolute -top-2 -right-2 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all z-10"
              aria-label="Закрыть превью"
              @click="closeAvatarPreview"
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
                v-if="userAvatar && !imageError"
                :src="userAvatar"
                :alt="`Полное фото ${userName || 'Пользователь'}`"
                class="rounded-full shadow-2xl transition-transform duration-300"
                :style="{ transform: `scale(${avatarScale})` }"
                style="max-width: 500px; max-height: 500px; object-fit: cover;"
                @error="handleImageError"
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
              id="avatar-preview-title"
            >
              <h3 class="text-2xl font-bold mb-2">
                {{ userName }}
              </h3>
              <p class="text-blue-300 mb-4">
                {{ userRole }}
              </p>
            </div>

            <!-- Zoom Controls -->
            <div 
              class="flex items-center justify-center gap-4 mt-6 bg-white/10 backdrop-blur-md rounded-xl px-6 py-3 border border-white/20"
              role="toolbar"
              aria-label="Управление масштабом"
            >
              <button
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="avatarScale <= 0.5"
                aria-label="Уменьшить"
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
              
              <span 
                class="text-white text-sm font-medium px-4" 
                aria-live="polite"
              >
                {{ Math.round(avatarScale * 100) }}%
              </span>
              
              <button
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="avatarScale >= 3"
                aria-label="Увеличить"
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
                aria-label="Сбросить масштаб"
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
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
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

// Refs
const dropdownRef = ref(null)
const modalRef = ref(null)

// State
const userDropdownOpen = ref(false)
const hoveringAvatar = ref(false)
const showAvatarPreview = ref(false)
const avatarScale = ref(1)
const imageError = ref(false)
const previousFocusedElement = ref(null)

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

// Utility: Safe localStorage
const safeLocalStorage = {
  getItem(key) {
    try {
      return localStorage.getItem(key)
    } catch {
      return null
    }
  },
  setItem(key, value) {
    try {
      localStorage.setItem(key, value)
    } catch {
      console.warn('localStorage недоступен')
    }
  },
  removeItem(key) {
    try {
      localStorage.removeItem(key)
    } catch {
      console.warn('localStorage недоступен')
    }
  }
}

// Clear avatar cache utility
const clearAvatarCache = () => {
  safeLocalStorage.removeItem('avatar_key')
  safeLocalStorage.removeItem('avatar_url_cached')
  safeLocalStorage.removeItem('avatar_url_expires')
}

// Image error handler
const handleImageError = () => {
  imageError.value = true
}

// Dropdown functions
const toggleDropdown = () => {
  userDropdownOpen.value = !userDropdownOpen.value
}

const closeDropdown = () => {
  userDropdownOpen.value = false
}

// Avatar preview functions
const openAvatarPreview = () => {
  if (!isAuthenticated.value || !userName.value) return
  
  previousFocusedElement.value = document.activeElement
  showAvatarPreview.value = true
  
  nextTick(() => {
    if (modalRef.value) {
      modalRef.value.focus()
    }
  })
}

const closeAvatarPreview = () => {
  showAvatarPreview.value = false
  resetZoom()
  
  // Restore focus
  nextTick(() => {
    if (previousFocusedElement.value) {
      previousFocusedElement.value.focus()
    }
  })
}

// Zoom functions with limits
const ZOOM_STEP = 0.2
const MIN_ZOOM = 0.5
const MAX_ZOOM = 3

const zoomIn = () => {
  if (avatarScale.value < MAX_ZOOM) {
    avatarScale.value = Math.min(avatarScale.value + ZOOM_STEP, MAX_ZOOM)
  }
}

const zoomOut = () => {
  if (avatarScale.value > MIN_ZOOM) {
    avatarScale.value = Math.max(avatarScale.value - ZOOM_STEP, MIN_ZOOM)
  }
}

const resetZoom = () => {
  avatarScale.value = 1
}

// Logout function
const handleLogout = async () => {
  try {
    closeDropdown()
    
    clearAvatarCache()
    
    const result = await authService.logout()
    
    if (result.success) {
      // Single navigation - no double redirect
      await router.push('/')
    } else {
      // Fallback: clear local data
      safeLocalStorage.removeItem('auth_token')
      safeLocalStorage.removeItem('user')
      await router.push('/')
    }
  } catch (error) {
    console.error('Logout error:', error)
    // Emergency cleanup
    safeLocalStorage.removeItem('auth_token')
    safeLocalStorage.removeItem('user')
    clearAvatarCache()
    await router.push('/')
  }
}

// Click outside handler - more specific
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    closeDropdown()
  }
}

// Keyboard handler for modal
const handleKeydown = (event) => {
  if (event.key === 'Escape' && showAvatarPreview.value) {
    closeAvatarPreview()
  }
}

// Focus trap for modal
const setupFocusTrap = () => {
  if (!modalRef.value) return
  
  const focusableElements = modalRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  
  if (focusableElements.length === 0) return
  
  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]
  
  const handleTabKey = (e) => {
    if (e.key !== 'Tab') return
    
    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault()
        lastElement.focus()
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    }
  }
  
  document.addEventListener('keydown', handleTabKey)
  
  return () => {
    document.removeEventListener('keydown', handleTabKey)
  }
}

// Watch for modal open/close
watch(showAvatarPreview, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
    nextTick(() => {
      const cleanup = setupFocusTrap()
      // Store cleanup function
      if (cleanup) {
        // Will be called on unmount or modal close
      }
    })
  } else {
    document.body.style.overflow = ''
  }
})

// Reset image error when avatar changes
watch(userAvatar, () => {
  imageError.value = false
})

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = '' // Cleanup
})
</script>

<style scoped>
/* Fade animation for avatar preview modal */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Prevent body scroll when modal is open */
body.modal-open {
  overflow: hidden;
}
</style>