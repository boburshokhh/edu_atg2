<template>
  <section id="about" class="relative section-padding bg-white overflow-hidden">
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0 opacity-5">
        <svg class="w-full h-full">
          <defs>
            <pattern id="about-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1E3A8A" stroke-width="0.5"></path>
              <path d="M 0 20 L 40 20 M 20 0 L 20 40" fill="none" stroke="#1E3A8A" stroke-width="0.3"></path>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#about-grid)"></rect>
        </svg>
      </div>
    </div>

    <div class="page-container relative z-10">
      <!-- Заголовок секции -->
      <div class="text-center mb-12 sm:mb-16">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-tamex-blue-800 mb-6 px-4">
          {{ $t('about.title') }}
        </h2>
        <p class="text-base sm:text-lg text-tamex-blue-600 font-medium max-w-4xl mx-auto mb-4 px-4 italic">
          "{{ $t('about.motto') }}"
        </p>
      </div>

      <!-- Основное описание -->
      <div class="max-w-5xl mx-auto mb-16">
        <div class="bg-gradient-to-br from-tamex-blue-50 to-white rounded-2xl p-8 sm:p-12 shadow-xl border border-tamex-blue-100">
          <h3 class="text-xl sm:text-2xl font-bold text-tamex-blue-800 mb-6">
            {{ $t('about.staffDevelopment.title') }}
          </h3>
          <p class="text-sm sm:text-base text-gray-700 leading-relaxed mb-8">
            {{ $t('about.staffDevelopment.description') }}
          </p>

          <!-- Направления обучения -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div 
              v-for="(program, index) in trainingPrograms" 
              :key="index"
              class="group bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-tamex-blue-300"
            >
              <div class="flex items-start space-x-4">
                <div class="flex-1">
                  <h4 class="text-base font-semibold text-tamex-blue-800 mb-2 group-hover:text-tamex-blue-600 transition-colors">
                    {{ $t(program.titleKey) }}
                  </h4>
                  <p class="text-xs sm:text-sm text-gray-600 leading-relaxed">
                    {{ $t(program.descKey) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Международные сертификации -->
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-12">
          <h3 class="text-xl sm:text-2xl md:text-3xl font-bold text-tamex-blue-800 mb-4">
            {{ $t('about.certifications.title') }}
          </h3>
          <p class="text-sm sm:text-base text-gray-600 max-w-3xl mx-auto px-4">
            {{ $t('about.certifications.subtitle') }}
          </p>
          <p class="text-xs sm:text-sm text-gray-500 mt-2 italic">
            {{ $t('about.certifications.year') }}
          </p>
        </div>

        <!-- Изображение сертификатов -->
        <div class="flex justify-center mb-12">
          <div class="relative max-w-4xl w-full">
            <img 
              src="/sertification/image.png" 
              alt="Международные сертификации ISO 9001, OHSAS 18001, ISO 14001"
              class="w-full h-auto rounded-2xl shadow-2xl border border-gray-200 hover:shadow-3xl transition-all duration-500"
            />
            <!-- Декоративная рамка -->
            <div class="absolute inset-0 rounded-2xl border-2 border-tamex-blue-200 opacity-0 hover:opacity-100 transition-opacity duration-500"></div>
          </div>
        </div>

        <!-- Карточки сертификатов -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          <div 
            v-for="(cert, index) in certifications" 
            :key="index"
            class="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 border-2 border-gray-100 hover:border-tamex-gold-500 overflow-hidden"
          >
            <!-- Декоративный элемент -->
            <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-tamex-blue-50 to-transparent rounded-bl-full opacity-50"></div>
            
            <div class="relative z-10">
              <!-- Стандарт -->
              <div class="text-center mb-4">
                <div class="inline-block px-3 py-2 bg-gray-50 rounded-lg border border-gray-200 group-hover:border-tamex-gold-500 transition-colors">
                  <span class="text-lg font-bold text-tamex-blue-800">
                    {{ cert.standard }}
                  </span>
                </div>
              </div>

              <!-- Название -->
              <h4 class="text-lg font-bold text-center mb-3 text-gray-800 group-hover:text-tamex-blue-700 transition-colors">
                {{ $t(cert.nameKey) }}
              </h4>

              <!-- Описание -->
              <p class="text-xs sm:text-sm text-gray-600 text-center leading-relaxed">
                {{ $t(cert.descKey) }}
              </p>

              <!-- Декоративная линия -->
              <div class="mt-6 pt-4 border-t border-gray-200 group-hover:border-tamex-gold-500 transition-colors">
                <div class="flex justify-center">
                  <div class="h-1 w-16 bg-gradient-to-r from-tamex-blue-600 to-tamex-gold-500 rounded-full group-hover:w-24 transition-all duration-500"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Политика компании -->
        <div class="mt-12 text-center">
          <div class="inline-block bg-gradient-to-r from-tamex-blue-50 via-white to-tamex-blue-50 rounded-2xl px-6 py-4 shadow-md border border-tamex-blue-100">
            <p class="text-sm sm:text-base text-gray-700 max-w-3xl italic">
              {{ $t('about.certifications.policy') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AboutSection',
  setup() {
    const trainingPrograms = [
      {
        titleKey: 'about.programs.technical.title',
        descKey: 'about.programs.technical.desc'
      },
      {
        titleKey: 'about.programs.technology.title',
        descKey: 'about.programs.technology.desc'
      },
      {
        titleKey: 'about.programs.safety.title',
        descKey: 'about.programs.safety.desc'
      },
      {
        titleKey: 'about.programs.digital.title',
        descKey: 'about.programs.digital.desc'
      }
    ]

    const certifications = [
      {
        standard: 'ISO 9001',
        nameKey: 'about.certs.iso9001.name',
        descKey: 'about.certs.iso9001.desc'
      },
      {
        standard: 'OHSAS 18001',
        nameKey: 'about.certs.ohsas.name',
        descKey: 'about.certs.ohsas.desc'
      },
      {
        standard: 'ISO 14001',
        nameKey: 'about.certs.iso14001.name',
        descKey: 'about.certs.iso14001.desc'
      }
    ]

    return {
      trainingPrograms,
      certifications
    }
  }
}
</script>

<style scoped>
.section-padding {
  padding: 4rem 1rem;
}

@media (min-width: 640px) {
  .section-padding {
    padding: 5rem 1.5rem;
  }
}

@media (min-width: 1024px) {
  .section-padding {
    padding: 6rem 2rem;
  }
}
</style>

