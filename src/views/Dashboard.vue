<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Header -->
        <div class="mb-6 sm:mb-8">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                {{ $t('dashboard.title') }}
              </h1>
              <p class="text-sm sm:text-base text-gray-600">
                {{ $t('dashboard.welcome') }}
              </p>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div class="card p-4 sm:p-6">
            <div class="flex items-center">
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <el-icon
                  :size="20"
                  class="text-blue-600 sm:w-6 sm:h-6"
                >
                  <VideoPlay />
                </el-icon>
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm text-gray-600">
                  {{ $t('dashboard.stats.activeCourses') }}
                </p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">
                  {{ stats.activeCourses }}
                </p>
              </div>
            </div>
          </div>

          <div class="card p-4 sm:p-6">
            <div class="flex items-center">
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <el-icon
                  :size="20"
                  class="text-orange-600 sm:w-6 sm:h-6"
                >
                  <Trophy />
                </el-icon>
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm text-gray-600">
                  {{ $t('dashboard.stats.completedCourses') }}
                </p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">
                  {{ stats.completedCourses }}
                </p>
              </div>
            </div>
          </div>

          <div class="card p-4 sm:p-6">
            <div class="flex items-center">
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-blue-200 rounded-lg flex items-center justify-center">
                <el-icon
                  :size="20"
                  class="text-blue-700 sm:w-6 sm:h-6"
                >
                  <Clock />
                </el-icon>
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm text-gray-600">
                  {{ $t('dashboard.stats.hoursStudied') }}
                </p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">
                  {{ stats.hoursStudied }}
                </p>
              </div>
            </div>
          </div>

          <div class="card p-4 sm:p-6">
            <div class="flex items-center">
              <div class="w-10 h-10 sm:w-12 sm:h-12 bg-orange-200 rounded-lg flex items-center justify-center">
                <el-icon
                  :size="20"
                  class="text-orange-700 sm:w-6 sm:h-6"
                >
                  <Medal />
                </el-icon>
              </div>
              <div class="ml-3 sm:ml-4">
                <p class="text-xs sm:text-sm text-gray-600">
                  {{ $t('dashboard.stats.certificates') }}
                </p>
                <p class="text-lg sm:text-2xl font-bold text-gray-900">
                  {{ stats.certificates }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Active Courses -->
          <div class="lg:col-span-2">
            <div class="card p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-semibold text-gray-900">
                  {{ $t('dashboard.activeCourses.title') }}
                </h2>
                <el-button
                  type="primary"
                  plain
                  @click="$router.push('/courses')"
                >
                  {{ $t('dashboard.activeCourses.viewAll') }}
                </el-button>
              </div>

              <div class="space-y-4">
                <div 
                  v-for="course in activeCourses" 
                  :key="course.id"
                  class="flex items-center gap-4 p-4 bg-gray-50 rounded-lg"
                >
                  <div class="w-16 h-12 bg-gradient-to-br from-blue-100 to-orange-100 rounded flex items-center justify-center">
                    <el-icon
                      :size="24"
                      class="text-blue-600"
                    >
                      <component :is="course.icon" />
                    </el-icon>
                  </div>
                  
                  <div class="flex-1">
                    <h3 class="font-semibold text-gray-900">
                      {{ course.title }}
                    </h3>
                    <p class="text-sm text-gray-600">
                      {{ course.progress }}% {{ $t('dashboard.activeCourses.completed') }}
                    </p>
                    <el-progress 
                      :percentage="course.progress" 
                      :show-text="false"
                      :stroke-width="6"
                      color="#0284c7"
                    />
                  </div>
                  
                  <div class="text-right">
                    <el-button
                      type="primary"
                      size="small"
                      @click="$router.push(`/course/${course.id}`)"
                    >
                      {{ $t('dashboard.activeCourses.continue') }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <!-- Recent Activity -->
            <div class="card p-6 mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">
                {{ $t('dashboard.activity.title') }}
              </h3>
              <div class="space-y-4">
                <div 
                  v-for="activity in recentActivity" 
                  :key="activity.id"
                  class="flex items-center gap-3"
                >
                  <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <el-icon
                      :size="16"
                      class="text-blue-600"
                    >
                      <component :is="activity.icon" />
                    </el-icon>
                  </div>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">
                      {{ activity.title }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ activity.time }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Achievements -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">
                {{ $t('dashboard.achievements.title') }}
              </h3>
              <div class="space-y-4">
                <div 
                  v-for="achievement in achievements" 
                  :key="achievement.id"
                  class="flex items-center gap-3"
                >
                  <div class="w-10 h-10 bg-gradient-to-br from-orange-100 to-orange-200 rounded-full flex items-center justify-center">
                    <el-icon
                      :size="20"
                      class="text-orange-600"
                    >
                      <component :is="achievement.icon" />
                    </el-icon>
                  </div>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">
                      {{ achievement.title }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ achievement.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommended Courses -->
        <div class="mt-8">
          <div class="card p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900">
                {{ $t('dashboard.recommended.title') }}
              </h2>
              <el-button
                type="primary"
                plain
                @click="$router.push('/courses')"
              >
                {{ $t('dashboard.recommended.viewAll') }}
              </el-button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div 
                v-for="course in recommendedCourses" 
                :key="course.id"
                class="card-hover overflow-hidden"
              >
                <div class="aspect-video bg-gradient-to-br from-blue-100 to-orange-100 flex items-center justify-center">
                  <el-icon
                    :size="48"
                    class="text-blue-600"
                  >
                    <component :is="course.icon" />
                  </el-icon>
                </div>
                <div class="p-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-2">
                    {{ course.title }}
                  </h3>
                  <p class="text-gray-600 mb-4">
                    {{ course.description }}
                  </p>
                  <div class="flex items-center justify-between">
                    <span class="text-blue-600 font-semibold">{{ $t('dashboard.recommended.free') }}</span>
                    <el-button
                      type="primary"
                      size="small"
                      @click="$router.push(`/course/${course.id}`)"
                    >
                      {{ $t('dashboard.recommended.details') }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AppLayout from '@/components/AppLayout.vue'
import authService from '@/services/auth'
import userProfileService from '@/services/userProfile'
import { 
  VideoPlay, 
  Trophy, 
  Clock, 
  Medal, 
  Setting, 
  Lock, 
  Tools, 
  Check, 
  Star, 
  Monitor,
  UserFilled
} from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  components: {
    AppLayout,
    VideoPlay,
    Trophy,
    Clock,
    Medal,
    Setting,
    Lock,
    Tools,
    Check,
    Star,
    Monitor,
    UserFilled
  },
  setup() {
    const { t } = useI18n()
    const loading = ref(false)
    
    const isAdmin = computed(() => authService.isAdmin())
    
    const stats = ref({
      activeCourses: 0,
      completedCourses: 0,
      hoursStudied: 0,
      certificates: 0
    })

    const loadUserStats = async () => {
      const currentUser = authService.getCurrentUser()
      if (!currentUser) return

      loading.value = true
      try {
        // Data loading disabled - Supabase removed
        // Пока используем mock данные
        stats.value = {
          activeCourses: 3,
          completedCourses: 5,
          hoursStudied: 120,
          certificates: 2
        }
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadUserStats()
    })

    const activeCourses = ref([
      {
        id: 1,
        title: 'Компрессорная станция WKC1',
        icon: 'Setting',
        progress: 65
      },
      {
        id: 2,
        title: 'Промышленная безопасность',
        icon: 'Lock',
        progress: 30
      },
      {
        id: 3,
        title: 'Техническое обслуживание',
        icon: 'Tools',
        progress: 80
      }
    ])

    const recentActivity = ref([
      {
        id: 1,
        title: 'Завершен урок "Основы эксплуатации КС"',
        icon: 'Check',
        time: '2 часа назад'
      },
      {
        id: 2,
        title: 'Получен сертификат по безопасности',
        icon: 'Medal',
        time: '1 день назад'
      },
      {
        id: 3,
        title: 'Начат курс "Экологическая безопасность"',
        icon: 'VideoPlay',
        time: '3 дня назад'
      }
    ])

    const achievements = ref([
      {
        id: 1,
        title: 'Первые шаги',
        description: 'Завершили первый урок',
        icon: 'Trophy'
      },
      {
        id: 2,
        title: 'Упорный ученик',
        description: 'Изучили 10 часов',
        icon: 'Medal'
      },
      {
        id: 3,
        title: 'Сертифицированный специалист',
        description: 'Получили первый сертификат',
        icon: 'Medal'
      }
    ])

    const recommendedCourses = ref([
      {
        id: 4,
        title: 'Эксплуатация газопровода',
        description: 'Полный курс по эксплуатации газотранспортной системы',
        icon: 'Setting'
      },
      {
        id: 5,
        title: 'Экологическая безопасность',
        description: 'Охрана окружающей среды при эксплуатации газопровода',
        icon: 'Star'
      },
      {
        id: 6,
        title: 'Системы автоматизации',
        description: 'Работа с системами автоматизации и контроля',
        icon: 'Monitor'
      }
    ])

    return {
      isAdmin,
      loading,
      stats,
      activeCourses,
      recentActivity,
      achievements,
      recommendedCourses,
      loadUserStats
    }
  }
}
</script>
