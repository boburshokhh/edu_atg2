<template>
  <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
    <!-- Background Slider -->
    <div class="absolute inset-0">
      <swiper
        :modules="modules"
        :slides-per-view="1"
        :space-between="0"
        :loop="true"
        :autoplay="{
          delay: 5000,
          disableOnInteraction: false,
        }"
        :effect="'fade'"
        :fadeEffect="{ crossFade: true }"
        class="w-full h-full"
      >
        <swiper-slide v-for="(image, index) in backgroundImages" :key="index">
          <div class="w-full h-full relative">
            <img 
              :src="image" 
              :alt="`Slide ${index + 1}`"
              class="w-full h-full object-cover"
            />
            <!-- Dark Overlay -->
            <div class="absolute inset-0 bg-gradient-to-br from-gray-900/75 via-slate-900/80 to-gray-900/75"></div>
          </div>
        </swiper-slide>
      </swiper>
      
      <!-- Additional Effects -->
      <div class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/40"></div>
      
      <!-- Animated Circles -->
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-tamex-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <!-- Grid Pattern -->
      <div class="absolute inset-0 opacity-[0.02]" style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 50px 50px;"></div>
    </div>

    <!-- Content -->
    <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-24 lg:py-32">
      <div class="text-center space-y-8 sm:space-y-10">
        
        <!-- Main Heading -->
        <div class="space-y-4 sm:space-y-6 animate-fade-in-up delay-100">
          <h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold leading-tight tracking-tight">
            <span class="block text-white mb-2">
              {{ $t('hero.welcome') }}
            </span>
            <span class="block bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent animate-gradient">
              {{ $t('hero.platform') }}
            </span>
            <span class="block text-white mt-2">
              {{ $t('hero.company') }}
            </span>
          </h1>
          
          <p class="max-w-3xl mx-auto text-lg sm:text-xl md:text-2xl text-white/80 font-light leading-relaxed">
            {{ $t('hero.description') }}
          </p>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up delay-200">
          <button
            @click="$router.push('/courses')"
            class="group relative w-full sm:w-auto px-8 py-4 bg-tamex-blue-600 text-white rounded-xl font-semibold text-base overflow-hidden transition-all duration-300 hover:bg-tamex-blue-700 hover:scale-105 hover:shadow-2xl hover:shadow-tamex-blue-500/50"
          >
            <span class="relative z-10 flex items-center justify-center space-x-2">
              <span>{{ $t('home.startLearning') }}</span>
              <svg class="w-5 h-5 transform group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
            <!-- Shine Effect -->
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
          </button>
          
          <button
            @click="scrollToAbout"
            class="group w-full sm:w-auto px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/20 text-white rounded-xl font-semibold text-base transition-all duration-300 hover:bg-white/10 hover:scale-105 hover:shadow-xl"
          >
            <span class="flex items-center justify-center space-x-2">
              <span>{{ $t('home.aboutCompany') }}</span>
              <svg class="w-5 h-5 transform group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Scroll Indicator -->
    <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
      <div class="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center p-2">
        <div class="w-1 h-3 bg-white/50 rounded-full animate-pulse"></div>
      </div>
    </div>

    <!-- Decorative Elements -->
    <div class="absolute top-20 left-10 w-20 h-20 border border-white/10 rounded-lg rotate-12 animate-float"></div>
    <div class="absolute bottom-20 right-10 w-16 h-16 border border-white/10 rounded-lg -rotate-12 animate-float delay-500"></div>
  </section>
</template>

<script>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, EffectFade } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/effect-fade'
import 'swiper/css/autoplay'

export default {
  name: 'HeroSection',
  components: {
    Swiper,
    SwiperSlide
  },
  setup() {
    const backgroundImages = [
      '/slider/photo_2025-10-16_14-31-39.jpg',
      '/slider/photo_2025-10-16_14-32-18.jpg',
      '/slider/photo_2025-10-16_14-32-35.jpg',
      '/slider/photo_2025-10-16_14-35-01.jpg'
    ]

    const scrollToAbout = () => {
      const aboutSection = document.getElementById('about')
      if (aboutSection) {
        aboutSection.scrollIntoView({ behavior: 'smooth' })
      }
    }

    return {
      modules: [Autoplay, EffectFade],
      backgroundImages,
      scrollToAbout
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(12deg);
  }
  50% {
    transform: translateY(-20px) rotate(12deg);
  }
}

@keyframes gradient {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-fade-in {
  animation: fade-in 1s ease-out;
}

.animate-fade-in-up {
  animation: fade-in-up 1s ease-out;
}

.delay-100 {
  animation-delay: 0.1s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.delay-200 {
  animation-delay: 0.2s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.delay-300 {
  animation-delay: 0.3s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.delay-500 {
  animation-delay: 0.5s;
}

.delay-1000 {
  animation-delay: 1s;
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}
</style>
