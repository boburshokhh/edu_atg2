<template>
  <section
    ref="featuresSection"
    class="relative section-padding bg-white overflow-hidden"
  >
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0">
        <svg class="w-full h-full">
          <defs>
            <pattern
              id="blueprint-grid-features"
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
            fill="url(#blueprint-grid-features)"
          />
        </svg>
      </div>
      <!-- Decorative Elements -->
      <svg class="absolute inset-0 w-full h-full opacity-30 dark:opacity-40">
        <g>
          <rect
            x="15%"
            y="20%"
            width="80"
            height="60"
            fill="none"
            stroke="#22d3ee"
            stroke-width="2"
            rx="8"
          />
          <circle
            cx="15%"
            cy="35%"
            r="4"
            fill="#06b6d4"
          />
        </g>
        <g>
          <rect
            x="29%"
            y="60%"
            width="80"
            height="60"
            fill="none"
            stroke="#22d3ee"
            stroke-width="2"
            rx="8"
          />
          <circle
            cx="29%"
            cy="75%"
            r="4"
            fill="#06b6d4"
          />
        </g>
        <g>
          <rect
            x="43%"
            y="20%"
            width="80"
            height="60"
            fill="none"
            stroke="#22d3ee"
            stroke-width="2"
            rx="8"
          />
          <circle
            cx="43%"
            cy="35%"
            r="4"
            fill="#06b6d4"
          />
        </g>
        <g>
          <rect
            x="57%"
            y="60%"
            width="80"
            height="60"
            fill="none"
            stroke="#22d3ee"
            stroke-width="2"
            rx="8"
          />
          <circle
            cx="57%"
            cy="75%"
            r="4"
            fill="#06b6d4"
          />
        </g>
        <g>
          <rect
            x="71%"
            y="20%"
            width="80"
            height="60"
            fill="none"
            stroke="#22d3ee"
            stroke-width="2"
            rx="8"
          />
          <circle
            cx="71%"
            cy="35%"
            r="4"
            fill="#06b6d4"
          />
        </g>
        <g>
          <rect
            x="85%"
            y="60%"
            width="80"
            height="60"
            fill="none"
            stroke="#22d3ee"
            stroke-width="2"
            rx="8"
          />
          <circle
            cx="85%"
            cy="75%"
            r="4"
            fill="#06b6d4"
          />
        </g>
      </svg>
    </div>

    <div class="page-container relative z-10">
      <div class="text-center mb-12 sm:mb-16">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
          Преимущества
        </h2>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="group relative bg-white rounded-2xl overflow-hidden transition-all duration-500 hover:shadow-2xl hover:-translate-y-2 border border-gray-100 hover:border-tamex-blue-200"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <!-- Number Badge -->
          <div class="absolute top-4 left-4 z-30">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-tamex-blue-500 to-tamex-blue-700 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
              <span class="text-white font-bold text-lg">{{ String(index + 1).padStart(2, '0') }}</span>
            </div>
          </div>

          <!-- Icon Container -->
          <div class="relative h-80 bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-8 overflow-hidden">
            <!-- Background Decoration -->
            <div class="absolute inset-0 opacity-5">
              <svg
                class="w-full h-full"
                viewBox="0 0 200 200"
              >
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1"
                  class="text-tamex-blue-500"
                />
                <circle
                  cx="100"
                  cy="100"
                  r="60"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1"
                  class="text-tamex-blue-400"
                />
              </svg>
            </div>
            
            <!-- Icon -->
            <img 
              :src="feature.icon" 
              :alt="feature.title"
              class="relative z-10 w-48 h-48 sm:w-56 sm:h-56 object-contain transition-transform duration-300 group-hover:scale-105"
            >
            
            <!-- Hover Overlay with Description -->
            <div class="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center p-6 opacity-0 group-hover:opacity-100 transition-all duration-300 z-20">
              <div class="text-center">
                <p class="text-white text-sm sm:text-base leading-relaxed font-medium">
                  {{ feature.description }}
                </p>
              </div>
            </div>
          </div>

          <!-- Title Section -->
          <div class="p-6 bg-white">
            <h3 class="text-lg sm:text-xl font-bold text-gray-900 leading-tight text-center group-hover:text-tamex-blue-600 transition-colors duration-300">
              {{ feature.title }}
            </h3>
            
            <!-- Bottom Accent Line -->
            <div class="mt-4 h-1 w-16 bg-gradient-to-r from-tamex-blue-500 to-tamex-blue-700 rounded-full mx-auto group-hover:w-24 transition-all duration-300" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'FeaturesSection',
  setup() {
    const features = [
      {
        icon: '/icons/Повышение безопасности работы.svg',
        title: 'Повышение безопасности работы',
        description: 'Умение правильно соблюдать процедуры и быстро реагировать на аварийные ситуации снижает риск инцидентов и аварий.'
      },
      {
        icon: '/icons/Снижение простоев и аварий оборудования.svg',
        title: 'Снижение простоев и аварий оборудования',
        description: 'Квалифицированные инженеры оперативно выявляют и устраняют неисправности, что минимизирует незапланированные остановки.'
      },
      {
        icon: '/icons/Оптимизация затрат на ремонт и эксплуатацию.svg',
        title: 'Оптимизация затрат на ремонт и эксплуатацию',
        description: 'Предиктивное и своевременное обслуживание позволяет экономить на ремонтах и замене деталей.'
      },
      {
        icon: '/icons/Соответствие нормативным требованиям.svg',
        title: 'Соответствие нормативным требованиям',
        description: 'Обеспечение соответствия требованиям безопасности и законодательства предотвращает штрафы и юридические риски.'
      }
    ]
    
    return {
      features
    }
  }
}
</script>
