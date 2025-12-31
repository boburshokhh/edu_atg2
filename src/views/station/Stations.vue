<template>
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
              <!-- Loading Skeleton - показываем пока URL не готов -->
              <div 
                v-if="!isImageUrlReady(station)"
                class="skeleton-loader absolute inset-0 z-30"
              />
              
              <!-- Изображение показываем только когда URL готов -->
              <img 
                v-if="isImageUrlReady(station)"
                :src="getStationImageUrl(station)" 
                :alt="station.name"
                loading="lazy"
                decoding="async"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 relative z-10"
                @load="imageLoaded"
                @error="imageError"
              >
              <!-- Gradient Overlay -->
              <div 
                v-if="isImageUrlReady(station)"
                class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent z-20" 
              />
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
                  class="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2.5 rounded-lg font-semibold text-sm hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-md hover:shadow-lg"
                  @click="$router.push(`/station/${station.id}`)"
                >
                  Подробнее
                </button>
                <button 
                  class="px-4 py-2.5 border border-blue-600 text-blue-600 rounded-lg font-semibold text-sm hover:bg-blue-600 hover:text-white transition-all duration-300"
                  @click="$router.push(`/station/${station.id}/courses`)"
                >
                  Тренинги
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import minioService from '@/services/minioService'
import stationService from '@/services/stationService'
import { resolveStationMedia } from '@/utils/stationsMedia'

export default {
  name: 'Stations',
  setup() {
    // Хранилище URL изображений из MinIO
    const stationImageUrls = ref({})
    const loadingImages = ref(false)
    const loadingStations = ref(false)
    const stationsError = ref('')

    // Данные станций
    const stations = ref([])

    const mapStationRow = (s) => ({
      id: s.id,
      name: s.name || '',
      shortName: s.short_name || s.shortName || '',
      description: s.description || '',
      image: s.image || '',
      power: s.power || '',
      commissionDate: s.commission_date || s.commissionDate || '',
      coursesCount: s.courses_count ?? s.coursesCount ?? 0,
      status: s.status || 'active',
    })

    const loadStations = async () => {
      loadingStations.value = true
      stationsError.value = ''
      try {
        const data = await stationService.getStations()
        stations.value = (data || []).map(mapStationRow)
      } catch (e) {
        stationsError.value = e?.message || 'Не удалось загрузить список станций'
        stations.value = []
      } finally {
        loadingStations.value = false
      }
    }

    // Проверить, готов ли URL изображения для отображения
    const isImageUrlReady = (station) => {
      const cacheKey = String(station?.id ?? station?.image ?? '')
      if (!cacheKey) return false
      
      // Если URL уже в кеше, значит готов
      if (stationImageUrls.value[cacheKey]) {
        return true
      }

      // Проверяем, есть ли публичный URL
      const resolved = resolveStationMedia(station?.image, { defaultFolder: 'stations' })
      if (resolved.kind === 'url' || resolved.kind === 'public') {
        return !!resolved.url
      }
      
      // Для MinIO нужен presigned URL из кеша
      return false
    }

    // Получить URL изображения станции
    const getStationImageUrl = (station) => {
      const cacheKey = String(station?.id ?? station?.image ?? '')
      if (cacheKey && stationImageUrls.value[cacheKey]) {
        return stationImageUrls.value[cacheKey]
      }

      const resolved = resolveStationMedia(station?.image, { defaultFolder: 'stations' })
      if (resolved.kind === 'url' || resolved.kind === 'public') return resolved.url
      if (resolved.kind === 'minio') return minioService.getFileUrl(resolved.objectKey)
      return ''
    }

    // Загрузить все URL изображений из MinIO последовательно (по одному)
    // Это позволяет показывать изображения по мере загрузки, улучшая UX
    const loadStationImages = async () => {
      loadingImages.value = true
      try {
        // Загружаем изображения последовательно, чтобы показывать их по одному
        for (const station of stations.value) {
          const cacheKey = String(station?.id ?? station?.image ?? '')
          if (!cacheKey) continue

          const resolved = resolveStationMedia(station?.image, { defaultFolder: 'stations' })

          // Если это публичный URL, сразу устанавливаем
          if (resolved.kind === 'url' || resolved.kind === 'public') {
            stationImageUrls.value[cacheKey] = resolved.url
            continue
          }

          // Если не MinIO, пропускаем
          if (resolved.kind !== 'minio') continue

          try {
            // Получаем presigned URL (действителен 7 дней)
            // Загружаем по одному, чтобы первое изображение появилось быстрее
            const url = await minioService.getPresignedDownloadUrl(
              resolved.objectKey, 
              7 * 24 * 60 * 60, // 7 дней в секундах
              resolved.contentType
            )
            // Обновляем URL - Vue реактивность покажет изображение сразу
            stationImageUrls.value[cacheKey] = url
          } catch (error) {
            console.error(`Ошибка загрузки изображения станции ${station?.id}:`, error)
            // Fallback к public или direct MinIO URL
            stationImageUrls.value[cacheKey] =
              resolved.fallbackPublicPath || minioService.getFileUrl(resolved.objectKey)
          }
        }
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
      // Скрываем изображение и показываем серый фон вместо текста "Изображение не загружено"
      event.target.style.display = 'none'
      // Skeleton останется видимым, что лучше чем показывать ошибку
    }

    // Загружаем URL изображений при монтировании компонента
    onMounted(async () => {
      await loadStations()
      await loadStationImages()
    })

    return {
      stations,
      stationImageUrls,
      loadingImages,
      loadingStations,
      stationsError,
      isImageUrlReady,
      getStationImageUrl,
      imageLoaded,
      imageError
    }
  }
}
</script>

<style scoped>
/* Skeleton loader animation with shimmer effect */
.skeleton-loader {
  background: linear-gradient(
    90deg,
    #e5e7eb 0%,
    #f3f4f6 50%,
    #e5e7eb 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
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
