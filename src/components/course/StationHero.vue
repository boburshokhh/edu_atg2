<template>
  <main class="relative w-full h-screen flex items-center justify-center overflow-hidden">
    <!-- Background Image with Overlays -->
    <div class="absolute inset-0 z-0">
      <img 
        :src="stationImageSrc" 
        :alt="station?.name"
        class="w-full h-full object-cover animate-scale-in origin-center scale-105"
      />
      <!-- Gradient Overlay -->
      <div class="absolute inset-0 hero-gradient-overlay pointer-events-none"></div>
      <!-- Glow Effect -->
      <div class="absolute bottom-0 right-0 w-2/3 h-2/3 bg-blue-600/10 blur-[120px] rounded-full mix-blend-screen pointer-events-none"></div>
    </div>

    <!-- Main Content -->
    <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex flex-col justify-center">
      <div class="w-full max-w-5xl space-y-10 animate-fade-in-up" style="animation-delay: 0.1s;">
        
        <!-- Navigation Bar -->
        <div class="flex flex-wrap items-center gap-4 mb-8">
          <button 
            class="group flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/10 transition-all"
            @click="$router.push('/stations')"
          >
            <ChevronLeftIcon class="w-4 h-4 text-gray-300 group-hover:-translate-x-1 transition-transform" />
            <span class="text-sm font-medium text-gray-200 group-hover:text-white">Все станции</span>
          </button>

          <!-- Breadcrumb -->
          <div class="flex text-sm text-gray-400 font-medium items-center gap-2">
            <span class="hidden sm:inline">Станции</span>
            <ChevronRightIcon class="w-3 h-3 hidden sm:inline" />
            <span>{{ station?.short_name || station?.shortName }}</span>
            <ChevronRightIcon class="w-3 h-3" />
            <span class="text-white">Обучающая программа</span>
          </div>

          <!-- Badge -->
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-500/30 border border-indigo-400/30 text-indigo-200 text-xs font-semibold tracking-wide uppercase shadow-sm backdrop-blur-md ml-auto sm:ml-4">
            <BookOpenIcon class="w-4 h-4" />
            Онлайн-тренинг
          </div>
        </div>

        <!-- Title and Description -->
        <div class="space-y-6">
          <h1 class="font-display font-extrabold text-6xl sm:text-7xl lg:text-8xl leading-[1.05] text-white tracking-tight drop-shadow-2xl max-w-4xl">
            {{ getFirstLine(courseProgram?.title) }}<br v-if="hasSecondLine(courseProgram?.title)" />
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-blue-200">
              {{ getSecondLine(courseProgram?.title) }}
            </span>
          </h1>
          
          <p class="text-xl sm:text-2xl text-gray-300 max-w-3xl leading-relaxed font-light border-l-4 border-primary/50 pl-8">
            {{ courseProgram?.description }}
          </p>
        </div>

        <!-- Course Stats -->
        <CourseStats :stats="courseStats" />

        <!-- Call to Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-5 pt-8">
          <button 
            class="glow-effect flex items-center justify-center gap-3 bg-primary hover:bg-primary-600 text-white text-xl font-bold px-10 py-5 rounded-2xl transition-all w-full sm:w-auto shadow-lg shadow-blue-900/20"
            @click="handleStartCourse"
          >
            <span>Начать обучение</span>
            <ChevronRightIcon class="w-6 h-6 animate-pulse" />
          </button>
          
          <button 
            class="group flex items-center justify-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/30 text-white text-lg font-medium px-10 py-5 rounded-2xl backdrop-blur-md transition-all w-full sm:w-auto"
            @click="handleMoreInfo"
          >
            <InformationCircleIcon class="w-6 h-6 text-gray-400 group-hover:text-white transition-colors" />
            <span>Подробнее о курсе</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Scroll Down Indicator -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce opacity-50 hover:opacity-100 transition-opacity cursor-pointer">
      <span class="text-xs text-gray-400 uppercase tracking-widest font-semibold">Листайте вниз</span>
      <ChevronDownIcon class="w-5 h-5 text-gray-400" />
    </div>
  </main>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  BookOpenIcon, 
  ChevronRightIcon, 
  ChevronLeftIcon, 
  ChevronDownIcon,
  InformationCircleIcon 
} from '@heroicons/vue/24/outline'
import CourseStats from './CourseStats.vue'

export default {
  name: 'StationHero',
  components: {
    BookOpenIcon,
    ChevronRightIcon,
    ChevronLeftIcon,
    ChevronDownIcon,
    InformationCircleIcon,
    CourseStats
  },
  props: {
    station: {
      type: Object,
      default: null
    },
    stationId: {
      type: Number,
      required: true
    },
    stationImageSrc: {
      type: String,
      default: ''
    },
    courseProgram: {
      type: Object,
      default: null
    },
    courseStats: {
      type: Object,
      required: true
    }
  },
  setup() {
    const router = useRouter()

    const getFirstLine = (title) => {
      if (!title) return ''
      const parts = title.split(' ')
      return parts.slice(0, Math.ceil(parts.length / 2)).join(' ')
    }

    const getSecondLine = (title) => {
      if (!title) return ''
      const parts = title.split(' ')
      return parts.slice(Math.ceil(parts.length / 2)).join(' ')
    }

    const hasSecondLine = (title) => {
      if (!title) return false
      return title.split(' ').length > 1
    }

    const handleStartCourse = () => {
      // Navigate to first lesson or emit event
      console.log('Starting course...')
    }

    const handleMoreInfo = () => {
      // Scroll to course details or emit event
      console.log('Show more info...')
    }

    return { 
      router,
      getFirstLine,
      getSecondLine,
      hasSecondLine,
      handleStartCourse,
      handleMoreInfo
    }
  }
}
</script>

<style scoped>
.hero-gradient-overlay {
  background: linear-gradient(
    to right, 
    rgba(15, 23, 42, 0.95) 0%, 
    rgba(15, 23, 42, 0.85) 55%, 
    rgba(15, 23, 42, 0.3) 100%
  );
}

.glow-effect {
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
  transition: box-shadow 0.3s ease, transform 0.2s ease;
}

.glow-effect:hover {
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.8);
  transform: translateY(-2px);
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  0% {
    opacity: 0;
    transform: scale(0.95);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out forwards;
}

.animate-scale-in {
  animation: scaleIn 0.6s ease-out forwards;
}
</style>
