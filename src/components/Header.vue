<template>
  <header 
    ref="headerRef"
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out"
    :class="[
      isScrolled ? 'bg-white/98 backdrop-blur-lg shadow-xl' : 'bg-transparent',
      isScrolled ? 'py-3' : 'py-6'
    ]"
  >
    <div class="page-container">
      <div class="flex items-center justify-between h-12 sm:h-14">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-2 sm:space-x-3">
            <img 
              src="/logo.e75fb66.svg" 
              alt="Asia Trans Gas Logo" 
              class="w-8 h-8 sm:w-10 sm:h-10 transition-all duration-500"
              :class="isScrolled ? 'drop-shadow-sm' : 'drop-shadow-lg'"
              @error="handleLogoError"
            />
            <span 
              class="font-semibold text-lg sm:text-xl transition-all duration-500"
              :class="isScrolled ? 'text-gray-900' : 'text-white drop-shadow-lg'"
            >Asia Trans Gas</span>
          </router-link>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center space-x-8">
          <router-link 
            to="/" 
            class="transition-all duration-500 relative font-medium"
            :class="[
              isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white/90 hover:text-white drop-shadow-lg',
              { 'text-tamex-blue-600': isScrolled && $route.name === 'Home' },
              { 'text-white': !isScrolled && $route.name === 'Home' }
            ]"
          >
            {{ $t('nav.home') }}
            <div 
              v-if="$route.name === 'Home'" 
              class="absolute -bottom-1 left-0 right-0 h-0.5 transition-all duration-500"
              :class="isScrolled ? 'bg-tamex-blue-600' : 'bg-white'"
            ></div>
          </router-link>
          <router-link 
            to="/courses" 
            class="transition-all duration-500 relative font-medium"
            :class="[
              isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white/90 hover:text-white drop-shadow-lg',
              { 'text-tamex-blue-600': isScrolled && $route.name === 'Courses' },
              { 'text-white': !isScrolled && $route.name === 'Courses' }
            ]"
          >
            {{ $t('nav.courses') }}
            <div 
              v-if="$route.name === 'Courses'" 
              class="absolute -bottom-1 left-0 right-0 h-0.5 transition-all duration-500"
              :class="isScrolled ? 'bg-tamex-blue-600' : 'bg-white'"
            ></div>
          </router-link>
          <router-link 
            to="/stations" 
            class="transition-all duration-500 relative font-medium"
            :class="[
              isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white/90 hover:text-white drop-shadow-lg',
              { 'text-tamex-blue-600': isScrolled && $route.name === 'Stations' },
              { 'text-white': !isScrolled && $route.name === 'Stations' }
            ]"
          >
            {{ $t('nav.stations') }}
            <div 
              v-if="$route.name === 'Stations'" 
              class="absolute -bottom-1 left-0 right-0 h-0.5 transition-all duration-500"
              :class="isScrolled ? 'bg-tamex-blue-600' : 'bg-white'"
            ></div>
          </router-link>
          <router-link 
            to="/dashboard" 
            class="transition-all duration-500 relative font-medium"
            :class="[
              isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white/90 hover:text-white drop-shadow-lg',
              { 'text-tamex-blue-600': isScrolled && $route.name === 'Dashboard' },
              { 'text-white': !isScrolled && $route.name === 'Dashboard' }
            ]"
          >
            {{ $t('nav.dashboard') }}
            <div 
              v-if="$route.name === 'Dashboard'" 
              class="absolute -bottom-1 left-0 right-0 h-0.5 transition-all duration-500"
              :class="isScrolled ? 'bg-tamex-blue-600' : 'bg-white'"
            ></div>
          </router-link>
        </nav>

        <!-- User Actions -->
        <div class="flex items-center space-x-2 sm:space-x-4">
          <!-- Language Switcher -->
          <el-dropdown @command="changeLanguage">
            <span 
              class="flex items-center space-x-1 cursor-pointer transition-all duration-500"
              :class="isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white/90 hover:text-white drop-shadow-lg'"
            >
              <span class="text-xs sm:text-sm font-medium">{{ currentLocale.toUpperCase() }}</span>
              <el-icon class="w-3 h-3"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="ru" :class="{ 'is-active': currentLocale === 'ru' }">
                  🇷🇺 Русский
                </el-dropdown-item>
                <el-dropdown-item command="en" :class="{ 'is-active': currentLocale === 'en' }">
                  🇺🇸 English
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <template v-if="isAuthenticated">
            <el-dropdown>
              <span class="flex items-center space-x-1 sm:space-x-2 cursor-pointer transition-all duration-500">
                <el-avatar :size="24" :src="userAvatar" class="sm:w-8 sm:h-8" />
                <span 
                  class="text-sm hidden sm:inline transition-all duration-500"
                  :class="isScrolled ? 'text-gray-700' : 'text-white drop-shadow-lg'"
                >{{ userName }}</span>
                <el-icon 
                  class="w-3 h-3 transition-all duration-500"
                  :class="isScrolled ? 'text-gray-700' : 'text-white'"
                ><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">
                    <el-icon><user /></el-icon>
                    {{ $t('nav.profile') }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/dashboard')">
                    <el-icon><data-board /></el-icon>
                    {{ $t('nav.dashboard') }}
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="logout">
                    <el-icon><switch-button /></el-icon>
                    {{ $t('nav.logout') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <div class="hidden sm:flex items-center space-x-2">
              <el-button 
                @click="$router.push('/login')" 
                type="primary" 
                plain 
                size="small" 
                class="transition-all duration-500"
                :class="isScrolled ? 'text-tamex-blue-600 border-tamex-blue-600 hover:bg-tamex-blue-600 hover:text-white' : 'text-white border-white hover:bg-white hover:text-tamex-blue-600'"
              >
                {{ $t('nav.login') }}
              </el-button>
              <el-button 
                @click="$router.push('/register')" 
                type="primary" 
                size="small" 
                class="transition-all duration-500"
                :class="isScrolled ? 'bg-tamex-blue-600 hover:bg-tamex-blue-700' : 'bg-white text-tamex-blue-600 hover:bg-white/90'"
              >
                {{ $t('nav.register') }}
              </el-button>
            </div>
          </template>

          <!-- Mobile Menu Button -->
          <el-button 
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden transition-all duration-500"
            :class="isScrolled ? 'text-tamex-blue-600 border-tamex-blue-600 hover:bg-tamex-blue-600 hover:text-white' : 'text-white border-white hover:bg-white hover:text-tamex-blue-600'"
            :icon="mobileMenuOpen ? 'close' : 'menu'"
            circle
            size="small"
          />
        </div>
      </div>

      <!-- Mobile Menu -->
      <div 
        v-if="mobileMenuOpen" 
        class="md:hidden py-4 transition-all duration-500"
        :class="[
          isScrolled ? 'mt-2 border-t border-gray-200 bg-white/95' : 'mt-4 border-t border-white/20 bg-black/20 backdrop-blur-md',
          isScrolled ? '' : 'rounded-lg'
        ]"
      >
        <div class="flex flex-col space-y-4">
          <router-link 
            to="/" 
            class="transition-all duration-500 py-2 font-medium"
            :class="isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white hover:text-white/80'"
            @click="mobileMenuOpen = false"
          >
            {{ $t('nav.home') }}
          </router-link>
          <router-link 
            to="/courses" 
            class="transition-all duration-500 py-2 font-medium"
            :class="isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white hover:text-white/80'"
            @click="mobileMenuOpen = false"
          >
            {{ $t('nav.courses') }}
          </router-link>
          <router-link 
            to="/stations" 
            class="transition-all duration-500 py-2 font-medium"
            :class="isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white hover:text-white/80'"
            @click="mobileMenuOpen = false"
          >
            {{ $t('nav.stations') }}
          </router-link>
          <router-link 
            to="/dashboard" 
            class="transition-all duration-500 py-2 font-medium"
            :class="isScrolled ? 'text-gray-700 hover:text-tamex-blue-600' : 'text-white hover:text-white/80'"
            @click="mobileMenuOpen = false"
          >
            {{ $t('nav.dashboard') }}
          </router-link>
          
          <!-- Mobile Auth Buttons -->
          <div 
            v-if="!isAuthenticated" 
            class="flex flex-col space-y-2 pt-4 transition-all duration-500"
            :class="isScrolled ? 'border-t border-gray-200' : 'border-t border-white/20'"
          >
            <el-button 
              @click="$router.push('/login')" 
              type="primary" 
              plain 
              class="w-full transition-all duration-500"
              :class="isScrolled ? 'text-tamex-blue-600 border-tamex-blue-600 hover:bg-tamex-blue-600 hover:text-white' : 'text-white border-white hover:bg-white hover:text-tamex-blue-600'"
            >
              {{ $t('nav.login') }}
            </el-button>
            <el-button 
              @click="$router.push('/register')" 
              type="primary" 
              class="w-full transition-all duration-500"
              :class="isScrolled ? 'bg-tamex-blue-600 hover:bg-tamex-blue-700' : 'bg-white text-tamex-blue-600 hover:bg-white/90'"
            >
              {{ $t('nav.register') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowDown, Menu, Close, User, SwitchButton, DataBoard } from '@element-plus/icons-vue'

export default {
  name: 'Header',
  components: {
    'arrow-down': ArrowDown,
    'menu': Menu,
    'close': Close,
    'user': User,
    'switch-button': SwitchButton,
    'data-board': DataBoard
  },
  setup() {
    const { locale } = useI18n()
    const mobileMenuOpen = ref(false)
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
    
    const userAvatar = computed(() => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.avatar || ''
    })
    
    const changeLanguage = (lang) => {
      locale.value = lang
      localStorage.setItem('locale', lang)
    }
    
    const handleScroll = () => {
      isScrolled.value = window.scrollY > 50
    }
    
    const handleLogoError = (event) => {
      // Fallback to text logo if image fails to load
      event.target.style.display = 'none'
      const parent = event.target.parentElement
      const fallback = document.createElement('div')
      fallback.className = 'w-10 h-10 bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 rounded-lg flex items-center justify-center'
      fallback.innerHTML = '<span class="text-white font-bold text-sm">ATG</span>'
      parent.insertBefore(fallback, event.target)
    }
    
    const logout = () => {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/'
    }
    
    onMounted(() => {
      // Add scroll listener
      window.addEventListener('scroll', handleScroll)
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })
    
    return {
      headerRef,
      mobileMenuOpen,
      currentLocale,
      isAuthenticated,
      userName,
      userAvatar,
      isScrolled,
      changeLanguage,
      handleLogoError,
      logout
    }
  }
}
</script>
