<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
    <div class="page-container">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Отделы
        </h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          Структурные подразделения компании
        </p>
      </div>

      <!-- Departments Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-12">
        <div 
          v-for="department in departments" 
          :key="department.id"
          class="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-blue-200 hover:-translate-y-2"
        >
          <!-- Image Container -->
          <div class="relative h-48 overflow-hidden bg-gray-200">
            <!-- Loading Skeleton - показываем пока URL не готов -->
            <div 
              v-if="!isImageUrlReady(department)"
              class="skeleton-loader absolute inset-0 z-30"
            />
            
            <!-- Изображение показываем только когда URL готов -->
            <img 
              v-if="isImageUrlReady(department)"
              :src="getDepartmentImageUrl(department)" 
              :alt="department.name"
              loading="lazy"
              decoding="async"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 relative z-10"
              @load="imageLoaded"
              @error="imageError"
            >
            <!-- Gradient Overlay -->
            <div 
              v-if="isImageUrlReady(department)"
              class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent z-20" 
            />
          </div>
          
          <!-- Content -->
          <div class="p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
              {{ department.name }}
            </h3>
            
            <p class="text-gray-600 text-sm leading-relaxed mb-6 line-clamp-3">
              {{ department.description }}
            </p>
            
            <!-- Action Buttons -->
            <div class="flex gap-3">
              <button 
                class="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2.5 rounded-lg font-semibold text-sm hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-md hover:shadow-lg"
                @click="$router.push(`/department/${department.id}`)"
              >
                Подробнее
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
import AppLayout from '@/components/layout/AppLayout.vue'
import minioService from '@/services/minioService'
import departmentService from '@/services/departmentService'
import { resolveDepartmentMedia } from '@/utils/departmentsMedia'

export default {
  name: 'Departments',
  components: {
    AppLayout
  },
  setup() {
    // Хранилище URL изображений из MinIO
    const departmentImageUrls = ref({})
    const loadingImages = ref(false)
    const loadingDepartments = ref(false)
    const departmentsError = ref('')

    // Данные отделов
    const departments = ref([])

    const mapDepartmentRow = (d) => ({
      id: d.id,
      name: d.name || '',
      shortName: d.short_name || d.shortName || '',
      description: d.description || '',
      image: d.image || '',
      status: d.status || 'active',
    })

    const loadDepartments = async () => {
      loadingDepartments.value = true
      departmentsError.value = ''
      try {
        const data = await departmentService.getDepartments()
        departments.value = (data || []).map(mapDepartmentRow)
      } catch (e) {
        departmentsError.value = e?.message || 'Не удалось загрузить список отделов'
        departments.value = []
      } finally {
        loadingDepartments.value = false
      }
    }

    // Проверить, готов ли URL изображения для отображения
    const isImageUrlReady = (department) => {
      const cacheKey = String(department?.id ?? department?.image ?? '')
      if (!cacheKey) return false
      
      // Если URL уже в кеше, значит готов
      if (departmentImageUrls.value[cacheKey]) {
        return true
      }

      // Проверяем, есть ли публичный URL
      const resolved = resolveDepartmentMedia(department?.image, { defaultFolder: 'departments' })
      if (resolved.kind === 'url' || resolved.kind === 'public') {
        return !!resolved.url
      }
      
      // Для MinIO нужен presigned URL из кеша
      return false
    }

    // Получить URL изображения отдела
    const getDepartmentImageUrl = (department) => {
      const cacheKey = String(department?.id ?? department?.image ?? '')
      if (cacheKey && departmentImageUrls.value[cacheKey]) {
        return departmentImageUrls.value[cacheKey]
      }

      const resolved = resolveDepartmentMedia(department?.image, { defaultFolder: 'departments' })
      if (resolved.kind === 'url' || resolved.kind === 'public') return resolved.url
      if (resolved.kind === 'minio') return minioService.getFileUrl(resolved.objectKey)
      return ''
    }

    // Загрузить все URL изображений из MinIO последовательно (по одному)
    // Это позволяет показывать изображения по мере загрузки, улучшая UX
    const loadDepartmentImages = async () => {
      loadingImages.value = true
      try {
        // Загружаем изображения последовательно, чтобы показывать их по одному
        for (const department of departments.value) {
          const cacheKey = String(department?.id ?? department?.image ?? '')
          if (!cacheKey) continue

          const resolved = resolveDepartmentMedia(department?.image, { defaultFolder: 'departments' })

          // Если это публичный URL, сразу устанавливаем
          if (resolved.kind === 'url' || resolved.kind === 'public') {
            departmentImageUrls.value[cacheKey] = resolved.url
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
            departmentImageUrls.value[cacheKey] = url
          } catch (error) {
            console.error(`Ошибка загрузки изображения отдела ${department?.id}:`, error)
            // Fallback к public или direct MinIO URL
            departmentImageUrls.value[cacheKey] =
              resolved.fallbackPublicPath || minioService.getFileUrl(resolved.objectKey)
          }
        }
      } catch (error) {
        console.error('Ошибка загрузки изображений отделов:', error)
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
      await loadDepartments()
      await loadDepartmentImages()
    })

    return {
      departments,
      departmentImageUrls,
      loadingImages,
      loadingDepartments,
      departmentsError,
      isImageUrlReady,
      getDepartmentImageUrl,
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

