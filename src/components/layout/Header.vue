<template>
  <!-- Mobile Header (Top Bar) -->
  <header 
    ref="headerRef"
    class="lg:hidden fixed top-0 left-0 right-0 z-50 h-14 bg-white/95 backdrop-blur-md border-b border-gray-100 transition-all duration-300 ease-out"
  >
    <div class="max-w-7xl mx-auto px-4 h-full grid grid-cols-3 items-center">
      <!-- Burger Menu Button -->
      <button
        @click="mobileMenuOpen = true"
        class="w-10 h-10 flex items-center justify-center rounded-lg transition-all duration-200 hover:bg-gray-100 active:bg-gray-200"
        aria-label="Открыть меню"
      >
        <svg 
          class="w-6 h-6 text-gray-700" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M4 6h16M4 12h16M4 18h16" 
          />
        </svg>
      </button>
      
      <!-- Logo (Center) -->
      <div class="justify-self-center">
        <router-link to="/" class="flex items-center">
          <img 
            src="/logo.e75fb66.svg" 
            alt="Asia Trans Gas" 
            class="h-6 w-auto transition-all duration-300"
            @error="handleLogoError"
          >
        </router-link>
      </div>
      
      <!-- Language Switcher (Right) -->
      <div class="relative justify-self-end">
        <button
          @click="langDropdownOpen = !langDropdownOpen"
          class="w-10 h-10 flex items-center justify-center rounded-lg transition-all duration-200 hover:bg-gray-100 active:bg-gray-200"
          aria-label="Сменить язык"
        >
          <svg
            class="w-6 h-6 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </button>
        
        <!-- Language Dropdown -->
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
            class="absolute right-0 mt-2 w-32 bg-white rounded-lg shadow-lg py-1 border border-gray-100 z-50"
            @click="langDropdownOpen = false"
          >
            <button
              class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
              :class="currentLocale === 'ru' ? 'text-tamex-blue-600 font-semibold' : 'text-gray-700'"
              @click="changeLanguage('ru')"
            >
              🇷🇺 Русский
            </button>
            <button
              class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
              :class="currentLocale === 'en' ? 'text-tamex-blue-600 font-semibold' : 'text-gray-700'"
              @click="changeLanguage('en')"
            >
              🇺🇸 English
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>

  <!-- Desktop Header -->
  <header 
    ref="headerRef"
    class="hidden lg:block fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-out"
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
            >
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
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full" />
          </router-link>
          
          <a 
            href="#about" 
            class="nav-link cursor-pointer relative group"
            :class="isLightTheme ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white'"
            @click.prevent="scrollToAbout"
          >
            {{ $t('nav.about') }}
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full" />
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
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full" />
          </router-link>
          
          <router-link 
            to="/departments" 
            class="nav-link relative group"
            :class="[
              isLightTheme ? 'text-gray-700 hover:text-gray-900' : 'text-white/90 hover:text-white',
              $route.name === 'Departments' ? (isLightTheme ? 'text-gray-900 font-semibold' : 'text-white font-semibold') : ''
            ]"
          >
            Отделы
            <div class="absolute bottom-0 left-0 w-0 h-0.5 bg-tamex-blue-600 transition-all duration-300 group-hover:w-full" />
          </router-link>
        </nav>

        <!-- Right Actions -->
        <div class="flex items-center space-x-3">
          <!-- Language Switcher -->
          <div class="relative">
            <button
              class="flex items-center space-x-1 px-3 py-2 rounded-lg transition-all duration-200"
              :class="isLightTheme 
                ? 'text-gray-700 hover:bg-gray-100' 
                : 'text-white/90 hover:bg-white/10'"
              @click="langDropdownOpen = !langDropdownOpen"
            >
              <span class="text-sm font-medium">{{ currentLocale.toUpperCase() }}</span>
              <svg
                class="w-4 h-4"
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
                  class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                  :class="currentLocale === 'ru' ? 'text-tamex-blue-600 font-semibold' : 'text-gray-700'"
                  @click="changeLanguage('ru')"
                >
                  🇷🇺 Русский
                </button>
                <button
                  class="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors"
                  :class="currentLocale === 'en' ? 'text-tamex-blue-600 font-semibold' : 'text-gray-700'"
                  @click="changeLanguage('en')"
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
                class="flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-opacity-80"
                :class="isLightTheme 
                  ? 'text-gray-700 hover:bg-gray-100' 
                  : 'text-white/90 hover:bg-white/10'"
                @click="userDropdownOpen = !userDropdownOpen"
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
                  class="flex flex-col items-start"
                >
                  <span class="text-sm font-medium">{{ userName }}</span>
                  <span class="text-xs opacity-70">{{ userRole }}</span>
                </div>
                <svg
                  class="w-4 h-4 transition-transform duration-200"
                  :class="userDropdownOpen ? 'rotate-180' : ''"
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
                  <hr class="my-1 border-gray-100">
                  <button
                    class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    @click="logout"
                  >
                    {{ $t('nav.logout') }}
                  </button>
                </div>
              </transition>
            </div>
          </template>

        </div>
      </div>
    </div>

    <!-- Mobile Drawer -->
    <Teleport to="body">
      <!-- Backdrop -->
      <Transition name="drawer-backdrop">
        <div 
          v-if="mobileMenuOpen"
          class="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm"
          @click="closeDrawer"
          @touchstart="handleTouchStart"
          @touchmove="handleTouchMove"
          @touchend="handleTouchEnd"
        />
      </Transition>
      
      <!-- Drawer Panel -->
      <Transition name="drawer-slide">
        <aside 
          v-if="mobileMenuOpen"
          class="fixed top-0 right-0 bottom-0 z-[101] w-80 max-w-[85vw] bg-white shadow-2xl overflow-y-auto"
          @click.stop
          @touchstart="handleDrawerTouchStart"
          @touchmove="handleDrawerTouchMove"
          @touchend="handleDrawerTouchEnd"
        >
          <div class="flex flex-col h-full">
            <!-- Section 1: Navigation -->
            <nav class="px-4 py-3 border-b border-gray-100">
              <router-link
                to="/"
                class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-gray-700 hover:bg-gray-50 active:bg-gray-100"
                @click="closeDrawer"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span>{{ $t('nav.home') }}</span>
              </router-link>
              
              <router-link
                to="/stations"
                class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-gray-700 hover:bg-gray-50 active:bg-gray-100 mt-1"
                @click="closeDrawer"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>{{ $t('nav.stations') }}</span>
              </router-link>
              
              <router-link
                to="/departments"
                class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-gray-700 hover:bg-gray-50 active:bg-gray-100 mt-1"
                @click="closeDrawer"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span>Отделы</span>
              </router-link>
              
              <a
                href="#about"
                class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-gray-700 hover:bg-gray-50 active:bg-gray-100 mt-1 cursor-pointer"
                @click.prevent="scrollToAbout(); closeDrawer()"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ $t('nav.about') }}</span>
              </a>
            </nav>
            
            <!-- Section 2: Account -->
            <template v-if="isAuthenticated && userName">
              <div class="px-4 py-3 border-b border-gray-100">
                <router-link
                  to="/profile"
                  class="flex items-center space-x-3 py-2 rounded-lg transition-colors hover:bg-gray-50 active:bg-gray-100"
                  @click="closeDrawer"
                >
                  <div 
                    class="w-12 h-12 rounded-full overflow-hidden flex-shrink-0 ring-2 ring-gray-200"
                    :class="userAvatar 
                      ? '' 
                      : 'bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700'"
                  >
                    <img 
                      v-if="userAvatar" 
                      :src="userAvatar" 
                      :alt="userName"
                      class="w-full h-full object-cover"
                    >
                    <div
                      v-else
                      class="w-full h-full flex items-center justify-center text-white text-lg font-semibold"
                    >
                      {{ userName.charAt(0).toUpperCase() }}
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-medium text-gray-900 truncate">
                      {{ userName }}
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      {{ userRole }}
                    </div>
                  </div>
                </router-link>
              </div>
              
              <!-- Section 3: Settings / Tools -->
              <div class="px-4 py-2 border-b border-gray-100">
                <router-link
                  to="/dashboard"
                  class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-gray-700 hover:bg-gray-50 active:bg-gray-100"
                  @click="closeDrawer"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  <span>{{ $t('nav.dashboard') }}</span>
                </router-link>
                
                <router-link
                  v-if="isAdminUser"
                  to="/admin"
                  class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-blue-600 hover:bg-blue-50 active:bg-blue-100 mt-1"
                  @click="closeDrawer"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>Админ-панель</span>
                </router-link>
              </div>
              
              <!-- Section 4: Danger Zone -->
              <div class="px-4 py-2 mt-auto">
                <button
                  @click="confirmLogout"
                  class="flex items-center space-x-3 h-11 px-3 rounded-lg transition-colors text-sm font-normal text-gray-600 hover:bg-gray-50 active:bg-gray-100 w-full text-left"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>{{ $t('nav.logout') }}</span>
                </button>
              </div>
            </template>
            
            <!-- Not Authenticated -->
            <template v-else>
              <div class="px-4 py-3 mt-auto">
                <router-link
                  to="/login"
                  class="flex items-center justify-center h-11 px-4 rounded-lg transition-colors text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 active:bg-gray-700"
                  @click="closeDrawer"
                >
                  {{ $t('nav.login') }}
                </router-link>
              </div>
            </template>
          </div>
        </aside>
      </Transition>
    </Teleport>

    <!-- Logout Confirmation Dialog -->
    <Teleport to="body">
      <Transition name="dialog">
        <div 
          v-if="showLogoutConfirm"
          class="fixed inset-0 z-[200] bg-black/50 flex items-center justify-center p-4"
          @click.self="showLogoutConfirm = false"
        >
          <div class="bg-white rounded-lg p-6 max-w-sm w-full shadow-xl">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Выйти из системы?</h3>
            <p class="text-sm text-gray-600 mb-4">Вы уверены, что хотите выйти?</p>
            <div class="flex gap-3">
              <button 
                @click="showLogoutConfirm = false" 
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Отмена
              </button>
              <button 
                @click="handleLogout" 
                class="flex-1 px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
              >
                {{ userName.charAt(0).toUpperCase() }}
              </div>
              <div
                v-else
                class="w-64 h-64 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-6xl font-bold"
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
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all"
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
                class="w-10 h-10 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all"
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

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import authService from '@/services/auth'
import userProfileService from '@/services/userProfile'

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
    const showLogoutConfirm = ref(false)
    
    // Swipe detection for drawer
    const touchStartX = ref(0)
    const touchStartY = ref(0)
    const isSwiping = ref(false)
    const drawerTouchStartX = ref(0)
    
    const currentLocale = computed(() => locale.value)

    const isAuthenticated = computed(() => {
      return authService.getCurrentUser() !== null
    })
    
    // Ref для принудительного обновления computed свойств
    const userDataVersion = ref(0)
    
    // Флаг для отслеживания первичной загрузки данных
    const isDataLoaded = ref(false)
    
    // Функция для проверки и использования кешированного avatar URL
    const getCachedAvatarUrl = (newAvatarKey, newAvatarUrl) => {
      if (!newAvatarKey || !newAvatarUrl) {
        return newAvatarUrl
      }
      
      // Проверяем кеш
      const cachedAvatarKey = localStorage.getItem('avatar_key')
      const cachedAvatarUrl = localStorage.getItem('avatar_url_cached')
      const avatarUrlExpires = parseInt(localStorage.getItem('avatar_url_expires') || '0')
      
      // Если ключ совпадает и кеш не истек (6 дней из 7), используем кешированный URL
      if (cachedAvatarKey === newAvatarKey && 
          cachedAvatarUrl && 
          Date.now() < avatarUrlExpires) {
        console.log('[Header] Using cached avatar URL, key:', newAvatarKey)
        return cachedAvatarUrl
      }
      
      // Обновляем кеш
      console.log('[Header] Updating avatar cache, key:', newAvatarKey)
      localStorage.setItem('avatar_key', newAvatarKey)
      localStorage.setItem('avatar_url_cached', newAvatarUrl)
      // Кеш действителен 6 дней (из 7 дней presigned URL)
      localStorage.setItem('avatar_url_expires', String(Date.now() + (6 * 24 * 60 * 60 * 1000)))
      
      return newAvatarUrl
    }
    
    // Функция для обновления данных пользователя
    const refreshUserData = async (force = false) => {
      // Если данные уже загружены и не требуется принудительное обновление, пропускаем
      if (isDataLoaded.value && !force) {
        // Проверяем, есть ли данные пользователя в authService
        const currentUser = authService.getCurrentUser()
        if (currentUser && currentUser.full_name && currentUser.avatar_url) {
          // Данные уже есть, просто обновляем computed свойства
          userDataVersion.value++
          return
        }
      }
      
      try {
        // Сначала обновляем базовые данные через authService
        await authService.checkAuth()
        const currentUser = authService.getCurrentUser()
        
        // Если пользователь авторизован, загружаем расширенные данные профиля из БД
        if (currentUser?.id) {
          try {
            const profileResult = await userProfileService.getProfile(currentUser.id)
            if (profileResult.success && profileResult.data) {
              const profileData = profileResult.data
              
              // Применяем кеширование для avatar URL
              const avatarKey = profileData.avatar_key || null
              const newAvatarUrl = profileData.avatar_url || profileData.avatar || null
              const cachedAvatarUrl = avatarKey ? getCachedAvatarUrl(avatarKey, newAvatarUrl) : newAvatarUrl
              
              // Обновляем данные в authService
              if (authService.currentUser) {
                // Создаем обновленный объект пользователя, объединяя данные из auth и профиля
                const updatedUser = {
                  ...authService.currentUser,
                  full_name: profileData.full_name || authService.currentUser.full_name,
                  role: profileData.role || authService.currentUser.role,
                  avatar_url: cachedAvatarUrl,
                  position: profileData.position || authService.currentUser.position || null,
                  station: profileData.station || profileData.company || authService.currentUser.station || null, // Маппинг company -> station
                  email: profileData.email || authService.currentUser.email || null
                }
                
                authService.currentUser = updatedUser
                
                // Сохраняем обновленные данные в localStorage, чтобы при перезагрузке они были доступны сразу
                localStorage.setItem('user', JSON.stringify(updatedUser))
              }
              
              // Отмечаем, что данные загружены
              isDataLoaded.value = true
            }
          } catch (error) {
            console.error('Error loading user profile:', error)
            // Не прерываем выполнение, используем данные из authService
          }
        } else {
          // Пользователь не авторизован, отмечаем что загрузка завершена
          isDataLoaded.value = true
        }
      } catch (error) {
        console.error('Error refreshing user data:', error)
      }
      
      userDataVersion.value++ // Принудительно обновляем computed свойства
    }
    
    const userName = computed(() => {
      userDataVersion.value // Зависимость для обновления
      const user = authService.getCurrentUser()
      
      if (user) {
        // Приоритет: полное имя > имя пользователя > 'Пользователь'
        return user.full_name || user.username || 'Пользователь'
      }
      
      return null // Не показываем данные для неавторизованных пользователей
    })

    const userAvatar = computed(() => {
      userDataVersion.value // Зависимость для обновления
      const user = authService.getCurrentUser()
      
      if (user) {
        return user.avatar_url || user.avatar || null
      }
      
      return null // Не показываем аватар для неавторизованных пользователей
    })

    const userRole = computed(() => {
      userDataVersion.value // Зависимость для обновления
      const user = authService.getCurrentUser()
      
      if (!user) {
        return null // Не показываем роль для неавторизованных пользователей
      }
      
      const roles = {
        admin: 'Администратор',
        instructor: 'Инструктор',
        user: 'Студент'
      }
      return roles[user.role] || 'Студент'
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
    
    // Drawer close function
    const closeDrawer = () => {
      mobileMenuOpen.value = false
    }
    
    // Touch handlers for backdrop swipe
    const handleTouchStart = (e) => {
      touchStartX.value = e.touches[0].clientX
      touchStartY.value = e.touches[0].clientY
      isSwiping.value = false
    }
    
    const handleTouchMove = (e) => {
      const deltaX = e.touches[0].clientX - touchStartX.value
      const deltaY = e.touches[0].clientY - touchStartY.value
      
      // Detect horizontal swipe
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
        isSwiping.value = true
      }
    }
    
    const handleTouchEnd = (e) => {
      if (isSwiping.value) {
        const deltaX = e.changedTouches[0].clientX - touchStartX.value
        // Swipe left to close (threshold: 100px)
        if (deltaX < -100) {
          closeDrawer()
        }
      }
      isSwiping.value = false
    }
    
    // Touch handlers for drawer panel swipe
    const handleDrawerTouchStart = (e) => {
      drawerTouchStartX.value = e.touches[0].clientX
    }
    
    const handleDrawerTouchMove = (e) => {
      // Prevent default scrolling when swiping
      const deltaX = e.touches[0].clientX - drawerTouchStartX.value
      if (deltaX < 0 && Math.abs(deltaX) > 10) {
        e.preventDefault()
      }
    }
    
    const handleDrawerTouchEnd = (e) => {
      const deltaX = e.changedTouches[0].clientX - drawerTouchStartX.value
      // Swipe left to close (threshold: 100px)
      if (deltaX < -100) {
        closeDrawer()
      }
    }
    
    // Logout confirmation
    const confirmLogout = () => {
      showLogoutConfirm.value = true
      closeDrawer()
    }
    
    const handleLogout = async () => {
      showLogoutConfirm.value = false
      await logout()
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
    
    // Обработчик обновления профиля
    const handleProfileUpdate = () => {
      // При обновлении профиля принудительно обновляем данные
      refreshUserData(true)
    }
    
    onMounted(async () => {
      window.addEventListener('scroll', handleScroll)
      document.addEventListener('click', handleClickOutside)
      // Слушаем обновления профиля
      window.addEventListener('user-profile-updated', handleProfileUpdate)
      // Загружаем данные пользователя при монтировании
      await refreshUserData()
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
      document.removeEventListener('click', handleClickOutside)
      window.removeEventListener('user-profile-updated', handleProfileUpdate)
    })
    
    return {
      headerRef,
      mobileMenuOpen,
      langDropdownOpen,
      userDropdownOpen,
      hoveringAvatar,
      showAvatarPreview,
      avatarScale,
      showLogoutConfirm,
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
      resetZoom,
      closeDrawer,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      handleDrawerTouchStart,
      handleDrawerTouchMove,
      handleDrawerTouchEnd,
      confirmLogout,
      handleLogout
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

/* Drawer backdrop animation */
.drawer-backdrop-enter-active,
.drawer-backdrop-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-backdrop-enter-from,
.drawer-backdrop-leave-to {
  opacity: 0;
}

/* Drawer slide animation */
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-slide-enter-from {
  transform: translateX(100%);
}

.drawer-slide-leave-to {
  transform: translateX(100%);
}

/* Dialog animation */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-enter-active .bg-white,
.dialog-leave-active .bg-white {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.dialog-enter-from {
  opacity: 0;
}

.dialog-enter-from .bg-white {
  transform: scale(0.95);
  opacity: 0;
}

.dialog-leave-to {
  opacity: 0;
}

.dialog-leave-to .bg-white {
  transform: scale(0.95);
  opacity: 0;
}

/* Fade animation for avatar preview */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
