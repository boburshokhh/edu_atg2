<template>
  <header 
    ref="headerRef"
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-out"
    :class="[
      (isScrolled || $route.name !== 'Home')
        ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100' 
        : 'bg-transparent',
      (isScrolled || $route.name !== 'Home') ? 'py-4' : 'py-6'
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
              (isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white',
              $route.name === 'Home' ? ((isScrolled || $route.name !== 'Home') ? 'text-gray-900 font-semibold' : 'text-white font-semibold') : ''
            ]"
          >
            {{ $t('nav.home') }}
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full"></div>
          </router-link>
          
          <a 
            href="#about" 
            @click.prevent="scrollToAbout"
            class="nav-link cursor-pointer relative group"
            :class="(isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white'"
          >
            {{ $t('nav.about') }}
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full"></div>
          </a>
          
          <router-link 
            to="/stations" 
            class="nav-link relative group"
            :class="[
              (isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white',
              $route.name === 'Stations' ? ((isScrolled || $route.name !== 'Home') ? 'text-gray-900 font-semibold' : 'text-white font-semibold') : ''
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
              :class="(isScrolled || $route.name !== 'Home') 
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
              :class="(isScrolled || $route.name !== 'Home') 
                ? 'text-gray-700 hover:bg-gray-100' 
                : 'text-white/90 hover:bg-white/10'"
            >
              {{ $t('nav.login') }}
            </router-link>
            <router-link
              to="/register"
              class="hidden md:inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 bg-tamex-blue-600 text-white hover:bg-tamex-blue-700 shadow-sm hover:shadow-md"
            >
              {{ $t('nav.register') }}
            </router-link>
          </template>

          <!-- User Menu -->
          <template v-else>
            <div class="relative hidden md:block">
              <button
                @click="userDropdownOpen = !userDropdownOpen"
                class="flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200"
                :class="isScrolled 
                  ? 'text-gray-700 hover:bg-gray-100' 
                  : 'text-white/90 hover:bg-white/10'"
              >
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 flex items-center justify-center text-white text-sm font-semibold">
                  {{ userName.charAt(0).toUpperCase() }}
                </div>
                <span class="text-sm font-medium">{{ userName }}</span>
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
            :class="(isScrolled || $route.name !== 'Home') 
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
          :class="(isScrolled || $route.name !== 'Home') 
            ? 'border-gray-100 bg-white/95 backdrop-blur-md' 
            : 'border-white/10 bg-white/10 backdrop-blur-md'"
        >
          <div class="flex flex-col space-y-1 mt-4">
            <router-link
              to="/"
              class="mobile-nav-link"
              :class="(isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
              @click="mobileMenuOpen = false"
            >
              {{ $t('nav.home') }}
            </router-link>
            
            <a
              href="#about"
              @click.prevent="scrollToAbout(); mobileMenuOpen = false"
              class="mobile-nav-link cursor-pointer"
              :class="(isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
            >
              {{ $t('nav.about') }}
            </a>
            
            <router-link
              to="/stations"
              class="mobile-nav-link"
              :class="(isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
              @click="mobileMenuOpen = false"
            >
              {{ $t('nav.stations') }}
            </router-link>

            <!-- Mobile Auth Buttons -->
            <template v-if="!isAuthenticated">
              <div class="pt-4 space-y-2" :class="(isScrolled || $route.name !== 'Home') ? 'border-t border-gray-100' : 'border-t border-white/10'">
                <router-link
                  to="/login"
                  class="block w-full text-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all"
                  :class="(isScrolled || $route.name !== 'Home') 
                    ? 'text-gray-700 bg-gray-100 hover:bg-gray-200' 
                    : 'text-white bg-white/10 hover:bg-white/20'"
                  @click="mobileMenuOpen = false"
                >
                  {{ $t('nav.login') }}
                </router-link>
                <router-link
                  to="/register"
                  class="block w-full text-center px-4 py-2.5 text-sm font-medium rounded-lg bg-tamex-blue-600 text-white hover:bg-tamex-blue-700 transition-all"
                  @click="mobileMenuOpen = false"
                >
                  {{ $t('nav.register') }}
                </router-link>
              </div>
            </template>

            <!-- Mobile User Menu -->
            <template v-else>
              <div class="pt-4 space-y-1" :class="(isScrolled || $route.name !== 'Home') ? 'border-t border-gray-100' : 'border-t border-white/10'">
                <div 
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg"
                  :class="(isScrolled || $route.name !== 'Home') ? 'bg-gray-50' : 'bg-white/5'"
                >
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 flex items-center justify-center text-white font-semibold">
                    {{ userName.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="text-sm font-medium" :class="(isScrolled || $route.name !== 'Home') ? 'text-gray-900' : 'text-white'">
                      {{ userName }}
                    </p>
                  </div>
                </div>
                <router-link
                  to="/profile"
                  class="mobile-nav-link"
                  :class="(isScrolled || $route.name !== 'Home') ? 'text-gray-700 hover:bg-gray-50' : 'text-white hover:bg-white/10'"
                  @click="mobileMenuOpen = false"
                >
                  {{ $t('nav.profile') }}
                </router-link>
                <button
                  @click="logout"
                  class="mobile-nav-link w-full text-left text-red-600"
                  :class="(isScrolled || $route.name !== 'Home') ? 'hover:bg-red-50' : 'hover:bg-red-500/10'"
                >
                  {{ $t('nav.logout') }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </transition>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

export default {
  name: 'Header',
  setup() {
    const { locale } = useI18n()
    const mobileMenuOpen = ref(false)
    const langDropdownOpen = ref(false)
    const userDropdownOpen = ref(false)
    const isScrolled = ref(false)
    const headerRef = ref(null)
    
    const currentLocale = computed(() => locale.value)
    
    const isAuthenticated = computed(() => {
      return localStorage.getItem('auth_token') !== null
    })
    
    const userName = computed(() => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.name || 'Пользователь'
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
    
    const logout = () => {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/'
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
      currentLocale,
      isAuthenticated,
      userName,
      isScrolled,
      changeLanguage,
      handleLogoError,
      logout,
      scrollToAbout
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
</style>
