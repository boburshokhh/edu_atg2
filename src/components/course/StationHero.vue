<template>
  <div class="relative h-[80vh] min-h-[700px] overflow-hidden">
    <!-- Изображение станции -->
    <div class="absolute inset-0">
      <img 
        :src="stationImageSrc" 
        :alt="station?.name"
        class="w-full h-full object-cover"
      >
      <!-- Градиентный оверлей -->
      <div class="absolute inset-0 bg-gradient-to-r from-black/80 via-black/60 to-transparent" />
      <!-- Дополнительный вертикальный градиент для читаемости текста -->
      <div class="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-transparent" />
    </div>

    <!-- Контент хедера -->
    <div class="relative h-full page-container flex flex-col gap-6 md:gap-10 pt-28 pb-16">
      <!-- Навигация -->
      <div>
        <button 
          class="inline-flex items-center bg-white/10 backdrop-blur-md text-white hover:bg-white/20 transition-all duration-300 group px-4 py-2.5 rounded-xl border border-white/20 hover:border-white/40"
          @click="$router.push('/stations')"
        >
          <ChevronLeftIcon class="w-5 h-5 mr-2 transition-transform group-hover:-translate-x-1" />
          <span class="text-sm font-semibold">Все станции</span>
        </button>

        <!-- Breadcrumb сразу под кнопкой -->
        <nav class="mt-4 flex items-center space-x-2 text-sm text-white/70">
          <a
            href="/stations"
            class="hover:text-white transition-colors"
          >Станции</a>
          <ChevronRightIcon class="w-4 h-4" />
          <a
            :href="`/station/${stationId}`"
            class="hover:text-white transition-colors"
          >{{ station?.short_name || station?.shortName }}</a>
          <ChevronRightIcon class="w-4 h-4" />
          <span class="text-white font-medium">Обучающая программа</span>
        </nav>
      </div>

      <!-- Основная информация -->
      <div class="max-w-4xl">
        <div class="inline-flex items-center bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-md px-3.5 py-1.5 rounded-full mb-3 border border-white/20">
          <BookOpenIcon class="w-4 h-4 mr-2 text-white" />
          <span class="text-sm font-semibold text-white">Онлайн-тренинг</span>
        </div>

        <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-3 leading-tight">
          {{ courseProgram?.title }}
        </h1>
        
        <p class="text-base md:text-lg text-white/90 mb-6 max-w-3xl leading-relaxed">
          {{ courseProgram?.description }}
        </p>

        <!-- Статистика курса -->
        <CourseStats :stats="courseStats" />
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpenIcon, ChevronRightIcon, ChevronLeftIcon } from '@heroicons/vue/24/solid'
import CourseStats from './CourseStats.vue'

export default {
  name: 'StationHero',
  components: {
    BookOpenIcon,
    ChevronRightIcon,
    ChevronLeftIcon,
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
    return { router }
  }
}
</script>

