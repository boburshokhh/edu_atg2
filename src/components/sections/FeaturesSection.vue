<template>
  <section ref="featuresSection" class="relative section-padding bg-white overflow-hidden">
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0">
        <svg class="w-full h-full">
          <defs>
            <pattern id="blueprint-grid-features" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#06b6d4" stroke-width="0.5"></path>
              <path d="M 0 20 L 40 20 M 20 0 L 20 40" fill="none" stroke="#06b6d4" stroke-width="0.3"></path>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#blueprint-grid-features)"></rect>
        </svg>
      </div>
      <!-- Decorative Elements -->
      <svg class="absolute inset-0 w-full h-full opacity-30 dark:opacity-40">
        <g>
          <rect x="15%" y="20%" width="80" height="60" fill="none" stroke="#22d3ee" stroke-width="2" rx="8"></rect>
          <circle cx="15%" cy="35%" r="4" fill="#06b6d4"></circle>
        </g>
        <g>
          <rect x="29%" y="60%" width="80" height="60" fill="none" stroke="#22d3ee" stroke-width="2" rx="8"></rect>
          <circle cx="29%" cy="75%" r="4" fill="#06b6d4"></circle>
        </g>
        <g>
          <rect x="43%" y="20%" width="80" height="60" fill="none" stroke="#22d3ee" stroke-width="2" rx="8"></rect>
          <circle cx="43%" cy="35%" r="4" fill="#06b6d4"></circle>
        </g>
        <g>
          <rect x="57%" y="60%" width="80" height="60" fill="none" stroke="#22d3ee" stroke-width="2" rx="8"></rect>
          <circle cx="57%" cy="75%" r="4" fill="#06b6d4"></circle>
        </g>
        <g>
          <rect x="71%" y="20%" width="80" height="60" fill="none" stroke="#22d3ee" stroke-width="2" rx="8"></rect>
          <circle cx="71%" cy="35%" r="4" fill="#06b6d4"></circle>
        </g>
        <g>
          <rect x="85%" y="60%" width="80" height="60" fill="none" stroke="#22d3ee" stroke-width="2" rx="8"></rect>
          <circle cx="85%" cy="75%" r="4" fill="#06b6d4"></circle>
        </g>
      </svg>
    </div>

    <div class="page-container relative z-10">
      <div class="text-center mb-12 sm:mb-16">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
          {{ $t('home.advantages') }}
        </h2>
        <p class="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto px-4">
          {{ $t('home.advantagesDesc') }}
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="bg-white rounded-xl p-6 border border-gray-200 transition-all duration-500 opacity-100 translate-y-0 hover:shadow-xl hover:-translate-y-1"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <div class="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-tamex-blue-50 to-tamex-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
            <el-icon :size="24" class="text-tamex-blue-600 sm:w-8 sm:h-8">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <h3 class="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">
            {{ $t(feature.titleKey) }}
          </h3>
          <p class="text-sm sm:text-base text-gray-600">
            {{ $t(feature.descriptionKey) }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { VideoPlay, User, Trophy, Clock, Medal, Star } from '@element-plus/icons-vue'

export default {
  name: 'FeaturesSection',
  components: {
    VideoPlay,
    User,
    Trophy,
    Clock,
    Medal,
    Star
  },
  setup() {
    const features = [
      {
        icon: 'VideoPlay',
        titleKey: 'features.interactiveModules.title',
        descriptionKey: 'features.interactiveModules.description'
      },
      {
        icon: 'User',
        titleKey: 'features.experiencedInstructors.title',
        descriptionKey: 'features.experiencedInstructors.description'
      },
      {
        icon: 'Trophy',
        titleKey: 'features.practicalSkills.title',
        descriptionKey: 'features.practicalSkills.description'
      },
      {
        icon: 'Clock',
        titleKey: 'features.flexibleSchedule.title',
        descriptionKey: 'features.flexibleSchedule.description'
      },
      {
        icon: 'Medal',
        titleKey: 'features.certification.title',
        descriptionKey: 'features.certification.description'
      },
      {
        icon: 'Star',
        titleKey: 'features.corporateCulture.title',
        descriptionKey: 'features.corporateCulture.description'
      }
    ]
    
    return {
      features
    }
  }
}
</script>
