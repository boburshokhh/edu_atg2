<template>
  <header 
    ref="headerRef"
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-out"
    :class="[
      isLightTheme
        ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100' 
        : 'bg-transparent',
      isLightTheme ? 'py-4' : 'py-6'
    ]"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <router-link 
          to="/" 
          class="flex items-center space-x-3 group"
        >
          <div class="relative">
            <img 
              src="/logo.e75fb66.svg" 
              alt="Asia Trans Gas" 
              class="h-8 w-auto transition-all duration-300"
              :class="isScrolled ? 'opacity-100' : 'opacity-100'"
              @error="handleLogoError"
            />
          </div>

        </router-link>

        <!-- Desktop Navigation -->
        <nav class="hidden lg:flex items-center space-x-2">
          <router-link 
            to="/" 
            class="nav-link relative group"
            :class="[
              isLightTheme ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white',
              $route.name === 'Home' ? (isLightTheme ? 'text-gray-900 font-semibold' : 'text-white font-semibold') : ''
            ]"
          >
            {{ $t('nav.home') }}
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full"></div>
          </router-link>
          
          <a 
            href="#about" 
            @click.prevent="scrollToAbout"
            class="nav-link cursor-pointer relative group"
            :class="isLightTheme ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white'"
          >
            {{ $t('nav.about') }}
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full"></div>
          </a>
          
          <router-link 
            to="/stations" 
            class="nav-link relative group"
            :class="[
              isLightTheme ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white',
              $route.name === 'Stations' ? (isLightTheme ? 'text-gray-900 font-semibold' : 'text-white font-semibold') : ''
            ]"
          >
            {{ $t('nav.stations') }}
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full"></div>
          </router-link>
        </nav>

        <!-- Right Actions -->
        <div class="flex items-center space-x-3">
          <!-- Language Switcher -->
          <div class="relative">
            <button
              @click="langDropdownOpen = !langDropdownOpen"
              class="flex items-center space-x-1 px-3 py-2 rounded-lg transition-all duration-200"
              :class="isLightTheme 
                ? 'text-gray-700 hover:bg-gray-100' 
                : 'text-white/90 hover:bg-white/10'"
            >
              <span class="text-sm font-medium">{{ currentLocale.toUpperCase() }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <!-- Dropdown -->
            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <div 
                v-if="langDropdownOpen"
                class="absolute right-0 mt-2 w-32 bg-white rounded-lg shadow-lg py-1 border border-gray-100"
                @click="langDropdownOpen = false"
              >
                <button
                  @click="changeLanguage('ru')"
                  class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                  :class="currentLocale === 'ru' ? 'text-tamex-blue-600 font-semibold' : 'text-gray-700'"
                >
                  🇷🇺 Русский
                </button>
                <button
                  @click="changeLanguage('en')"
                  class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                  :class="currentLocale === 'en' ? 'text-tamex-blue-600 font-semibold' : 'text-gray-700'"
                >
                  🇺🇸 English
                </button>
              </div>
            </transition>
          </div>

          <!-- Auth Buttons -->
          <template v-if="!isAuthenticated">
            <router-link
              to="/login"
              class="hidden md:inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200"
              :class="isLightTheme 
                ? 'text-gray-700 hover:bg-gray-100' 
                : 'text-white/90 hover:bg-white/10'"
            >
              {{ $t('nav.login') }}
            </router-link>
          </template>

          <!-- User Menu -->
          <template v-else>
            <div class="relative hidden md:block">
              <button
                @click="userDropdownOpen = !userDropdownOpen"
                class="flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-opacity-80"
                :class="isLightTheme 
                  ? 'text-gray-700 hover:bg-gray-100' 
                  : 'text-white/90 hover:bg-white/10'"
              >
                <div 
                  class="w-10 h-10 rounded-full overflow-hidden ring-2 ring-offset-2 transition-all hover:ring-offset-4"
                  :class="userAvatar ? 'ring-blue-500' : 'bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 ring-gray-300'"
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
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-white text-sm font-semibold">
                    {{ userName.charAt(0).toUpperCase() }}
                  </div>
                </div>
                <div class="flex flex-col items-start">
                  <span class="text-sm font-medium">{{ userName }}</span>
                  <span class="text-xs opacity-70">{{ userRole }}</span>
                </div>
                <svg class="w-4 h-4 transition-transform duration-200" :class="userDropdownOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
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
                  class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 border border-gray-100"
                  @click="userDropdownOpen = false"
                >
                  <router-link
                    to="/profile"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    {{ $t('nav.profile') }}
                  </router-link>
                  <router-link
                    to="/dashboard"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    {{ $t('nav.dashboard') }}
                  </router-link>
                  <router-link
                    v-if="isAdminUser"
                    to="/admin"
                    class="block px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 transition-colors font-medium"
                  >
                    Админ-панель
                  </router-link>
                  <hr class="my-1 border-gray-100" />
                  <button
                    @click="logout"
                    class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    {{ $t('nav.logout') }}
                  </button>
                </div>
              </transition>
            </div>
          </template>

          <!-- Mobile Menu Button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="lg:hidden p-2 rounded-lg transition-all duration-200"
            :class="isLightTheme 
              ? 'text-gray-700 hover:bg-gray-100' 
              : 'text-white hover:bg-white/10'"
          >
            <svg 
              class="w-6 h-6" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                v-if="!mobileMenuOpen"
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M4 6h16M4 12h16M4 18h16" 
              />
              <path 
                v-else
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M6 18L18 6M6 6l12 12" 
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="transform opacity-0 -translate-y-2"
        enter-to-class="transform opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="transform opacity-100 translate-y-0"
        leave-to-class="transform opacity-0 -translate-y-2"
      >
        <div 
          v-if="mobileMenuOpen" 
          class="lg:hidden mt-4 pb-4 border-t"
          :class="isLightTheme 
            ? 'border-gray-100 bg-white/95 backdrop-blur-md' 
            : 'border-white/10 bg-white/10 backdrop-blur-md'"
        >
          <div class="flex flex-col space-y-1 mt-4">
            <router-link
              to="/"
              class="mobile-nav-link"
              :class="isLightTheme ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
              @click="mobileMenuOpen = false"
            >
              {{ $t('nav.home') }}
            </router-link>
            
            <a
              href="#about"
              @click.prevent="scrollToAbout(); mobileMenuOpen = false"
              class="mobile-nav-link cursor-pointer"
              :class="isLightTheme ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
            >
              {{ $t('nav.about') }}
            </a>
            
            <router-link
              to="/stations"
              class="mobile-nav-link"
              :class="isLightTheme ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
              @click="mobileMenuOpen = false"
            >
              {{ $t('nav.stations') }}
            </router-link>

            <!-- Mobile Auth Buttons -->
            <template v-if="!isAuthenticated">
              <div class="pt-4 space-y-2" :class="isLightTheme ? 'border-t border-gray-100' : 'border-t border-white/10'">
                <router-link
                  to="/login"
                  class="block w-full text-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all"
                  :class="isLightTheme 
                    ? 'text-gray-700 bg-gray-100 hover:bg-gray-200' 
                    : 'text-white bg-white/10 hover:bg-white/20'"
                  @click="mobileMenuOpen = false"
                >
                  {{ $t('nav.login') }}
                </router-link>
              </div>
            </template>

            <!-- Mobile User Menu -->
            <template v-else>
              <div class="pt-4 space-y-1" :class="isLightTheme ? 'border-t border-gray-100' : 'border-t border-white/10'">
                <div 
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg"
                  :class="isLightTheme ? 'bg-gray-50' : 'bg-white/5'"
                >
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 flex items-center justify-center text-white font-semibold">
                    {{ userName.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-sm font-medium" :class="isLightTheme ? 'text-gray-900' : 'text-white'">
                      {{ userName }}
                    </p>
                  </div>
                </div>
                <router-link
                  to="/profile"
                  class="mobile-nav-link"
                  :class="isLightTheme ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
                  @click="mobileMenuOpen = false"
                >
                  {{ $t('nav.profile') }}
                </router-link>
                <button
                  @click="logout"
                  class="mobile-nav-link w-full text-left text-red-600"
                  :class="isLightTheme ? 'hover:bg-red-50' : 'hover:bg-red-500/10'"
                >
                  {{ $t('nav.logout') }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </transition>
    </div>

    <!-- Avatar Preview Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div 
          v-if="showAvatarPreview"
          class="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-sm flex items-center justify-center"
          @click="showAvatarPreview = false; resetZoom()"
        >
          <div class="relative max-w-4xl max-h-[90vh] p-8" @click.stop>
            <!-- Close Button -->
            <button
              @click="showAvatarPreview = false; resetZoom()"
              class="absolute -top-2 -right-2 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all z-10"
            >
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <!-- Avatar Image -->
            <div class="flex items-center justify-center bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
              <img 
                v-if="userAvatar"
                :src="userAvatar"
                :alt="userName"
                class="rounded-full shadow-2xl transition-transform duration-300"
                :style="{ transform: `scale(${avatarScale})` }"
                style="max-width: 500px; max-height: 500px; object-fit: cover;"
              />
              <div v-else class="w-64 h-64 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-6xl font-bold">
                {{ userName.charAt(0).toUpperCase() }}
              </div>
            </div>

            <!-- User Info -->
            <div class="mt-6 text-center text-white">
              <h3 class="text-2xl font-bold mb-2">{{ userName }}</h3>
              <p class="text-blue-300 mb-4">{{ userRole }}</p>
            </div>

            <!-- Zoom Controls -->
            <div class="flex items-center justify-center gap-4 mt-6 bg-white/10 backdrop-blur-md rounded-xl px-6 py-3 border border-white/20">
              <button
                @click="zoomOut"
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all"
                :disabled="avatarScale <= 0.5"
              >
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                </svg>
              </button>
              
              <span class="text-white text-sm font-medium px-4">{{ Math.round(avatarScale * 100) }}%</span>
              
              <button
                @click="zoomIn"
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all"
                :disabled="avatarScale >= 3"
              >
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                </svg>
              </button>

              <button
                @click="resetZoom"
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all ml-4"
              >
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import authService from '@/services/auth'

export default {
  name: 'Header',
  setup() {
    const { locale } = useI18n()
    const router = useRouter()
    const route = useRoute()
    const mobileMenuOpen = ref(false)
    const langDropdownOpen = ref(false)
    const userDropdownOpen = ref(false)
    const isScrolled = ref(false)
    const headerRef = ref(null)
    const hoveringAvatar = ref(false)
    const showAvatarPreview = ref(false)
    const avatarScale = ref(1)
    
    const currentLocale = computed(() => locale.value)
    
    const isAuthenticated = computed(() => {
      return authService.getCurrentUser() !== null
    })
    
    const userName = computed(() => {
      const user = authService.getCurrentUser()
      return user ? (user.full_name || user.username) : 'Пользователь'
    })

    const userAvatar = computed(() => {
      const user = authService.getCurrentUser()
      return user?.avatar_url || user?.avatar || ''
    })

    const userRole = computed(() => {
      const user = authService.getCurrentUser()
      if (!user) return ''
      const roles = {
        admin: 'Администратор',
        instructor: 'Инструктор',
        user: 'Пользователь'
      }
      return roles[user.role] || 'Пользователь'
    })
    
    const isAdminUser = computed(() => {
      return authService.isAdmin()
    })

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
    
    // Определяем, нужно ли использовать светлую тему (темный текст на белом фоне)
    const isLightTheme = computed(() => {
      return isScrolled.value || route.name !== 'Home'
    })
    
    const changeLanguage = (lang) => {
      locale.value = lang
      localStorage.setItem('locale', lang)
    }
    
    const handleScroll = () => {
      isScrolled.value = window.scrollY > 20
    }
    
    const handleLogoError = (event) => {
      event.target.style.display = 'none'
      const parent = event.target.parentElement
      const fallback = document.createElement('div')
      fallback.className = 'w-8 h-8 bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 rounded-lg flex items-center justify-center'
      fallback.innerHTML = '<span class="text-white font-bold text-xs">ATG</span>'
      parent.insertBefore(fallback, event.target)
    }
    
    const logout = async () => {
      try {
        // Закрываем все dropdown меню
        userDropdownOpen.value = false
        mobileMenuOpen.value = false
        
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
        window.location.href = '/'
      }
    }
    
    const scrollToAbout = () => {
      const aboutSection = document.getElementById('about')
      if (aboutSection) {
        aboutSection.scrollIntoView({ behavior: 'smooth' })
      } else {
        window.location.href = '/#about'
      }
    }
    
    // Close dropdowns when clicking outside
    const handleClickOutside = (event) => {
      if (!event.target.closest('.relative')) {
        langDropdownOpen.value = false
        userDropdownOpen.value = false
      }
    }
    
    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      headerRef,
      mobileMenuOpen,
      langDropdownOpen,
      userDropdownOpen,
      hoveringAvatar,
      showAvatarPreview,
      avatarScale,
      currentLocale,
      isAuthenticated,
      userName,
      userAvatar,
      userRole,
      isAdminUser,
      isScrolled,
      isLightTheme,
      changeLanguage,
      handleLogoError,
      logout,
      scrollToAbout,
      zoomIn,
      zoomOut,
      resetZoom
    }
  }
}
</script>

<style scoped>
.nav-link {
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.5rem;
  transition: all 0.2s;
  padding-bottom: 0.75rem;
}

.mobile-nav-link {
  display: block;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
