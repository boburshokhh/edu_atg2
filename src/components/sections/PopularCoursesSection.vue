<template>
  <section class="relative section-padding bg-gray-50 overflow-hidden">
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0">
        <svg class="w-full h-full">
          <defs>
            <pattern id="blueprint-grid-courses" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#06b6d4" stroke-width="0.5"></path>
              <path d="M 0 20 L 40 20 M 20 0 L 20 40" fill="none" stroke="#06b6d4" stroke-width="0.3"></path>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#blueprint-grid-courses)"></rect>
        </svg>
      </div>
    </div>

    <div class="page-container relative z-10">
      <div class="text-center mb-12 sm:mb-16">
        <h2 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-tamex-blue-600 via-tamex-blue-700 to-tamex-blue-800 bg-clip-text text-transparent mb-4 sm:mb-6 px-4">
          {{ $t('home.popularCourses') }}
        </h2>
        <p class="text-base sm:text-lg text-gray-600 max-w-3xl mx-auto px-4">
          {{ $t('home.coursesDesc') }}
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-8 sm:mb-12">
        <div 
          v-for="course in popularCourses" 
          :key="course.id"
          class="group relative overflow-hidden rounded-lg"
          style="min-height: 250px;"
        >
          <div class="relative h-full cursor-pointer rounded-lg overflow-hidden">
            <img 
              :src="course.image" 
              :alt="course.title"
              class="absolute inset-0 w-full h-full object-cover"
              loading="lazy"
              @error="handleImageError"
            />
            <div class="absolute inset-0 bg-black opacity-0 group-hover:opacity-60 transition-opacity duration-300"></div>
            <div class="absolute inset-0 p-4 sm:p-6 md:p-8 flex flex-col justify-between z-10">
              <div class="h-1 bg-white/50 transition-all duration-300 w-0 group-hover:w-full"></div>
              <div>
                <h3 class="text-white font-bold mb-2 sm:mb-3 transition-all duration-300 text-lg sm:text-xl md:text-2xl">
                  {{ course.title }}
                </h3>
                <div class="overflow-hidden transition-all duration-300 max-h-0 opacity-0 group-hover:max-h-96 group-hover:opacity-100">
                  <p class="text-white/95 text-xs sm:text-sm leading-relaxed mb-2 sm:mb-3">
                    {{ course.description }}
                  </p>
                </div>
                <div class="h-1 bg-white w-16 opacity-40"></div>
              </div>
            </div>
            <div class="absolute inset-0 border-2 border-white/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
        </div>
      </div>

      <div class="flex justify-center mt-6 sm:mt-8 px-4">
        <el-button 
          @click="$router.push('/courses')" 
          type="primary" 
          size="large"
          class="w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-tamex-blue-600 hover:bg-tamex-blue-700 text-white font-semibold rounded-lg transition-colors duration-300 shadow-lg hover:shadow-xl"
        >
          <span class="flex items-center justify-center gap-2 sm:gap-3 text-sm sm:text-base">
            <el-icon class="w-5 h-5 sm:w-6 sm:h-6">
              <Setting />
            </el-icon>
            {{ $t('courses.viewAll') }}
            <el-icon class="w-4 h-4 sm:w-5 sm:h-5">
              <ArrowRight />
            </el-icon>
          </span>
        </el-button>
      </div>
    </div>
  </section>
</template>

<script>
import { Setting, Lock, Tools, ArrowRight } from '@element-plus/icons-vue'

export default {
  name: 'PopularCoursesSection',
  components: {
    Setting,
    Lock,
    Tools,
    ArrowRight
  },
  setup() {
    const popularCourses = [
      {
        id: 1,
        title: 'Компрессорная станция WKC1',
        description: 'Эксплуатация и техническое обслуживание головной компрессорной станции',
        icon: 'Setting',
        rating: 4.8,
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 2,
        title: 'Безопасность труда',
        description: 'Основы промышленной безопасности на газотранспортных объектах',
        icon: 'Lock',
        rating: 4.9,
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 3,
        title: 'Техническое обслуживание',
        description: 'Плановое и аварийное обслуживание газопроводного оборудования',
        icon: 'Tools',
        rating: 4.7,
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      }
    ]
    
    const handleImageError = (event) => {
      // Fallback to gradient background if image fails to load
      event.target.style.display = 'none'
      const parent = event.target.parentElement
      parent.classList.remove('bg-gradient-to-br', 'from-tamex-blue-100', 'to-tamex-blue-200')
      parent.classList.add('bg-gradient-to-br', 'from-tamex-blue-100', 'to-tamex-blue-200')
    }
    
    return {
      popularCourses,
      handleImageError
    }
  }
}
</script>
