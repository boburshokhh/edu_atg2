<template>
  <section class="relative section-padding overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0">
        <svg class="w-full h-full">
          <defs>
            <pattern
              id="blueprint-grid-cta"
              width="40"
              height="40"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="#06b6d4"
                stroke-width="0.5"
              />
              <path
                d="M 0 20 L 40 20 M 20 0 L 20 40"
                fill="none"
                stroke="#06b6d4"
                stroke-width="0.3"
              />
            </pattern>
          </defs>
          <rect
            width="100%"
            height="100%"
            fill="url(#blueprint-grid-cta)"
          />
        </svg>
      </div>
    </div>

    <div class="page-container text-center relative z-10">
      <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 sm:mb-4 px-4">
        {{ $t('home.cta.title') }}
      </h2>
      <p class="text-base sm:text-lg text-gray-600 mb-6 sm:mb-8 max-w-2xl mx-auto px-4">
        {{ $t('home.cta.description') }}
      </p>
      <el-button 
        type="primary" 
        size="large" 
        class="px-6 sm:px-8 py-3 bg-gradient-to-r from-tamex-blue-600 to-tamex-blue-700 hover:from-tamex-blue-700 hover:to-tamex-blue-800 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl shadow-lg"
        @click="$router.push('/stations')"
      >
        {{ $t('nav.stations') }}
      </el-button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'CTASection'
}
</script>
