<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Header -->
        <div class="text-center mb-12">
          <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Станции
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Обучающие программы по эксплуатации и техническому обслуживанию компрессорных станций газопровода
          </p>
        </div>

        <!-- Stations Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-12">
          <div 
            v-for="station in stations" 
            :key="station.id"
            class="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-blue-200 hover:-translate-y-2"
          >
            <!-- Image Container -->
            <div class="relative h-48 overflow-hidden bg-gray-200">
              <!-- Loading Skeleton -->
              <div class="skeleton-loader absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200"></div>
              
              <img 
                :src="getStationImageUrl(station.image)" 
                :alt="station.name"
                loading="lazy"
                decoding="async"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 relative z-10"
                @load="imageLoaded"
                @error="imageError"
              />
              <!-- Gradient Overlay -->
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent z-20"></div>
            </div>
            
            <!-- Content -->
            <div class="p-6">
              <h3 class="text-lg font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
                {{ station.name }}
              </h3>
              
              <p class="text-gray-600 text-sm leading-relaxed mb-6 line-clamp-3">
                {{ station.description }}
              </p>
              
              <!-- Action Buttons -->
              <div class="flex gap-3">
                <button 
                  @click="$router.push(`/station/${station.id}`)"
                  class="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2.5 rounded-lg font-semibold text-sm hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-md hover:shadow-lg"
                >
                  Подробнее
                </button>
                <button 
                  @click="$router.push(`/station/${station.id}/courses`)"
                  class="px-4 py-2.5 border border-blue-600 text-blue-600 rounded-lg font-semibold text-sm hover:bg-blue-600 hover:text-white transition-all duration-300"
                >
                  Тренинги
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import minioService from '@/services/minioService'

export default {
  name: 'Stations',
  components: {
    AppLayout
  },
  setup() {
    // Хранилище URL изображений из MinIO
    const stationImageUrls = ref({})
    const loadingImages = ref(false)

    // Данные станций
    const stations = ref([
      {
        id: 1,
        name: 'Компрессорная станция WKC1',
        shortName: 'WKC1',
        description: 'Головная компрессорная станция в Миришкорском районе Кашкадарьинской области',
        image: 'WKC1.jpg',
        power: '25 МВт',
        commissionDate: '25.11.2009',
        coursesCount: 8,
        status: 'active'
      },
      {
        id: 2,
        name: 'Компрессорная станция WKC2',
        shortName: 'WKC2',
        description: 'Компрессорная станция на участке газопровода',
        image: 'WKC2.jpg',
        power: '22 МВт',
        commissionDate: '01.12.2009',
        coursesCount: 7,
        status: 'active'
      },
      {
        id: 3,
        name: 'Компрессорная станция WKC3',
        shortName: 'WKC3',
        description: 'Компрессорная станция на участке газопровода',
        image: 'WKC3.jpg',
        power: '20 МВт',
        commissionDate: '15.06.2010',
        coursesCount: 6,
        status: 'active'
      },
      {
        id: 4,
        name: 'Компрессорная станция UCS1',
        shortName: 'UCS1',
        description: 'Компрессорная станция на территории Бухарской области',
        image: 'UCS1.jpg',
        power: '20 МВт',
        commissionDate: '30.07.2014',
        coursesCount: 6,
        status: 'active'
      },
      {
        id: 5,
        name: 'Компрессорная станция UCS3',
        shortName: 'UCS3',
        description: 'Компрессорная станция в Навоийской области',
        image: 'UCS3.jpg',
        power: '18 МВт',
        commissionDate: '30.07.2014',
        coursesCount: 5,
        status: 'active'
      },
      {
        id: 6,
        name: 'Газокомпрессорная станция GCS',
        shortName: 'GCS',
        description: 'Газокомпрессорная станция на магистральном газопроводе',
        image: 'GCS.jpg',
        power: '24 МВт',
        commissionDate: '20.08.2010',
        coursesCount: 7,
        status: 'active'
      },
      {
        id: 7,
        name: 'Модульная станция MS',
        shortName: 'MS',
        description: 'Модульная компрессорная станция',
        image: 'MS.jpg',
        power: '16 МВт',
        commissionDate: '10.05.2012',
        coursesCount: 4,
        status: 'active'
      },
      {
        id: 8,
        name: 'Узбекская компрессорная станция UKMS',
        shortName: 'UKMS',
        description: 'Узбекская компрессорная станция магистрального газопровода',
        image: 'UKMS.jpg',
        power: '21 МВт',
        commissionDate: '12.03.2011',
        coursesCount: 6,
        status: 'maintenance'
      }
    ])

    // Получить URL изображения станции
    const getStationImageUrl = (imageName) => {
      const objectName = `stations/${imageName}`
      // Возвращаем URL из кэша, если он есть, иначе возвращаем пустую строку или placeholder
      if (stationImageUrls.value[imageName]) {
        return stationImageUrls.value[imageName]
      }
      // Возвращаем прямой URL как fallback (пока не загружен presigned URL)
      return minioService.getFileUrl(objectName)
    }

    // Загрузить все URL изображений из MinIO
    const loadStationImages = async () => {
      loadingImages.value = true
      try {
        const promises = stations.value.map(async (station) => {
          const objectName = `stations/${station.image}`
          try {
            // Получаем presigned URL (действителен 7 дней)
            const url = await minioService.getPresignedDownloadUrl(
              objectName, 
              7 * 24 * 60 * 60, // 7 дней в секундах
              'image/jpeg'
            )
            stationImageUrls.value[station.image] = url
          } catch (error) {
            console.error(`Ошибка загрузки изображения ${station.image}:`, error)
            // Fallback к прямому URL
            stationImageUrls.value[station.image] = minioService.getFileUrl(objectName)
          }
        })
        
        await Promise.all(promises)
      } catch (error) {
        console.error('Ошибка загрузки изображений станций:', error)
      } finally {
        loadingImages.value = false
      }
    }

    // Handle image loading
    const imageLoaded = (event) => {
      event.target.classList.add('loaded')
      // Remove skeleton
      const skeleton = event.target.parentElement.querySelector('.skeleton-loader')
      if (skeleton) {
        skeleton.style.opacity = '0'
        setTimeout(() => skeleton.remove(), 300)
      }
    }

    const imageError = (event) => {
      event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="20" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EИзображение не загружено%3C/text%3E%3C/svg%3E'
    }

    // Загружаем URL изображений при монтировании компонента
    onMounted(() => {
      loadStationImages()
    })

    return {
      stations,
      stationImageUrls,
      loadingImages,
      getStationImageUrl,
      imageLoaded,
      imageError
    }
  }
}
</script>

<style scoped>
/* Skeleton loader animation */
.skeleton-loader {
  animation: pulse 1.5s ease-in-out infinite;
  background: linear-gradient(to right, #e5e7eb 0%, #d1d5db 50%, #e5e7eb 100%);
  background-size: 200% 100%;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Smooth fade-in animation for loaded images */
img.loaded {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Smooth transition for skeleton removal */
.skeleton-loader {
  transition: opacity 0.3s ease-out;
}
</style>
