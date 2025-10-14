<template>
  <section class="hero-bg">
    <!-- Background Overlays -->
    <div class="hero-overlay"></div>
    <div class="hero-overlay-additional"></div>
    
    <div class="page-container relative z-10">
      <div class="text-center flex flex-col items-center justify-center min-h-screen pt-16 sm:pt-20">
        <!-- Badge -->
        <div class="badge-style mb-4">
          <el-icon class="w-4 h-4 text-tamex-yellow">
            <Medal />
          </el-icon>
          <span class="text-sm font-medium text-white/90">
            {{ $t('home.badge') }}
          </span>
        </div>
        
        <!-- Logo -->
        <div class="flex justify-center mb-8 sm:mb-10">
          <div class="relative">
            <img 
              src="/logo.e75fb66.svg" 
              alt="Asia Trans Gas Logo" 
              class="w-24 h-24 sm:w-32 sm:h-32 md:w-40 md:h-40 drop-shadow-lg"
              @error="handleLogoError"
            />
          </div>
        </div>
        
        <!-- Title -->
        <h1 class="title-style">
          <span class="text-white">{{ $t('home.title') }}</span>
          <span class="text-gradient">
            {{ $t('home.subtitle') }}
          </span>
          <br>
          <span class="text-white">{{ $t('home.titleEnd') }}</span>
        </h1>
        
        <!-- Description -->
        <p class="description-style">
          {{ $t('home.description') }}
        </p>
        
        <!-- Buttons -->
        <div class="button-group">
          <el-button 
            @click="$router.push('/courses')" 
            type="primary" 
            size="large"
            class="group w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-tamex-blue-600 to-tamex-blue-700 hover:from-tamex-blue-700 hover:to-tamex-blue-800 text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-xl shadow-lg flex items-center justify-center space-x-2 text-sm sm:text-base"
          >
            <span>{{ $t('home.startLearning') }}</span>
            <el-icon class="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition-transform duration-300">
              <VideoPlay />
            </el-icon>
          </el-button>
          <el-button 
            @click="scrollToFeatures" 
            size="large"
            class="group w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/30 text-white rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-xl shadow-lg flex items-center justify-center space-x-2 text-sm sm:text-base"
          >
            <span>{{ $t('home.aboutCompany') }}</span>
            <el-icon class="w-4 h-4 sm:w-5 sm:h-5 group-hover:scale-110 transition-transform duration-300">
              <InfoFilled />
            </el-icon>
          </el-button>
        </div>
        
        <!-- Stats Preview -->
        <div class="mt-12 sm:mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 max-w-4xl mx-auto">
          <div class="text-center">
            <div class="text-2xl sm:text-3xl font-bold text-tamex-blue-400 mb-2">500+</div>
            <div class="text-sm sm:text-base text-white/90">{{ $t('home.stats.employees') }}</div>
          </div>
          <div class="text-center">
            <div class="text-2xl sm:text-3xl font-bold text-tamex-yellow mb-2">8</div>
            <div class="text-sm sm:text-base text-white/90">{{ $t('home.stats.stations') }}</div>
          </div>
          <div class="text-center">
            <div class="text-2xl sm:text-3xl font-bold text-tamex-blue-400 mb-2">1586</div>
            <div class="text-sm sm:text-base text-white/90">{{ $t('home.stats.pipeline') }}</div>
          </div>
          <div class="text-center">
            <div class="text-2xl sm:text-3xl font-bold text-tamex-yellow mb-2">30</div>
            <div class="text-sm sm:text-base text-white/90">{{ $t('home.stats.capacity') }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Scroll Indicator -->
    <div class="scroll-indicator">
      <div class="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center" aria-label="Прокрутите вниз">
        <div class="w-1 h-3 bg-white/50 rounded-full mt-2 animate-pulse"></div>
      </div>
    </div>
  </section>
</template>

<script>
import { VideoPlay, InfoFilled, Medal } from '@element-plus/icons-vue'

export default {
  name: 'HeroSection',
  components: {
    VideoPlay,
    InfoFilled,
    Medal
  },
  emits: ['scroll-to-features'],
  setup(props, { emit }) {
    const scrollToFeatures = () => {
      emit('scroll-to-features')
    }
    
    const handleLogoError = (event) => {
      // Fallback to text logo if image fails to load
      event.target.style.display = 'none'
      const parent = event.target.parentElement
      const fallback = document.createElement('div')
      fallback.className = 'w-32 h-32 sm:w-40 sm:h-40 md:w-48 md:h-48 bg-gradient-to-br from-tamex-blue-600 to-tamex-blue-700 rounded-lg flex items-center justify-center'
      fallback.innerHTML = '<span class="text-white font-bold text-2xl sm:text-3xl md:text-4xl">ATG</span>'
      parent.insertBefore(fallback, event.target)
    }
    
    return {
      scrollToFeatures,
      handleLogoError
    }
  }
}
</script>
