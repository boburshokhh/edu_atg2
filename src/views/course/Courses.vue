<template>
  <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Header -->
        <div class="text-center mb-8 sm:mb-12">
          <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
            {{ $t('courses.title') }}
          </h1>
          <p class="text-base sm:text-lg md:text-xl text-gray-600 max-w-2xl mx-auto px-4">
            {{ $t('courses.description') }}
          </p>
        </div>

        <!-- Filters -->
        <div class="card p-4 sm:p-6 mb-6 sm:mb-8">
          <div class="flex flex-col lg:flex-row gap-3 sm:gap-4 items-center">
            <div class="flex-1 w-full">
              <el-input
                v-model="searchQuery"
                :placeholder="$t('courses.searchPlaceholder')"
                :prefix-icon="Search"
                clearable
                size="default"
                @input="handleSearch"
              />
            </div>
            <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full lg:w-auto">
              <el-select 
                v-model="selectedCategory" 
                :placeholder="$t('courses.category')"
                clearable
                class="w-full lg:w-48"
                size="default"
                @change="handleFilter"
              >
                <el-option
                  v-for="category in categories"
                  :key="category.value"
                  :label="getCategoryDisplayName(category.labelKey)"
                  :value="category.value"
                />
              </el-select>
              <el-select 
                v-model="selectedLevel" 
                :placeholder="$t('courses.level')"
                clearable
                class="w-full lg:w-48"
                size="default"
                @change="handleFilter"
              >
                <el-option
                  v-for="level in levels"
                  :key="level.value"
                  :label="getLevelDisplayName(level.labelKey)"
                  :value="level.value"
                />
              </el-select>
              <el-select 
                v-model="sortBy" 
                :placeholder="$t('courses.sortBy')"
                class="w-full lg:w-48"
                @change="handleSort"
              >
                <el-option
                  :label="$t('courses.sortPopularity')"
                  value="popularity"
                />
                <el-option
                  :label="$t('courses.sortRating')"
                  value="rating"
                />
                <el-option
                  :label="$t('courses.sortDate')"
                  value="date"
                />
              </el-select>
            </div>
          </div>
        </div>

        <!-- Courses Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          <div 
            v-for="course in filteredCourses" 
            :key="course.id"
            class="card-hover overflow-hidden"
          >
            <div class="aspect-video bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center relative">
              <img 
                :src="course.image" 
                :alt="course.title"
                class="w-full h-full object-cover"
                @error="handleImageError"
              >
              <div class="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
                <el-icon
                  :size="32"
                  class="text-white sm:w-12 sm:h-12"
                >
                  <component :is="course.icon" />
                </el-icon>
              </div>
              <div class="absolute top-4 right-4">
                <el-tag 
                  :type="getCategoryTagType(course.category)"
                  size="small"
                >
                  {{ $t(getCategoryLabel(course.category)) }}
                </el-tag>
              </div>
            </div>
            
            <div class="p-4 sm:p-6">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                <span class="text-xs sm:text-sm text-gray-500">{{ course.level }}</span>
                <div class="flex items-center space-x-1">
                  <el-rate 
                    v-model="course.rating" 
                    disabled 
                    size="small"
                    text-color="#ff9900"
                  />
                  <span class="text-xs sm:text-sm text-gray-500">({{ course.reviews }})</span>
                </div>
              </div>
              
              <h3 class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
                {{ course.title }}
              </h3>
              
              <p class="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4 line-clamp-2">
                {{ course.description }}
              </p>
              
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3 sm:mb-4">
                <div class="flex items-center space-x-2">
                  <el-icon><user /></el-icon>
                  <span class="text-xs sm:text-sm text-gray-600">{{ course.students }} студентов</span>
                </div>
                <div class="flex items-center space-x-2">
                  <el-icon><clock /></el-icon>
                  <span class="text-xs sm:text-sm text-gray-600">{{ course.duration }}</span>
                </div>
              </div>
              
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div class="flex items-center space-x-2">
                  <span class="text-sm sm:text-base text-blue-600 font-semibold">{{ $t('courses.free') }}</span>
                </div>
                <el-button 
                  type="primary"
                  size="default"
                  class="w-full sm:w-auto"
                  @click="$router.push(`/course/${course.id}`)"
                >
                  {{ $t('courses.details') }}
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="filteredCourses.length === 0"
          class="text-center py-12 sm:py-16"
        >
          <el-icon
            :size="48"
            class="text-gray-400 mb-4 sm:w-16 sm:h-16"
          >
            <search />
          </el-icon>
          <h3 class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
            Курсы не найдены
          </h3>
          <p class="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6 px-4">
            Попробуйте изменить параметры поиска или фильтры
          </p>
          <el-button
            type="primary"
            @click="clearFilters"
          >
            Сбросить фильтры
          </el-button>
        </div>

        <!-- Pagination -->
        <div
          v-if="filteredCourses.length > 0"
          class="flex justify-center mt-8 sm:mt-12"
        >
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalCourses"
            layout="prev, pager, next"
            class="flex-wrap"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, Setting, Lock, Tools, Monitor, Star } from '@element-plus/icons-vue'

export default {
  name: 'Courses',
  setup() {
    const { t } = useI18n()
    const searchQuery = ref('')
    const selectedCategory = ref('')
    const selectedLevel = ref('')
    const sortBy = ref('popularity')
    const currentPage = ref(1)
    const pageSize = ref(9)
    
    const categories = [
      { labelKey: 'courses.categories.stations', value: 'stations' },
      { labelKey: 'courses.categories.safety', value: 'safety' },
      { labelKey: 'courses.categories.maintenance', value: 'maintenance' },
      { labelKey: 'courses.categories.operation', value: 'operation' },
      { labelKey: 'courses.categories.automation', value: 'automation' },
      { labelKey: 'courses.categories.ecology', value: 'ecology' }
    ]
    
    const levels = [
      { labelKey: 'courses.levels.beginner', value: 'beginner' },
      { labelKey: 'courses.levels.intermediate', value: 'intermediate' },
      { labelKey: 'courses.levels.advanced', value: 'advanced' }
    ]
    
    const courses = ref([
      {
        id: 1,
        title: 'Эксплуатация компрессорной станции WKC1',
        description: 'Обучение персонала работе с головной компрессорной станцией газопровода',
        icon: 'Setting',
        category: 'stations',
        level: 'Средний',
        rating: 4.8,
        reviews: 45,
        students: 120,
        duration: '40 часов',
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 2,
        title: 'Промышленная безопасность',
        description: 'Основы безопасности труда на газотранспортных объектах',
        icon: 'Lock',
        category: 'safety',
        level: 'Начинающий',
        rating: 4.9,
        reviews: 38,
        students: 95,
        duration: '24 часа',
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 3,
        title: 'Техническое обслуживание оборудования',
        description: 'Плановое и аварийное обслуживание газопроводного оборудования',
        icon: 'Tools',
        category: 'maintenance',
        level: 'Продвинутый',
        rating: 4.7,
        reviews: 52,
        students: 78,
        duration: '32 часа',
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 4,
        title: 'Системы автоматизации КИПиА',
        description: 'Работа с контрольно-измерительными приборами и автоматикой',
        icon: 'Monitor',
        category: 'automation',
        level: 'Средний',
        rating: 4.8,
        reviews: 31,
        students: 65,
        duration: '28 часов',
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 5,
        title: 'Экологическая безопасность',
        description: 'Охрана окружающей среды при эксплуатации газопровода',
        icon: 'Star',
        category: 'ecology',
        level: 'Начинающий',
        rating: 4.6,
        reviews: 28,
        students: 55,
        duration: '20 часов',
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      },
      {
        id: 6,
        title: 'Эксплуатация компрессорных станций UCS',
        description: 'Работа с компрессорными станциями UCS1 и UCS3',
        icon: 'Setting',
        category: 'stations',
        level: 'Средний',
        rating: 4.7,
        reviews: 42,
        students: 88,
        duration: '36 часов',
        image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop'
      }
    ])
    
    const filteredCourses = computed(() => {
      let result = courses.value
      
      // Поиск
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(course => 
          course.title.toLowerCase().includes(query) ||
          course.description.toLowerCase().includes(query)
        )
      }
      
      // Фильтр по категории
      if (selectedCategory.value) {
        result = result.filter(course => course.category === selectedCategory.value)
      }
      
      // Фильтр по уровню
      if (selectedLevel.value) {
        result = result.filter(course => course.level === selectedLevel.value)
      }
      
      // Сортировка
      result.sort((a, b) => {
        switch (sortBy.value) {
          case 'rating':
            return b.rating - a.rating
          case 'date':
            return b.id - a.id
          default: // popularity
            return b.students - a.students
        }
      })
      
      return result
    })
    
    const totalCourses = computed(() => filteredCourses.value.length)
    
    const getCategoryLabel = (category) => {
      const categoryMap = {
        stations: 'courses.categories.stations',
        safety: 'courses.categories.safety',
        maintenance: 'courses.categories.maintenance',
        operation: 'courses.categories.operation',
        automation: 'courses.categories.automation',
        ecology: 'courses.categories.ecology'
      }
      return categoryMap[category] || category
    }
    
    const getCategoryTagType = (category) => {
      const types = {
        stations: 'primary',
        safety: 'success',
        maintenance: 'warning',
        operation: 'info',
        automation: 'danger',
        ecology: 'primary'
      }
      return types[category] || 'primary'
    }
    
    const handleSearch = () => {
      currentPage.value = 1
    }
    
    const handleFilter = () => {
      currentPage.value = 1
    }
    
    const handleSort = () => {
      currentPage.value = 1
    }
    
    const handlePageChange = (page) => {
      currentPage.value = page
    }
    
    const clearFilters = () => {
      searchQuery.value = ''
      selectedCategory.value = ''
      selectedLevel.value = ''
      sortBy.value = 'popularity'
      currentPage.value = 1
    }
    
    const handleImageError = (event) => {
      // Fallback to gradient background if image fails to load
      event.target.style.display = 'none'
      const parent = event.target.parentElement
      parent.classList.remove('bg-gradient-to-br', 'from-blue-100', 'to-blue-200')
      parent.classList.add('bg-gradient-to-br', 'from-blue-100', 'to-blue-200')
    }
    
    const getCategoryDisplayName = (labelKey) => {
      return t(labelKey)
    }
    
    const getLevelDisplayName = (labelKey) => {
      return t(labelKey)
    }
    
    return {
      searchQuery,
      selectedCategory,
      selectedLevel,
      sortBy,
      currentPage,
      pageSize,
      categories,
      levels,
      courses,
      filteredCourses,
      totalCourses,
      getCategoryLabel,
      getCategoryTagType,
      getCategoryDisplayName,
      getLevelDisplayName,
      handleSearch,
      handleFilter,
      handleSort,
      handlePageChange,
      clearFilters,
      handleImageError,
      Search,
      Setting,
      Lock,
      Tools,
      Monitor,
      Star
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
