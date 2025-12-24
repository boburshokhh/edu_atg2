<template>
  <section
    id="about"
    class="relative section-padding bg-white overflow-hidden"
  >
    <!-- Background Pattern -->
    <div class="section-pattern">
      <div class="absolute inset-0 opacity-5">
        <svg class="w-full h-full">
          <defs>
            <pattern
              id="about-grid"
              width="40"
              height="40"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="#1E3A8A"
                stroke-width="0.5"
              />
              <path
                d="M 0 20 L 40 20 M 20 0 L 20 40"
                fill="none"
                stroke="#1E3A8A"
                stroke-width="0.3"
              />
            </pattern>
          </defs>
          <rect
            width="100%"
            height="100%"
            fill="url(#about-grid)"
          />
        </svg>
      </div>
    </div>

    <!-- Image Lightbox -->
    <vue-easy-lightbox
      :visible="lightboxVisible"
      :imgs="lightboxImages"
      :index="lightboxIndex"
      @hide="handleHideLightbox"
    />

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

          <!-- Кнопка "Подробнее" для секции О нас -->
          <div class="mt-8 text-center">
            <a 
              href="https://asiatransgas.uz/ru/about" 
              target="_blank" 
              rel="noopener noreferrer"
              class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-tamex-blue-600 to-tamex-blue-700 text-white font-semibold text-base rounded-lg shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-105 hover:from-tamex-blue-700 hover:to-tamex-blue-800 group"
            >
              <span>{{ $t('about.readMore') }}</span>
              <svg 
                class="w-4 h-4 ml-2 transition-transform duration-300 group-hover:translate-x-1" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>
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
            >
            <!-- Декоративная рамка -->
            <div class="absolute inset-0 rounded-2xl border-2 border-tamex-blue-200 opacity-0 hover:opacity-100 transition-opacity duration-500" />
          </div>
        </div>

        <!-- Карточки сертификатов -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          <div 
            v-for="(cert, index) in certifications" 
            :key="index"
            class="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 border-2 border-gray-100 hover:border-tamex-gold-500 overflow-hidden cursor-pointer"
            @click="openLightbox(index)"
          >
            <!-- Изображение сертификата -->
            <div class="relative h-64 sm:h-72 overflow-hidden bg-gray-50">
              <img 
                :src="cert.image" 
                :alt="cert.standard"
                class="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
              >
              <!-- Overlay при наведении -->
              <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div class="bg-white rounded-full p-3 shadow-lg">
                    <svg
                      class="w-6 h-6 text-tamex-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Информация о сертификате -->
            <div class="p-6">
              <!-- Стандарт -->
              <div class="flex justify-center mb-4">
                <div class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-tamex-blue-50 to-tamex-blue-100 rounded-lg border border-tamex-blue-200 group-hover:border-tamex-gold-500 transition-colors">
                  <span class="text-base sm:text-lg font-bold text-tamex-blue-800">
                    {{ cert.standard }}
                  </span>
                </div>
              </div>

              <!-- Название -->
              <h4 class="text-lg sm:text-xl font-bold text-center mb-3 text-gray-800 group-hover:text-tamex-blue-700 transition-colors">
                {{ $t(cert.nameKey) }}
              </h4>

              <!-- Описание -->
              <p class="text-xs sm:text-sm text-gray-600 text-center leading-relaxed mb-4">
                {{ $t(cert.descKey) }}
              </p>

              <!-- Кнопка просмотра -->
              <div class="flex justify-center">
                <button 
                  class="inline-flex items-center text-sm font-semibold text-tamex-blue-600 hover:text-tamex-blue-800 transition-colors group"
                >
                  <span>{{ $t('about.viewCertificate') }}</span>
                  <svg
                    class="w-4 h-4 ml-2 transition-transform group-hover:scale-110"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                </button>
              </div>

              <!-- Декоративная линия -->
              <div class="mt-4 pt-4 border-t border-gray-200 group-hover:border-tamex-gold-500 transition-colors">
                <div class="flex justify-center">
                  <div class="h-1 w-16 bg-gradient-to-r from-tamex-blue-600 to-tamex-gold-500 rounded-full group-hover:w-24 transition-all duration-500" />
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

        <!-- Кнопка "Подробнее" -->
        <div class="mt-12 text-center">
          <a 
            href="https://asiatransgas.uz/ru/certificates" 
            target="_blank" 
            rel="noopener noreferrer"
            class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-tamex-blue-600 to-tamex-blue-700 text-white font-semibold text-lg rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:from-tamex-blue-700 hover:to-tamex-blue-800 group"
          >
            <span>{{ $t('about.readMore') }}</span>
            <svg 
              class="w-5 h-5 ml-2 transition-transform duration-300 group-hover:translate-x-1" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { ref, computed } from 'vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import { useI18n } from 'vue-i18n'

export default {
  name: 'AboutSection',
  components: {
    VueEasyLightbox
  },
  setup() {
    const { locale } = useI18n()
    
    const lightboxVisible = ref(false)
    const lightboxIndex = ref(0)

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

    // Функция для определения изображения сертификата на основе языка
    const getCertImage = (certId, currentLocale) => {
      const lang = currentLocale === 'en' ? 'en' : 'ru'
      
      // Проверяем доступные изображения для каждого сертификата
      const images = {
        'ISO 9001': {
          en: '/sertification/ISO_9001_en.jpg',
          ru: '/sertification/ISO_9001_en.jpg' // используем английскую версию, так как русской нет
        },
        'ISO 45001': {
          en: '/sertification/ISO_45001_ru.jpg', // используем русскую версию, так как английской нет
          ru: '/sertification/ISO_45001_ru.jpg'
        },
        'ISO 14001': {
          en: '/sertification/ISO_14001_en.jpg',
          ru: '/sertification/ISO_14001_ru.jpg'
        }
      }
      
      return images[certId]?.[lang] || images[certId]?.ru || '/sertification/image.png'
    }

    const certifications = computed(() => [
      {
        standard: 'ISO 9001',
        nameKey: 'about.certs.iso9001.name',
        descKey: 'about.certs.iso9001.desc',
        image: getCertImage('ISO 9001', locale.value)
      },
      {
        standard: 'ISO 45001',
        nameKey: 'about.certs.ohsas.name',
        descKey: 'about.certs.ohsas.desc',
        image: getCertImage('ISO 45001', locale.value)
      },
      {
        standard: 'ISO 14001',
        nameKey: 'about.certs.iso14001.name',
        descKey: 'about.certs.iso14001.desc',
        image: getCertImage('ISO 14001', locale.value)
      }
    ])

    const lightboxImages = computed(() => {
      return certifications.value.map(cert => cert.image)
    })

    const openLightbox = (index) => {
      lightboxIndex.value = index
      lightboxVisible.value = true
    }

    const handleHideLightbox = () => {
      lightboxVisible.value = false
    }

    return {
      trainingPrograms,
      certifications,
      lightboxVisible,
      lightboxIndex,
      lightboxImages,
      openLightbox,
      handleHideLightbox
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

