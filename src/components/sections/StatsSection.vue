<template>
  <section class="relative section-padding bg-white overflow-hidden">
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0">
        <svg class="w-full h-full">
          <defs>
            <pattern id="blueprint-grid-stats" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#06b6d4" stroke-width="0.5"></path>
              <path d="M 0 20 L 40 20 M 20 0 L 20 40" fill="none" stroke="#06b6d4" stroke-width="0.3"></path>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#blueprint-grid-stats)"></rect>
        </svg>
      </div>
    </div>

    <div class="page-container relative z-10">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 text-center">
        <div 
          v-for="stat in stats" 
          :key="stat.label" 
          class="p-4 transition-all duration-500 opacity-100 translate-y-0"
        >
          <div class="text-2xl sm:text-3xl md:text-4xl font-bold text-tamex-blue-600 mb-1 sm:mb-2">
            {{ stat.value }}
          </div>
          <div class="text-xs sm:text-sm md:text-base text-gray-600">
            {{ $t(stat.labelKey) }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'StatsSection',
  setup() {
    const stats = [
      { value: '500+', labelKey: 'home.stats.employees' },
      { value: '6', labelKey: 'home.stats.stations' },
      { value: '1586', labelKey: 'home.stats.pipeline' },
      { value: '55', labelKey: 'home.stats.capacity' }
    ]
    
    return {
      stats
    }
  }
}
</script>
